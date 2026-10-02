# How we know it works, and how often it does not

## Issue classifier (digest)
Method: random samples of tickets, each label compared with my reading of the customer message. Labels were judged by me (with an AI assistant), **not** by a Vireo agent, so treat as an internal check.

| Round | Rules | Sample | Wrong | Unlabelled |
|---|---|---|---|---|
| 1 | first draft | 40 (seed 2026) | 10 (25%) | 2 |
| 2 | rewritten | 40 (seed 99) | 2 (5%) | 1 (2.5%) |

Main failure found in round 1: a trailing "I want my money back" made delivery, connectivity and battery complaints look like refund-status complaints. Round 2 failures: a delivery message with "refund" later in it (one rule line then fixed), watch touch-screen faults (no rule). After the last fix round 2 is no longer an unseen sample, so **plan on 5-8% wrong**; also expect errors on short vague messages ("it is not working"), mixed-issue messages, and Hinglish. `audit_sample.csv` is a blank 60-row sheet: Vireo should label it and run `evaluate.py score` for a number nobody on our side touched.

## Remedy-leak finder
Rule, not a model: group remedies by order_id. Leak = refund above order value, plus replacement cost (unit cost + Rs 340, policy s5) on orders that also got a refund. 199 orders flagged of 1,833 with any remedy. Not hand-verified one by one; 5 examples read end to end (e.g. VR889387: Rs 6,499 refunded as DUP-PAYMENT, again as RETURN-QC-OK, then a replacement unit). Gets wrong: partial refunds that legitimately sum to the order value (handled), refunds on orders with qty>1 where a separate unit is returned (could be over-flagged), and 35% of remedy tickets have no order_id so cannot be matched (under-flagged).

## Data checks
Dedupe (653 pairs), UTC shift, CSAT zero, one smoke test file. Unit test for the UTC bug asserts resolved_at >= created_at.

## Not verified
Leaderboard counts were reconciled to ticket totals only. Refund-unit (legacy "native unit") issue could not be seen in this export.
