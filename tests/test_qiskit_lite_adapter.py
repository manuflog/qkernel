from pathlib import Path

from qkernel.adapters.qiskit_lite import (
    normalize_qiskit_pauli_label,
    parse_qiskit_lite_data,
    load_qiskit_lite_program,
)
from qkernel.analyzer import analyze
from qkernel.optimizer import compress_min_odd_q


ROOT = Path(__file__).resolve().parents[1]


def test_qiskit_label_order_reversal():
    assert normalize_qiskit_pauli_label("IZ", qubit_order="qiskit") == "ZI"
    assert normalize_qiskit_pauli_label("ZI", qubit_order="qkernel") == "ZI"


def test_parse_qiskit_lite_pm_layers():
    parsed = parse_qiskit_lite_data({
        "type": "qiskit_pauli_layers",
        "qubit_order": "qiskit",
        "layers": [{"paulis": ["IZ", "ZI", "ZZ"]}],
    })

    assert parsed.layers == [["ZI", "IZ", "ZZ"]]
    assert parsed.qubit_order == "qiskit"


def test_qiskit_lite_pm_is_contextual():
    program = load_qiskit_lite_program(ROOT / "examples/peres_mermin_qiskit_lite.json")
    result = analyze(program)

    assert result.contextual
    assert result.q_value == 1
    assert result.selected_contexts == [0, 1, 2, 3, 4, 5]


def test_qiskit_lite_pm_compresses_to_six():
    program = load_qiskit_lite_program(ROOT / "examples/peres_mermin_qiskit_lite.json")
    kernel = compress_min_odd_q(program)

    assert kernel.contextual
    assert kernel.compressed_contexts == 6


def test_flat_terms_record_ignored_coefficients():
    parsed = parse_qiskit_lite_data({
        "type": "qiskit_sparse_pauli_terms",
        "qubit_order": "qiskit",
        "terms": [
            {"pauli": "IZ", "layer": "r0", "coeff": 1.0},
            {"pauli": "ZI", "layer": "r0", "coeff": -1.0},
            {"pauli": "ZZ", "layer": "r0", "coeff": "0.5"},
        ],
    })

    assert parsed.layers == [["ZI", "IZ", "ZZ"]]
    assert "-1.0" in parsed.ignored_coefficients
    assert "0.5" in parsed.ignored_coefficients
