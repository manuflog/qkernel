import json
import subprocess
import sys
from pathlib import Path

from qkernel.factory_candidates import (
    factory_candidate_corpus_report,
    factory_candidate_corpus_report_dict,
    factory_candidate_markdown,
)


ROOT = Path(__file__).resolve().parents[1]


def test_factory_candidate_corpus_reports_template_compatible_but_not_factory():
    report = factory_candidate_corpus_report(ROOT / "examples/factory_candidate_corpus.json")
    data = factory_candidate_corpus_report_dict(report)
    candidate = data["candidates"][0]

    assert data["schema"] == "qkernel.factory_candidates.v1"
    assert data["corpus_id"] == "factory_candidate_demo"
    assert candidate["candidate_id"] == "pm_magic_verification_candidate"
    assert candidate["magic_report"]["contextual"] is True
    assert candidate["magic_report"]["kernel_weight"] == 6
    assert "contextuality_witness" in candidate["compatible_template_ids"]
    assert "magic_verification_subroutine" in candidate["compatible_template_ids"]
    assert candidate["candidate_status"] == "template_compatible_missing_factory_metrics"
    assert "valid magic-state factory" in candidate["not_claimed"]
    assert any("factory metrics" in item for item in candidate["missing_evidence"])
    json.dumps(data)


def test_factory_candidate_markdown_contains_non_claims():
    report = factory_candidate_corpus_report(ROOT / "examples/factory_candidate_corpus.json")
    md = factory_candidate_markdown(report)

    assert "# Factory Candidate Corpus" in md
    assert "pm_magic_verification_candidate" in md
    assert "template_compatible_missing_factory_metrics" in md
    assert "does not construct valid magic-state factories" in md


def test_cli_factory_candidates_writes_markdown(tmp_path):
    out = tmp_path / "factory_candidates.md"
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "qkernel.cli",
            "factory-candidates",
            str(ROOT / "examples/factory_candidate_corpus.json"),
            "--out-md",
            str(out),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )

    assert f"wrote Markdown factory candidate report: {out}" in proc.stdout
    data = json.loads(proc.stdout.split("\nwrote Markdown factory candidate report:", 1)[0])
    assert data["candidates"][0]["candidate_status"] == "template_compatible_missing_factory_metrics"
    assert "does not construct valid magic-state factories" in out.read_text(encoding="utf-8")
