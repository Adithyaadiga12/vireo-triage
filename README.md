# Vireo Audio — support ticket triage

Re-categorises Vireo's support tickets with Gemini, compares the result with the chat bot's
tags and with the team that actually resolved each ticket, and puts a rupee figure on the gap.

**Headline:** 29% of tickets the bot sends to Billing are delivery problems that Logistics ends
up resolving. Fixing that routing is worth about **Rs 2.1 lakh a year** on the exported data
(about Rs 7.8 lakh if the export is a sample of Vireo's ~650 tickets/week), and it removes the
case for two Billing hires (Rs 9 lakh a year). See `docs/memo.md`.

## Run it (about 5 minutes)

Needs Python 3.10 or newer.

```bash
# 1. Get the code and install
git clone <this repo> && cd vireo-triage
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. Put the data pack in data/
#    tickets.csv, agents.csv, orders.csv, customers.csv, products.csv, support-policy.pdf

# 3a. No API key? Everything except Gemini still runs:
python -m triage --engine rules all

# 3b. With a Gemini key (free at https://aistudio.google.com):
cp .env.example .env               # then paste your key into .env
python -m triage all               # ~45 Gemini calls, costs well under Rs 5
```

Results land in `outputs/`. Start with `outputs/summary.md`, `outputs/evaluation.md` and the
three `chart_*.png` files.

Run the tests (no key or network needed): `python -m pytest -q`

## Commands

| Command | What it does | Calls Gemini? |
|---|---|---|
| `python -m triage analyse` | Cleans the data, computes the headline numbers, draws the team charts | No |
| `python -m triage evaluate` | Scores the bot, keyword baseline, and Gemini prompts v1 and v2 on the same 300 tickets | Yes |
| `python -m triage label-sheet` | Writes 100 tickets to `outputs/hand_labels.csv` for hand labelling | No |
| `python -m triage categorise [--all]` | Re-categorises tickets and draws the monthly-by-category chart | Yes |
| `python -m triage all` | analyse + evaluate + categorise | Yes |

Add `--engine rules` before the command to use the free keyword baseline instead of Gemini.
Gemini answers are cached in `outputs/cache/`, so re-running never pays twice.

## How it works

```
data/*.csv ──> data.py (clean) ──> analysis.py (numbers) ──> charts.py (PNGs)
                               └─> classify_llm.py (Gemini)  ─┐
                               └─> classify_rules.py (free)   ├─> evaluate.py (scorecard)
                                   bot tag (from the export)  ┘
```

| File | Responsibility |
|---|---|
| `triage/config.py` | Every number that could change: costs, SLA targets, model, batch size |
| `triage/taxonomy.py` | The 11 categories and which team owns each (policy §6) |
| `triage/data.py` | Loads the export and fixes its known problems, logging each fix |
| `triage/classify_llm.py` | Gemini: batches of 20, JSON output, cache, retries, token-cost counter |
| `triage/classify_rules.py` | Keyword baseline: the bar Gemini must beat, and a no-key fallback |
| `triage/evaluate.py` | Scorecard vs resolving team; hand-label sheet and scoring |
| `triage/analysis.py` | Team share, workload per agent, misroute cost |
| `triage/charts.py` | The three charts |
| `prompts/classify_v1.txt`, `v2.txt` | Prompt versions, kept side by side so they can be compared |

## Data problems found and how they are handled

1. **Legacy resolution times are in UTC** (policy §9). 2,379 tickets appeared to resolve before
   they were created. Legacy `resolved_at` is shifted +5:30; afterwards there are 0.
2. **139 tickets fall before Jan 2025**, outside the stated window. They are dropped.
3. **Two agents share the name "Om Sharma".** Every join uses `agent_id`.
4. **`transfers` is blank, not zero, on legacy rows.** Routing is judged by *assigned team vs
   resolving team*, which exists for every ticket.
5. **The roster is "one row per assignment"**, so the resolving team is matched by date. In
   this export every agent has exactly one row, but the code handles moves.
6. **Legacy refund amounts are in a different unit** (policy §9); about 120 look ~12x too small.
   Refund value is not used in any headline number, so this is flagged, not fixed.

Design decisions and their reasons are in `docs/decisions.md`.
