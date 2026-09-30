"""Run bounded development probes with the saved offline model."""
import argparse,json,time
from pathlib import Path
import numpy as np
import torch
from lab import Recognizer,dataset,batch,evaluate,features,collapse

def beam_decode(logp, width=10):
    # Exact path expansion followed by prefix aggregation, pruned each frame.
    # State keeps last frame symbol because repeated-label collapse depends on it.
    states={("",0):0.0}
    for frame in logp.tolist():
        nxt={}
        for (text,last),score in states.items():
            for token,lp in enumerate(frame):
                output=text+(str(token-1) if token and token!=last else '')
                key=(output,token)
                nxt[key]=np.logaddexp(nxt.get(key,-np.inf),score+lp)
        totals={}
        for (text,last),score in nxt.items():totals[text]=np.logaddexp(totals.get(text,-np.inf),score)
        keep=set(sorted(totals,key=totals.get,reverse=True)[:width])
        states={k:v for k,v in nxt.items() if k[0] in keep}
    totals={}
    for (text,last),score in states.items():totals[text]=np.logaddexp(totals.get(text,-np.inf),score)
    return max(totals,key=totals.get)

def main():
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);p.add_argument('--run',type=Path,default=Path('run'));a=p.parse_args()
    torch.set_num_threads(4);model=Recognizer();model.load_state_dict(torch.load(a.run/'best.pt',weights_only=True));model.eval()
    rows=dataset(a.data,120,['yweweler'],19);result={}
    for snr in (20,10,0):
        changed=[]
        for i,r in enumerate(rows):
            noise=np.random.default_rng(17+i).standard_normal(r['audio'].shape).astype('float32');noise/=np.sqrt(np.mean(noise**2))
            audio=r['audio']+noise*np.sqrt(np.mean(r['audio']**2))*10**(-snr/20)
            changed.append(r|{'x':features(audio)})
        score=evaluate(model,changed);result[str(snr)]={k:v for k,v in score.items() if k!='predictions'}
    trace=[];r=rows[0]
    with torch.inference_mode():
        for samples in range(1600,len(r['audio'])+1600,1600):
            end=min(samples,len(r['audio']));f=features(r['audio'][:end]);p,n=model(f[None],torch.tensor([len(f)]))
            trace.append({'audio_ms':end/8,'hypothesis':collapse(p.argmax(-1)[:n[0],0].tolist())})
        x,n,_,_=batch(rows[:1]);p,l=model(x,n);greedy=collapse(p.argmax(-1)[:l[0],0].tolist());t=time.perf_counter();beam=beam_decode(p[:l[0],0]);beam_ms=(time.perf_counter()-t)*1000
    result['prefix_trace']={'reference':r['text'],'events':trace,'method':'offline prefix recomputation, not stateful streaming'}
    result['beam_probe']={'reference':r['text'],'greedy':greedy,'beam':beam,'width':10,'decode_ms':beam_ms,'scope':'one development example'}
    (a.run/'probes.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
