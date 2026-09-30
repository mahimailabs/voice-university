"""Small, offline digit-sequence CTC experiment. See README before interpreting results."""
import argparse, hashlib, json, platform, random, subprocess, time
from pathlib import Path
import numpy as np
from scipy.io import wavfile
import torch
from torch import nn
from torch.nn.utils.rnn import pad_sequence, pack_padded_sequence, pad_packed_sequence

SEED = 17
VOCAB = '_0123456789'  # blank is NOT a space or the digit zero

def features(audio):
    x = torch.tensor(audio, dtype=torch.float32)
    power = torch.stft(x, n_fft=256, hop_length=80, win_length=200,
                      window=torch.hann_window(200), center=False, return_complex=True).abs().square()
    x = power.clamp_min(1e-8).log().T
    return (x - x.mean()) / x.std().clamp_min(1e-5)  # offline, whole-utterance statistics

def collapse(path):
    return ''.join(VOCAB[v] for i, v in enumerate(path) if v and (i == 0 or v != path[i-1]))

def edits(reference, hypothesis):
    d = list(range(len(hypothesis)+1))
    for i, a in enumerate(reference, 1):
        e = [i]
        for j, b in enumerate(hypothesis, 1):
            e.append(min(d[j]+1, e[-1]+1, d[j-1]+(a != b)))
        d = e
    return d[-1]

def dataset(root, count, speakers, seed):
    rng = random.Random(seed)
    by_key, cache = {}, {}
    for p in sorted((root/'recordings').glob('*.wav')):
        digit, speaker, _ = p.stem.split('_')
        if speaker not in speakers: continue
        sr, a = wavfile.read(p)
        assert sr == 8000 and a.ndim == 1 and a.dtype == np.int16
        cache[p.name] = a.astype(np.float32) / 32768
        by_key.setdefault((speaker,digit), []).append(p.name)
    rows = []
    for i in range(count):
        speaker = rng.choice(speakers)
        text = ''.join(str(rng.randrange(10)) for _ in range(rng.randint(1,3)))
        names = [rng.choice(by_key[speaker,c]) for c in text]
        audio = np.concatenate([v for name in names for v in (cache[name], np.zeros(800,dtype=np.float32))])
        rows.append(dict(id=f'{seed}-{i}', speaker=speaker, text=text, files=names,
                         audio=audio, x=features(audio), y=torch.tensor([VOCAB.index(c) for c in text])))
    return rows

def batch(rows):
    return (pad_sequence([r['x'] for r in rows],batch_first=True),
            torch.tensor([len(r['x']) for r in rows]),
            torch.cat([r['y'] for r in rows]),torch.tensor([len(r['y']) for r in rows]))

class Recognizer(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv = nn.Sequential(nn.Conv1d(129,64,5,stride=2,padding=2),nn.ReLU(),
                                  nn.Conv1d(64,64,5,stride=2,padding=2),nn.ReLU())
        self.gru = nn.GRU(64,64,batch_first=True,bidirectional=True)
        self.head = nn.Linear(128,len(VOCAB))
    def forward(self, x, lengths):
        x = self.conv(x.transpose(1,2)).transpose(1,2)
        lengths = ((lengths+1)//2+1)//2
        x = pack_padded_sequence(x,lengths.cpu(),batch_first=True,enforce_sorted=False)
        x,_ = self.gru(x)
        x,_ = pad_packed_sequence(x,batch_first=True)
        return self.head(x).log_softmax(-1).transpose(0,1),lengths

@torch.inference_mode()
def evaluate(model, rows):
    model.eval(); predictions=[]; error=0; tokens=0
    for start in range(0,len(rows),16):
        chunk=rows[start:start+16]; x,n,_,_=batch(chunk); logp,lens=model(x,n)
        for r, path, length in zip(chunk,logp.argmax(-1).T.tolist(),lens.tolist()):
            hyp=collapse(path[:length]); error+=edits(r['text'],hyp); tokens+=len(r['text'])
            predictions.append(dict(id=r['id'],speaker=r['speaker'],reference=r['text'],hypothesis=hyp,files=r['files']))
    return dict(digit_error_rate=error/tokens,exact_match=sum(p['reference']==p['hypothesis'] for p in predictions)/len(predictions),
                edits=error,reference_digits=tokens,sequences=len(rows),predictions=predictions)

def main():
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);p.add_argument('--out',type=Path,default=Path('run'))
    p.add_argument('--epochs',type=int,default=12);p.add_argument('--threads',type=int,default=4);a=p.parse_args()
    torch.set_num_threads(a.threads);torch.manual_seed(SEED);random.seed(SEED);np.random.seed(SEED)
    a.out.mkdir(parents=True,exist_ok=True)
    train=dataset(a.data,600,['george','jackson','lucas','nicolas'],17)
    val=dataset(a.data,120,['theo'],18);test=dataset(a.data,120,['yweweler'],19)
    source_sets=[set(f for r in rs for f in r['files']) for rs in (train,val,test)]
    assert not(source_sets[0]&source_sets[1] or source_sets[0]&source_sets[2] or source_sets[1]&source_sets[2])
    manifest=[{k:v for k,v in r.items() if k not in ('x','y','audio')}|{'split':s} for s,rs in [('train',train),('validation',val),('test',test)] for r in rs]
    (a.out/'manifest.json').write_text(json.dumps(manifest,indent=2))
    model=Recognizer();opt=torch.optim.AdamW(model.parameters(),lr=.002);criterion=nn.CTCLoss(blank=0,zero_infinity=False)
    logs=[];best=float('inf');started=time.perf_counter()
    for epoch in range(1,a.epochs+1):
        model.train();order=list(range(len(train)));random.Random(SEED+epoch).shuffle(order);losses=[]
        for start in range(0,len(order),16):
            x,n,y,m=batch([train[i] for i in order[start:start+16]])
            opt.zero_grad();logp,lens=model(x,n);loss=criterion(logp,y,lens,m)
            if not torch.isfinite(loss): raise ValueError('Invalid CTC loss; check lengths and targets')
            loss.backward();nn.utils.clip_grad_norm_(model.parameters(),5);opt.step();losses.append(loss.item())
        score=evaluate(model,val); row=dict(epoch=epoch,train_loss=float(np.mean(losses)),validation_der=score['digit_error_rate'],validation_exact=score['exact_match'],elapsed_s=round(time.perf_counter()-started,3));logs.append(row);print(json.dumps(row),flush=True)
        if score['digit_error_rate']<best:
            best=score['digit_error_rate'];torch.save(model.state_dict(),a.out/'best.pt');best_epoch=epoch
    model.load_state_dict(torch.load(a.out/'best.pt',weights_only=True));result=evaluate(model,test)
    # Timing excludes features, training, file I/O and networking. Warm model, one utterance.
    x,n,_,_=batch(test[:1]); durations=[]
    with torch.inference_mode():
        for _ in range(3):model(x,n)
        for _ in range(30):
            t=time.perf_counter();model(x,n);durations.append(time.perf_counter()-t)
    result.update(parameters=sum(p.numel() for p in model.parameters()),best_epoch=best_epoch,training_seconds=logs[-1]['elapsed_s'],
                  forward_median_ms=float(np.median(durations)*1000),timed_audio_seconds=len(test[0]['audio'])/8000,
                  platform=platform.platform(),processor=platform.machine(),threads=a.threads,torch=torch.__version__,seed=SEED,
                  dataset_commit=subprocess.check_output(['git','-C',str(a.data),'rev-parse','HEAD'],text=True).strip(),
                  checkpoint_sha256=hashlib.sha256((a.out/'best.pt').read_bytes()).hexdigest())
    (a.out/'history.json').write_text(json.dumps(logs,indent=2));(a.out/'results.json').write_text(json.dumps(result,indent=2))
    # Export actual held-out examples with attribution supplied in README.
    for i,r in enumerate(test[:3]):wavfile.write(a.out/f'example-{i}.wav',8000,(r['audio']*32767).astype(np.int16))
    print(json.dumps({k:v for k,v in result.items() if k!='predictions'}),flush=True)
if __name__=='__main__':main()
