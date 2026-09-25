# Decisions log

The brief says: when unclear, decide, write it down, explain why. These are those decisions.

## 1. Changed the question from "who has most volume" to "who does the work"
**What:** Headcount is measured by the team whose agent *resolved* the ticket, not the bot's
routing tag.
**When:** First hour, after reading Sameer's email (the tag is set by the bot and rarely
corrected) and Neha's (Billing says half its queue isn't theirs).
**Why:** Priya's rule ("most volume gets the hires") is only as good as the volume number. The
tag says Billing is 21%; the resolving team says 15%, and Logistics goes from 16% to 22%.
Answering the literal question would have confirmed a wrong hiring decision.

## 2. Pushed back on the hires, kept the chart
**What:** We still deliver the monthly chart by category and by team, as asked, but side by
side (bot view vs real view), and the memo recommends holding the Billing hires.
**Why:** Arjun explicitly prefers fixing a process to hiring into it, and the data shows the
process that needs fixing. We did not refuse the ask; we answered it properly.

## 3. The headline rupee figure counts only one, unambiguous mistake
**What:** Rs 2.1 lakh/yr = Billing-to-Logistics misroutes x (Rs 305 transfer + excess Rs 350
breach credits). All cross-team hand-offs (Rs 3.2 lakh/yr) are reported separately, not used.
**Why:** Some hand-offs are legitimate escalations (Frontline -> Warranty). Counting them would
inflate the number. A smaller number that survives Finance's scrutiny beats a bigger one that
doesn't.

## 4. Rupees reported on the export, scaled figure shown alongside
**What:** The export has ~180 tickets/week; the brief quotes ~650/week. We report the figure
from the data (Rs 2.1 lakh) and state the scaled one (Rs 7.8 lakh) as conditional.
**Why:** We don't know whether the export is a sample. Stating both, with the assumption named,
lets Priya pick.

## 5. Classifiers only see the customer's opening message when evaluated
**What:** `evaluate` uses intake mode (no agent notes). `categorise` uses message + agent note.
**Why:** The fix is at intake, where agent notes don't exist yet. Testing with notes would
overstate how well routing could work. For historical reporting, notes make labels more accurate.

## 6. Ground truth = resolving team, plus 100 hand labels
**Why:** The resolving team is available for every ticket and is set by humans, but it penalises
legitimate escalations. Hand labels are the real truth but slow. Using both shows the error rate
and its direction.

## 7. Kept a keyword baseline, even though it loses
**Why:** It runs without a key (the tool must start on a clean machine) and it is the bar the
LLM must beat. It scores 68% vs the bot's 91% on routing, which is also a finding: this text is
too messy (Hinglish, typos, "I want my money back" added to everything) for keywords.

## 8. Dropped 139 tickets before Jan 2025; shifted legacy times by +5:30
**Why:** The brief states the window. Policy §9 states the legacy timestamps are UTC, and the
data confirms it: 2,379 tickets resolved "before" creation, and exactly 0 after the shift.

## 9. Not committing client data to a public repo
**What:** `data/` is gitignored; the README says to copy the pack in.
**Why:** It's customer data. Even for an exercise, the habit matters.

## 10. Gemini Flash-Lite, batches of 20, cached
**Why:** The task is simple classification with a fixed list, so the cheapest model is enough.
Batching sends the instructions once per 20 tickets. The cache means reruns and interruptions
cost nothing.

## 11. Two yardsticks, and they disagree, which is the point
**What:** Against "who resolved it" (300 tickets) the bot wins, 91% vs 73%. Against 100 careful
labels the AI wins, 91% vs 71% (team level).
**Why we trust the labels more:** a ticket stays with whoever it was routed to unless someone
bothers to transfer it, so "who resolved it" is partly *caused by* the bot's routing. Reading the
AI's 81 "misses", 48 were Frontline agents handling specialist tickets themselves.
**Caveat:** the 100 labels were produced by Claude, not a person, and Claude also helped write
prompt v2. Stated openly in the form; a human re-label is the first follow-up.

## 12. No prompt v3
The labels exposed a wrong rule in v2 ("wrong item" → Delivery; Vireo's Returns Desk owns it).
Fixing it is a one-line change, but re-running and re-scoring would push past the time cap, so
it is documented instead.
