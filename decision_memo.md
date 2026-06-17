# Decision Memo

**From:** Analytics
**To:** VP of Product
**Re:** `exp_201_pdp_strikethrough` — PDP strikethrough pricing read-out
**Date:** 2026-05-30

## Recommendation: **Hold the global ship. Run a monitored, apparel/beauty-only confirmatory rollout.**

The top-line lift is real. But it breaches a guardrail we committed to before the test, and no single category clears the bar on its own — so the disciplined call is not "ship it everywhere," and not "kill it." It's a narrow, instrumented rollout that banks the upside where the evidence concentrates while we confirm the cost.

## Findings

**1. The primary metric won — clearly.**
Customer-level conversion 3.82% → 4.27%, a **+11.8% relative lift** (Z = 2.56, two-tailed **p = 0.010**, 95% CI **+2.8% to +20.9%** — excludes zero). Enrollment ran 28 days (2026-05-01 → 05-29); a customer is credited a conversion if they place ≥1 paid order within **7 days of their own assignment**. SRM passed (50.1/49.9, χ² p = 0.67); exposure balanced at ~92% both arms; no peeking. The Z sits in the believable 2–3 band — a real effect, not a seeding artefact.

**2. The effect is directional by category, but not proven per-segment.**
Sorted by point estimate: home +17% (p = 0.071), apparel/beauty +14% (p = 0.019), electronics −3% (p = 0.80). The lift concentrates in apparel/beauty and reverses on electronics — the brand team's worry about premium is real. **But with a Bonferroni correction across the 9 segment tests (α ≈ 0.006), none of these survive** — the experiment is powered for the overall effect, not for slicing. This is a genuine heterogeneous effect (the aggregate agrees with most segments; it isn't a Simpson's averaging artefact), but at the segment level it is a *signal to confirm*, not a result to bank. That distinction is why the rollout below is confirmatory.

**3. Two guardrails breach the pre-registered tolerance.**
- **Refund rate: 1.04% → 2.06%** (+1.0pp, ≈ doubles) — deal-seekers return more.
- **30-day repeat: 22.6% → 19.0%** (−3.5pp) — a brand-erosion signal.
- AOV ₹2,927 → ₹2,693 (smaller baskets); payment-failure ~flat (sanity OK).

**This breaches the pre-registered refund gate** (committed tolerance +≤0.3pp; observed +1.0pp) and the repeat gate (−≤1pp; observed −3.5pp). I am **not** weakening the rule after the fact — the rule says a breach blocks an unconditional ship, so we don't ship unconditionally. The refund lift rides the same deal-seeker traffic that drives the conversion win, so the rollout gates **each segment on its own refund trajectory** rather than the blended number. The lift is real, but it is *not* free conversion — which is exactly why this ends in a narrow, monitored rollout instead of a global on/off.

**4. The money, roughly** (directional sizing, not a booked forecast: incremental converters × AOV × ~30% contribution margin, netted against the added refund cost):
- **Apparel/beauty (+14%):** the lift clears the refund drag comfortably — this is where the incremental margin lives and what justifies a rollout at all.
- **Home (+17%, held):** positive point estimate but its CI crosses zero — not enough signal to commit; revisit with more data.
- **Electronics (−3%, held):** shipping here would cost money twice — no conversion gain, plus higher refunds and a dented premium repeat-rate. Holding it protects value; it isn't timidity.
- **Cost of the wrong global call:** "ship everywhere" trades away electronics margin to chase an apparel win; "kill everywhere" leaves the apparel lift on the table. The per-segment call captures the upside and avoids the drag — that gap *is* this memo's value.

**5. Operational risk: low.** A front-end price-block change behind one feature flag; instant rollback. No payment-path or latency risk (failure rate flat).

## Rollout plan
- **Week 1:** apparel/beauty at 100%, as a **confirmatory** rollout — it both captures the lift and re-tests it on fresh traffic. Instrument the refund kill-switch from day one.
- **Monitoring / rollback trigger:** **pause apparel/beauty if its refund rate exceeds 3.0% sustained 3+ days.** Watch 30-day repeat weekly.
- **Hold:** home (underpowered — collect more data before committing) and electronics (clean pricing stays).
- **No global ship** until the apparel/beauty confirmatory read clears both conversion and the refund/repeat guardrails at 30–60 days.

## Limitations
- **Novelty effect:** a discount frame can inflate *early* lift; we cap enrollment at 28 days to limit it and schedule a 90-day re-read to see what survives.
- **Underpowered segments:** the test is sized for the overall effect; segment verdicts are directional, which is precisely why the rollout is confirmatory rather than a per-segment commit.
- **Repeat-rate read is early** at 30 days — confirm at 60–90 before treating brand-erosion as settled.
- **Cross-device:** ~5–10% of users may see mixed variants (anonymous→login); likely dilutes the measured effect (conservative).
- **Synthetic dataset:** runs on seeded data (see README); production would re-confirm the baseline and category split, which can move the per-segment calls.

## Follow-up
- 30/60/90-day read on the apparel/beauty rollout: did the lift survive novelty, and did refunds and repeat-rate hold within trigger?
- Premium-electronics creative test ("member price" vs strikethrough vs clean) as exp 202.
- Refund-rate-by-discounted-SKU dashboard as a standing guardrail.
