# Test plan (pre-registered) — `exp_201_pdp_strikethrough`

> **Locked 2026-04-29, before any data was collected.** Pre-registration is the
> thing that makes the read-out trustworthy: the metric, the effect size, the
> decision rule, and the stopping rule are all committed *before* we can be
> tempted by the numbers. Nothing below was changed after launch.

## Experiment
- **ID / name:** `201` — PDP Strikethrough vs Clean Pricing
- **Surface:** Product Detail Page price block
- **Control:** current clean price (`₹1,499`)
- **Treatment:** struck-through MRP + savings badge (`₹1,499` ~~`₹1,999`~~ · Save 25%)
- **Window:** 2026-05-01 → 2026-05-29 (28 days)

## Hypothesis
**If** we show a strikethrough MRP and savings badge on the PDP, **then** customer-level
conversion will rise by **≥ ~13% relative (0.5pp absolute)**, **because** an explicit
discount frame creates urgency and a value signal at the decision point.
**Counter-hypothesis we are watching:** the same frame attracts deal-seekers who return
more and repeat less — so guardrails can veto a primary-metric win.

## Metrics
- **Primary (decision-gating):** customer-level conversion rate — did an assigned
  customer place ≥1 paid order within a **7-day** window of assignment.
- **Secondary (reported, not gated):** AOV, items/order, carousel/PDP engagement.
- **Guardrails (a regression can block ship):** refund rate, 30-day repeat-purchase
  rate (brand-erosion proxy), payment-failure rate (sanity).
- **North Star:** revenue per customer — the business metric the conversion lever
  ladders up to; reported alongside the guardrails, not gated on directly.

## Statistical plan
- **Randomization unit:** customer (`stable_user_id`) — analysis unit matches.
- **Allocation:** 50/50.
- **Baseline:** 3.9% customer-level CR (prior 30 days).
- **MDE:** 0.5pp absolute (~13% relative) — chosen from economics: the build is cheap
  (~one-time front-end change), so the bar is not break-even cost but *being sure the
  effect clears the guardrail risk*. We size to detect a clear, actionable effect.
- **α = 0.05** (two-tailed — the change can plausibly *hurt* conversion), **power = 0.80**.
- **Sample size:** ~24.5k per arm (~49k total). Test: two-proportion z-test.
- **Segmentation (pre-committed):** broken out by category (apparel/beauty · electronics ·
  home), device, and country — read for *where* the effect lives, not just whether.

## Decision rule (committed)
- **Ship** if: primary is significant (Z > 1.96) **AND** the guardrails hold (refund rate
  and 30-day repeat don't regress materially). If the lift is real but a guardrail moves,
  ship only where it clears both bars — not blindly across the board.
- **Stage / partial ship** if: primary is significant but a guardrail or a segment
  fails — ship only the segments that clear both bars.
- **Hold** if: primary not significant, or a guardrail breaches tolerance broadly.

## Stopping rule
Run to the planned sample size (28-day cap). **Don't stop early just because it looks
significant** — that inflates the false-positive rate. The cap also limits novelty
inflation. The analysis was written and reviewed before any data landed.

## Out of scope
- Cross-device identity stitching (~5–10% of users may see mixed variants) — accepted,
  noted in the README limitations.
