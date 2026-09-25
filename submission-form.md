# Submission form — Vireo Audio, Set E

> Only **[FILL]** left: honest hours.

---

### What did you build, and what business outcome does it move? State the number and the money.

A Python tool that re-reads every ticket with Gemini, labels its real category, and compares
three views of each ticket: the chat bot's tag, the AI label, and the team that actually
resolved it. It produces the monthly chart by category and by team that Priya asked for, in
two versions: the bot's view and the real one.

The outcome it moves: **cut delivery tickets misrouted to Billing from 29% to under 5%.** That
is worth **about Rs 46,000 a quarter** on the exported data (Rs 305 per transfer plus Rs 350
first-reply breach credits, both from policy §3–4), or about **Rs 1.7 lakh a quarter** if the
export is a sample of Vireo's ~650 tickets/week. More importantly, it stops a **Rs 9 lakh/year**
hiring decision (two Billing hires) that rests on a mislabelled number. By the resolving team,
Billing is 15% of work, not 22%, and Logistics is 22%, not 16%.

### What does one run cost, and what would a month cost at Vireo's volume (~650 tickets a week)? Show the arithmetic.

Model: `gemini-3.5-flash-lite`, paid-tier price $0.30 per 1M input tokens and $2.50 per 1M output
tokens (ai.google.dev pricing page, 24 Sep 2026). 20 tickets per call.

Measured on my run (from `outputs/evaluation.md`):
- Prompt v2, 300 tickets: 15 calls, 29,781 input + 11,645 output tokens = **$0.038 (about Rs 3.35)**.
- Per ticket: $0.038 / 300 = **$0.00013 (about 1.1 paise)**.
- Month at Vireo's volume: 650 × 52 / 12 ≈ 2,817 tickets × $0.00013 ≈ **$0.36 ≈ Rs 31 a month**.
- The whole `python -m triage all` run (v1 + v2 evaluation + categorising 300 tickets = 45 calls)
  cost $0.108 ≈ Rs 9.5.

On the free tier the actual cost is Rs 0. The keyword baseline and all analysis cost nothing.

### How do you know it works? Sample size, how you checked, error rate, and the kind of case it gets wrong.

Two checks on the same fixed random sample (seed 42):

1. **300 tickets vs the team that resolved them** (automatic, human-set signal). Only the
   customer's opening message goes to the model, which is what the bot sees at intake.

   | Method | Routing accuracy | Share of Billing queue that is really Billing |
   |---|---|---|
   | Bot tag (today) | 91% | 69% |
   | Keyword baseline | 68% | 49% |
   | Gemini prompt v1 | 69% | 62% |
   | Gemini prompt v2 | 73% | 65% |

   Gemini v2 catches **88% of delivery tickets** (the bot catches 70%). On this yardstick the bot
   looks better overall (91% vs 73%), but see check 2 for why this yardstick favours the bot.

2. **100 tickets with careful reference labels.** Honest disclosure: these were labelled by
   Claude (a different AI from Gemini), reading both the customer message and the agent's
   closing note, *without* seeing any prediction. They are not human labels, and I
   did not re-check them myself.

   | Method | Correct category | Correct team |
   |---|---|---|
   | Bot tag (today) | 70% | 71% |
   | Keyword baseline | 77% | 83% |
   | Gemini prompt v1 | 81% | 84% |
   | **Gemini prompt v2** | **88%** | **91%** |

   The resolving team itself agrees with these labels only 75% of the time, which confirms that
   "who resolved it" is a noisy yardstick that flatters the bot.

   **Error rate: Gemini v2 gets about 1 ticket in 10 wrong (12 of 100 categories, 9 of 100 teams).**

The kinds of case it gets wrong:
- **Against the 300-ticket "who resolved it" check (73%):** 48 of its 81 misses are tickets a
  Frontline agent resolved themselves, where Gemini named the specialist category ("payment
  deducted but no order" → Billing, "please cancel" → Returns). Gemini's label is usually right
  there; Frontline just didn't transfer it.
- **Against the 100 reference labels (12 wrong):**
  - 4 are "wrong item delivered" or "courier never came for the pickup". Vireo's Returns Desk owns
    these, but my prompt v2 told Gemini they were Delivery. **My rule was wrong**; a v3 prompt fixes it.
  - 3 are dead hardware that starts as a symptom ("left earbud not charging"). The labels used the
    agent's note, which says the unit was dead; from the first message alone "Charging & Battery"
    is a fair answer. Not fixable at intake.
  - 5 are genuine near-misses between neighbouring categories (Connectivity vs Audio vs App).
    These all go to the same Frontline team, so routing is unaffected.
- **The bot's 29 routing errors on the same 100:** 8 are delivery tickets sent to Billing (the
  finding), and 9 are cancellations or pickup problems left with Frontline instead of Returns.

### Did you change, narrow, or push back on the client's ask? What, when, and why.

Yes. In the first hour, after reading the email thread, I pushed back on "whichever team has the
most volume gets the hires". The volume number comes from the bot's tag, and 3 in 10 Billing
tickets are really delivery problems resolved by Logistics. I kept the requested chart but show
it both ways, and the memo recommends holding the Billing hires and fixing one step in the bot.
This aligns with Arjun's email ("I'd rather fix a process than hire into it").

I also narrowed the money claim to the one unambiguous mistake (Billing to Logistics) rather
than all hand-offs, because some hand-offs are legitimate escalations. Full log in
`docs/decisions.md`.

### What is wrong with what you are handing us? Be specific.

- The resolving team is a biased truth: it favours the bot (tickets stay where they were routed
  unless someone transfers them) and marks correct labels as wrong when Frontline handles a
  specialist ticket itself. 48 of Gemini's 81 "errors" are this. Accuracy vs resolving team
  understates Gemini and flatters the bot.
- Prompt v2 contains a rule that is wrong for Vireo: it sends "wrong item delivered" to Delivery,
  but Vireo's Returns Desk handles those (4 of the 100 labelled tickets). Not fixed, to stay
  within time.
- Gemini is only run on a 300-ticket sample, not all 11,641 tickets, to keep time and cost down.
  `categorise --all` does the full set (about Rs 130).
- The keyword baseline is weak (68%). It exists as a no-key fallback and a comparison, not as
  something to deploy.
- The Rs figures assume one transfer per misroute; the `transfers` field shows some tickets had
  two, so this is a floor.
- About 120 legacy refund amounts look ~12x too small (policy §9: different money unit). Not
  fixed, because refunds are not in any headline number.
- "Workload per agent" uses ticket counts, not handle time; Vireo's data has no effort field.
- The per-agent figures (~30 tickets/month) look low for a real desk, which supports the
  export being a sample.
- **The 100 reference labels were made by an AI (Claude), not a person, and the same AI helped
  write prompt v2.** Its idea of the categories may lean towards v2's rules, which could flatter
  v2. Two things limit this: the labels read the agent's note (Gemini did not), and on the
  "wrong item" rule the labels disagree with v2. A human re-label of these 100 is the first
  thing to do next.
- The USD to INR rate (88) is hard-coded and approximate.

### What did you deliberately leave out, and why that rather than something else?

- **Refund and replacement analysis.** I found agents flag `replacement_issued = N` on over 1,100
  tickets whose notes say "reshipped", and 19 tickets got both a refund and a reshipment (against
  policy §5). It is real money, but it is a different question from headcount, and the unit
  problem in legacy refunds needs care.
- **Product and lot defect trends.** Pulse 2 dominates volume since launch, but it also dominates
  sales. Separating defect rate from sales volume needs order-level work.
- **Night-shift and SLA staffing by hour.** Useful for *when* to add people, but Priya asked
  *which team*.
- **A web UI.** A command-line tool that runs beats a dashboard that might not.

I chose the misrouting story because it directly answers the question asked, it is backed by
two independent signals (resolving team and agent notes), and it changes a Rs 9 lakh decision.

### Anything you built or found that nobody asked for?

- Misrouted tickets take 27 hours to resolve instead of under 2, breach first-reply SLA 22% vs 9%,
  and score 2.6 vs 3.5 CSAT.
- SLA breaches are reported against the *resolving* agent (policy §3), so Logistics is blamed for
  late replies caused by the bot's misrouting.
- The legacy timezone bug: 2,379 tickets appeared to resolve before they were created.
- Replacement flag vs agent-note mismatch (above).
- "Who resolved the ticket" is not a clean truth for routing: tickets stay wherever the bot sent
  them unless someone transfers them, so it flatters the bot (91%) against careful labels (71%).
- A reusable monthly report: rerun `python -m triage analyse` on each month's export.

### What did you use AI for? Which tools and models, where they helped, where they wasted your time, what you threw away. Link your screen recording.

- **Claude (Anthropic, claude.ai):** used heavily. It explored the data with me, found the
  legacy timezone bug and the Billing/Logistics misrouting, wrote most of the Python code, tests
  and first drafts of the memo and these answers. I reviewed, ran and edited everything.
  It also produced the 100 reference labels used in the accuracy check (disclosed above).
  My part: I directed the work, set up and ran the tool on my own laptop with my Gemini key,
  reviewed the results and the memo, recorded the walkthrough, and published the repo. I did not
  write most of the code myself.
- **Gemini (`gemini-3.5-flash-lite`):** the classifier inside the tool.
- **Where it helped:** fast data exploration; spotting the UTC issue from the policy PDF.
- **Where it wasted time:** the first keyword rules (57% accuracy) needed rewriting because
  generic words like "money" and "paid" appear in every complaint. Getting the tool set up and running on Windows also took some back-and-forth.
- **What I threw away:** keyword rules v1 (57%) → v2 (68%), kept only as a baseline; prompt v1
  (category names only, 69%) in favour of v2 (definitions + rules for the paid-but-not-delivered
  case, 73%; delivery recall 68% → 88%); an "all hand-offs" cost figure (Rs 3.2 lakh), replaced by
  the narrower Billing-to-Logistics figure.

Screen recording: in the Drive folder: https://drive.google.com/drive/folders/1RwSC2NuWJ_mrgpu0PeMh3LpXs6tIJad7?usp=drive_link

### Your public Google Drive link
https://drive.google.com/drive/folders/1RwSC2NuWJ_mrgpu0PeMh3LpXs6tIJad7?usp=drive_link

### Someone picks this up on Monday and you are unreachable. The three things they need to know.

1. **The finding doesn't depend on the AI.** It comes from comparing `assigned_team` with the
   resolving agent's team (`python -m triage analyse`, free, 10 seconds). The AI adds
   better category labels on top.
2. **The data has traps, all handled in `triage/data.py`:** legacy `resolved_at` is UTC (+5:30),
   `transfers` is blank not zero on legacy rows, two agents share a name (join on `agent_id`),
   and legacy refunds are in a different unit.
3. **To extend it,** change `triage/taxonomy.py` (categories), `prompts/` (add `classify_v3.txt`
   and run `evaluate --prompts v2 v3`), or `triage/config.py` (costs, model). Gemini answers are
   cached in `outputs/cache/`; delete that folder to force fresh calls.

### Honest hours spent. One number.
**[FILL]**

### GitHub repo link
https://github.com/Adithyaadiga12/vireo-triage
