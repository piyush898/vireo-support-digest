# Memo: what the support tickets are telling you

**To:** Priya Raman  **cc:** Arjun Mehta, Neha Kulkarni, Sameer Qureshi

Priya, short version: the weekly digest and the leaderboard you asked for are built and run in about a minute. Reading the tickets also turned up something nobody asked for, which is where the money is.

**1. We are paying some customers twice.** In 1,833 orders that received a refund or replacement, 199 (11%) were paid out more than once: either a refund plus a replacement unit (policy s5 says never both), or refunds adding up to more than the order was worth. That is Rs 5.9 lakh over 18 months, about **Rs 98,000 a quarter**. Typical pattern: Billing refunds a "double payment", then Returns Desk refunds the same order again, because neither can see the other's payout. **Goal: cut the share of remedied orders paid twice from 10.9% to 2% or less, which takes this from about Rs 98,000 to under Rs 20,000 a quarter, roughly Rs 78,000 saved per quarter**, by flagging any order that already has a remedy before a second one is approved. The finder produces the list weekly; `remedy_leaks.csv` is the first Rs 5.9 lakh to review with Arjun.

**2. The weekly digest.** It reads what customers actually wrote rather than the bot's tag. The bot files 14% of tickets as "Other", and in about 3 in 10 tickets the customer's words point to a different issue than the tag. Biggest steady complaints: orders not delivered, refund status, connectivity, app/firmware, double payments. Each week it lists what is rising against the last four weeks.

**3. The leaderboard, with two changes.** Tickets closed per week is there, but ranked within each team. Logistics closes about twice as many tickets as Chat per agent because the work is different, so one list would be misleading. Following Neha's request, Escalations & Warranty is shown on days to resolve, not counts. Each Tier 1 row also shows repeat-contact rate and CSAT next to volume, so closing fast and badly does not win.

**4. Two things we checked.** The "I already told your colleague" complaint: no ticket uses those words; about 6% mention an earlier contact ("fourth time writing"). Real repeat contacts (same customer, same issue, within 30 days) are 9.6%, costing about Rs 54,000 a quarter at Rs 290 per contact. They are highest in Logistics (13.5%) and Returns Desk (11%); Chat (9%) is about average, so Chat is not the problem. Separately, 8.9% of tickets miss their first-response target and each costs a Rs 350 credit (Rs 3.7 lakh in 18 months). Email on morning and night shifts misses about twice as often as day shift, a staffing issue, not an agent one, so we kept it out of the leaderboard.

**5. Caveats.** Your 650 tickets a week does not match the export (about 190 a week, after removing 653 duplicate migrated tickets). Our rupee figures use the export; if the export is a sample, scale up. Issue labels are about 5-8% wrong in our checks. Please have someone label the 60-row sample sheet. We used Rs 290 per contact (policy v3.2), not Rs 180. Running cost: Rs 0, no model calls.

**Decision needed:** approve a check for "order already refunded or replaced" in the refund workflow, and name someone in Finance to review the weekly leak list.
