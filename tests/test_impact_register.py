import json
import subprocess
import sys

from qkernel.impact_register import (
    impact_register_markdown,
    impact_register_report,
    impact_register_report_dict,
)


def test_impact_register_tracks_application_surfaces_and_non_claims():
    report = impact_register_report()
    data = impact_register_report_dict(report)
    applications = {app["application_id"]: app for app in data["applications"]}

    assert data["schema"] == "qkernel.impact_register.v1"
    assert data["summary"]["total_applications"] >= 8
    assert data["summary"]["implemented"] >= 7
    assert "compiler_candidates" in applications
    assert "factory_candidates" in applications
    assert "circuit_builder" in applications
    assert "new_application_prd" in applications
    assert "compiler-candidates" in applications["compiler_candidates"]["commands"]
    assert "factory-candidates" in applications["factory_candidates"]["commands"]
    assert "does not claim qkernel is a production compiler" in data["not_claimed"]
    json.dumps(data)


def test_impact_register_entries_keep_evidence_gaps_visible():
    data = impact_register_report_dict(impact_register_report())

    for app in data["applications"]:
        assert app["missing_evidence"], app["application_id"]
        assert app["next_actions"], app["application_id"]
        assert app["not_claimed"], app["application_id"]
        assert app["claim_scope"], app["application_id"]


def test_impact_register_markdown_mentions_magic_compiler_and_circuit_builder():
    md = impact_register_markdown(impact_register_report())

    assert "# QKernel Application Impact Register" in md
    assert "Compiler and optimizer candidate corpus" in md
    assert "MagicScout motif triage" in md
    assert "Circuit builder readiness manifest" in md
    assert "does not claim resource improvements without external resource evidence" in md


def test_cli_impact_register_writes_markdown(tmp_path):
    out = tmp_path / "impact_register.md"
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "qkernel.cli",
            "impact-register",
            "--out-md",
            str(out),
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    assert f"wrote Markdown impact register: {out}" in proc.stdout
    data = json.loads(proc.stdout.split("\nwrote Markdown impact register:", 1)[0])
    assert "compiler_candidates" in data["summary"]["application_ids"]
    assert "Magic-state factory candidate ledger" in out.read_text(encoding="utf-8")
