from qkernel.examples import peres_mermin_program, noisy_peres_mermin_program
from qkernel.optimizer import compress_min_odd_q
from qkernel.solvers import find_min_odd_cycle_branch_bound
from qkernel.verify import verify_kernel


def test_branch_bound_finds_pm_cycle():
    program = peres_mermin_program()
    lam = find_min_odd_cycle_branch_bound(program)

    assert lam == [1, 1, 1, 1, 1, 1]


def test_optimizer_branch_bound_finds_pm_kernel():
    program = peres_mermin_program()
    kernel = compress_min_odd_q(program, solver="branch-bound")

    assert kernel.contextual
    assert kernel.selected_contexts == [0, 1, 2, 3, 4, 5]
    assert verify_kernel(program, kernel).valid


def test_branch_bound_with_decomposition_handles_noisy_pm():
    program = noisy_peres_mermin_program(noise_contexts=40)
    kernel = compress_min_odd_q(program, solver="branch-bound")

    assert kernel.contextual
    assert kernel.selected_contexts == [0, 1, 2, 3, 4, 5]
