import json
import subprocess
import sys
from pathlib import Path

from qkernel.compiler_candidates import (
    compiler_candidate_corpus_report,
    compiler_candidate_corpus_report_dict,
    compiler_candidate_markdown,
)


ROOT = Path(__file__).resolve().parents[1]


def test_compiler_candidate_corpus_reports_diagnostic_only_status():
    report = compiler_candidate_corpus_report(ROOT / "examples/compiler_candidate_corpus.json")
    data = compiler_candidate_corpus_report_dict(report)
    candidate = data["candidates"][0]

    assert data["schema"] == "qkernel.compiler_candidates.v1"
    assert data["corpus_id"] == "compiler_candidate_demo"
    assert candidate["candidate_id"] == "pm_nonkernel_prune_qiskit_lite"
    assert candidate["candidate_status"] == "diagnostic_only_missing_semantic_proof"
    assert candidate["allowed_to_report"] is True
    assert candidate["allowed_to_apply"] is False
    assert candidate["comparison"]["requires_semantic_equivalence_proof"] is True
    assert candidate["comparison"]["context_delta"] < 0
    assert "does not reduce T-count" in candidate["not_claimed"]
    assert any("semantic-equivalence proof" in item for item in candidate["missing_evidence"])
    json.dumps(data)


def test_compiler_candidate_markdown_contains_guardrails():
    report = compiler_candidate_corpus_report(ROOT / "examples/compiler_candidate_corpus.json")
    md = compiler_candidate_markdown(report)

    assert "# Compiler Candidate Corpus" in md
    assert "pm_nonkernel_prune_qiskit_lite" in md
    assert "diagnostic_only_missing_semantic_proof" in md
    assert "does not certify compiler rewrites" in md


def test_cli_compiler_candidates_writes_markdown(tmp_path):
    out = tmp_path / "compiler_candidates.md"
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "qkernel.cli",
            "compiler-candidates",
            str(ROOT / "examples/compiler_candidate_corpus.json"),
            "--out-md",
            str(out),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )

    assert f"wrote Markdown compiler candidate report: {out}" in proc.stdout
    data = json.loads(proc.stdout.split("\nwrote Markdown compiler candidate report:", 1)[0])
    assert data["candidates"][0]["allowed_to_apply"] is False
    assert "diagnostic_only_missing_semantic_proof" in out.read_text(encoding="utf-8")
