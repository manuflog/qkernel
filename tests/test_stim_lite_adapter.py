from pathlib import Path

import pytest

from qkernel.adapters.stim_lite import parse_mpp_product, parse_stim_lite_text, load_stim_lite_program
from qkernel.analyzer import analyze
from qkernel.optimizer import compress_min_odd_q


ROOT = Path(__file__).resolve().parents[1]


def test_parse_mpp_product_sparse():
    assert parse_mpp_product("Z0*X2") == {0: "Z", 2: "X"}


def test_repeated_factor_multiplies_ignoring_phase():
    assert parse_mpp_product("X0*Z0") == {0: "Y"}
    assert parse_mpp_product("X0*X0") == {}


def test_parse_stim_lite_pm_layers():
    parsed = parse_stim_lite_text((ROOT / "examples/peres_mermin_mpp.stim").read_text())

    assert parsed.num_qubits == 2
    assert parsed.layers[0] == ["ZI", "IZ", "ZZ"]
    assert parsed.layers[-1] == ["ZZ", "XX", "YY"]


def test_stim_lite_pm_is_contextual():
    program = load_stim_lite_program(ROOT / "examples/peres_mermin_mpp.stim")
    result = analyze(program)

    assert result.contextual
    assert result.q_value == 1
    assert result.selected_contexts == [0, 1, 2, 3, 4, 5]


def test_stim_lite_pm_compresses_to_six_contexts():
    program = load_stim_lite_program(ROOT / "examples/peres_mermin_mpp.stim")
    kernel = compress_min_odd_q(program)

    assert kernel.contextual
    assert kernel.compressed_contexts == 6


def test_stim_lite_loose_mode_ignores_non_mpp_lines():
    parsed = parse_stim_lite_text((ROOT / "examples/stim_lite_ignored_lines.stim").read_text())

    assert "H 0" in parsed.ignored_lines
    assert "CX 0 1" in parsed.ignored_lines
    assert parsed.layers == [["ZI", "IZ", "ZZ"]]


def test_stim_lite_strict_mode_rejects_non_mpp_lines():
    with pytest.raises(ValueError):
        parse_stim_lite_text((ROOT / "examples/stim_lite_ignored_lines.stim").read_text(), strict=True)


def test_stim_lite_rejects_unsupported_mpp_factor():
    with pytest.raises(ValueError):
        parse_stim_lite_text("MPP Q0\n")
