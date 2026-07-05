from __future__ import annotations

from pathlib import Path

from qkernel.io import dump_program, load_program
from qkernel.fiber_lift import find_even_base_fiber_lift
from qkernel.lift_pipeline import run_lift_pipeline, write_lift_pipeline_outputs


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments" / "output"


def run_demo() -> tuple[Path, Path, Path]:
    base = load_program(ROOT / "examples" / "tower_pair_d2_base.json")
    report = run_lift_pipeline(base)

    OUT.mkdir(parents=True, exist_ok=True)
    program_path = OUT / "lift_pipeline_demo_lifted.json"
    json_path = OUT / "lift_pipeline_demo_report.json"
    md_path = OUT / "lift_pipeline_demo_report.md"

    fiber = find_even_base_fiber_lift(base)
    if fiber.program is not None:
        dump_program(fiber.program, program_path)

    write_lift_pipeline_outputs(report, json_path=json_path, markdown_path=md_path)
    return program_path, json_path, md_path


def main() -> None:
    program_path, json_path, md_path = run_demo()
    print(f"Wrote: {program_path}")
    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")


if __name__ == "__main__":
    main()
