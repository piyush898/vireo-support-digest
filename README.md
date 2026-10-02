# Vireo support digest + leaderboard + remedy-leak finder

Runs on a clean machine with Python 3.9+ and no API keys. No model calls, no cost.

```bash
pip install -r requirements.txt
python vireo.py --data /path/to/folder/with/the/csvs --out out
# optional: python vireo.py --data DIR --week 2026-06-22      (Monday of the week to digest)
VIREO_DATA=/path/to/csvs python test_smoke.py                 # 4 smoke checks
python evaluate.py sample --data DIR --n 60 --seed 7          # blank audit sheet for a human to label
python evaluate.py score --file audit_sample.csv              # error rate once human_issue is filled
```
`--data` folder needs tickets/agents/orders/customers/products .csv (filename prefixes are fine).

## Outputs (`sample_output/` is a committed example run)
| File | What |
|---|---|
| digest.md | Weekly digest: volume, top complaint issues vs 4-week average, rising issues, SLA, remedy leaks to review |
| leaderboard_tier1.csv | Tier 1 tickets closed/week (median, last 12 weeks), ranked **within team**, shown beside 30-day repeat rate and CSAT |
| tier2_resolution_days.csv | Escalations & Warranty, measured in days to resolve, not ranked on counts (policy s6; Neha's request) |
| remedy_leaks.csv | Orders paid out more than once: refund + replacement, or refunds above order value |
| ticket_labels.csv | Intake-bot tag vs issue read from the customer's text |

## Data cleaning decisions (all in `vireo.py: load`)
1. 653 ticket IDs appear twice (legacy_fd + helpdesk re-import). Keep the helpdesk copy -> 11,875 unique tickets from 12,528 rows.
2. Legacy `resolved_at` is UTC (policy s9); +5:30 to match IST. Without this 618 duplicate pairs disagree by 5.5h.
3. Legacy CSAT 0 = no response -> blank. Blank CSAT is excluded from averages, never zero.
4. Breach = first response later than channel target (chat 15m, voice 2h, social 4h, email 8h).
5. Refund amounts: legacy "native unit" warning checked; duplicate pairs and refund/order-value ratios (max 1.0) show no unit difference in this export, so no conversion applied. See limitations.

## Classifier
`classify.py`: ordered keyword rules over the customer's text, falling back to the agent note. 17 issue types. Deliberately not an LLM: the messages are templated + typos, rules are free, deterministic, auditable, and Finance asked for no per-ticket bill. Swap-in point for an LLM: `classify()`.
