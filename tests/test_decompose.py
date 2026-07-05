from pathlib import Path
from qkernel.decompose import decompose_components
from qkernel.examples import noisy_peres_mermin_program, peres_mermin_program
from qkernel.optimizer import compress_min_odd_q
from qkernel.pauli_schedule import load_pauli_schedule


def test_pm_is_one_component():
    program = peres_mermin_program()
    components = decompose_components(program)

    assert len(components) == 1
    assert components[0].context_indices == [0, 1, 2, 3, 4, 5]


def test_noisy_pm_has_many_components_and_compresses_to_core():
    program = noisy_peres_mermin_program(noise_contexts=12)
    components = decompose_components(program)
    kernel = compress_min_odd_q(program)

    assert len(components) > 1
    assert kernel.contextual
    assert kernel.selected_contexts == [0, 1, 2, 3, 4, 5]
    assert kernel.compressed_contexts == 6


def test_schedule_noise_decomposes_and_finds_pm_core():
    program = load_pauli_schedule(str(Path(__file__).resolve().parents[1] / "examples/peres_mermin_with_noise_schedule.json"))
    components = decompose_components(program)
    kernel = compress_min_odd_q(program)

    assert len(components) > 1
    assert kernel.contextual
    assert kernel.selected_contexts == [0, 1, 2, 3, 4, 5]
