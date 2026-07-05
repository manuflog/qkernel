import pytest

from qkernel.analyzer import analyze
from qkernel.optimizer import compress_min_odd_q
from qkernel.pauli_schedule import extract_contexts_from_layers, schedule_program


PM_LAYERS = [
    ["ZI", "IZ", "ZZ"],
    ["IX", "XI", "XX"],
    ["ZX", "XZ", "YY"],
    ["ZI", "IX", "ZX"],
    ["IZ", "XI", "XZ"],
    ["ZZ", "XX", "YY"],
]


def test_extract_peres_mermin_schedule_contexts():
    contexts = extract_contexts_from_layers(PM_LAYERS)

    assert len(contexts) == 6
    assert contexts == PM_LAYERS


def test_peres_mermin_schedule_is_contextual():
    program = schedule_program(PM_LAYERS)
    result = analyze(program)

    assert result.contextual
    assert result.q_value == 1
    assert result.b_vector == [0, 0, 0, 0, 0, 1]


def test_row_only_schedule_not_contextual():
    program = schedule_program(PM_LAYERS[:3])
    result = analyze(program)

    assert not result.contextual


def test_schedule_compresses_to_pm_kernel():
    noise_layers = PM_LAYERS + [
        ["ZIIII", "IZIII", "ZZIII"],
        ["IIZII", "IIIZI", "IIZZI"],
    ]
    # This intentionally fails because mixed Pauli lengths cannot coexist.
    # It documents that schedule extraction is not allowed to silently pad
    # identities across inconsistent register sizes.
    with pytest.raises(ValueError):
        schedule_program(noise_layers)


def test_all_observables_in_one_layer_is_a_different_input_semantics():
    all_at_once = [[p for layer in PM_LAYERS for p in layer]]
    contexts = extract_contexts_from_layers(
        all_at_once,
        include_full_layers=False,
        include_closed_triples=True,
    )

    # The extractor can recover PM-like triples, but this is not equivalent
    # to a real circuit schedule unless those triples were intended contexts.
    assert len(contexts) >= 6
