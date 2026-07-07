import json
import subprocess
import sys
from pathlib import Path

from qkernel.correlation_study import (
    correlation_study_markdown,
    correlation_study_report,
    correlation_study_report_dict,
)


ROOT = Path(__file__).resolve().parents[1]


def test_correlation_study_joins_features_metrics_and_controls():
    report = correlation_study_report(ROOT / "examples/resource_correlation_study.json")
    data = correlation_study_report_dict(report)
    rows = {row["program_id"]: row for row in data["rows"]}

    assert data["schema"] == "qkernel.correlation_study.v1"
    assert data["study_id"] == "resource_correlation_demo"
    assert data["summary"]["total_rows"] == 3
    assert data["summary"]["rows_with_external_metrics"] == 3
    assert data["summary"]["negative_controls"] == 1
    assert data["summary"]["correlation_ready"] is True
    assert rows["peres_mermin_probe"]["qkernel_features"]["kernel_weight"] == 6
    assert rows["peres_mermin_probe"]["external_resource_metrics"]["t_count"] == 7
    assert rows["single_context_negative_control"]["negative_control"] is True
    assert rows["single_context_negative_control"]["interpretation_status"] == (
        "negative_control_do_not_infer_resource_signal"
    )
    assert "does not prove a resource theorem" in data["not_claimed"]
    json.dumps(data)


def test_correlation_study_markdown_is_correlation_only():
    report = correlation_study_report(ROOT / "examples/resource_correlation_study.json")
    md = correlation_study_markdown(report)

    assert "# Correlation Study Report" in md
    assert "correlation_ready" in md
    assert "single_context_negative_control" in md
    assert "does not predict resource metrics" in md


def test_cli_correlation_study_writes_markdown(tmp_path):
    out = tmp_path / "correlation_study.md"
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "qkernel.cli",
            "correlation-study",
            str(ROOT / "examples/resource_correlation_study.json"),
            "--out-md",
            str(out),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )

    assert f"wrote Markdown correlation study report: {out}" in proc.stdout
    data = json.loads(proc.stdout.split("\nwrote Markdown correlation study report:", 1)[0])
    assert data["summary"]["correlation_ready"] is True
    assert "does not optimize T-count" in out.read_text(encoding="utf-8")
