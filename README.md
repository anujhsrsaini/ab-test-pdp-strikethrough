# A/B Test — PDP Strikethrough vs Clean Pricing

> Does showing a struck-through MRP + "Save X%" badge on the product page lift conversion — or just attract deal-seekers who return more and churn? An end-to-end experiment: design → pre-registration → seeding → validity checks → statistical analysis → a VP decision memo. **Verdict: it wins in apparel/beauty (+14%), is flat-to-negative on electronics (−3%), and roughly doubles refund rate — so ship it by category, not globally.**

**Runs end-to-end on a fresh clone in ~30 seconds, no database credentials needed** (see [Why synthetic](#why-synthetic-and-local)).

```bash
pip install -r requirements.txt
python seed_experiment.py                       # deterministic synthetic seed → data/experiment.duckdb
pytest -q                                        # 7 tests pin the stats + the assignment hash
jupyter nbconvert --to notebook --execute analysis/analysis.ipynb --inplace   # the read-out
```

## Headline result

| | Control (clean) | Treatment (strikethrough) |
|---|---|---|
| Customers | 25,047 | 24,953 |
| Conversion rate | 3.82% | **4.27%** |
| **Relative lift** | — | **+11.8%** (95% CI +2.8% … +20.9%), Z = 2.56, p = 0.011 |
| Refund rate | 1.04% | **2.06%** ⚠ |
| 30-day repeat | 22.6% | **19.0%** ⚠ |
| AOV | ₹2,927 | ₹2,693 |

![Overall conversion](figures/01_overall_conversion.png)
![Category heterogeneity](figures/02_category_heterogeneity.png)

The overall win is real but **concentrated** — and it comes with a quality-of-revenue cost. The full reasoning and rollout plan are in **[`decision_memo.md`](decision_memo.md)**.

## Problem
Merchandising wants strikethrough pricing on the PDP (urgency → conversion). Brand pushes back (cheapens us, attracts deal-seekers, erodes repeat rate). Both have anecdotes; neither has data. This experiment settles it — and the honest answer is "it depends on the category," which is exactly why a global decision would be wrong.

## Approach
- **Design & pre-registration** ([`PRE_REGISTRATION.md`](PRE_REGISTRATION.md)) — one primary metric (customer-level conversion), guardrails (refund / repeat / payment-failure), MDE from economics, decision + stopping rules locked *before* data.
- **Randomization** — at the **customer** (SHA256 of `experiment_id:customer_id`, salted per experiment), so the analysis unit matches the randomization unit and the same user never sees both variants.
- **Validity first** — SRM (chi-square) and exposure (ITT vs ATT) are checked *before* any conversion number is read.
- **Inference** — two-proportion z-test, absolute **and** relative lift with 95% CIs, a power/MDE reality-check, Bonferroni-corrected segmentation, and an explicit Simpson's-paradox-vs-heterogeneity distinction.
- **Decision** — a one-page memo to a VP: ship/hold by segment, guardrails quantified, rollout with a refund-rate kill-switch.

## What's in here
```
seed_experiment.py        deterministic synthetic seed → DuckDB + CSVs
PRE_REGISTRATION.md       design locked before data (the trust anchor)
sql/                      01 SRM · 02 exposure(ITT/ATT) · 03 per-variant metrics · 04 segmentation
analysis/
  analysis.ipynb          the executed read-out (figures + numbers inline)
  stats.py                z-test, lift+CI, SRM, Bonferroni, power — small and auditable
tests/test_stats.py       7 pytest checks (incl. cross-check vs statsmodels; Z in a sane range)
decision_memo.md          the VP-facing recommendation
DESIGN_SPEC.md            the full design rationale / "why each choice"
figures/                  generated charts (committed for this README)
```

## Why synthetic and local
In the graded task you seed assignments into `ecom.experiment_assignments` (within your assigned experiment-id block) and read outcomes from `ecom.orders` on the shared Postgres. This sample instead generates a deterministic synthetic dataset into a local DuckDB file so the whole repo runs anywhere with no credentials — clone, run, green. **The SQL in `sql/` is standard and ports directly to the ecom Postgres schema** (the Postgres equivalent is noted at the top of each file: `product_view` events, the `ecom.order_refunds` view, the `customers`/`sessions`/`devices` joins for segments).

## Limitations (the honest part)
- **Synthetic data:** numbers are seeded to be realistic (baseline 3.9%, lift in the +3–12% band strikethrough actually produces), not pulled from production — so the *method* is the deliverable, not the exact lift. On real ecom you'd re-confirm the baseline and category split.
- **Novelty effect:** a 28-day window can overstate the long-run lift ~10–20%; the memo schedules a 90-day re-read.
- **Repeat-rate signal is early** at a 30-day window — directional, not settled.
- **Cross-device:** ~5–10% of users may see mixed variants; dilutes (conservative).
- **CUPED** noted but not implemented (the pre-period covariate is in the data if you want to add it).

## Resume bullet
> Designed and analysed a customer-level A/B test on PDP discount framing (n ≈ 50k, 28-day run): pre-registered design, SHA256 randomization, SRM + ITT/ATT validity checks, two-proportion z-test with 95% CIs, and Bonferroni-corrected segmentation. Found a +11.8% conversion lift concentrated in apparel/beauty (flat-to-negative on electronics) against a doubled refund rate, and shipped a segment-specific rollout via a VP decision memo.
