# Submission form

**1. What did you build, and what business outcome does it move?**
A rules-based Python tool (no API, no keys) that produces a weekly complaint digest, a Tier 1 leaderboard ranked within team, a Tier 2 days-to-resolve table, and a list of orders paid out twice. Business goal: **cut the share of remedied orders that are paid twice from 10.9% to 2% or less, i.e. double-remedy payouts (refund + replacement, or refunds above order value) from about Rs 98,000 a quarter to under Rs 20,000, saving about Rs 78,000 a quarter.** Source: 199 of 1,833 remedied orders (10.9%), Rs 5,88,119 over Jan 2025-Jun 2026 (6 quarters). Secondary: same-issue repeat contacts are 9.6% (1,076 of 11,266 closed tickets), about Rs 54,000 a quarter at Rs 290/contact.

**2. What does one run cost, and a month at ~650 tickets/week?**
Rs 0. No paid calls; a full run on 11,875 tickets takes about a minute on a laptop. If the rules were replaced by an LLM labeller (not built): 650 x 52 / 12 = 2,817 tickets/month x about 400 input + 20 output tokens = 1.13M input + 0.06M output tokens. At an assumed Haiku-class price of $1 / $5 per M tokens (verify current pricing): $1.13 + $0.28 = about $1.41, about Rs 120/month at Rs 85/$. Fixed ceiling, so no November surprise.

**3. How do you know it works?**
Classifier: two random samples of 40 tickets each, read by me against the rule label. Round 1 (first rules): 10/40 wrong (25%). Rules rewritten. Round 2: 2/40 wrong (5%), 1/40 unlabelled. One rule line fixed afterwards, so round 2 is no longer unseen: expect 5-8% wrong. Judged by me with an AI assistant, not by a Vireo agent. Gets wrong: short vague messages, mixed-issue messages, a delivery message mentioning a refund, watch touch faults, Hinglish. Remedy finder: 5 flagged orders read end to end; not all 199 checked. Data cleaning verified by smoke tests (unique IDs, resolved >= created, no CSAT zeros). `evaluate.py` plus a blank 60-row sheet lets Vireo measure it independently.

**4. Did you change, narrow, or push back on the ask?** **
Yes. (a) Leaderboard kept (Priya said it stays) but ranked within team, with repeat rate and CSAT beside volume; Tier 2 shown in days, per policy s6 and Neha's request. (b) Digest groups by the customer's text, not the bot tag (14% "Other", ~29% differ). (c) Business goal is not about reading tickets: Arjun said only contact or cost reduction earns its keep, so the headline is leak reduction. (d) Used Rs 290 per contact (policy), not Rs 180 (Arjun). (e) Left breaches off the leaderboard even though the policy reports them against the resolving agent: email morning/night breach ~15% vs ~7% on day shift, a staffing pattern.

**5. What is wrong with what you are handing us?** **
- The tool itself contains no AI model: it was built with AI help but classifies with keyword rules. The brief says 'AI-assisted'; if you want a model in the loop, `classify()` is the swap-in point (an LLM fallback for the 2% unlabelled tickets would cost well under Rs 10 a month) but I have not built or tested it.
- Classifier is keyword rules: ~5-8% wrong, brittle to new phrasing. 2% unlabelled.
- Audit labels were mine, not independent. Round 2 sample was partly tuned on.
- Export has ~190 tickets/week vs the client's 650; I did not scale rupee figures.
- 35% of remedy tickets have no order_id, so leaks are under-counted. Orders with qty>1 and separate returns may be over-counted.
- Leak target (-80%) is an assumption, not measured. Q2 2026 leaks may be under-counted because later tickets are not yet in the export.
- Refund "native unit" warning for legacy data: checked ratios to order value and duplicate pairs, found no sign of a unit difference; not proven.
- Repeat-contact match uses customer + SKU + issue; customers with two real issues of the same type are merged.
- Leaderboard median over last 12 weeks ignores part-weeks and roster changes (agent_id only, from/to dates not used).
- No UI; outputs are markdown and CSV. No customer-facing or weekly scheduler (cron needed).

**6. What did you deliberately leave out, and why?**
LLM classification (rules are free and good enough at this volume; Finance said no surprise bill). A dashboard (Priya: "I don't need a platform"). Product-lot defect analysis: I looked at lot codes and found no lot clearly above noise once recent lots were allowed for ticket lag, so it is not claimed. Breach-by-agent ranking (shift-driven). Sentiment scoring. A root-cause model for repeat contacts. I picked leak detection over these because it has a rupee figure and a clear owner.

**7. Anything you built or found that nobody asked for?**
Remedy-leak finder (Rs 5.9 lakh). Duplicate-ticket and UTC finding (653 duplicates, legacy resolution times 5.5h off). SLA credits Rs 3.7 lakh concentrated in email morning/night and voice night. Transfers cost Rs 3.6 lakh (1,169 x Rs 305). Check of the "I already told your colleague" claim: zero tickets use it; Logistics (13.5%) and Returns Desk (11%) highest, Chat (9%) about average. `evaluate.py` audit tool.

**8. What did you use AI for?**
Claude (chat, with code execution) to profile the data, write the pipeline, draft the memo. Helped: finding the duplicate/UTC/CSAT traps quickly; reading samples. Wasted time / thrown away: first classifier (25% wrong); a first "30% repeat contact" figure (customer+SKU only, inflated 3x; replaced by the policy's same-issue definition, 9.6%); a regex that matched "repeat myself" mic complaints as "told your colleague"; first leak number (Rs 6.5 lakh) that counted legitimate split refunds. Cost: whatever my Claude subscription costs; no API spend. Screen recording link: **[https://drive.google.com/file/d/1rJCWZSj4BjUFFlIrO3l6WQOpmc7yLJgz/view?usp=drive_link]**

**Public Google Drive link:** **[https://drive.google.com/file/d/1rJCWZSj4BjUFFlIrO3l6WQOpmc7yLJgz/view?usp=drive_link]**

**9. Someone picks this up on Monday and you are unreachable: the three things they need to know.**
1. `python vireo.py --data DIR` regenerates everything; README lists the cleaning rules (dedupe, UTC, CSAT zero) that must not be skipped.
2. The headline number is remedy leakage (Rs 98k/quarter): send `remedy_leaks.csv` to Arjun/Neha and get the "already refunded/replaced" check approved. The 650 vs ~190/week volume gap is unresolved.
3. Classifier is rules; have Vireo label `audit_sample.csv` and run `evaluate.py score` before anyone trusts the issue counts.

**10. Honest hours spent:** **[ADD YOUR NUMBER]** (about 5)

**11. GitHub repo link:** **[ADD YOUR LINK]**
