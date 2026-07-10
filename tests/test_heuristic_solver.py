"""Tests for the sparse-cycle heuristic solver and high cycle-dimension robustness.

The heuristic must (a) match the exact solver on tractable families, (b) return a
genuine odd cycle, and (c) let analyze/compress handle dense Pauli families whose
cycle space is far too large for exhaustive enumeration (where exact previously
raised).
"""
from pathlib import Path

from qkernel.io import load_program
from qkernel.analyzer import analyze
from qkernel.optimizer import compress_min_odd_q
from qkernel.verify import verify_kernel
from qkernel.incidence import build_incidence, left_kernel_basis
from qkernel.carry import b_vector
from qkernel.solvers import (
    find_min_odd_cycle_heuristic,
    find_min_odd_cycle_span,
    hamming_weight,
)
from experiments.dense_pauli import dense_pauli_triples

EX = Path(__file__).resolve().parents[1] / "examples"


def _is_odd_cycle(program, lam) -> bool:
    A, _ = build_incidence(program)
    b = b_vector(program)
    cols = len(A[0])
    closed = all(sum(A[r][c] * lam[r] for r in range(len(A))) % 2 == 0 for c in range(cols))
    odd = sum(x * y for x, y in zip(lam, b)) % 2 == 1
    return closed and odd


def test_heuristic_matches_exact_on_peres_mermin():
    prog = load_program(str(EX / "peres_mermin.json"))
    h = find_min_odd_cycle_heuristic(prog)
    e = find_min_odd_cycle_span(prog)
    assert h is not None and _is_odd_cycle(prog, h)
    assert hamming_weight(h) == hamming_weight(e) == 6


def test_heuristic_returns_none_when_noncontextual():
    from qkernel.pauli_schedule import load_pauli_schedule
    prog = load_pauli_schedule(str(EX / "row_only_schedule.json"))
    assert analyze(prog).contextual is False
    assert find_min_odd_cycle_heuristic(prog) is None


def test_dense_pauli_cycle_dimension_is_large():
    # m=3 has a cycle space of dimension 259 -- exhaustive 2^dim enumeration is
    # infeasible; this is the regime the heuristic exists for.
    prog = dense_pauli_triples(3)
    assert len(left_kernel_basis(prog)) > 100


def test_analyze_does_not_crash_on_high_cycle_dim():
    prog = dense_pauli_triples(3)  # cycle_dim ~ 259
    result = analyze(prog)
    assert result.contextual is True
    assert result.odd_cycle is not None
    assert _is_odd_cycle(prog, result.odd_cycle)


def test_compress_finds_verified_kernel_on_high_cycle_dim():
    prog = dense_pauli_triples(3)
    kernel = compress_min_odd_q(prog)
    assert len(kernel.selected_contexts) == 6  # a Peres-Mermin core
    assert verify_kernel(prog, kernel).valid is True


def test_heuristic_solver_selectable_via_dispatch():
    from qkernel.solvers import find_min_odd_cycle
    prog = load_program(str(EX / "peres_mermin.json"))
    lam = find_min_odd_cycle(prog, solver="heuristic")
    assert lam is not None and hamming_weight(lam) == 6


def test_all_min_odd_cycles_peres_mermin_is_unique():
    from qkernel.solvers import find_all_min_odd_cycles
    prog = load_program(str(EX / "peres_mermin.json"))
    cycles = find_all_min_odd_cycles(prog)
    assert len(cycles) == 1
    assert all(_is_odd_cycle(prog, c) and hamming_weight(c) == 6 for c in cycles)


def test_all_min_odd_cycles_dense_m2_has_ten_witnesses():
    from qkernel.solvers import find_all_min_odd_cycles
    prog = dense_pauli_triples(2)  # all 15 two-qubit commuting lines
    cycles = find_all_min_odd_cycles(prog)
    assert len(cycles) == 10  # ten distinct minimal (weight-6) contextual kernels
    assert all(_is_odd_cycle(prog, c) and hamming_weight(c) == 6 for c in cycles)


def test_all_min_odd_cycles_refuses_infeasible_dimension():
    import pytest
    from qkernel.solvers import find_all_min_odd_cycles
    prog = dense_pauli_triples(3)  # cycle_dim ~ 259
    with pytest.raises(ValueError):
        find_all_min_odd_cycles(prog)


def test_enumerate_kernels_cli(monkeypatch, capsys):
    from qkernel.cli import main
    monkeypatch.setattr("sys.argv", ["qkernel", "enumerate-kernels", str(EX / "peres_mermin.json")])
    main()
    out = capsys.readouterr().out
    assert "1 distinct minimal" in out and "weight 6" in out
