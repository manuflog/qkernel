import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PM_PROTOCOL = ROOT / "examples/magic_protocol_pm_probe.json"
PM_PAULIS = ["XI", "IX", "XX", "IY", "YI", "YY", "XY", "YX", "ZZ"]


def _run_qkernel(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "qkernel.cli", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )


def test_cli_magic_protocol_outputs_report_json():
    proc = _run_qkernel("magic-protocol", str(PM_PROTOCOL))
    data = json.loads(proc.stdout)

    assert data["protocol_id"] == "pm_magic_probe"
    assert data["contextual"] is True
    assert data["kernel_weight"] == 6
    assert data["criterion_ledger"]["criterion_id"] == "odd_Q_even_d_v1"


def test_cli_magic_search_outputs_ranked_json():
    proc = _run_qkernel("magic-search", *PM_PAULIS, "--top", "1")
    data = json.loads(proc.stdout)

    assert data["candidates_returned"] == 1
    assert data["results"][0]["rank"] == 1
    assert data["results"][0]["report"]["contextual"] is True
    assert "magic-state factory synthesis" in data["not_claimed"]


def test_cli_magic_templates_and_assessment():
    catalog = json.loads(_run_qkernel("magic-templates").stdout)
    assert catalog["count"] >= 5

    assessed = json.loads(
        _run_qkernel(
            "magic-template-assess",
            str(PM_PROTOCOL),
            "--template",
            "contextuality_witness",
        ).stdout
    )
    assert assessed["count"] == 1
    assert assessed["compatible_count"] == 1


def test_cli_magic_report_writes_markdown(tmp_path):
    out = tmp_path / "magic_report.md"
    proc = _run_qkernel("magic-report", str(PM_PROTOCOL), "--out", str(out))

    assert f"wrote Markdown MagicScout report: {out}" in proc.stdout
    text = out.read_text(encoding="utf-8")
    assert "# MagicScout Report" in text
    assert "## Criterion ledger" in text
