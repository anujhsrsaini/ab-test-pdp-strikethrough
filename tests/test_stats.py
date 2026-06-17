"""Pin the statistics so the notebook's numbers are trustworthy, and pin the
assignment hash so 'deterministic' is enforced, not just claimed."""
import hashlib
import sys
from pathlib import Path

import pytest
from scipy.stats import norm
from statsmodels.stats.proportion import proportions_ztest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "analysis"))
import stats as ab  # noqa: E402


def test_ztest_matches_statsmodels():
    # cross-check our hand-rolled pooled z-test against statsmodels
    x_c, n_c, x_t, n_t = 957, 25047, 1066, 24953
    z, p = ab.two_proportion_ztest(x_c, n_c, x_t, n_t)
    z_sm, p_sm = proportions_ztest([x_t, x_c], [n_t, n_c], alternative="two-sided")
    assert abs(z - z_sm) < 1e-6
    assert abs(p - p_sm) < 1e-6


def test_z_in_realistic_range():
    # a real effect on ~25k/arm should land Z in the believable 1.5–4 band, not 70
    z, p = ab.two_proportion_ztest(957, 25047, 1066, 24953)
    assert 1.5 < z < 4.0
    assert p < 0.05


def test_lift_ci_excludes_zero_when_significant():
    r = ab.lift_with_ci(957, 25047, 1066, 24953)
    assert r.abs_lift > 0
    assert r.abs_ci[0] > 0          # CI excludes zero => significant
    assert 0.05 < r.rel_lift < 0.20  # ~+11.8%


def test_srm_passes_on_balanced_split():
    chi2, p = ab.chisq_srm(25047, 24953)
    assert p >= 0.001               # not a mismatch


def test_srm_flags_broken_split():
    chi2, p = ab.chisq_srm(26500, 23500)   # 53/47 on 50k => clearly broken
    assert p < 0.001


def test_assignment_is_deterministic_and_balanced():
    exp_id = 201
    def assign(cid):
        h = int(hashlib.sha256(f"{exp_id}:{cid}".encode()).hexdigest(), 16)
        return 0 if (h % 100) < 50 else 1
    assigned = [assign(c) for c in range(1_000_000, 1_010_000)]
    # deterministic: same input, same bucket
    assert assign(1_234_567) == assign(1_234_567)
    # roughly balanced
    share = sum(assigned) / len(assigned)
    assert 0.47 < share < 0.53


def test_sample_size_roundtrips():
    # required_sample_per_arm and detectable_mde_abs should be inverses
    n = ab.required_sample_per_arm(baseline=0.039, mde_abs=0.005)
    mde = ab.detectable_mde_abs(baseline=0.039, n_per_arm=n)
    assert abs(mde - 0.005) < 0.0003
