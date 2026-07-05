from qkernel.carry import compute_b
from qkernel.examples import peres_mermin_program
from qkernel.symplectic import symplectic_int


def test_integer_carry_not_modded_away():
    program = peres_mermin_program()
    last_context = program.contexts[5]

    # The last Peres-Mermin column is the negative product context.
    assert compute_b(program, last_context) == 1

    # If one reduces pairings modulo d before division, the carry disappears.
    broken_total = 0
    for i in range(len(last_context)):
        for j in range(i + 1, len(last_context)):
            u = program.observables[last_context[i]]
            v = program.observables[last_context[j]]
            broken_total += symplectic_int(u, v) % program.d

    assert (broken_total // program.d) % 2 == 0
