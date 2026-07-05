from qkernel.closed_form import (
    compare_q_forms,
    is_cycle,
    observable_multiset_pairing_numerator,
    q_from_context_carries,
    q_from_observable_multiset,
)
from qkernel.examples import peres_mermin_program
from qkernel.gf2 import span
from qkernel.incidence import left_kernel_basis


def test_pm_closed_q_form_matches_context_carry_dot():
    program = peres_mermin_program()
    lam = [1, 1, 1, 1, 1, 1]

    assert is_cycle(program, lam)
    assert q_from_context_carries(program, lam) == 1
    assert q_from_observable_multiset(program, lam) == 1

    comparison = compare_q_forms(program, lam)
    assert comparison.valid
    assert comparison.numerator % program.d == 0


def test_closed_q_forms_match_on_cycle_space():
    program = peres_mermin_program()
    basis = left_kernel_basis(program)

    for lam in span(basis):
        assert is_cycle(program, lam)
        assert q_from_context_carries(program, lam) == q_from_observable_multiset(program, lam)


def test_closed_q_pairing_numerator_is_aggregate_not_termwise():
    program = peres_mermin_program()
    lam = [1, 1, 1, 1, 1, 1]

    numerator = observable_multiset_pairing_numerator(program, lam)

    assert numerator % program.d == 0
    assert (numerator // program.d) % 2 == 1
