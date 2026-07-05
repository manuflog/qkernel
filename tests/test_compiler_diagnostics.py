import json
import subprocess
import sys
from pathlib import Path

from qkernel.compiler import compiler_report, compare_compiler_pass
from qkernel.examples import peres_mermin_program


ROOT = Path(__file__).resolve().parents[1]


def test_compiler_report_pm():
    report = compiler_report(peres_mermin_program())

    assert report.contextual
    assert report.verified
    assert report.kernel_contexts == 6
    assert report.optimization_claim == "diagnostic_only"
    assert any("semantic-equivalence" in item or "semantic" in item for item in report.unsafe_use)


def test_compare_compiler_pass_requires_semantic_proof():
    program = peres_mermin_program()
    comparison = compare_compiler_pass(program, program)

    assert comparison.requires_semantic_equivalence_proof
    assert comparison.kernel_context_delta == 0


def test_cli_compiler_report():
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "qkernel.cli",
            "compiler-report",
            str(ROOT / "examples/peres_mermin_pauli.json"),
            "--input",
            "pauli",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )

    data = json.loads(proc.stdout)
    assert data["contextual"] is True
    assert data["verified"] is True
    assert data["kernel_contexts"] == 6
    assert data["optimization_claim"] == "diagnostic_only"


def test_cli_compare_pass():
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "qkernel.cli",
            "compare-pass",
            str(ROOT / "examples/peres_mermin_pauli.json"),
            str(ROOT / "examples/peres_mermin_pauli.json"),
            "--input",
            "pauli",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )

    data = json.loads(proc.stdout)
    assert data["requires_semantic_equivalence_proof"] is True
    assert data["kernel_context_delta"] == 0
