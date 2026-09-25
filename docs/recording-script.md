# Screen recording script (max 3 minutes)

Record your screen with a voice-over. No slides. Show files and the terminal.

**0:00–0:20 — The finding.** Open `outputs/chart_team_share.png`.
> "Priya wants to hire for Billing because it's 22% of tickets. That number comes from the
> chat bot's tag. By who actually resolved the tickets, Billing is 15% and Logistics is 22%. The
> bot sends 'I paid but it didn't arrive' to Billing."

**0:20–0:50 — Prompt v1.** Open `prompts/classify_v1.txt`.
> "My first prompt just listed the category names. It got 69%, and it only caught 68% of
> delivery tickets, no better than the bot."

**0:50–1:40 — What changed in v2.** Open `prompts/classify_v2.txt`, scroll to the rules.
> "In v2 I added a one-line meaning for each category, and rules for the confusions I saw in the
> errors: paid-but-not-delivered is Delivery; ignore 'I want my money back' because customers
> add it to everything; refund after a return goes to Returns. I also send only the customer's
> first message, because the fix has to work at intake. v2 got 73%, and caught 88% of delivery tickets instead of 68%."

**1:40–2:20 — What I threw away.** Open `triage/classify_rules.py`.
> "Before the LLM I tried keyword rules. Version 1 got 57%: words like 'money' and 'paid' are in
> every complaint. Version 2 reordered the rules and got 68%, still far below the bot's 91%. I
> kept it only as a free fallback and a baseline. I also dropped my first cost figure, Rs 3.2
> lakh for all hand-offs, because some hand-offs are legitimate escalations. I kept the narrower
> Rs 2.1 lakh."

**2:20–2:50 — Proof.** Open `outputs/evaluation.md`.
> "Scored on 300 tickets against the team that resolved them. Honest result: Gemini is worse than
> the bot overall, 73% vs 91%, so I'm not recommending replacing the bot. But most of its 'errors'
> are Frontline agents handling billing or delivery tickets themselves, where Gemini's label is
> actually right. One real mistake of mine: my prompt
> sent 'wrong item delivered' to Delivery, but Vireo's Returns Desk handles those."

**2:50–3:00 — Close.**
> "Recommendation: hold the Billing hires, fix one step in the bot, re-measure in 8 weeks."
