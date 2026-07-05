"""Smoke test for the Phase-3 benchmark suite: runs it on small sizes and checks
the correctness invariants it asserts (kernel stays the 6-context PM core,
contextuality preserved, kernel verifies, and the exact solvers agree)."""
from experiments.benchmark_suite import run


def test_benchmark_suite_invariants_small():
    rows = run(sizes=[0, 5, 10], repeats=1)
    assert len(rows) == 3
    for r in rows:
        assert r["kernel"] == 6
        assert r["contextual"] is True
        assert r["verified"] is True
        assert r["solvers_agree"] is True
    # problem size grows with the ladder parameter
    assert [r["contexts"] for r in rows] == [6, 11, 16]


def test_benchmark_exact_solve_is_monotone_in_size():
    rows = run(sizes=[0, 25, 100], repeats=1)
    sizes = [r["contexts"] for r in rows]
    assert sizes == sorted(sizes)
