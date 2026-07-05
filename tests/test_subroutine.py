"""Tests for the composable contextuality subroutine."""
from pathlib import Path

from qkernel.io import load_program
from qkernel.pauli_schedule import load_pauli_schedule
from qkernel.subroutine import analyze_contextuality

EX = Path(__file__).resolve().parents[1] / "examples"


def test_subroutine_peres_mermin_full():
    r = analyze_contextuality(load_program(str(EX / "peres_mermin.json")),
                              enumerate_all_kernels=True)
    assert r.contextual is True
    assert r.kernel_weight == 6
    assert r.min_kernel_contexts == [0, 1, 2, 3, 4, 5]
    assert r.verified is True
    assert r.n_minimal_kernels == 1
    assert r.obstruction_value == 1  # d/2 for d=2


def test_subroutine_noncontextual():
    r = analyze_contextuality(load_pauli_schedule(str(EX / "row_only_schedule.json")))
    assert r.contextual is False
    assert r.min_kernel_contexts is None
    assert r.obstruction_value == 0


def test_subroutine_certify_minimal_requires_ortools_but_is_optional():
    import pytest
    pytest.importorskip("ortools")
    r = analyze_contextuality(load_program(str(EX / "peres_mermin.json")),
                              certify_minimal=True)
    assert r.certified_minimal is True


def test_subroutine_counts_multiple_minimal_kernels():
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
    from dense_pauli import dense_pauli_triples
    r = analyze_contextuality(dense_pauli_triples(2), enumerate_all_kernels=True)
    assert r.n_minimal_kernels == 10  # ten Mermin squares in the doily
