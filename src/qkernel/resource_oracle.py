from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .ir import WeylProgram
from .subroutine import analyze_contextuality


SCHEMA_VERSION = "qkernel.resource_oracle.v1"


@dataclass(frozen=True)
class ExternalResourceMetrics:
    program_id: str
    source: str
    t_count: int | None = None
    t_depth: int | None = None
    magic_injections: int | None = None
    stabilizer_rank: int | None = None
    notes: str = ""


@dataclass(frozen=True)
class QKernelResourceFeatures:
    program_id: str
    contexts: int
    observables: int
    contextual: bool
    kernel_weight: int | None
    n_minimal_kernels: int | None
    obstruction_value: int | None
    zd_avn_contextual: bool | None
    verified: bool
    criterion_ledger: dict[str, Any] | None


@dataclass(frozen=True)
class ResourceOracleReport:
    schema: str
    features: QKernelResourceFeatures
    external_metrics: ExternalResourceMetrics | None
    comparison_status: str
    missing_evidence: list[str]
    next_actions: list[str]
    claim_scope: str
    not_claimed: list[str]


def _optional_nonnegative_int(item: dict[str, Any], key: str) -> int | None:
    value = item.get(key)
    if value is None:
        return None
    out = int(value)
    if out < 0:
        raise ValueError(f"resource metric `{key}` must be non-negative")
    return out


def _resource_metrics_from_dict(item: dict[str, Any]) -> ExternalResourceMetrics:
    if "program_id" not in item:
        raise ValueError("external resource metrics require `program_id`")
    if "source" not in item:
        raise ValueError("external resource metrics require `source`")
    return ExternalResourceMetrics(
        program_id=str(item["program_id"]),
        source=str(item["source"]),
        t_count=_optional_nonnegative_int(item, "t_count"),
        t_depth=_optional_nonnegative_int(item, "t_depth"),
        magic_injections=_optional_nonnegative_int(item, "magic_injections"),
        stabilizer_rank=_optional_nonnegative_int(item, "stabilizer_rank"),
        notes=str(item.get("notes", "")),
    )


def load_external_resource_metrics(path: str | Path) -> ExternalResourceMetrics:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    metrics_data = data.get("external_resource_metrics", data)
    if not isinstance(metrics_data, dict):
        raise ValueError("resource metrics file must be an object or contain `external_resource_metrics`")
    return _resource_metrics_from_dict(metrics_data)


def resource_feature_report(
    program: WeylProgram,
    *,
    program_id: str = "program",
    external_metrics: ExternalResourceMetrics | None = None,
) -> ResourceOracleReport:
    result = analyze_contextuality(program, enumerate_all_kernels=True)
    ledger = result.criterion_ledger or {}
    features = QKernelResourceFeatures(
        program_id=program_id,
        contexts=len(program.contexts),
        observables=len(program.observables),
        contextual=result.contextual,
        kernel_weight=result.kernel_weight,
        n_minimal_kernels=result.n_minimal_kernels,
        obstruction_value=result.obstruction_value,
        zd_avn_contextual=ledger.get("stronger_verifier_passed"),
        verified=result.verified,
        criterion_ledger=result.criterion_ledger,
    )

    missing_evidence = [
        "no bridge theorem from odd-Q kernel features to T-count, T-depth, magic injections, or stabilizer rank",
        "no validated statistical correlation study attached",
    ]
    next_actions = [
        "collect an external resource-oracle table over a benchmark corpus",
        "fit and validate correlations outside qkernel before making resource claims",
        "keep qkernel features and external resource metrics as separate columns",
    ]
    comparison_status = "no_external_resource_oracle"
    if external_metrics is not None:
        comparison_status = "external_metrics_attached"
        next_actions.insert(1, "compare this row against additional oracle rows before interpreting trends")

    return ResourceOracleReport(
        schema=SCHEMA_VERSION,
        features=features,
        external_metrics=external_metrics,
        comparison_status=comparison_status,
        missing_evidence=missing_evidence,
        next_actions=next_actions,
        claim_scope=(
            "exploratory feature export for external resource-correlation studies; "
            "qkernel does not compute or predict compiler resource metrics"
        ),
        not_claimed=[
            "does not predict T-count",
            "does not predict T-depth",
            "does not predict magic injections",
            "does not predict stabilizer rank",
            "does not prove resource advantage",
        ],
    )


def resource_oracle_report_dict(report: ResourceOracleReport) -> dict:
    return asdict(report)


def _fmt(value: object) -> str:
    if value is None:
        return "-"
    if value is True:
        return "yes"
    if value is False:
        return "no"
    return str(value)


def resource_oracle_markdown(report: ResourceOracleReport | dict) -> str:
    data = asdict(report) if isinstance(report, ResourceOracleReport) else report
    features = data["features"]
    metrics = data.get("external_metrics") or {}
    lines = [
        "# Resource Oracle Feature Report",
        "",
        "## Scope",
        "",
        data["claim_scope"],
        "",
        "## Q-Kernel Features",
        "",
        "| field | value |",
        "| --- | --- |",
    ]
    for key in [
        "program_id",
        "contexts",
        "observables",
        "contextual",
        "kernel_weight",
        "n_minimal_kernels",
        "obstruction_value",
        "zd_avn_contextual",
        "verified",
    ]:
        lines.append(f"| {key} | {_fmt(features.get(key))} |")
    lines.extend([
        "",
        "## External Resource Metrics",
        "",
        "| field | value |",
        "| --- | --- |",
    ])
    for key in ["program_id", "source", "t_count", "t_depth", "magic_injections", "stabilizer_rank", "notes"]:
        lines.append(f"| {key} | {_fmt(metrics.get(key))} |")
    lines.extend([
        "",
        "## Missing Evidence",
        "",
        "\n".join(f"- {item}" for item in data["missing_evidence"]),
        "",
        "## Next Actions",
        "",
        "\n".join(f"- {item}" for item in data["next_actions"]),
        "",
        "## Non-Claims",
        "",
        "\n".join(f"- {item}" for item in data["not_claimed"]),
        "",
    ])
    return "\n".join(lines)


def write_resource_oracle_markdown(report: ResourceOracleReport | dict, path: str | Path) -> None:
    Path(path).write_text(resource_oracle_markdown(report), encoding="utf-8")
