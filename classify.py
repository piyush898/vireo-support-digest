"""Rule-based issue classifier for Vireo tickets. First matching rule wins. Order matters.
Reads the customer's message first; falls back to the agent's closing note (label gets a '*' internally)."""
import re
RULES=[
('mic_issue',r'repeat myself|hear me|cannot hear me|mic(rophone)? (not|issue)|underwater|callers','Audio Quality'),
('dup_payment',r'paid once|statement disagrees|bank says|went to you but|charged (twice|two times)|double (charge|payment)|deducted|debited|upi (shows|success)|payment (went|was)|page failed after|failed after i paid|no order (id|confirmation)|still waiting for something to show','Billing & Payments'),
('coupon',r'coupon|promo|dis?count|dscount|20% off|your ad said','Billing & Payments'),
('cancel',r'cancel|stop t\w* ship\w*|by mistake|change of mind|don.?t ship|ordered the wrong colou?r','Billing & Payments'),
('address_change',r'change (of )?(delivery )?address|old flat|moved houses|wrong (address|pin)','Delivery & Shipping'),
('damaged_wrong',r'wrong (product|item)|got (white|black|blue|red)|ordered (black|white|blue|red)|different (colou?r|thing|product)|something else|not what i paid for|damaged|crack|dent|kicked|crushed|before i even switched','Delivery & Shipping'),
('invoice',r'invo+i?ce|gstin|\bgst\b|tax bill|the bill','Billing & Payments'),
('refund_status',r'refund (not|was|is|promised|status)|still waiting for my refund|money for the return|amount is nowhere|return was accepted|refund.{0,25}(delay|credited)','Returns & Refunds'),
('return_pickup',r'pickup|pick-up|pick up|return (request|label)|nobody came','Returns & Refunds'),
('warranty_repair',r'repair|warranty|\brma\b|rma\d|service cent|claim number','Warranty & Repair'),
('login',r'log ?in|otp|password|sign ?in|locked out|verification code|sent me a code|my account','Account & Login'),
('enquiry',r'compatible|work w(ith|/)|will (this|the|it) |can i connect|before i buy|survive|run on|talk to|waterproof','Product Enquiry'),
('not_delivered',r'not (been )?delivered|haven.t received|not received|tracking|out for delivery|courier|awb|parcel|shipment|waiting for (my|your)|still here|nobody in my house|nothing in hand|status stuck|stuck on shipped','Delivery & Shipping'),
('app_firmware',r'\bapp\b|firmware|after (the )?update|white screen|loading screen|progress bar|spinning|wifi setup','App & Firmware'),
('connectivity',r'pair|bluetooth|connect|disconnect|device list|losing my phone|vanish|see it in the list|stutter|cutting out','Connectivity'),
('battery',r'batter|charg|drain|lasts|dies by|dead every|light use|power bank|won.?t turn on|not powering|same battery level','Charging & Battery'),
('audio',r'sound|audio|hiss|crackl|static|bass|volume|silent|distort|decoration|one ear|left one|right one|does not wake up|frying|only the right','Audio Quality'),
('refund_generic',r'refund|money back','Returns & Refunds'),
]
def _n(s): return re.sub(r'\s+',' ',str(s).lower())
def classify(msg,note=''):
    m=_n(msg)
    for issue,pat,cat in RULES:
        if re.search(pat,m): return issue,cat
    n=_n(note)
    for issue,pat,cat in RULES:
        if issue!='refund_generic' and re.search(pat,n): return issue+'*',cat
    return 'unclassified','Other'
