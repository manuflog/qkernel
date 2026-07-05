from qkernel.analyzer import analyze
from qkernel.examples import peres_mermin_program


def test_peres_mermin_is_contextual():
    result = analyze(peres_mermin_program())

    assert result.contextual
    assert result.q_value == 1
    assert result.selected_contexts == [0, 1, 2, 3, 4, 5]
    assert result.b_vector == [0, 0, 0, 0, 0, 1]
