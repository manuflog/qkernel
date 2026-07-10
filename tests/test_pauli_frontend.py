from qkernel.analyzer import analyze
from qkernel.pauli import PERES_MERMIN_CONTEXTS, pauli_program, pauli_string_to_vector


def test_pauli_string_to_vector():
    assert pauli_string_to_vector("I") == (0, 0)
    assert pauli_string_to_vector("X") == (0, 1)
    assert pauli_string_to_vector("Z") == (1, 0)
    assert pauli_string_to_vector("Y") == (1, 1)
    assert pauli_string_to_vector("ZI") == (1, 0, 0, 0)
    assert pauli_string_to_vector("IX") == (0, 0, 0, 1)
    assert pauli_string_to_vector("YY") == (1, 1, 1, 1)


def test_peres_mermin_from_pauli_contexts_is_contextual():
    program = pauli_program(PERES_MERMIN_CONTEXTS)
    result = analyze(program)

    assert result.contextual
    assert result.q_value == 1
    assert result.b_vector == [0, 0, 0, 0, 0, 1]


def test_row_only_pauli_subprogram_is_not_contextual():
    program = pauli_program(PERES_MERMIN_CONTEXTS[:3])
    result = analyze(program)

    assert not result.contextual
    assert result.selected_contexts == []
