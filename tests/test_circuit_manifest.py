import json
import subprocess
import sys
from pathlib import Path

from qkernel.circuit_manifest import (
    circuit_builder_manifest,
    circuit_builder_manifest_dict,
    circuit_builder_manifest_markdown,
)
from qkernel.examples import peres_mermin_program
from qkernel.io import load_program


ROOT = Path(__file__).resolve().parents[1]


def test_circuit_manifest_marks_pm_exportable_without_emitting_script():
    report = circuit_builder_manifest(peres_mermin_program(), program_id="pm")
    data = circuit_builder_manifest_dict(report)

    assert data["schema"] == "qkernel.circuit_manifest.v1"
    assert data["program_id"] == "pm"
    assert data["exportable"] is True
    assert data["supported_exporter"] == "export_qiskit_protocol"
    assert data["blocker_reasons"] == []
    assert "does not optimize T-count or magic-state cost" in data["not_claimed"]
    json.dumps(data)


def test_circuit_manifest_reports_high_d_blockers():
    program = load_program(ROOT / "examples/activation_base_d4.json")
    data = circuit_builder_manifest_dict(circuit_builder_manifest(program, program_id="d4_base"))

    assert data["exportable"] is False
    assert data["supported_exporter"] is None
    assert any("d=2 required" in item for item in data["blocker_reasons"])
    assert any("do not emit" in item for item in data["next_actions"])


def test_circuit_manifest_markdown_contains_scope_and_blockers():
    program = load_program(ROOT / "examples/activation_base_d4.json")
    md = circuit_builder_manifest_markdown(circuit_builder_manifest(program))

    assert "# Circuit Builder Manifest" in md
    assert "## Blockers" in md
    assert "d=2 required" in md
    assert "does not synthesize unsupported qudit protocols" in md


def test_cli_circuit_manifest_writes_markdown(tmp_path):
    out = tmp_path / "circuit_manifest.md"
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "qkernel.cli",
            "circuit-manifest",
            str(ROOT / "examples/peres_mermin.json"),
            "--program-id",
            "pm",
            "--out-md",
            str(out),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )

    assert f"wrote Markdown circuit builder manifest: {out}" in proc.stdout
    data = json.loads(proc.stdout.split("\nwrote Markdown circuit builder manifest:", 1)[0])
    assert data["exportable"] is True
    assert "export_qiskit_protocol" in out.read_text(encoding="utf-8")
