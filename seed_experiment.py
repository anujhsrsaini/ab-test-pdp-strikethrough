"""
Seed a realistic A/B experiment: PDP Strikethrough Pricing vs Clean Pricing.

WHY SYNTHETIC + LOCAL: in a production deployment you'd seed assignments into a
warehouse `experiment_assignments` table and read outcomes from `orders`. This repo
instead generates a deterministic synthetic dataset into a local DuckDB file so the
whole analysis runs end-to-end on any machine with no warehouse credentials — clone,
run, green. The SQL in sql/ is standard and ports directly to a Postgres e-commerce
schema (equivalents noted at the top of each file).

Determinism: numpy seed is fixed AND variant assignment is a SHA256 hash of
(experiment_id, customer_id) — exactly the production pattern. Re-running produces
identical assignments; only the Bernoulli outcomes carry seeded noise.

Design parameters live in CONFIG below and are mirrored in PRE_REGISTRATION.md.
"""
from __future__ import annotations

import hashlib
import logging
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s",
                    datefmt="%H:%M:%S")
log = logging.getLogger("seed")

HERE = Path(__file__).parent
DATA = HERE / "data"
DATA.mkdir(exist_ok=True)

# ---------------------------------------------------------------- CONFIG
SEED = 20260617
EXPERIMENT_ID = 201                       # numeric id
EXPERIMENT_NAME = "PDP Strikethrough vs Clean Pricing"
VARIANTS = {0: ("control", True), 1: ("treatment", False)}   # variant_id -> (name, is_control)
N_CUSTOMERS = 50_000                      # 28-day run @ ~1,800 eligible PDP-viewing customers/day
START = pd.Timestamp("2026-05-01", tz="UTC")
END = pd.Timestamp("2026-05-29", tz="UTC")  # 28-day cap (novelty decay guardrail)
ATTRIBUTION_DAYS = 7

# Segment mix and TRUE effects (the realism: strikethrough helps deal-seekers in
# apparel/beauty, is flat-to-negative on premium electronics — a documented pattern).
SEGMENTS = {
    #                 share  control_cr  treatment_relative_lift
    "apparel_beauty": (0.50, 0.045,      +0.16),
    "electronics":    (0.25, 0.030,      -0.03),
    "home":           (0.25, 0.038,      +0.06),
}
DEVICES = {"mobile": 0.55, "desktop": 0.38, "tablet": 0.07}
COUNTRIES = {"India": 0.78, "United States": 0.14, "Other": 0.08}
DEVICE_MULT = {"mobile": 1.05, "desktop": 0.95, "tablet": 0.90}  # urgency framing lands a touch more on mobile

# Guardrails — treatment deliberately slightly worse (forces a real tradeoff in the memo)
REFUND_RATE = {"control": 0.012, "treatment": 0.016}      # deal-seekers return more
REPEAT_30D = {"control": 0.22, "treatment": 0.20}         # brand-erosion proxy
AOV = {"control": 2650.0, "treatment": 2480.0}            # discount framing → slightly smaller baskets (INR)
PMT_FAILURE_RATE = 0.018                                  # ~flat across arms (sanity guardrail)
EXPOSURE_RATE = 0.92                                      # assigned-but-not-exposed → ITT vs ATT


def assign_variant(cid: int) -> int:
    h = int(hashlib.sha256(f"{EXPERIMENT_ID}:{cid}".encode()).hexdigest(), 16)
    return 0 if (h % 100) < 50 else 1


def main() -> None:
    rng = np.random.default_rng(SEED)
    n = N_CUSTOMERS
    cid = np.arange(1_000_000, 1_000_000 + n)

    seg_names = list(SEGMENTS)
    segment = rng.choice(seg_names, size=n, p=[SEGMENTS[s][0] for s in seg_names])
    device = rng.choice(list(DEVICES), size=n, p=list(DEVICES.values()))
    country = rng.choice(list(COUNTRIES), size=n, p=list(COUNTRIES.values()))
    prior_orders = rng.poisson(1.3, size=n)                 # pre-period covariate (CUPED-ready)

    variant = np.array([assign_variant(c) for c in cid])
    variant_name = np.where(variant == 0, "control", "treatment")

    # assignment timestamps spread across the run
    offs = rng.integers(0, int((END - START).total_seconds()), size=n)
    assigned_at = START + pd.to_timedelta(offs, unit="s")
    exposed = rng.random(n) < EXPOSURE_RATE

    # ---- outcome probability per customer (heterogeneous treatment effect) ----
    base = np.array([SEGMENTS[s][1] for s in segment])
    lift = np.array([SEGMENTS[s][2] for s in segment])
    dmult = np.array([DEVICE_MULT[d] for d in device])
    p_convert = base * np.where(variant == 1, 1 + lift, 1.0) * dmult
    # only exposed customers can be influenced; unexposed revert to base (ITT dilutes)
    p_convert = np.where(exposed, p_convert, base * dmult)
    converted = rng.random(n) < p_convert

    assign_df = pd.DataFrame({
        "experiment_id": EXPERIMENT_ID,
        "variant_id": variant,
        "variant_name": variant_name,
        "customer_id": cid,
        "assigned_at": assigned_at,
        "assignment_source": "customer_id",
        "exposed": exposed,
        "category_segment": segment,
        "device": device,
        "country": country,
        "prior_period_orders": prior_orders,
    })

    # ---- orders table (mirrors ecom.orders): one paid order per converter, plus
    #      a small number of failed-payment rows for the payment-failure guardrail ----
    conv_idx = np.where(converted)[0]
    order_rows = []
    oid = 5_000_000
    for i in conv_idx:
        vname = variant_name[i]
        total = float(np.round(rng.lognormal(np.log(AOV[vname]), 0.45), 2))
        refunded = rng.random() < REFUND_RATE[vname]
        repeat = rng.random() < REPEAT_30D[vname]
        ot = assigned_at[i] + pd.Timedelta(hours=int(rng.integers(1, ATTRIBUTION_DAYS * 24)))
        order_rows.append((oid, int(cid[i]), total, "paid", ot, refunded, repeat))
        oid += 1
    # failed-payment attempts (guardrail; ~flat across arms) for a random slice of all customers
    fail_idx = np.where(rng.random(n) < PMT_FAILURE_RATE)[0]
    for i in fail_idx:
        ot = assigned_at[i] + pd.Timedelta(hours=int(rng.integers(1, ATTRIBUTION_DAYS * 24)))
        order_rows.append((oid, int(cid[i]), 0.0, "failed", ot, False, False))
        oid += 1

    orders_df = pd.DataFrame(order_rows, columns=[
        "order_id", "customer_id", "order_total", "payment_status", "created_at", "refunded", "repeat_30d"])

    # ---- write CSVs (committed, browsable) + DuckDB (gitignored, regenerable) ----
    assign_df.to_csv(DATA / "assignments.csv", index=False)
    orders_df.to_csv(DATA / "orders.csv", index=False)

    db = DATA / "experiment.duckdb"
    if db.exists():
        db.unlink()
    con = duckdb.connect(str(db))
    con.execute("create table experiment_assignments as select * from assign_df")
    con.execute("create table orders as select * from orders_df")
    con.execute("""create table experiments as select * from (values
        (201, 'PDP Strikethrough vs Clean Pricing', 'growth-team', 'running',
         'customer_conversion_rate', TIMESTAMPTZ '2026-05-01', TIMESTAMPTZ '2026-05-29'))
        t(experiment_id, name, owner, status, primary_metric, start_date, end_date)""")
    con.execute("""create table experiment_variants as select * from (values
        (0, 201, 'control', 50.0, true), (1, 201, 'treatment', 50.0, false))
        t(variant_id, experiment_id, variant_name, allocation_pct, is_control)""")
    con.close()

    n_c = int((variant == 0).sum()); n_t = int((variant == 1).sum())
    x_c = int(converted[variant == 0].sum()); x_t = int(converted[variant == 1].sum())
    log.info("seeded %d customers  | control %d (conv %d, %.3f) | treatment %d (conv %d, %.3f)",
             n, n_c, x_c, x_c / n_c, n_t, x_t, x_t / n_t)
    log.info("observed relative lift: %+.1f%%  | orders rows: %d  | wrote CSVs + experiment.duckdb",
             100 * ((x_t / n_t) / (x_c / n_c) - 1), len(orders_df))


if __name__ == "__main__":
    main()
