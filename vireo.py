"""Vireo support-ticket digest, leaderboard and remedy-leak finder.
Usage: python vireo.py --data DIR [--out out] [--week YYYY-MM-DD(Monday)]
DIR holds tickets.csv agents.csv orders.csv customers.csv products.csv (file names may carry a prefix)."""
import argparse, glob, os, numpy as np, pandas as pd
from classify import classify
SLA_H={'chat':.25,'voice':2,'social':4,'email':8}
CONTACT_COST={'chat':210,'email':260,'voice':520,'social':240}

def find(d,name):
    f=glob.glob(os.path.join(d,f'*{name}.csv')); assert f,f'missing {name}.csv'; return f[0]

def load(d):
    t=pd.read_csv(find(d,'tickets'));a=pd.read_csv(find(d,'agents'));o=pd.read_csv(find(d,'orders'))
    p=pd.read_csv(find(d,'products'));c=pd.read_csv(find(d,'customers'))
    # 1. dedupe: legacy tickets re-imported into helpdesk appear twice; keep the helpdesk copy
    t['_p']=(t.source_system=='helpdesk').astype(int)
    t=t.sort_values(['ticket_id','_p'],ascending=[True,False]).drop_duplicates('ticket_id').drop(columns='_p')
    for col in ['created_at','first_response_at','resolved_at']: t[col]=pd.to_datetime(t[col])
    # 2. legacy resolved_at is UTC -> IST
    m=(t.source_system=='legacy_fd')&t.resolved_at.notna(); t.loc[m,'resolved_at']+=pd.Timedelta(hours=5,minutes=30)
    # 3. legacy CSAT 0 = no response
    t.loc[(t.source_system=='legacy_fd')&(t.csat_score==0),'csat_score']=np.nan
    t['fr_h']=(t.first_response_at-t.created_at).dt.total_seconds()/3600
    t['breach']=t.fr_h>t.channel.map(SLA_H)
    r=[classify(x,y) for x,y in zip(t.customer_message,t.agent_notes.fillna(''))]
    t['issue']=[i.rstrip('*') for i,_ in r]; t['text_category']=[c_ for _,c_ in r]
    t['retagged']=(t.text_category!=t.category)&(t.issue!='unclassified')
    return t,a,o,p,c

def remedy_leaks(t,p,o):
    """Orders where Vireo paid out more than one legitimate remedy.
    leak = refunds above the order value  +  replacement cost (unit cost + Rs 340) when a refund was also paid (policy s5: never both)."""
    k=t[t.order_id.notna()].merge(p[['sku','unit_cost_inr']],left_on='product_sku',right_on='sku').merge(o[['order_id','order_value_inr']],on='order_id')
    k['rep_cost']=np.where(k.replacement_issued=='Y',k.unit_cost_inr+340,0)
    k=k[(k.refund_amount_inr.fillna(0)+k.rep_cost)>0].sort_values('created_at')
    g=k.groupby('order_id').agg(tickets=('ticket_id',lambda s:', '.join(s)),n=('ticket_id','size'),
        teams=('assigned_team',lambda s:' + '.join(dict.fromkeys(s))),reasons=('refund_reason_code',lambda s:','.join(s.dropna())),
        refunds=('refund_amount_inr','sum'),replacements=('replacement_issued',lambda s:(s=='Y').sum()),rep_cost=('rep_cost','sum'),
        order_value=('order_value_inr','first'),first=('created_at','min'))
    g['over_refund']=(g.refunds-g.order_value).clip(lower=0)
    g['leak_inr']=g.over_refund+np.where((g.refunds>0)&(g.replacements>0),g.rep_cost,0)
    g['type']=np.select([(g.refunds>0)&(g.replacements>0),g.over_refund>0],['refund+replacement','refunded above order value'],'')
    g.attrs['remedied_orders']=len(g)
    return g[g.leak_inr>0].sort_values('leak_inr',ascending=False).assign(remedied_orders=len(g))

def leaderboard(t,a,weeks=12):
    end=t.created_at.max().normalize(); start=end-pd.Timedelta(weeks=weeks)
    d=t[t.status.isin(['resolved','closed'])&(t.resolved_at>=start)&(t.resolved_at<=end)].merge(a[['agent_id','name','team','tier','site','shift']],on='agent_id')
    d['wk']=d.resolved_at.dt.to_period('W')
    # repeat: same customer+sku+issue again within 30d after this ticket
    x=t.sort_values('created_at').copy(); x['nxt']=x.groupby(['customer_id','product_sku','issue']).created_at.shift(-1)
    x['repeat30']=(x.nxt-x.created_at).dt.days<=30; d=d.merge(x[['ticket_id','repeat30']],on='ticket_id')
    d['days']=(d.resolved_at-d.created_at).dt.total_seconds()/86400
    rows=[]
    for (aid,nm,team,tier,site,shift),g in d.groupby(['agent_id','name','team','tier','site','shift']):
        wk=g.groupby('wk').size().reindex(pd.period_range(start,end,freq='W'),fill_value=0)
        rows.append(dict(agent_id=aid,name=nm,team=team,tier=tier,site=site,shift=shift,closed_per_week=round(wk.median(),1),
            closed_total=len(g),repeat_rate_30d=round(g.repeat30.mean(),3),csat_avg=round(g.csat_score.mean(),2),csat_n=int(g.csat_score.notna().sum()),median_days_to_resolve=round(g.days.median(),1)))
    r=pd.DataFrame(rows)
    return r

def digest(t,o,p,week_start,leaks):
    ws=pd.Timestamp(week_start); we=ws+pd.Timedelta(days=7)
    w=t[(t.created_at>=ws)&(t.created_at<we)]; prev=t[(t.created_at>=ws-pd.Timedelta(weeks=4))&(t.created_at<ws)]
    L=[f'# Weekly support digest — week of {ws:%d %b %Y} to {(we-pd.Timedelta(days=1)):%d %b %Y}\n']
    L.append(f'**{len(w)} tickets** (prior 4-week average {len(prev)/4:.0f}). First-response breach rate {w.breach.mean():.1%} (prior {prev.breach.mean():.1%}). '
             f'Each breach auto-issues a Rs 350 credit: about Rs {int(w.breach.sum()*350):,} this week.\n')
    def top(df): return df[df.issue!='unclassified'].issue.value_counts()
    cw,cp=top(w),top(prev)/4
    L.append('## What people complained about (from the customer\'s own words, not the intake tag)\n')
    L.append('| Issue | This week | 4-wk avg | Change |\n|---|---|---|---|')
    for i,n in cw.head(10).items():
        b=cp.get(i,0); L.append(f'| {i.replace("_"," ")} | {n} | {b:.1f} | {"+" if n>=b else ""}{n-b:.1f} |')
    rising=[(i,n,cp.get(i,0)) for i,n in cw.items() if n>=8 and n>=1.5*max(cp.get(i,0),1)]
    L.append('\n**Rising:** '+(', '.join(f'{i.replace("_"," ")} ({n} vs {b:.0f})' for i,n,b in rising) if rising else 'nothing above the 1.5x-and-8-tickets threshold.'))
    L.append(f'\n**Tag quality:** {(w.category=="Other").mean():.0%} of tickets were tagged "Other" by the intake bot; {w.retagged.mean():.0%} carry a different issue in the customer\'s text than in the tag. {(w.issue=="unclassified").mean():.0%} could not be classified and need a human read.')
    hw=w.merge(o[['order_id','sku']],on='order_id',how='left')
    L.append('\n## Products with most complaints\n'+', '.join(f'{s} ({n})' for s,n in w.product_sku.value_counts().head(3).items()))
    ch=w.groupby('channel').breach.agg(['mean','size']); L.append('\n## SLA by channel\n'+'; '.join(f'{c} {r["mean"]:.0%} of {int(r["size"])}' for c,r in ch.iterrows()))
    lw=leaks[(leaks['first']>=ws-pd.Timedelta(weeks=8))&(leaks['first']<we)]
    L.append(f'\n## Remedy leaks to review\n{len(lw)} orders in the last 8 weeks were refunded above the order value or given a refund and a replacement, Rs {int(lw.leak_inr.sum()):,} at risk. Top 5 for Finance / Team Lead:\n')
    L.append('| Order | Tickets | Teams | Leak Rs |\n|---|---|---|---|')
    for oid,r in lw.head(5).iterrows(): L.append(f'| {oid} | {r.tickets} | {r.teams} | {int(r.leak_inr):,} |')
    L.append('\n*Caveats: issue labels come from keyword rules (see EVALUATION.md); open/pending tickets are included in volume; timestamps normalised to IST.*')
    return '\n'.join(L)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--data',required=True); ap.add_argument('--out',default='out'); ap.add_argument('--week')
    ar=ap.parse_args(); os.makedirs(ar.out,exist_ok=True)
    t,a,o,p,c=load(ar.data); leaks=remedy_leaks(t,p,o)
    ws=pd.Timestamp(ar.week) if ar.week else (t.created_at.max().normalize()-pd.Timedelta(days=t.created_at.max().weekday()+7))
    open(f'{ar.out}/digest.md','w').write(digest(t,o,p,ws,leaks))
    lb=leaderboard(t,a); lb1=lb[lb.tier==1].copy(); lb1['rank_in_team']=lb1.groupby('team').closed_per_week.rank(ascending=False,method='min').astype(int)
    lb1.sort_values(['team','rank_in_team']).to_csv(f'{ar.out}/leaderboard_tier1.csv',index=False)
    lb[lb.tier==2].to_csv(f'{ar.out}/tier2_resolution_days.csv',index=False)
    leaks.to_csv(f'{ar.out}/remedy_leaks.csv')
    t[['ticket_id','category','text_category','issue','retagged']].to_csv(f'{ar.out}/ticket_labels.csv',index=False)
    print(f'{len(t)} unique tickets | leaks: {len(leaks)} orders, Rs {int(leaks.leak_inr.sum()):,} | outputs in {ar.out}/')
if __name__=='__main__': main()
