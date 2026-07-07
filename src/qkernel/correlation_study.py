from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal

from .adapters.pauli_table import load_pauli_table
from .adapters.qiskit_lite import load_qiskit_lite_program
from .adapters.stim_lite import load_stim_lite_program
from .io import load_program
from .pauli import load_pauli_program
from .pauli_schedule import load_pauli_schedule
from .resource_oracle import ExternalResourceMetrics, _resource_metrics_from_dict, resource_feature_report


SCHEMA_VERSION = "qkernel.correlation_study.v1"
InputKind = Literal["weyl", "pauli", "schedule", "table", "stim-lite", "qiskit-lite"]


@dataclass(frozen=True)
class CorrelationStudyRowSpec:
    program_id: str
    path: str
    input_kind: InputKind
    role: str = "candidate"
    external_resource_metrics: ExternalResourceMetrics | None = None
    notes: str = ""


@dataclass(frozen=True)
class CorrelationStudyRow:
    program_id: str
    role: str
    path: str
    input_kind: InputKind
    qkernel_features: dict[str, Any]
    external_resource_metrics: dict[str, Any] | None
    has_external_metrics: bool
    negative_control: bool
    interpretation_status: str
    notes: str


@dataclass(frozen=True)
class CorrelationStudySummary:
    total_rows: int
    rows_with_external_metrics: int
    contextual_rows: int
    negative_controls: int
    complete_metric_counts: dict[str, int]
    correlation_ready: bool
    blocker_reasons: list[str]


@dataclass(frozen=True)
class CorrelationStudyReport:
    schema: str
    study_id: str
    rows: list[CorrelationStudyRow]
    summary: CorrelationStudySummary
    claim_scope: str
    not_claimed: list[str]
    next_actions: list[str]


def _load_by_kind(path: Path, kind: InputKind):
    if kind == "weyl":
        return load_program(path)
    if kind == "pauli":
        return load_pauli_program(path)
    if kind == "schedule":
        return load_pauli_schedule(path)
    if kind == "table":
        return load_pauli_table(path)
    if kind == "stim-lite":
        return load_stim_lite_program(path)
    if kind == "qiskit-lite":
        return load_qiskit_lite_program(path)
    raise ValueError(f"unknown input kind {kind!r}")


def _row_spec_from_dict(item: dict[str, Any]) -> CorrelationStudyRowSpec:
    required = ["program_id", "path", "input_kind"]
    missing = [key for key in required if key not in item]
    if missing:
        raise ValueError(f"correlation study row missing required field(s): {', '.join(missing)}")
    kind = str(item["input_kind"])
    if kind not in {"weyl", "pauli", "schedule", "table", "stim-lite", "qiskit-lite"}:
        raise ValueError(f"unknown correlation study input_kind {kind!r}")
    metrics_data = item.get("external_resource_metrics")
    metrics = _resource_metrics_from_dict(metrics_data) if isinstance(metrics_data, dict) else None
    return CorrelationStudyRowSpec(
        program_id=str(item["program_id"]),
        path=str(item["path"]),
        input_kind=kind,  # type: ignore[arg-type]
        role=str(item.get("role", "candidate")),
        external_resource_metrics=metrics,
        notes=str(item.get("notes", "")),
    )


def load_correlation_study_specs(path: str | Path) -> tuple[str, list[CorrelationStudyRowSpec]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    rows_data = data.get("rows", data.get("corpus", data))
    if not isinstance(rows_data, list):
        raise ValueError("correlation study file must be a list or contain a `rows` list")
    study_id = str(data.get("study_id", "correlation_study")) if isinstance(data, dict) else "correlation_study"
    specs = [_row_spec_from_dict(item) for item in rows_data]
    seen: set[str] = set()
    for spec in specs:
        if spec.program_id in seen:
            raise ValueError(f"duplicate correlation study program_id {spec.program_id!r}")
        seen.add(spec.program_id)
    return study_id, specs


def _interpretation_status(features: dict[str, Any], metrics: ExternalResourceMetrics | None, role: str) -> str:
    if role == "negative_control":
        return "negative_control_do_not_infer_resource_signal"
    if metrics is None:
        return "missing_external_resource_metrics"
    if not features.get("contextual"):
        return "metrics_attached_noncontextual_control"
    return "joined_row_for_correlation_only"


def _summary(rows: list[CorrelationStudyRow]) -> CorrelationStudySummary:
    metric_names = ["t_count", "t_depth", "magic_injections", "stabilizer_rank"]
    complete_counts = {
        name: sum(
            1
            for row in rows
            if row.external_resource_metrics is not None and row.external_resource_metrics.get(name) is not None
        )
        for name in metric_names
    }
    blockers: list[str] = []
    rows_with_metrics = sum(1 for row in rows if row.has_external_metrics)
    negative_controls = sum(1 for row in rows if row.negative_control)
    if rows_with_metrics < 3:
        blockers.append("fewer than 3 rows have external resource metrics")
    if negative_controls == 0:
        blockers.append("no negative-control rows supplied")
    if not any(count >= 3 for count in complete_counts.values()):
        blockers.append("no resource metric has at least 3 populated rows")
    return CorrelationStudySummary(
        total_rows=len(rows),
        rows_with_external_metrics=rows_with_metrics,
        contextual_rows=sum(1 for row in rows if bool(row.qkernel_features.get("contextual"))),
        negative_controls=negative_controls,
        complete_metric_counts=complete_counts,
        correlation_ready=not blockers,
        blocker_reasons=blockers,
    )


def correlation_study_report(path: str | Path) -> CorrelationStudyReport:
    study_path = Path(path)
    study_id, specs = load_correlation_study_specs(study_path)
    rows: list[CorrelationStudyRow] = []
    for spec in specs:
        program = _load_by_kind(study_path.parent / spec.path, spec.input_kind)
        feature_report = resource_feature_report(
            program,
            program_id=spec.program_id,
            external_metrics=spec.external_resource_metrics,
        )
        features = asdict(feature_report.features)
        metrics = asdict(spec.external_resource_metrics) if spec.external_resource_metrics is not None else None
        rows.append(CorrelationStudyRow(
            program_id=spec.program_id,
            role=spec.role,
            path=spec.path,
            input_kind=spec.input_kind,
            qkernel_features=features,
            external_resource_metrics=metrics,
            has_external_metrics=metrics is not None,
            negative_control=spec.role == "negative_control",
            interpretation_status=_interpretation_status(features, spec.external_resource_metrics, spec.role),
            notes=spec.notes,
        ))
    return CorrelationStudyReport(
        schema=SCHEMA_VERSION,
        study_id=study_id,
        rows=rows,
        summary=_summary(rows),
        claim_scope=(
            "correlation-study harness; joins qkernel features with externally supplied resource metrics "
            "for exploratory analysis only"
        ),
        not_claimed=[
            "does not prove a resource theorem",
            "does not predict resource metrics",
            "does not optimize T-count",
            "does not optimize magic-state factories",
            "does not prove resource advantage",
        ],
        next_actions=[
            "add more externally measured rows before interpreting correlations",
            "include negative controls in every study",
            "validate any statistical model outside this report before making claims",
        ],
    )


def correlation_study_report_dict(report: CorrelationStudyReport) -> dict:
    return asdict(report)


def _fmt(value: object) -> str:
    if value is None:
        return "-"
    if value is True:
        return "yes"
    if value is False:
        return "no"
    return str(value)


def correlation_study_markdown(report: CorrelationStudyReport | dict) -> str:
    data = asdict(report) if isinstance(report, CorrelationStudyReport) else report
    lines = [
        "# Correlation Study Report",
        "",
        "## Scope",
        "",
        data["claim_scope"],
        "",
        "## Summary",
        "",
        "| field | value |",
        "| --- | --- |",
    ]
    for key, value in data["summary"].items():
        lines.append(f"| {key} | {_fmt(value)} |")
    lines.extend([
        "",
        "## Rows",
        "",
        "| program | role | contextual | kernel K | t_count | t_depth | magic injections | stabilizer rank | status |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ])
    for row in data["rows"]:
        features = row["qkernel_features"]
        metrics = row.get("external_resource_metrics") or {}
        lines.append(
            "| "
            + " | ".join([
                _fmt(row["program_id"]),
                _fmt(row["role"]),
                _fmt(features.get("contextual")),
                _fmt(features.get("kernel_weight")),
                _fmt(metrics.get("t_count")),
                _fmt(metrics.get("t_depth")),
                _fmt(metrics.get("magic_injections")),
                _fmt(metrics.get("stabilizer_rank")),
                _fmt(row["interpretation_status"]),
            ])
            + " |"
        )
    lines.extend([
        "",
        "## Non-Claims",
        "",
        "\n".join(f"- {item}" for item in data["not_claimed"]),
        "",
    ])
    return "\n".join(lines)


def write_correlation_study_markdown(report: CorrelationStudyReport | dict, path: str | Path) -> None:
    Path(path).write_text(correlation_study_markdown(report), encoding="utf-8")
