from pathlib import Path

from qkernel.adapters.pauli_table import load_pauli_table, pauli_table_program
from qkernel.analyzer import analyze
from qkernel.optimizer import compress_min_odd_q


ROOT = Path(__file__).resolve().parents[1]


def test_load_pauli_table_json_detects_pm():
    program = load_pauli_table(ROOT / "examples/peres_mermin_table.json")
    result = analyze(program)

    assert result.contextual
    assert result.q_value == 1
    assert result.selected_contexts == [0, 1, 2, 3, 4, 5]


def test_load_pauli_table_csv_detects_pm():
    program = load_pauli_table(ROOT / "examples/peres_mermin_table.csv")
    kernel = compress_min_odd_q(program)

    assert kernel.contextual
    assert kernel.selected_contexts == [0, 1, 2, 3, 4, 5]


def test_event_scoped_table_does_not_merge_without_force():
    program = load_pauli_table(ROOT / "examples/peres_mermin_table_events.json")

    safe = compress_min_odd_q(program, canonicalize="by-vector")
    forced = compress_min_odd_q(program, canonicalize="by-vector-force")

    assert not safe.contextual
    assert forced.contextual


def test_table_rejects_mixed_pauli_lengths():
    rows = [
        {"context_id": "a", "pauli": "ZI"},
        {"context_id": "a", "pauli": "X"},
    ]

    import pytest
    with pytest.raises(ValueError):
        pauli_table_program(rows)


def test_table_rejects_reused_name_with_different_vector():
    rows = [
        {"context_id": "a", "pauli": "ZI", "name": "same"},
        {"context_id": "b", "pauli": "IX", "name": "same"},
    ]

    import pytest
    with pytest.raises(ValueError):
        pauli_table_program(rows)
