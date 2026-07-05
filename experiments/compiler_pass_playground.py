from __future__ import annotations

import json
from pathlib import Path

from qkernel.adapters.qiskit_lite import load_qiskit_lite_program
from qkernel.compiler import compare_compiler_pass_dict


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments" / "output"


def run_playground() -> tuple[Path, Path]:
    before_path = ROOT / "examples" / "compiler_before_qiskit_lite.json"
    after_path = ROOT / "examples" / "compiler_after_qiskit_lite.json"

    before = load_qiskit_lite_program(before_path)
    after = load_qiskit_lite_program(after_path)
    comparison = compare_compiler_pass_dict(before, after)

    OUT.mkdir(parents=True, exist_ok=True)
    json_path = OUT / "compiler_pass_playground.json"
    md_path = OUT / "compiler_pass_playground.md"

    json_path.write_text(json.dumps(comparison, indent=2), encoding="utf-8")

    md = [
        "# Compiler Pass Playground",
        "",
        "This is a conservative before/after diagnostic example.",
        "",
        "It does **not** prove a circuit rewrite is semantically valid.",
        "",
        "## Before",
        "",
        f"- contexts: {comparison['before']['contexts']}",
        f"- observables: {comparison['before']['observables']}",
        f"- components: {comparison['before']['components']}",
        f"- kernel contexts: {comparison['before']['kernel_contexts']}",
        f"- verified: {comparison['before']['verified']}",
        "",
        "## After",
        "",
        f"- contexts: {comparison['after']['contexts']}",
        f"- observables: {comparison['after']['observables']}",
        f"- components: {comparison['after']['components']}",
        f"- kernel contexts: {comparison['after']['kernel_contexts']}",
        f"- verified: {comparison['after']['verified']}",
        "",
        "## Delta",
        "",
        f"- context delta: {comparison['context_delta']}",
        f"- observable delta: {comparison['observable_delta']}",
        f"- kernel context delta: {comparison['kernel_context_delta']}",
        f"- requires semantic-equivalence proof: {comparison['requires_semantic_equivalence_proof']}",
        "",
        "## Verdict",
        "",
        comparison["verdict"],
        "",
    ]

    md_path.write_text("\n".join(md), encoding="utf-8")
    return json_path, md_path


def main() -> None:
    json_path, md_path = run_playground()
    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")


if __name__ == "__main__":
    main()
