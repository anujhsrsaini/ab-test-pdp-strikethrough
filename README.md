# Does strikethrough pricing actually lift conversion? — an A/B test

> **Strikethrough pricing lifts conversion +11.8% (significant) and nudges revenue per customer up ~3% — but it roughly doubles the refund rate, and the win is really an apparel/beauty story, not electronics. So the call isn't "ship it everywhere." It's ship it where it wins, with a refund alarm.**

`Python` · `SQL (DuckDB / Postgres)` · `scipy` · `statsmodels` · `pandas` · `matplotlib`

End-to-end: hypothesis → sample-size → randomization → conversion + significance → guardrails → North Star → a one-page decision memo. **Runs on a fresh clone in ~30 seconds, no database access required.**

**Jump to the good parts:** [📝 Decision memo](decision_memo.md) (2-min read) · [📊 Executed analysis](analysis/analysis.ipynb) · [🧪 Design rationale](DESIGN.md) · [🔒 Test plan](PRE_REGISTRATION.md)

---

## Result at a glance

| | Control (clean price) | Treatment (strikethrough) | |
|---|---|---|---|
| Customers | 25,047 | 24,953 | |
| **Conversion** | 3.82% | **4.27%** | **+11.8%** rel · Z = 2.56 · **p = 0.010** |
| Revenue / customer | ₹111.82 | ₹115.06 | **+2.9%** (the North Star) |
| Refund rate | 1.04% | 2.06% | ⚠ ~doubles |
| 30-day repeat | 22.6% | 19.0% | ⚠ −3.5pp |

Three pictures, three beats: the lift is real and its confidence interval clears zero (1); it lives in apparel/beauty and reverses on electronics (2); and it isn't free — two guardrails move the wrong way (3).

<p align="center">
  <img width="780" src="figures/01_lift_forest.png" alt="Forest plot of relative conversion lift with 95% confidence intervals. Overall +11.8% (CI +2.8% to +20.9%, significant). By category: home +17% (CI crosses zero, not significant), apparel/beauty +14% (significant), electronics -3% (not significant).">
</p>

<p align="center">
  <img width="780" src="figures/02_conversion_compare.png" alt="Dumbbell: control 3.82 percent versus treatment 4.27 percent, a +0.45pp absolute and +11.8 percent relative lift, p = 0.010. Axis starts at 3.5 percent.">
</p>

<p align="center">
  <img width="780" src="figures/03_guardrails.png" alt="Guardrails, control versus treatment. Refund rate 1.04 to 2.06 percent (doubles). 30-day repeat 22.6 to 19.0 percent (down 3.5pp). AOV down 233 rupees. Payment-failure flat.">
</p>

## The decision

**Ship strikethrough to apparel/beauty, with a refund alarm. Hold electronics. Watch home.**

- **Apparel/beauty (+14%, significant):** ship it — this is where the lift is real and the margin lives. Add a **refund kill-switch** (pause if refund rate > 3.0% sustained 3+ days).
- **Electronics (−3%, not significant):** keep clean pricing — no conversion gain and a worse repeat-rate; shipping there would cost margin for nothing.
- **Home (+17% but not significant):** promising, not proven — collect more data before committing.

There's no good global on/off setting, and the conversion win comes with a refund cost — so the recommendation captures the upside where it's real and guards the downside. Full reasoning, money sizing, and rollout in the [decision memo](decision_memo.md).

## What this shows

- **Designed before data** — hypothesis, primary metric, sample size, and guardrails written down up front (see the [test plan](PRE_REGISTRATION.md)).
- **Measured correctly** — randomized and analysed at the customer (the unit that matches), with a two-proportion z-test and a 95% CI, not just a point estimate.
- **Business-aware** — guardrail metrics tracked, the result tied to the North Star (revenue per customer), and the segments read for *where* to act.
- **Ends in a decision** — a clear ship/hold recommendation with a rollback trigger and rough money sizing, not a p-value dump.

## Run it

```bash
pip install -r requirements.txt
python seed_experiment.py        # deterministic dataset → data/experiment.duckdb (+ CSVs)
python make_figures.py           # renders the 3 figures above, from the data
pytest -q                        # 7 checks: stats correctness (vs statsmodels) + assignment determinism
jupyter nbconvert --to notebook --execute analysis/analysis.ipynb --inplace
```

Every number on every chart is computed from the data, and the notebook renders inline on GitHub — read the whole analysis without running anything.

## Repo tour

```
PRE_REGISTRATION.md     the test plan, written before the data (metric, sample size, guardrails, decision rule)
seed_experiment.py      deterministic data generator (SHA256 assignment, Bernoulli outcomes)
make_figures.py         renders the 3 README figures from the data
sql/                    01 split check · 02 exposure · 03 per-variant metrics · 04 segmentation
analysis/
  analysis.ipynb        the executed read-out — conversion, sample size, segments, guardrails, North Star, verdict
  stats.py              z-test, lift + CI, sample size — small and auditable
tests/test_stats.py     7 pytest checks (cross-checked vs statsmodels; Z-magnitude sanity; assignment determinism)
decision_memo.md        the one-page recommendation to a VP of Product
DESIGN.md               why each choice was made
figures/                charts used above
```

## How it was built

Full write-up in [DESIGN.md](DESIGN.md). The decisions that matter:

- **Customer-level, not session-level.** Sessions from one user are correlated; measuring per-session understates variance and overstates significance. Randomize and analyse on the same unit — the customer.
- **Sample size from economics.** A cheap front-end change → the bar is "detect a realistic effect (~3–12% relative)," and the test was sized for it.
- **Guardrails are first-class.** Refund rate, 30-day repeat, payment-failure — the metrics you don't want to move are tracked alongside the one you do.
- **Segments tell you where, not just whether.** The same headline can be a clear win in one category and a loss in another; reading the cut is what turns a number into a rollout plan.

## The data

The dataset is **synthetic but realistic**, produced by `seed_experiment.py` — a deliberate choice so the whole analysis is **reproducible by anyone** (clone and run) with no warehouse credentials. The baseline (3.9%) and the effect band (+3–12% relative, what strikethrough actually produces) are calibrated to real e-commerce, and the heterogeneity (fashion responds to discounting, premium electronics doesn't) mirrors a documented merchandising pattern. The SQL is standard and **ports directly to a production Postgres warehouse** — each file notes the mapping.

## Limitations

- **Synthetic data** — the *method* is the deliverable, not the exact lift; on production data you'd re-confirm the baseline and category split.
- **Novelty effect** — a discount frame can inflate early lift; capped at 28 days, with a 90-day re-read planned.
- **Repeat-rate is an early read** at 30 days — confirm at 60–90 days before treating it as settled.

---

*A self-directed analysis demonstrating end-to-end experimentation practice on an e-commerce dataset.*

**Résumé line:**

> Designed and analysed a customer-level A/B test on PDP discount framing (n ≈ 50k): sized the test from business economics, measured conversion with a two-proportion z-test and 95% CI, tracked guardrail metrics, and tied the result to the North Star (revenue per customer). Found a +11.8% lift concentrated in apparel/beauty that doubled refund rate, and recommended a targeted rollout with a refund-rate rollback trigger via a VP decision memo.
