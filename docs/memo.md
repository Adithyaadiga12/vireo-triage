**To:** Priya Raman, Head of Customer Experience, Vireo Audio  
**Cc:** Arjun Mehta, Neha Kulkarni, Sameer Qureshi  
**From:** Adithya Adiga (for Kabir Nanda, Banao)  
**Re:** Where the next two hires should go

---

**Short answer: not Billing, and possibly nobody yet.** Billing looks like the biggest queue
because the chat bot sends it tickets that are not billing problems. Fix that first. It costs
far less than two hires, and it will show where the real workload sits.

**What we found**

Your 22% figure for Billing is correct *by the bot's tag*. But the bot tags a ticket from the
customer's first words. When someone writes *"I paid, but my order hasn't arrived"*, it hears
"paid" and sends the ticket to Billing. Billing then passes it to Logistics.

Across Jan 2025 to Jun 2026, **about 3 in every 10 tickets sent to Billing were resolved by
Logistics.** The agents' own closing notes say so: *"not a billing issue, transferring to
logistics"*. Measured by who actually did the work:

| | By the bot's tag | By who resolved it |
|---|---|---|
| Billing | 21% of tickets | **15%** |
| Logistics | 16% of tickets | **22%** |

So Neha's view is supported by the data: Logistics carries the most work, about 32 tickets per
agent per month against Billing's 29 (Jan to Jun 2026).

*(Chart attached: "Logistics, not Billing, does the most work".)*

**What the wrong routing costs**

A ticket that goes to the wrong team first:

- takes **27 hours** to resolve instead of under 2 (median);
- misses its first-reply target **more than twice as often** (22% vs 9%), and each miss
  triggers the Rs 350 store credit;
- gets a satisfaction score of **2.6 out of 5 instead of 3.5**.

Using your policy's own costs (Rs 305 per internal transfer, Rs 350 per missed first reply),
the Billing-to-Logistics mix-up alone costs **about Rs 2.1 lakh a year** on the tickets we were
given. The export averages about 180 tickets a week; if Vireo's real volume is closer to 650 a
week, the same mistake costs **about Rs 7.8 lakh a year**. That excludes agent time and lost
customers, so treat it as a floor.

**The goal we propose**

> **Cut delivery tickets landing in Billing from 29% to under 5% within one quarter.** On the
> tickets we saw, that saves about **Rs 46,000 a quarter** (about Rs 1.7 lakh a quarter at 650
> tickets a week), and it stops a Rs 9 lakh-a-year hiring decision resting on a mislabelled number.

**What we recommend**

1. **Hold the two Billing hires.** This matches Arjun's request to fix the process before hiring
   into it.
2. **Change one step in the bot.** Before sending a "payment" conversation to Billing, ask *"Has
   your order arrived?"*. If not, send it to Logistics. Sameer can likely make this change in a
   day.
3. **Measure headcount by the team that resolves tickets, not by the bot's tag.** Our tool
   produces this report every month.
4. **Re-check in 8 weeks.** If Logistics is still the busiest team per agent, that is where the
   next hire should go, and the case will be solid enough for Arjun to sign.

**How sure are we?**

The core finding does not depend on AI: it comes straight from which agent closed each
ticket, and it holds in every quarter we looked at (26% to 31%). We also tested an AI
reader that reads the customer's first message the way the bot does. On 100 tickets we checked
one by one, it sent **91% to the right team; the bot managed 71%**. It costs about Rs 31 a month
at your volume. We suggest the one-step bot fix first because it is simplest, with the AI reader
as the next option if misrouting doesn't fall.

**What we did not look at:** refunds (the old system stored amounts in a different unit),
product-defect trends, and night-shift staffing. We can pick these up next if useful.
