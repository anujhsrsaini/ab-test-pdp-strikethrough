# Decision Memo

**From:** Analytics
**To:** VP of Product
**Re:** `exp_201_pdp_strikethrough` — PDP strikethrough pricing read-out
**Date:** 2026-05-30

## Recommendation: **Ship strikethrough to apparel/beauty (with a refund alarm). Hold electronics. Watch home.**

The change works — but not everywhere, and not for free. The disciplined call captures the lift where it's real and guards the downside, rather than flipping one global switch.

## Findings

**1. The lift is real and significant.**
Customer-level conversion 3.82% → 4.27%, a **+11.8% relative lift** (Z = 2.56, p = 0.010, 95% CI **+2.8% to +20.9%** — clears zero). Enrollment ran 28 days; a customer counts as converted if they placed ≥1 paid order within 7 days of assignment. The split came out 50/50 (sanity-checked first) and the Z sits in the believable 2–3 range — a real effect, not noise.

**2. It moves the North Star — revenue per customer — up ~2.9%.**
₹111.82 → ₹115.06. Directionally consistent with the conversion lift, which is what we'd want. Read it net of the refund and basket-size effects below before banking it.

**3. The win is concentrated by category.**
Apparel/beauty **+14% (significant)** — discount framing works on deal-seeking categories. Electronics **−3% (not significant)** — clean pricing is better for premium, high-consideration goods; the brand team's worry is right there. Home **+17% but not significant** (noisy) — promising, unproven. One headline number would have hidden all of this.

**4. The lift isn't free — two guardrails move the wrong way.**
- **Refund rate 1.04% → 2.06%** (≈ doubles) — deal-seekers return more.
- **30-day repeat 22.6% → 19.0%** (−3.5pp) — an early brand-erosion signal.
- AOV ₹2,927 → ₹2,693 (smaller baskets); payment-failure flat (sanity OK).
This is exactly why the recommendation ships *where the lift clears the cost* and watches refunds closely, rather than rolling out blindly.

**5. The money, roughly** (directional sizing: incremental converters × AOV × ~30% margin, net of the added refund cost):
- **Apparel/beauty:** the lift clears the refund drag comfortably — this is where the incremental margin is, and what justifies shipping.
- **Electronics:** shipping here would cost twice — no conversion gain *plus* higher refunds and a dented premium repeat-rate. Holding protects margin.
- **Cost of the wrong global call:** "ship everywhere" trades away electronics margin to chase an apparel win; "kill everywhere" leaves the apparel lift on the table. Targeting captures the upside and avoids the drag.

**6. Operational risk: low.** A front-end price-block change behind one feature flag; instant rollback. No payment-path or latency risk.

## Rollout plan
- **Week 1:** apparel/beauty at 100%, with the **refund kill-switch live from day one — pause if refund rate > 3.0% sustained 3+ days.**
- **Hold:** electronics (clean pricing stays); home (collect more data before committing).
- **Re-read at 30 / 60 / 90 days:** did the lift survive novelty, and did refunds and 30-day repeat hold within trigger? Expand only if yes.

## Limitations
- **Novelty effect** — a discount frame can inflate early lift; the 28-day cap limits it and the 90-day read confirms what survives.
- **Repeat-rate read is early** at 30 days — confirm at 60–90 before treating brand-erosion as settled.
- **Synthetic dataset** — runs on seeded data (see README); production would re-confirm the baseline and category split, which can move the per-category calls.

## Follow-up
- 30/60/90-day read on the apparel/beauty rollout.
- Premium-electronics creative test ("member price" vs strikethrough vs clean) as exp 202.
- Refund-rate-by-discounted-SKU view as a standing guardrail.
