import json
import subprocess
import sys
from pathlib import Path

import pytest

from qkernel.application_packet import (
    application_evidence_packet,
    application_evidence_packet_dict,
    application_evidence_packet_markdown,
    load_application_packet_spec,
)


ROOT = Path(__file__).resolve().parents[1]


def test_application_packet_loads_existing_evidence_sources():
    packet = application_evidence_packet(ROOT / "examples/application_packet_demo.json")
    data = application_evidence_packet_dict(packet)
    sources = {source["source_id"]: source for source in data["sources"]}

    assert data["schema"] == "qkernel.application_packet.v1"
    assert data["packet_id"] == "application_workbench_demo"
    assert data["summary"]["total_candidates"] == 3
    assert data["summary"]["ready_for_claims"] is False
    assert data["summary"]["uncovered_tracked_candidates"] == []
    assert sources["compiler_demo"]["exists"] is True
    assert sources["factory_demo"]["exists"] is True
    assert sources["correlation_demo"]["exists"] is True
    assert sources["compiler_demo"]["claim_gate_status"] == "blocked"
    assert "external semantic-equivalence proof is not attached" in sources["compiler_demo"]["missing_evidence"]
    assert "pm_magic_verification_candidate" in sources["factory_demo"]["candidate_ids"]
    json.dumps(data)


def test_application_packet_rejects_duplicate_tracked_candidate_ids(tmp_path):
    packet = {
        "packet_id": "bad_packet",
        "tracked_candidates": [
            {"candidate_id": "same", "role": "compiler"},
            {"candidate_id": "same", "role": "factory"},
        ],
        "sources": [],
    }
    path = tmp_path / "packet.json"
    path.write_text(json.dumps(packet), encoding="utf-8")

    with pytest.raises(ValueError, match="duplicate tracked candidate id"):
        load_application_packet_spec(path)


def test_application_packet_blocks_uncovered_tracked_candidates(tmp_path):
    packet = {
        "packet_id": "uncovered_packet",
        "tracked_candidates": [
            {
                "candidate_id": "not_in_source",
                "role": "compiler_candidate",
            },
        ],
        "sources": [
            {
                "source_id": "correlation_demo",
                "source_type": "correlation_study",
                "path": str(ROOT / "examples/resource_correlation_study.json"),
            },
        ],
    }
    path = tmp_path / "packet.json"
    path.write_text(json.dumps(packet), encoding="utf-8")

    data = application_evidence_packet_dict(application_evidence_packet(path))

    assert data["summary"]["ready_for_claims"] is False
    assert data["summary"]["uncovered_tracked_candidates"] == ["not_in_source"]
    assert "tracked candidate not covered by any loaded source: not_in_source" in data["summary"]["blocker_reasons"]


def test_application_packet_markdown_preserves_claim_gates():
    md = application_evidence_packet_markdown(
        application_evidence_packet(ROOT / "examples/application_packet_demo.json")
    )

    assert "# Application Workbench Demo Packet" in md
    assert "## Missing Evidence" in md
    assert "compiler_demo" in md
    assert "does not claim qkernel is a production compiler" in md
    assert "Keep this packet in evidence-gathering mode" in md


def test_cli_application_packet_writes_markdown(tmp_path):
    out = tmp_path / "packet.md"
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "qkernel.cli",
            "application-packet",
            str(ROOT / "examples/application_packet_demo.json"),
            "--out-md",
            str(out),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )

    assert f"wrote Markdown application evidence packet: {out}" in proc.stdout
    data = json.loads(proc.stdout.split("\nwrote Markdown application evidence packet:", 1)[0])
    assert data["summary"]["sources_with_blockers"] >= 1
    assert "Application Workbench Demo Packet" in out.read_text(encoding="utf-8")
