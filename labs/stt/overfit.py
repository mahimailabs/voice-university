"""Memorise eight fixed examples to debug the pipeline, not measure generalisation."""
import argparse,json
from pathlib import Path
import torch
from lab import Recognizer,dataset,batch,evaluate
p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);p.add_argument('--out',type=Path,default=Path('overfit.json'));a=p.parse_args()
torch.manual_seed(17);torch.set_num_threads(4)
rows=dataset(a.data,8,['jackson'],17);model=Recognizer();opt=torch.optim.AdamW(model.parameters(),lr=.003);criterion=torch.nn.CTCLoss()
x,n,y,m=batch(rows)
for step in range(300):
 model.train();opt.zero_grad();p,l=model(x,n);loss=criterion(p,y,l,m);loss.backward();torch.nn.utils.clip_grad_norm_(model.parameters(),5);opt.step()
result=evaluate(model,rows);result['steps']=300;result['scope']='training examples only; no generalisation claim'
a.out.write_text(json.dumps(result,indent=2));print(result['exact_match'])
