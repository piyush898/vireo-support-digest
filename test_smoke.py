"""Smoke tests: python test_smoke.py  (needs --data via env VIREO_DATA)"""
import os
from classify import classify
from vireo import load, remedy_leaks
def test_rules():
    assert classify('I want a refund. Nothing changed. tracking has said out for delivery for a week')[0]=='not_delivered'
    assert classify('the return was accepted but the amount is nowhere in my account')[0]=='refund_status'
    assert classify('Card charged two times')[0]=='dup_payment'
def test_data():
    t,a,o,p,c=load(os.environ['VIREO_DATA'])
    assert t.ticket_id.is_unique
    assert (t.resolved_at.dropna()>=t.created_at[t.resolved_at.notna()]).all()   # UTC bug would break this for early-morning tickets
    assert not (t.csat_score==0).any()
    assert len(remedy_leaks(t,p,o))>0
if __name__=='__main__': test_rules(); test_data(); print('ok')
