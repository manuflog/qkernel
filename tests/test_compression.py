from qkernel.examples import noisy_peres_mermin_program
from qkernel.optimizer import compress_min_odd_q


def test_noisy_pm_compresses_to_core():
    program = noisy_peres_mermin_program(noise_contexts=40)
    kernel = compress_min_odd_q(program)

    assert kernel.contextual
    assert kernel.q_value == 1
    assert kernel.compressed_contexts == 6
    assert kernel.compressed_observables == 9
    assert kernel.selected_contexts == [0, 1, 2, 3, 4, 5]
