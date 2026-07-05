import json
import subprocess
import sys
from pathlib import Path

from qkernel.adapters.qiskit_lite import load_qiskit_lite_program
from qkernel.compiler import compare_compiler_pass
from experiments.compiler_pass_playground import run_playground


ROOT = Path(__file__).resolve().parents[1]


def test_compiler_playground_examples_compare_as_nonkernel_pruning():
    before = load_qiskit_lite_program(ROOT / "examples/compiler_before_qiskit_lite.json")
    after = load_qiskit_lite_program(ROOT / "examples/compiler_after_qiskit_lite.json")

    comparison = compare_compiler_pass(before, after)

    assert comparison.before.contextual
    assert comparison.after.contextual
    assert comparison.before.kernel_contexts == 6
    assert comparison.after.kernel_contexts == 6
    assert comparison.context_delta < 0
    assert comparison.observable_delta < 0
    assert comparison.requires_semantic_equivalence_proof
    assert "nonkernel" in comparison.verdict


def test_cli_compare_pass_playground():
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "qkernel.cli",
            "compare-pass",
            str(ROOT / "examples/compiler_before_qiskit_lite.json"),
            str(ROOT / "examples/compiler_after_qiskit_lite.json"),
            "--input",
            "qiskit-lite",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )

    data = json.loads(proc.stdout)

    assert data["context_delta"] < 0
    assert data["observable_delta"] < 0
    assert data["kernel_context_delta"] == 0
    assert data["requires_semantic_equivalence_proof"] is True
    assert "nonkernel" in data["verdict"]


def test_compiler_pass_playground_script_writes_outputs():
    json_path, md_path = run_playground()

    assert json_path.exists()
    assert md_path.exists()

    data = json.loads(json_path.read_text(encoding="utf-8"))
    md = md_path.read_text(encoding="utf-8")

    assert data["context_delta"] < 0
    assert "Compiler Pass Playground" in md
    assert "semantic-equivalence proof" in md
