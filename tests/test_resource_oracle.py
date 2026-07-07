import json
import subprocess
import sys
from pathlib import Path

from qkernel.io import load_program
from qkernel.resource_oracle import (
    load_external_resource_metrics,
    resource_feature_report,
    resource_oracle_markdown,
    resource_oracle_report_dict,
)


ROOT = Path(__file__).resolve().parents[1]


def test_resource_feature_report_exports_qkernel_features_without_claiming_resources():
    program = load_program(ROOT / "examples/peres_mermin.json")
    report = resource_feature_report(program, program_id="peres_mermin_probe")
    data = resource_oracle_report_dict(report)

    assert data["schema"] == "qkernel.resource_oracle.v1"
    assert data["features"]["program_id"] == "peres_mermin_probe"
    assert data["features"]["contextual"] is True
    assert data["features"]["kernel_weight"] == 6
    assert data["features"]["zd_avn_contextual"] is True
    assert data["external_metrics"] is None
    assert data["comparison_status"] == "no_external_resource_oracle"
    assert "does not predict T-count" in data["not_claimed"]
    assert any("bridge theorem" in item for item in data["missing_evidence"])
    json.dumps(data)


def test_resource_feature_report_attaches_external_metrics_without_relabeling_them():
    program = load_program(ROOT / "examples/peres_mermin.json")
    metrics = load_external_resource_metrics(ROOT / "examples/resource_metrics_stub.json")
    report = resource_feature_report(program, program_id="peres_mermin_probe", external_metrics=metrics)
    data = resource_oracle_report_dict(report)

    assert data["comparison_status"] == "external_metrics_attached"
    assert data["external_metrics"]["program_id"] == "peres_mermin_probe"
    assert data["external_metrics"]["source"] == "external-resource-oracle-placeholder"
    assert data["external_metrics"]["t_count"] is None
    assert "does not prove resource advantage" in data["not_claimed"]


def test_resource_oracle_markdown_preserves_scope_and_non_claims():
    program = load_program(ROOT / "examples/peres_mermin.json")
    metrics = load_external_resource_metrics(ROOT / "examples/resource_metrics_stub.json")
    md = resource_oracle_markdown(resource_feature_report(program, external_metrics=metrics))

    assert "# Resource Oracle Feature Report" in md
    assert "## External Resource Metrics" in md
    assert "external-resource-oracle-placeholder" in md
    assert "does not predict T-count" in md
    assert "no bridge theorem" in md


def test_cli_resource_features_with_markdown(tmp_path):
    out = tmp_path / "resource_features.md"
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "qkernel.cli",
            "resource-features",
            str(ROOT / "examples/peres_mermin.json"),
            "--program-id",
            "peres_mermin_probe",
            "--resource-metrics",
            str(ROOT / "examples/resource_metrics_stub.json"),
            "--out-md",
            str(out),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )

    assert f"wrote Markdown resource feature report: {out}" in proc.stdout
    data = json.loads(proc.stdout.split("\nwrote Markdown resource feature report:", 1)[0])
    assert data["features"]["kernel_weight"] == 6
    assert data["comparison_status"] == "external_metrics_attached"
    assert "does not predict T-count" in out.read_text(encoding="utf-8")
