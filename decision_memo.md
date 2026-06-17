# Decision Memo

**From:** Analytics
**To:** VP of Product
**Re:** `exp_201_pdp_strikethrough` — PDP strikethrough pricing read-out
**Date:** 2026-05-30

## Recommendation: **Ship to apparel/beauty & home. Hold electronics on clean pricing. Watch refunds in rollout.**

Strikethrough pricing wins where deal-framing helps and quietly hurts where it doesn't. Treating it as one global on/off switch would leave money on the table in fashion *and* erode the premium electronics line. Ship it where it works.

## Findings

**1. Statistically significant — and clean.**
Customer-level conversion 3.82% → 4.27%, a **+11.8% relative lift** (Z = 2.56, two-tailed p = 0.011). 95% CI on the lift: **+2.8% to +20.9%** — excludes zero. SRM passed (50.1/49.9, χ² p = 0.67), exposure balanced at ~92% both arms, no peeking. The Z sits in the believable 2–3 band, not the 70s — the result is real, not a seeding artefact.

**2. Practically significant — but concentrated.** The headline hides strong heterogeneity (after Bonferroni across 9 segment tests, α = 0.0056):
- **Apparel/beauty: +14%** — the engine of the result, significant.
- **Home: +17%** — also positive.
- **Electronics: −3%** — flat-to-negative. The brand team's worry is correct *for premium*: discount framing cheapens high-consideration goods.
This is **heterogeneity, not Simpson's paradox** (the aggregate isn't reversing the segments — electronics is simply a genuine exception).

**3. Guardrails — a real quality-of-revenue tradeoff, quantified.**
- **Refund rate: 1.04% → 2.06%** (≈ doubles) — deal-seekers return more.
- **30-day repeat: 22.6% → 19.0%** (−3.5pp) — a brand-erosion signal worth respecting.
- **AOV: ₹2,927 → ₹2,693** — smaller baskets under discount framing.
- **Payment-failure rate: ~flat** (1.6% → 1.7%) — sanity OK.
Net: the conversion lift is partly offset by lower repeat and higher refunds. It's still positive in apparel/beauty, but it is *not* free conversion — which is exactly why we don't ship it to electronics.

**4. Operational risk: low.** Front-end price-block change behind one feature flag; instant rollback. No payment-path or latency risk (failure rate flat).

## Rollout plan
- **Week 1:** ship to **apparel/beauty** at 100% (the strongest, clearly-significant segment).
- **Week 2:** extend to **home**; monitor refund rate daily — **pause any segment whose refund rate crosses 3.0% sustained 3+ days**.
- **Week 3+:** keep **electronics on clean pricing**; revisit only with a premium-specific creative (e.g. "member price" framing) as a *new* experiment.
- **Hold indefinitely:** global strikethrough — there is no one-size setting.

## Limitations
- **Novelty effect:** 28-day window may overstate the long-run lift by ~10–20%; schedule a 90-day post-launch read.
- **Cross-device misattribution:** ~5–10% of users may have seen mixed variants (anonymous→login). Likely dilutes (conservative) the measured effect.
- **Repeat-rate read is early:** the 30-day repeat signal is directional at this window; confirm at 60–90 days before treating brand-erosion as settled.
- **Synthetic dataset:** this sample runs on seeded data (see README); on production ecom you'd re-confirm the baseline and the category split, which can shift the segment verdicts.

## Follow-up
- 90-day post-launch read on apparel/beauty: did the conversion lift survive novelty, and did repeat-rate recover?
- Premium-electronics creative test ("member price" vs strikethrough vs clean) as exp 202.
- Refund-rate-by-discounted-SKU dashboard as an ongoing guardrail.
