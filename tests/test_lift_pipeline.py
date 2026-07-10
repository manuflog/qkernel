import json
from pathlib import Path

from qkernel.cli import main
from qkernel.io import load_program
from qkernel.lift_pipeline import (
    lift_pipeline_report_markdown,
    run_lift_pipeline,
    write_lift_pipeline_outputs,
)
from experiments.lift_pipeline_demo import run_demo


ROOT = Path(__file__).resolve().parents[1]


def test_lift_pipeline_constructs_full_report():
    base = load_program(ROOT / "examples/tower_pair_d2_base.json")
    report = run_lift_pipeline(base)

    assert report.constructed
    assert report.lifted_d == 4
    assert report.zd_valuation is not None
    assert report.zd_valuation["contextual"] is True
    assert report.tower_law is not None
    assert report.tower_law["certified"] is True
    assert report.tower_law["generativity_bit"] == 0
    assert "resource advantage" in " ".join(report.unsafe_claims)


def test_lift_pipeline_markdown_contains_claim_boundaries():
    base = load_program(ROOT / "examples/tower_pair_d2_base.json")
    report = run_lift_pipeline(base)
    md = lift_pipeline_report_markdown(report)

    assert "Safe claim" in md
    assert "Unsafe claims" in md
    assert "Tower law" in md
    assert "resource advantage" in md


def test_lift_pipeline_writes_outputs(tmp_path):
    base = load_program(ROOT / "examples/tower_pair_d2_base.json")
    report = run_lift_pipeline(base)
    json_path = tmp_path / "report.json"
    md_path = tmp_path / "report.md"

    write_lift_pipeline_outputs(report, json_path=json_path, markdown_path=md_path)

    assert json_path.exists()
    assert md_path.exists()
    data = json.loads(json_path.read_text(encoding="utf-8"))
    assert data["constructed"] is True


def test_lift_pipeline_cli(monkeypatch, capsys, tmp_path):
    out_program = tmp_path / "lifted.json"
    out_json = tmp_path / "report.json"
    out_md = tmp_path / "report.md"

    monkeypatch.setattr(
        "sys.argv",
        [
            "qkernel",
            "lift-pipeline",
            str(ROOT / "examples/tower_pair_d2_base.json"),
            "--input",
            "weyl",
            "--out-program",
            str(out_program),
            "--out-json",
            str(out_json),
            "--out-md",
            str(out_md),
        ],
    )

    main()
    stdout = capsys.readouterr().out
    json_text = stdout.split("\nwrote lifted program:", 1)[0]
    data = json.loads(json_text)

    assert data["constructed"] is True
    assert out_program.exists()
    assert out_json.exists()
    assert out_md.exists()


def test_lift_pipeline_demo_script_outputs():
    program_path, json_path, md_path = run_demo()

    assert program_path.exists()
    assert json_path.exists()
    assert md_path.exists()
    data = json.loads(json_path.read_text(encoding="utf-8"))
    assert data["constructed"] is True
