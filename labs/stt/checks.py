"""Targeted semantic checks for the teaching decoder and scorer."""
import itertools
import numpy as np
import torch
from lab import collapse,edits,Recognizer,batch,features
from probes import beam_decode
assert collapse([8,8,0,8])=='77'
assert collapse([1,1,0,1])=='00'
assert collapse([0,0])==''
assert edits('007','07')==1
assert edits('7','7777')==3
assert edits('183','')==3
p=torch.tensor([[.4,.35,.25],[.3,.3,.4],[.4,.2,.4]]).log()
totals={}
for path in itertools.product(range(3),repeat=3):
 text=collapse(list(path));prob=float(sum(p[t,v] for t,v in enumerate(path)).exp())
 totals[text]=totals.get(text,0)+prob
assert beam_decode(p,width=100)==max(totals,key=totals.get)
model=Recognizer();x=torch.randn(2,19,129);p,n=model(x,torch.tensor([19,11]));assert n.tolist()==[5,3]
print('Decoder, edit-distance, beam aggregation and length checks passed.')
