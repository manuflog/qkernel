from __future__ import annotations

import csv
import statistics
import time
from pathlib import Path

from generate_noisy_pm import noisy_pm_with_disconnected_checks
from qkernel.decompose import decompose_components
from qkernel.optimizer import compress_min_odd_q
from qkernel.verify import verify_kernel


OUT = Path(__file__).resolve().parent / "output"
OUT.mkdir(parents=True, exist_ok=True)


def time_call(fn, repeats: int = 5):
    values = []
    result = None
    for _ in range(repeats):
        start = time.perf_counter()
        result = fn()
        values.append(time.perf_counter() - start)
    return result, statistics.median(values)


def main() -> None:
    rows = []

    for noise_blocks in [0, 1, 5, 10, 25, 50, 100, 250, 500]:
        program = noisy_pm_with_disconnected_checks(noise_blocks)

        components, t_components = time_call(lambda: decompose_components(program))
        kernel_decomp, t_decomp = time_call(lambda: compress_min_odd_q(program, decompose=True))
        verification, t_verify = time_call(lambda: verify_kernel(program, kernel_decomp))
        kernel_nodecomp, t_nodecomp = time_call(lambda: compress_min_odd_q(program, decompose=False))

        rows.append(
            {
                "noise_blocks": noise_blocks,
                "contexts": len(program.contexts),
                "observables": len(program.observables),
                "components": len(components),
                "kernel_contexts": kernel_decomp.compressed_contexts,
                "kernel_observables": kernel_decomp.compressed_observables,
                "verification_valid": verification.valid,
                "t_components_ms": round(t_components * 1000, 4),
                "t_compress_decomp_ms": round(t_decomp * 1000, 4),
                "t_compress_nodecomp_ms": round(t_nodecomp * 1000, 4),
                "t_verify_ms": round(t_verify * 1000, 4),
                "same_kernel": kernel_decomp.selected_contexts == kernel_nodecomp.selected_contexts,
            }
        )

    csv_path = OUT / "benchmark_decomposition.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    md_path = OUT / "benchmark_decomposition.md"
    md_path.write_text(render_markdown(rows), encoding="utf-8")

    print(md_path.read_text(encoding="utf-8"))
    print(f"\nWrote: {csv_path}")
    print(f"Wrote: {md_path}")


def render_markdown(rows: list[dict]) -> str:
    headers = [
        "noise_blocks",
        "contexts",
        "observables",
        "components",
        "kernel_contexts",
        "t_components_ms",
        "t_compress_decomp_ms",
        "t_compress_nodecomp_ms",
        "t_verify_ms",
        "same_kernel",
    ]
    lines = ["# Decomposition benchmark", ""]
    lines.append(
        "Synthetic PM core plus disconnected noncontextual closed triples. "
        "Numbers are median wall times over five repeats on the local test runtime."
    )
    lines.append("")
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for row in rows:
        lines.append("| " + " | ".join(str(row[h]) for h in headers) + " |")

    lines.append("")
    lines.append(
        "Interpretation: this benchmark does not prove compiler-scale performance. "
        "It checks that decomposition preserves the kernel and that verification remains cheap "
        "as disconnected irrelevant blocks grow."
    )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
