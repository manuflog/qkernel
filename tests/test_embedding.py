"""Tests for contextuality activation by dimension embedding (d -> 2d)."""
from pathlib import Path

from qkernel.io import load_program
from qkernel.analyzer import analyze
from qkernel.embedding import build_fiber_pool, activation_report

EX = Path(__file__).resolve().parents[1] / "examples"


def test_activation_base_is_noncontextual_fiber_is_contextual():
    base = load_program(str(EX / "activation_base_d4.json"))
    assert analyze(base).contextual is False  # base: no odd-Q obstruction at d=4
    pool = build_fiber_pool(base)
    assert pool.d == 2 * base.d == 8
    assert analyze(pool).contextual is True  # fiber pool at d=8 IS contextual


def test_activation_report_flags_activation():
    base = load_program(str(EX / "activation_base_d4.json"))
    report = activation_report(base)
    assert report.activated is True
    assert report.base_contextual is False
    assert report.fiber_contextual is True
    assert report.base_d == 4 and report.fiber_d == 8
    assert report.fiber_contexts > report.base_contexts


def test_activation_report_no_activation_when_base_already_contextual():
    # Peres-Mermin is already contextual, so there is nothing to activate.
    base = load_program(str(EX / "peres_mermin.json"))
    report = activation_report(base)
    assert report.base_contextual is True
    assert report.activated is False


def test_fiber_pool_is_a_valid_program_at_double_dimension():
    base = load_program(str(EX / "activation_base_d4.json"))
    pool = build_fiber_pool(base)
    # every observable named in a context exists in the observable table
    for ctx in pool.contexts:
        for name in ctx:
            assert name in pool.observables
            assert len(pool.observables[name]) == 2 * pool.m


def test_activation_yield_trend_smoke():
    # Fast, low-seed smoke test: the sweep runs and a larger base activates strictly
    # more than a size-3 base (full statistics live in experiments/activation_yield.py).
    import sys as _sys
    _sys.path.insert(0, "experiments")
    from activation_yield import yield_sweep, wilson
    assert wilson(0, 0) == (0.0, 0.0, 0.0)  # edge case
    rows = yield_sweep([3, 7], seeds_per=15)
    by = {r["nctx"]: r["act"] for r in rows}
    assert by[7] >= by[3]


def test_activated_resource_extracts_verified_test():
    from qkernel.embedding import activated_resource
    base = load_program(str(EX / "activation_base_d4.json"))
    r = activated_resource(base)
    assert r.activated is True
    assert r.fiber_d == 8 and r.obstruction_value == 4
    assert r.verified is True          # valid odd-Q obstruction
    assert r.test_weight and r.test_weight > 0
    assert r.test_contexts and all(len(c) == 3 for c in r.test_contexts)


def test_activated_resource_no_activation_when_already_contextual():
    from qkernel.embedding import activated_resource
    r = activated_resource(load_program(str(EX / "peres_mermin.json")))
    assert r.activated is False
    assert "already contextual" in r.reason
