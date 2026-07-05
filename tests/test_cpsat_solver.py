"""Tests for the CP-SAT (OR-Tools) exact backend. Skipped if OR-Tools is absent."""
import pytest

pytest.importorskip("ortools")

from pathlib import Path
from qkernel.io import load_program
from qkernel.pauli_schedule import load_pauli_schedule
from qkernel.solvers import find_min_odd_cycle_span, find_min_odd_cycle, hamming_weight
from qkernel.solvers_milp import find_min_odd_cycle_cpsat

EX = Path(__file__).resolve().parents[1] / "examples"


def test_cpsat_matches_span_and_certifies_on_peres_mermin():
    prog = load_program(str(EX / "peres_mermin.json"))
    cycle, certified = find_min_odd_cycle_cpsat(prog)
    assert certified is True
    assert hamming_weight(cycle) == hamming_weight(find_min_odd_cycle_span(prog)) == 6


def test_cpsat_reports_noncontextual_as_infeasible():
    prog = load_pauli_schedule(str(EX / "row_only_schedule.json"))
    cycle, certified = find_min_odd_cycle_cpsat(prog)
    assert cycle is None and certified is True  # infeasible == non-contextual, certified


def test_cpsat_selectable_via_dispatch():
    prog = load_program(str(EX / "peres_mermin.json"))
    lam = find_min_odd_cycle(prog, solver="cpsat")
    assert lam is not None and hamming_weight(lam) == 6


@pytest.mark.slow
def test_cpsat_certifies_optimum_on_dense_high_cycle_dim():
    # m=3 dense Pauli: cycle_dim ~259, so span (2^dim) is infeasible, yet CP-SAT
    # certifies the minimum is weight 6 -- an independent optimality certificate.
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
    from dense_pauli import dense_pauli_triples
    prog = dense_pauli_triples(3)
    cycle, certified = find_min_odd_cycle_cpsat(prog, max_time_seconds=120)
    assert certified is True
    assert hamming_weight(cycle) == 6
