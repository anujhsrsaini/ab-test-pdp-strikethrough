# Design rationale

Why each design and statistical choice was made. The README is the *what*; this is
the *why* — the part that separates an experiment that holds up under questioning
from one that doesn't.

## Why this experiment
Strikethrough pricing is the canonical "two senior people disagree and need data"
problem: marketing believes the discount frame creates urgency and lifts conversion;
brand believes it cheapens the product and attracts deal-seekers who churn. Both have
anecdotes. It also has a built-in **heterogeneous effect** — it tends to help in
fashion and hurt for premium, high-consideration goods — which makes it a good vehicle
for showing segmentation done properly rather than a single headline number.

## Design decisions

| Decision | Choice | Why |
|---|---|---|
| Primary metric | customer-level conversion (7-day window) | one gating metric forces a real decision; the window matches the randomization grain |
| Randomization unit | customer, `SHA256(experiment_id:customer_id)`, salted per experiment | the analysis unit must match the randomization unit; the salt stops a user being structurally stuck in the same bucket across experiments |
| Allocation | 50/50 | maximises power per unit time; the treatment is low-risk (front-end only) |
| MDE | 0.5pp absolute (~13% relative) | derived from economics: the build is cheap, so the bar isn't break-even cost — it's being sure the effect clears the guardrail risk |
| α / power | 0.05 two-tailed / 0.80 | two-tailed because strikethrough can plausibly *hurt* conversion (premium goods) |
| Sample / duration | ~25k per arm, 28-day cap | powered for the realistic effect band; the cap limits novelty-effect inflation |
| Guardrails | refund rate, 30-day repeat, payment-failure | precisely the side-effects the skeptics fear — quantify them rather than hand-wave |
| Segmentation | category, device, country, with Bonferroni | category is where the real story lives; the correction prevents reading noise as signal |

## Why customer-level randomization
A single user has many sessions, and those sessions are correlated. Randomizing and
analysing per-session treats them as independent, which underestimates variance and
inflates the false-positive rate — a test can look "significant" when it isn't. Random
assignment is also deterministic (a salted hash), so a user sees the same variant every
visit and never contaminates both arms.

## Why validity checks come before the result
- **SRM (sample ratio mismatch)** is the first cell in the notebook. If the observed
  split isn't ~50/50, randomization is broken (bot traffic, a one-sided filter, a
  logging bug) and *every* downstream number is unreliable. You check it before you let
  yourself look at conversion.
- **ITT vs ATT.** Not everyone assigned is actually exposed. Intent-to-treat (all
  assigned) is the conservative, non-cherry-picking denominator and is what the decision
  gates on; ATT (only-exposed) is reported alongside.

## Why we don't peek — and what we'd use if we had to
The pre-registration fixes the sample size with no early stopping. The reason is
mechanical, not dogmatic: checking significance at interim points and stopping on the
first "win" inflates Type-I error well past the nominal 5% — the notebook simulates this
(1,000 null experiments with interim looks push the false-positive rate from ~5% toward
~10%). If a stakeholder genuinely needs a mid-flight read — a reasonable ask — the right
answer isn't "peek anyway" but an alpha-spending design: an **mSPRT** (always-valid
sequential test) or **O'Brien–Fleming** boundaries that budget the error across looks so
the final inference stays honest. We didn't need it here, but naming the tool is the
difference between "no peeking" as a rule and as an understood constraint.

## Why the inference is reported the way it is
- **Both absolute and relative lift, with 95% CIs.** A point estimate alone doesn't say
  whether the effect is robust; the CI does (here it excludes zero). The pooled SE is
  used for the z-test under H₀; the unpooled SE is used for the CI — a distinction worth
  getting right.
- **Z-score sanity.** A real effect on ~25k/arm lands Z in the ~2–3 band. A Z of 70 means
  a bug, not a discovery — a test pins this explicitly.
- **Bonferroni on segments.** Nine segment tests at α=0.05 would expect ~1 false positive
  by chance. The corrected threshold (α≈0.006) is what stops the suggestive apparel/beauty
  result (p=0.019) from being oversold — at the adjusted bar no segment is significant, so
  the segment story drives a confirmatory rollout, not an immediate per-segment ship.
- **Heterogeneity, checked against Simpson's.** A Simpson's artefact would show the
  aggregate contradicting the within-segment pattern (an averaging illusion from uneven
  segment sizes). It doesn't here — the aggregate is positive and most segments agree —
  so the cut is a true heterogeneous effect. But note the limit: none of the segments
  survive Bonferroni, so the heterogeneity is a *direction to confirm*, not a proven
  per-segment result.

## Reproducibility & the synthetic dataset
The data is generated by `seed_experiment.py` so the whole repo runs anywhere with no
warehouse credentials. Assignment is **deterministic** (hash); outcomes are
**stochastic** (Bernoulli) — so the *measured* lift differs from the *true* seeded
lift, which is the entire reason you run a statistical test. The true effect is set
within the believable band (never the 100%+ that produces a meaningless Z), with the
guardrails seeded slightly worse in treatment so the decision involves a real tradeoff.

## Porting to a production warehouse
The SQL is standard and each file notes its mapping to a live Postgres e-commerce schema:
- assignments → `experiment_assignments` (filter on the experiment id)
- paid / refunded outcomes → `orders` (`payment_status`) and an `order_refunds` view
- exposure → "has a `product_view` event in the session event stream within the window"
- `category_segment` → the customer's modal category via `order_items → product_variants → products → categories`
- `device` → `sessions → devices`; `country` → `customers` (cleaned for missing-value variants)

The local DuckDB store is a stand-in for that warehouse so the analysis is portable and runnable.
