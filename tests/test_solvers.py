from qkernel.examples import peres_mermin_program
from qkernel.optimizer import compress_min_odd_q
from qkernel.solvers import find_min_odd_cycle_bounded_weight, find_min_odd_cycle_span


def test_span_solver_finds_pm_cycle():
    program = peres_mermin_program()
    lam = find_min_odd_cycle_span(program)

    assert lam == [1, 1, 1, 1, 1, 1]


def test_bounded_weight_solver_finds_pm_cycle():
    program = peres_mermin_program()
    lam = find_min_odd_cycle_bounded_weight(program, max_weight=6)

    assert lam == [1, 1, 1, 1, 1, 1]


def test_optimizer_accepts_explicit_solvers():
    program = peres_mermin_program()

    kernel_span = compress_min_odd_q(program, solver="span")
    kernel_bounded = compress_min_odd_q(program, solver="bounded-weight", max_weight=6)
    kernel_branch = compress_min_odd_q(program, solver="branch-bound")

    assert kernel_span.selected_contexts == [0, 1, 2, 3, 4, 5]
    assert kernel_bounded.selected_contexts == [0, 1, 2, 3, 4, 5]
    assert kernel_branch.selected_contexts == [0, 1, 2, 3, 4, 5]
