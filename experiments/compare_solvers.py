from __future__ import annotations

import csv
import statistics
import time
from pathlib import Path

from generate_noisy_pm import noisy_pm_with_connected_zero_carry_ladder, noisy_pm_with_disconnected_checks
from qkernel.optimizer import compress_min_odd_q
from qkernel.verify import verify_kernel


OUT = Path(__file__).resolve().parent / "output"
OUT.mkdir(parents=True, exist_ok=True)


def time_call(fn, repeats: int = 3):
    values = []
    result = None
    for _ in range(repeats):
        start = time.perf_counter()
        result = fn()
        values.append(time.perf_counter() - start)
    return result, statistics.median(values)


def bench_case(name: str, program):
    rows = []
    solvers = [
        ("span", {"solver": "span"}),
        ("bounded_weight_6", {"solver": "bounded-weight", "max_weight": 6}),
        ("branch_bound", {"solver": "branch-bound"}),
        ("auto", {"solver": "auto"}),
    ]

    for solver_name, kwargs in solvers:
        try:
            kernel, elapsed = time_call(lambda: compress_min_odd_q(program, **kwargs))
            verification = verify_kernel(program, kernel)
            rows.append(
                {
                    "case": name,
                    "solver": solver_name,
                    "contexts": len(program.contexts),
                    "observables": len(program.observables),
                    "contextual": kernel.contextual,
                    "kernel_contexts": kernel.compressed_contexts,
                    "verified": verification.valid,
                    "elapsed_ms": round(elapsed * 1000, 4),
                    "error": "",
                }
            )
        except Exception as exc:
            rows.append(
                {
                    "case": name,
                    "solver": solver_name,
                    "contexts": len(program.contexts),
                    "observables": len(program.observables),
                    "contextual": False,
                    "kernel_contexts": 0,
                    "verified": False,
                    "elapsed_ms": None,
                    "error": type(exc).__name__ + ": " + str(exc),
                }
            )

    return rows


def main() -> None:
    cases = [
        ("pm_plus_0_disconnected", noisy_pm_with_disconnected_checks(0)),
        ("pm_plus_25_disconnected", noisy_pm_with_disconnected_checks(25)),
        ("pm_plus_100_disconnected", noisy_pm_with_disconnected_checks(100)),
        ("pm_plus_5_connected_ladder", noisy_pm_with_connected_zero_carry_ladder(5)),
        ("pm_plus_10_connected_ladder", noisy_pm_with_connected_zero_carry_ladder(10)),
    ]

    rows = []
    for name, program in cases:
        rows.extend(bench_case(name, program))

    csv_path = OUT / "compare_solvers.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    md_path = OUT / "compare_solvers.md"
    md_path.write_text(render_markdown(rows), encoding="utf-8")

    print(md_path.read_text(encoding="utf-8"))
    print(f"\nWrote: {csv_path}")
    print(f"Wrote: {md_path}")


def render_markdown(rows: list[dict]) -> str:
    headers = [
        "case",
        "solver",
        "contexts",
        "observables",
        "contextual",
        "kernel_contexts",
        "verified",
        "elapsed_ms",
        "error",
    ]
    lines = ["# Solver comparison", ""]
    lines.append(
        "Synthetic solver comparison. These are smoke-test benchmarks, not performance claims."
    )
    lines.append("")
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for row in rows:
        lines.append("| " + " | ".join(str(row[h]) for h in headers) + " |")
    lines.append("")
    lines.append(
        "Interpretation: use this to catch regressions and to identify when a future SAT/SMT/MILP backend becomes necessary."
    )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
