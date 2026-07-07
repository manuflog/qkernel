from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from .magic import analyze_magic_protocol_record, load_magic_protocol, magic_report_dict
from .magic_templates import assess_magic_templates, magic_template_assessments_dict


SCHEMA_VERSION = "qkernel.factory_candidates.v1"


@dataclass(frozen=True)
class FactoryCandidateSpec:
    candidate_id: str
    protocol: str
    required_templates: list[str]
    factory_metrics_status: str = "not_provided"
    factory_metrics_ref: str = ""
    resource_metrics_status: str = "not_provided"
    resource_metrics_ref: str = ""
    rationale: str = ""


@dataclass(frozen=True)
class FactoryCandidateReport:
    candidate_id: str
    protocol: str
    magic_report: dict
    template_assessments: dict
    compatible_template_ids: list[str]
    factory_metrics_status: str
    factory_metrics_ref: str
    resource_metrics_status: str
    resource_metrics_ref: str
    candidate_status: str
    rationale: str
    missing_evidence: list[str]
    next_actions: list[str]
    not_claimed: list[str]


@dataclass(frozen=True)
class FactoryCandidateCorpusReport:
    schema: str
    corpus_id: str
    candidates: list[FactoryCandidateReport]
    claim_scope: str
    not_claimed: list[str]


def _spec_from_dict(item: dict) -> FactoryCandidateSpec:
    required = ["candidate_id", "protocol"]
    missing = [key for key in required if key not in item]
    if missing:
        raise ValueError(f"factory candidate missing required field(s): {', '.join(missing)}")
    return FactoryCandidateSpec(
        candidate_id=str(item["candidate_id"]),
        protocol=str(item["protocol"]),
        required_templates=[str(x) for x in item.get("required_templates", [])],
        factory_metrics_status=str(item.get("factory_metrics_status", "not_provided")),
        factory_metrics_ref=str(item.get("factory_metrics_ref", "")),
        resource_metrics_status=str(item.get("resource_metrics_status", "not_provided")),
        resource_metrics_ref=str(item.get("resource_metrics_ref", "")),
        rationale=str(item.get("rationale", "")),
    )


def load_factory_candidate_specs(path: str | Path) -> tuple[str, list[FactoryCandidateSpec]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    specs_data = data.get("factory_candidates", data.get("candidates", data))
    if not isinstance(specs_data, list):
        raise ValueError("factory candidate file must be a list or contain a `factory_candidates` list")
    corpus_id = str(data.get("corpus_id", "factory_candidate_corpus")) if isinstance(data, dict) else "factory_candidate_corpus"
    specs = [_spec_from_dict(item) for item in specs_data]
    seen: set[str] = set()
    for spec in specs:
        if spec.candidate_id in seen:
            raise ValueError(f"duplicate factory candidate id {spec.candidate_id!r}")
        seen.add(spec.candidate_id)
    return corpus_id, specs


def _candidate_status(
    *,
    compatible_count: int,
    required_count: int,
    factory_metrics_status: str,
    resource_metrics_status: str,
) -> str:
    if compatible_count < required_count:
        return "template_evidence_incomplete"
    if factory_metrics_status != "provided":
        return "template_compatible_missing_factory_metrics"
    if resource_metrics_status != "provided":
        return "factory_metrics_supplied_missing_resource_metrics"
    return "externally_supported_factory_candidate"


def factory_candidate_report(spec: FactoryCandidateSpec, *, root: str | Path = ".") -> FactoryCandidateReport:
    root_path = Path(root)
    protocol_path = root_path / spec.protocol
    protocol = load_magic_protocol(protocol_path)
    magic = analyze_magic_protocol_record(protocol)
    assessments = assess_magic_templates(magic, template_ids=spec.required_templates or None)
    assessment_data = magic_template_assessments_dict(assessments)
    compatible = [a.template_id for a in assessments if a.compatible]
    required_count = len(spec.required_templates) if spec.required_templates else len(assessments)

    missing_evidence = list(magic.missing_evidence)
    for assessment in assessments:
        missing_evidence.extend(assessment.missing_evidence)
    if spec.factory_metrics_status != "provided":
        missing_evidence.append("external factory metrics are not attached")
    if spec.resource_metrics_status != "provided":
        missing_evidence.append("external resource metrics are not attached")

    return FactoryCandidateReport(
        candidate_id=spec.candidate_id,
        protocol=spec.protocol,
        magic_report=magic_report_dict(magic),
        template_assessments=assessment_data,
        compatible_template_ids=compatible,
        factory_metrics_status=spec.factory_metrics_status,
        factory_metrics_ref=spec.factory_metrics_ref,
        resource_metrics_status=spec.resource_metrics_status,
        resource_metrics_ref=spec.resource_metrics_ref,
        candidate_status=_candidate_status(
            compatible_count=len(compatible),
            required_count=required_count,
            factory_metrics_status=spec.factory_metrics_status,
            resource_metrics_status=spec.resource_metrics_status,
        ),
        rationale=spec.rationale,
        missing_evidence=sorted(set(missing_evidence)),
        next_actions=[
            "attach factory metrics before calling the candidate viable",
            "attach external resource metrics before discussing overhead",
            "keep MagicScout compatibility separate from factory validity",
        ],
        not_claimed=[
            "valid magic-state factory",
            "distillation threshold",
            "output fidelity bound",
            "acceptance probability guarantee",
            "space-time-volume advantage",
            "lower magic-state overhead",
        ],
    )


def factory_candidate_corpus_report(path: str | Path) -> FactoryCandidateCorpusReport:
    corpus_path = Path(path)
    corpus_id, specs = load_factory_candidate_specs(corpus_path)
    reports = [factory_candidate_report(spec, root=corpus_path.parent) for spec in specs]
    return FactoryCandidateCorpusReport(
        schema=SCHEMA_VERSION,
        corpus_id=corpus_id,
        candidates=reports,
        claim_scope=(
            "factory-candidate research corpus; qkernel provides MagicScout diagnostics "
            "and template compatibility, not factory validity or overhead estimates"
        ),
        not_claimed=[
            "does not construct valid magic-state factories",
            "does not prove distillation thresholds",
            "does not prove output fidelity",
            "does not prove lower overhead",
            "does not prove resource advantage",
        ],
    )


def factory_candidate_corpus_report_dict(report: FactoryCandidateCorpusReport) -> dict:
    return asdict(report)


def _fmt(value: object) -> str:
    if value is None:
        return "-"
    if value is True:
        return "yes"
    if value is False:
        return "no"
    return str(value)


def factory_candidate_markdown(report: FactoryCandidateCorpusReport | dict) -> str:
    data = asdict(report) if isinstance(report, FactoryCandidateCorpusReport) else report
    lines = [
        "# Factory Candidate Corpus",
        "",
        "## Scope",
        "",
        data["claim_scope"],
        "",
        "## Candidates",
        "",
        "| candidate | status | protocol | compatible templates | factory metrics | resource metrics |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for cand in data["candidates"]:
        lines.append(
            "| "
            + " | ".join([
                _fmt(cand["candidate_id"]),
                _fmt(cand["candidate_status"]),
                _fmt(cand["protocol"]),
                ", ".join(cand["compatible_template_ids"]) or "-",
                _fmt(cand["factory_metrics_status"]),
                _fmt(cand["resource_metrics_status"]),
            ])
            + " |"
        )
    lines.extend(["", "## Missing Evidence", ""])
    for cand in data["candidates"]:
        lines.append(f"### {cand['candidate_id']}")
        lines.extend(f"- {item}" for item in cand["missing_evidence"])
        lines.append("")
    lines.extend([
        "## Non-Claims",
        "",
        "\n".join(f"- {item}" for item in data["not_claimed"]),
        "",
    ])
    return "\n".join(lines)


def write_factory_candidate_markdown(report: FactoryCandidateCorpusReport | dict, path: str | Path) -> None:
    Path(path).write_text(factory_candidate_markdown(report), encoding="utf-8")
