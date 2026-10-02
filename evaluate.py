"""Build a blind audit sample, then score it once a human has filled the human_issue column.
  python evaluate.py sample --data DIR --n 60 --seed 7   -> audit_sample.csv (human_issue blank)
  python evaluate.py score  --file audit_sample.csv      -> error rate"""
import argparse, pandas as pd, re
from vireo import load
ap=argparse.ArgumentParser(); ap.add_argument('cmd',choices=['sample','score']); ap.add_argument('--data'); ap.add_argument('--n',type=int,default=60); ap.add_argument('--seed',type=int,default=7); ap.add_argument('--file',default='audit_sample.csv')
a=ap.parse_args()
if a.cmd=='sample':
    t,*_=load(a.data); s=t.sample(a.n,random_state=a.seed)[['ticket_id','customer_message','issue']]
    s['customer_message']=s.customer_message.map(lambda x:re.sub(r'\s+',' ',x)); s['human_issue']=''; s.to_csv(a.file,index=False); print('wrote',a.file)
else:
    d=pd.read_csv(a.file).dropna(subset=['human_issue']); d=d[d.human_issue.str.strip()!='']
    ok=(d.issue.str.rstrip('*')==d.human_issue); un=d.issue=='unclassified'
    print(f'n={len(d)} wrong={(~ok&~un).sum()} unlabelled={un.sum()} error_rate={(~ok&~un).mean():.1%} error_or_unlabelled={(~ok).mean():.1%}')
