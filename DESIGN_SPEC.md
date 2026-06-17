# Design Spec — Task 5 A+ Sample (PDP Strikethrough)

> The reasoning behind the repo. Mentor-facing: this is the "why each choice", the
> map from the Task 5 brief's requirements to where they're demonstrated, and the
> rubric self-check. The repo itself is the "what".

## 1. Why this experiment (and not the others)
Deliberately **not** the A+ reference doc's experiment (Personalized Recs) and **not**
the live seeded experiment 106 (Social Proof Badge) — so it's a *pattern to learn from*,
not a copy of any student's likely answer or the DB's retrospective. Strikethrough
pricing is the canonical "two senior people disagree and need data" problem, and it has
a built-in **heterogeneous effect** (wins for apparel, loses for premium electronics)
that lets the sample show segmentation done right — the single most common place
student submissions stay shallow.

## 2. Design decisions and their justification

| Decision | Choice | Why |
|---|---|---|
| Primary metric | customer-level conversion (7-day window) | one gating metric forces a decision; window matches randomization grain |
| Randomization unit | customer, SHA256(`exp_id:cid`) salted | analysis unit must match; salt prevents cross-experiment structural bias |
| Allocation | 50/50 | max power per unit time; treatment is low-risk (front-end only) |
| MDE | 0.5pp abs (~13% rel) | from economics: cheap build, so the bar is "clear of guardrail risk", not break-even |
| α / power | 0.05 two-tailed / 0.80 | two-tailed because strikethrough can *hurt* (premium) |
| Sample / duration | ~25k/arm, 28-day cap | powered for the realistic band; cap limits novelty inflation |
| Guardrails | refund, 30-day repeat, payment-failure | the exact side-effects the brand team fears — quantify, don't hand-wave |
| Segments | category, device, country + Bonferroni | category is where the real story lives; correction prevents false positives |

## 3. Seeding design (what makes the data realistic)
- **Deterministic assignment** (hash), **stochastic outcomes** (Bernoulli) — so the
  *measured* lift differs from the *true* lift, which is the entire point of testing.
- **True effect within the believable band** (~+9% blended, never 100%+ → no Z=70).
- **Heterogeneity baked in:** apparel/beauty +16%, home +6%, electronics −3% — the
  brief's own observation that strikethrough helps fashion and hurts premium.
- **Guardrails seeded slightly worse in treatment** (refund 1.2→1.6%, repeat 22→20%,
  lower AOV) so the memo must grapple with a real tradeoff, not rubber-stamp a win.
- **~8% unexposed** → a genuine ITT-vs-ATT distinction to reason about.

## 4. Brief-requirement → where it's demonstrated
| Task 5 requirement | Location |
|---|---|
| One primary metric, defended | `PRE_REGISTRATION.md` §Metrics |
| MDE from business economics | `PRE_REGISTRATION.md`; `analysis.ipynb` §4 |
| Sample size derived, committed to one number | `analysis/stats.py::required_sample_per_arm`; §4 |
| Pre-registration before data | `PRE_REGISTRATION.md` (dated) |
| User-level randomization + SHA256 salt | `seed_experiment.py::assign_variant` |
| Realistic seeded lift + Bernoulli noise | `seed_experiment.py` CONFIG |
| Guardrail seeded with a wrinkle | `seed_experiment.py` REFUND/REPEAT/AOV |
| SRM before analysis | `sql/01_srm_check.sql`; notebook §1 |
| ITT vs ATT | `sql/02_exposure_itt_att.sql`; §2 |
| Per-variant metrics table | `sql/03_per_variant_metrics.sql`; §3 |
| 95% CI on lift (abs + rel) | `analysis/stats.py::lift_with_ci`; §3 |
| Z magnitude sanity-checked | `tests/test_stats.py::test_z_in_realistic_range` |
| Peeking discussed | `PRE_REGISTRATION.md` §Stopping; memo |
| Bonferroni on segments | notebook §5 |
| Simpson's vs heterogeneity, correctly distinguished | notebook §5 |
| VP memo, ship/hold + rollout + rollback trigger | `decision_memo.md` |
| Limitations + follow-up | `decision_memo.md`; README |
| CUPED mentioned | `PRE_REGISTRATION.md`; covariate present in data |

## 5. Porting to the live ecom warehouse (for graders / re-use)
Each `sql/*.sql` has a Postgres-port note. The mapping:
- `experiment_assignments` → `ecom.experiment_assignments` (filter `experiment_id = <your block id>`)
- `orders` paid/refunded → `ecom.orders` (`payment_status`), refunds via `ecom.order_refunds` view
- `exposed` → "has a `product_view` in `ecom.session_events` within the window"
- `category_segment` → modal category via `order_items → product_variants → products → categories`
- `device` → `sessions → devices`; `country` → `customers.country` (cleaned for the `''`/`N/A`/NULL variants)
- experiment ids are **numeric** and must sit in the student's assigned block; assignment INSERTs are allowed for students, outcome simulation must go to the student's `dev_` schema (never `ecom.orders`).

## 6. How to use this as a benchmark
Grade a student submission against §4's checklist. A submission missing 2–3 rows is
still a pass; missing 6+ needs revision. The highest-signal rows — the ones weak
submissions skip — are: **SRM-before-analysis, CI-not-just-a-point-estimate,
Bonferroni, the Simpson's-vs-heterogeneity distinction, and a memo that actually
decides (ship/hold by segment) rather than reporting stats.**
