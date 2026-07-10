import json
from pathlib import Path

from qkernel.cli import main
from qkernel.fiber_lift import (
    find_even_base_fiber_lift,
    lift_program_with_bits,
)
from qkernel.io import load_program
from qkernel.tower import tower_law_report
from qkernel.valuation import check_zd_valuation


ROOT = Path(__file__).resolve().parents[1]


def test_even_base_fiber_lift_constructs_valid_program():
    base = load_program(ROOT / "examples/tower_pair_d2_base.json")
    result = find_even_base_fiber_lift(base)

    assert result.constructed
    assert result.status == "constructed"
    assert result.program is not None
    assert result.program.d == 4
    assert result.program.context_phases == [0, 2]
    assert result.zd_contextual is True


def test_constructed_lift_runs_tower_law():
    base = load_program(ROOT / "examples/tower_pair_d2_base.json")
    result = find_even_base_fiber_lift(base)

    assert result.program is not None
    report = tower_law_report(result.program, [1, 1], base_d=2)

    assert report.certified
    assert report.generativity_bit == 0
    assert report.zd_contextual is True


def test_explicit_bits_match_valid_lift():
    base = load_program(ROOT / "examples/tower_pair_d2_base.json")
    lifted = lift_program_with_bits(
        base,
        {
            "A": [0, 0],
            "A_inv": [1, 0],
        },
    )

    assert lifted.d == 4
    assert lifted.observables["A"] == (1, 0)
    assert lifted.observables["A_inv"] == (3, 0)
    assert check_zd_valuation(lifted).contextual


def test_pm_base_reports_no_linear_fiber_lift():
    base = load_program(ROOT / "examples/peres_mermin.json")
    result = find_even_base_fiber_lift(base)

    assert not result.constructed
    assert result.status == "no_linear_lift"


def test_fiber_lift_cli_writes_output(monkeypatch, capsys, tmp_path):
    out = tmp_path / "lifted.json"
    monkeypatch.setattr(
        "sys.argv",
        [
            "qkernel",
            "fiber-lift",
            str(ROOT / "examples/tower_pair_d2_base.json"),
            "--input",
            "weyl",
            "--out",
            str(out),
        ],
    )

    main()
    stdout = capsys.readouterr().out
    # Last line is the write notice; parse the JSON prefix.
    json_text = stdout.split("\nwrote lifted program:", 1)[0]
    data = json.loads(json_text)

    assert data["constructed"] is True
    assert out.exists()
    lifted = load_program(out)
    assert lifted.d == 4
