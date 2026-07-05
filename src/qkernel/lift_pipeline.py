from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path

from .fiber_lift import FiberLiftResult, fiber_lift_result_dict, find_even_base_fiber_lift
from .ir import WeylProgram
from .tower import TowerLawReport, tower_law_report
from .valuation import ZDValuationResult, check_zd_valuation


@dataclass(frozen=True)
class LiftPipelineReport:
    """End-to-end d -> 2d certification pipeline report."""

    constructed: bool
    base_d: int
    lifted_d: int | None
    selected_contexts: list[int]
    fiber_lift: dict
    zd_valuation: dict | None
    tower_law: dict | None
    safe_claim: str
    unsafe_claims: list[str]


def _selected_to_lambda(context_count: int, selected_contexts: list[int] | None) -> tuple[list[int], list[int]]:
    if selected_contexts is None:
        selected = list(range(context_count))
    else:
        selected = list(selected_contexts)

    lam = [0] * context_count
    for idx in selected:
        if idx < 0 or idx >= context_count:
            raise ValueError(f"context index out of range: {idx}")
        lam[idx] ^= 1

    normalized = [idx for idx, bit in enumerate(lam) if bit]
    return lam, normalized


def _zd_to_dict(result: ZDValuationResult) -> dict:
    return {
        "contextual": result.contextual,
        "status": result.status,
        "solvable": result.solvable,
        "modulus": result.modulus,
        "phases": result.phases,
        "observable_order": result.observable_order,
        "reason": result.reason,
    }


def run_lift_pipeline(
    base_program: WeylProgram,
    *,
    selected_contexts: list[int] | None = None,
) -> LiftPipelineReport:
    """Run fiber-lift -> Z_d valuation -> tower-law report.

    This is a reproducibility pipeline, not an optimizer. It constructs a valid
    even-base fiber lift when possible, verifies the lifted family via the full
    Z_d valuation system, and evaluates the closed tower/doubling generativity
    bit on the selected lifted contexts.
    """
    fiber = find_even_base_fiber_lift(base_program)

    if not fiber.constructed or fiber.program is None:
        return LiftPipelineReport(
            constructed=False,
            base_d=fiber.base_d,
            lifted_d=fiber.lifted_d,
            selected_contexts=[],
            fiber_lift=fiber_lift_result_dict(fiber),
            zd_valuation=None,
            tower_law=None,
            safe_claim="no lifted certificate was constructed",
            unsafe_claims=[
                "do not claim tower generativity",
                "do not claim Z_d contextuality of a missing lift",
                "do not claim compiler/resource optimization",
            ],
        )

    lam, selected = _selected_to_lambda(len(fiber.program.contexts), selected_contexts)
    zd = check_zd_valuation(fiber.program)
    tower = tower_law_report(fiber.program, lam, base_d=base_program.d)

    return LiftPipelineReport(
        constructed=True,
        base_d=base_program.d,
        lifted_d=fiber.program.d,
        selected_contexts=selected,
        fiber_lift=fiber_lift_result_dict(fiber),
        zd_valuation=_zd_to_dict(zd),
        tower_law=asdict(tower),
        safe_claim=(
            "validated fiber lift plus Z_d valuation result plus closed tower-law generativity report"
        ),
        unsafe_claims=[
            "does not prove resource advantage",
            "does not prove T-count or magic-cost improvement",
            "does not certify compiler rewrite legality",
            "does not certify tower compression as an optimization",
        ],
    )


def lift_pipeline_report_dict(report: LiftPipelineReport) -> dict:
    return asdict(report)


def lift_pipeline_report_markdown(report: LiftPipelineReport) -> str:
    lines = [
        "# Q-Kernel Lift Pipeline Report",
        "",
        f"- constructed: `{report.constructed}`",
        f"- base d: `{report.base_d}`",
        f"- lifted d: `{report.lifted_d}`",
        f"- selected contexts: `{report.selected_contexts}`",
        "",
        "## Safe claim",
        "",
        report.safe_claim,
        "",
        "## Unsafe claims",
        "",
    ]

    for claim in report.unsafe_claims:
        lines.append(f"- {claim}")

    lines.extend(["", "## Fiber lift", "", "```json", json.dumps(report.fiber_lift, indent=2), "```"])

    if report.zd_valuation is not None:
        lines.extend(["", "## Z_d valuation", "", "```json", json.dumps(report.zd_valuation, indent=2), "```"])

    if report.tower_law is not None:
        lines.extend(["", "## Tower law", "", "```json", json.dumps(report.tower_law, indent=2), "```"])

    return "\n".join(lines) + "\n"


def write_lift_pipeline_outputs(
    report: LiftPipelineReport,
    *,
    json_path: str | Path | None = None,
    markdown_path: str | Path | None = None,
) -> None:
    if json_path is not None:
        Path(json_path).write_text(json.dumps(lift_pipeline_report_dict(report), indent=2) + "\n", encoding="utf-8")

    if markdown_path is not None:
        Path(markdown_path).write_text(lift_pipeline_report_markdown(report), encoding="utf-8")
