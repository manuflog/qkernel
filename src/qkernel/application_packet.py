from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal

from .compiler_candidates import compiler_candidate_corpus_report, compiler_candidate_corpus_report_dict
from .correlation_study import correlation_study_report, correlation_study_report_dict
from .factory_candidates import factory_candidate_corpus_report, factory_candidate_corpus_report_dict


SCHEMA_VERSION = "qkernel.application_packet.v1"
SourceType = Literal[
    "compiler_candidate_corpus",
    "factory_candidate_corpus",
    "correlation_study",
    "circuit_manifest_json",
    "resource_feature_json",
]


@dataclass(frozen=True)
class TrackedCandidate:
    candidate_id: str
    role: str
    rationale: str = ""


@dataclass(frozen=True)
class ApplicationPacketSourceSpec:
    source_id: str
    source_type: SourceType
    path: str
    candidate_ids: list[str]
    required: bool = True
    notes: str = ""


@dataclass(frozen=True)
class ApplicationPacketSpec:
    packet_id: str
    title: str
    tracked_candidates: list[TrackedCandidate]
    sources: list[ApplicationPacketSourceSpec]
    recommendation: str = ""


@dataclass(frozen=True)
class ApplicationPacketSourceSummary:
    source_id: str
    source_type: SourceType
    path: str
    required: bool
    exists: bool
    candidate_ids: list[str]
    referenced_candidate_ids: list[str]
    status: str
    claim_gate_status: str
    missing_evidence: list[str]
    next_actions: list[str]
    not_claimed: list[str]
    notes: str


@dataclass(frozen=True)
class ApplicationPacketSummary:
    total_candidates: int
    total_sources: int
    missing_required_sources: int
    sources_with_blockers: int
    uncovered_tracked_candidates: list[str]
    ready_for_claims: bool
    blocker_reasons: list[str]


@dataclass(frozen=True)
class CandidateCoverage:
    candidate_id: str
    role: str
    source_ids: list[str]
    covered: bool


@dataclass(frozen=True)
class ApplicationEvidencePacket:
    schema: str
    packet_id: str
    title: str
    tracked_candidates: list[TrackedCandidate]
    sources: list[ApplicationPacketSourceSummary]
    candidate_coverage: list[CandidateCoverage]
    summary: ApplicationPacketSummary
    recommendation: str
    claim_scope: str
    not_claimed: list[str]
    next_actions: list[str]


def _expect_dict(data: Any, label: str) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise ValueError(f"{label} must be a JSON object")
    return data


def _tracked_candidate_from_dict(item: dict[str, Any]) -> TrackedCandidate:
    if "candidate_id" not in item or "role" not in item:
        raise ValueError("tracked candidate requires candidate_id and role")
    return TrackedCandidate(
        candidate_id=str(item["candidate_id"]),
        role=str(item["role"]),
        rationale=str(item.get("rationale", "")),
    )


def _source_from_dict(item: dict[str, Any]) -> ApplicationPacketSourceSpec:
    required = ["source_id", "source_type", "path"]
    missing = [key for key in required if key not in item]
    if missing:
        raise ValueError(f"application packet source missing required field(s): {', '.join(missing)}")
    source_type = str(item["source_type"])
    allowed = {
        "compiler_candidate_corpus",
        "factory_candidate_corpus",
        "correlation_study",
        "circuit_manifest_json",
        "resource_feature_json",
    }
    if source_type not in allowed:
        raise ValueError(f"unknown application packet source_type {source_type!r}")
    return ApplicationPacketSourceSpec(
        source_id=str(item["source_id"]),
        source_type=source_type,  # type: ignore[arg-type]
        path=str(item["path"]),
        candidate_ids=[str(x) for x in item.get("candidate_ids", [])],
        required=bool(item.get("required", True)),
        notes=str(item.get("notes", "")),
    )


def load_application_packet_spec(path: str | Path) -> ApplicationPacketSpec:
    data = _expect_dict(json.loads(Path(path).read_text(encoding="utf-8")), "application packet")
    if "packet_id" not in data:
        raise ValueError("application packet requires packet_id")
    candidates_data = data.get("tracked_candidates", [])
    if not isinstance(candidates_data, list):
        raise ValueError("tracked_candidates must be a list")
    sources_data = data.get("sources", [])
    if not isinstance(sources_data, list):
        raise ValueError("sources must be a list")
    candidates = [_tracked_candidate_from_dict(_expect_dict(item, "tracked candidate")) for item in candidates_data]
    sources = [_source_from_dict(_expect_dict(item, "application packet source")) for item in sources_data]

    seen_candidates: set[str] = set()
    for candidate in candidates:
        if candidate.candidate_id in seen_candidates:
            raise ValueError(f"duplicate tracked candidate id {candidate.candidate_id!r}")
        seen_candidates.add(candidate.candidate_id)
    seen_sources: set[str] = set()
    for source in sources:
        if source.source_id in seen_sources:
            raise ValueError(f"duplicate application packet source id {source.source_id!r}")
        seen_sources.add(source.source_id)

    return ApplicationPacketSpec(
        packet_id=str(data["packet_id"]),
        title=str(data.get("title", data["packet_id"])),
        tracked_candidates=candidates,
        sources=sources,
        recommendation=str(data.get("recommendation", "")),
    )


def _json_report(path: Path) -> dict[str, Any]:
    return _expect_dict(json.loads(path.read_text(encoding="utf-8")), f"source {path}")


def _source_data(spec: ApplicationPacketSourceSpec, source_path: Path) -> dict[str, Any]:
    if spec.source_type == "compiler_candidate_corpus":
        return compiler_candidate_corpus_report_dict(compiler_candidate_corpus_report(source_path))
    if spec.source_type == "factory_candidate_corpus":
        return factory_candidate_corpus_report_dict(factory_candidate_corpus_report(source_path))
    if spec.source_type == "correlation_study":
        return correlation_study_report_dict(correlation_study_report(source_path))
    if spec.source_type in {"circuit_manifest_json", "resource_feature_json"}:
        return _json_report(source_path)
    raise ValueError(f"unknown source_type {spec.source_type!r}")


def _extract_candidate_ids(source_type: SourceType, data: dict[str, Any]) -> list[str]:
    if source_type in {"compiler_candidate_corpus", "factory_candidate_corpus"}:
        return [str(item["candidate_id"]) for item in data.get("candidates", [])]
    if source_type == "correlation_study":
        return [str(item["program_id"]) for item in data.get("rows", [])]
    if source_type == "circuit_manifest_json":
        return [str(data["program_id"])] if data.get("program_id") else []
    if source_type == "resource_feature_json":
        features = data.get("features", {})
        return [str(features["program_id"])] if isinstance(features, dict) and features.get("program_id") else []
    return []


def _extract_missing_evidence(source_type: SourceType, data: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    if source_type in {"compiler_candidate_corpus", "factory_candidate_corpus"}:
        for item in data.get("candidates", []):
            missing.extend(str(x) for x in item.get("missing_evidence", []))
    elif source_type == "correlation_study":
        missing.extend(str(x) for x in data.get("summary", {}).get("blocker_reasons", []))
    elif source_type == "circuit_manifest_json":
        missing.extend(str(x) for x in data.get("blocker_reasons", []))
    elif source_type == "resource_feature_json":
        missing.extend(str(x) for x in data.get("missing_evidence", []))
        metrics = data.get("external_metrics", data.get("external_resource_metrics"))
        if not metrics:
            missing.append("external resource metrics are not attached")
    return sorted(set(x for x in missing if x))


def _extract_next_actions(source_type: SourceType, data: dict[str, Any]) -> list[str]:
    actions: list[str] = []
    if source_type in {"compiler_candidate_corpus", "factory_candidate_corpus"}:
        for item in data.get("candidates", []):
            actions.extend(str(x) for x in item.get("next_actions", []))
    elif source_type == "correlation_study":
        actions.extend(str(x) for x in data.get("next_actions", []))
    else:
        actions.extend(str(x) for x in data.get("next_actions", []))
    return sorted(set(x for x in actions if x))


def _extract_not_claimed(source_type: SourceType, data: dict[str, Any]) -> list[str]:
    not_claimed: list[str] = [str(x) for x in data.get("not_claimed", [])]
    if source_type in {"compiler_candidate_corpus", "factory_candidate_corpus"}:
        for item in data.get("candidates", []):
            not_claimed.extend(str(x) for x in item.get("not_claimed", []))
    return sorted(set(x for x in not_claimed if x))


def _summarize_source(spec: ApplicationPacketSourceSpec, packet_root: Path) -> ApplicationPacketSourceSummary:
    source_path = packet_root / spec.path
    if not source_path.exists():
        status = "missing_required_source" if spec.required else "missing_optional_source"
        return ApplicationPacketSourceSummary(
            source_id=spec.source_id,
            source_type=spec.source_type,
            path=spec.path,
            required=spec.required,
            exists=False,
            candidate_ids=[],
            referenced_candidate_ids=spec.candidate_ids,
            status=status,
            claim_gate_status="blocked" if spec.required else "optional_missing",
            missing_evidence=[f"source file does not exist: {spec.path}"],
            next_actions=[f"add or correct source path for {spec.source_id}"],
            not_claimed=["does not make application claims without the referenced evidence source"],
            notes=spec.notes,
        )

    data = _source_data(spec, source_path)
    candidate_ids = _extract_candidate_ids(spec.source_type, data)
    missing = _extract_missing_evidence(spec.source_type, data)
    referenced_missing = [cid for cid in spec.candidate_ids if cid not in candidate_ids]
    if referenced_missing:
        missing.append("referenced candidate id(s) not present in source: " + ", ".join(referenced_missing))
    claim_gate_status = "blocked" if missing else "ready"
    return ApplicationPacketSourceSummary(
        source_id=spec.source_id,
        source_type=spec.source_type,
        path=spec.path,
        required=spec.required,
        exists=True,
        candidate_ids=candidate_ids,
        referenced_candidate_ids=spec.candidate_ids,
        status="loaded",
        claim_gate_status=claim_gate_status,
        missing_evidence=sorted(set(missing)),
        next_actions=_extract_next_actions(spec.source_type, data),
        not_claimed=_extract_not_claimed(spec.source_type, data),
        notes=spec.notes,
    )


def _summary(sources: list[ApplicationPacketSourceSummary], candidates: list[TrackedCandidate]) -> ApplicationPacketSummary:
    blockers: list[str] = []
    covered_candidate_ids = {candidate_id for source in sources for candidate_id in source.candidate_ids}
    uncovered = sorted(candidate.candidate_id for candidate in candidates if candidate.candidate_id not in covered_candidate_ids)
    for source in sources:
        if not source.exists and source.required:
            blockers.append(f"required source missing: {source.source_id}")
        if source.missing_evidence:
            blockers.append(f"{source.source_id} has missing evidence")
        if source.claim_gate_status == "blocked":
            blockers.append(f"{source.source_id} claim gate blocked")
    for candidate_id in uncovered:
        blockers.append(f"tracked candidate not covered by any loaded source: {candidate_id}")
    return ApplicationPacketSummary(
        total_candidates=len(candidates),
        total_sources=len(sources),
        missing_required_sources=sum(1 for source in sources if source.required and not source.exists),
        sources_with_blockers=sum(1 for source in sources if source.claim_gate_status == "blocked"),
        uncovered_tracked_candidates=uncovered,
        ready_for_claims=not blockers,
        blocker_reasons=sorted(set(blockers)),
    )


def _candidate_coverage(
    sources: list[ApplicationPacketSourceSummary],
    candidates: list[TrackedCandidate],
) -> list[CandidateCoverage]:
    out: list[CandidateCoverage] = []
    for candidate in candidates:
        source_ids = sorted(source.source_id for source in sources if candidate.candidate_id in source.candidate_ids)
        out.append(CandidateCoverage(
            candidate_id=candidate.candidate_id,
            role=candidate.role,
            source_ids=source_ids,
            covered=bool(source_ids),
        ))
    return out


def application_evidence_packet(path: str | Path) -> ApplicationEvidencePacket:
    packet_path = Path(path)
    spec = load_application_packet_spec(packet_path)
    sources = [_summarize_source(source, packet_path.parent) for source in spec.sources]
    summary = _summary(sources, spec.tracked_candidates)
    coverage = _candidate_coverage(sources, spec.tracked_candidates)
    next_actions = sorted(set(action for source in sources for action in source.next_actions))
    if not next_actions:
        next_actions = ["attach more evidence before promoting application claims"]
    not_claimed = sorted(set(claim for source in sources for claim in source.not_claimed))
    not_claimed.extend([
        "does not claim qkernel is a production compiler",
        "does not claim qkernel builds validated magic-state factories",
        "does not claim unsupported circuit manifests are hardware-ready circuits",
    ])
    return ApplicationEvidencePacket(
        schema=SCHEMA_VERSION,
        packet_id=spec.packet_id,
        title=spec.title,
        tracked_candidates=spec.tracked_candidates,
        sources=sources,
        candidate_coverage=coverage,
        summary=summary,
        recommendation=spec.recommendation,
        claim_scope=(
            "application evidence packet; composes existing qkernel artifacts for review "
            "without upgrading diagnostics into compiler, factory, resource, or hardware claims"
        ),
        not_claimed=sorted(set(not_claimed)),
        next_actions=next_actions,
    )


def application_evidence_packet_dict(packet: ApplicationEvidencePacket) -> dict:
    return asdict(packet)


def _fmt(value: object) -> str:
    if value is None:
        return "-"
    if value is True:
        return "yes"
    if value is False:
        return "no"
    if isinstance(value, list):
        return ", ".join(str(x) for x in value) or "-"
    return str(value)


def application_evidence_packet_markdown(packet: ApplicationEvidencePacket | dict) -> str:
    data = asdict(packet) if isinstance(packet, ApplicationEvidencePacket) else packet
    lines = [
        f"# {data['title']}",
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
        "## Tracked Candidates",
        "",
        "| candidate | role | rationale |",
        "| --- | --- | --- |",
    ])
    for candidate in data["tracked_candidates"]:
        lines.append(
            "| "
            + " | ".join([
                _fmt(candidate["candidate_id"]),
                _fmt(candidate["role"]),
                _fmt(candidate["rationale"]),
            ])
            + " |"
        )
    lines.extend([
        "",
        "## Evidence Sources",
        "",
        "| source | type | exists | candidates | claim gate | status |",
        "| --- | --- | --- | --- | --- | --- |",
    ])
    for source in data["sources"]:
        lines.append(
            "| "
            + " | ".join([
                _fmt(source["source_id"]),
                _fmt(source["source_type"]),
                _fmt(source["exists"]),
                _fmt(source["candidate_ids"]),
                _fmt(source["claim_gate_status"]),
                _fmt(source["status"]),
            ])
            + " |"
        )
    lines.extend([
        "",
        "## Candidate Coverage",
        "",
        "| candidate | role | sources | covered |",
        "| --- | --- | --- | --- |",
    ])
    for coverage in data["candidate_coverage"]:
        lines.append(
            "| "
            + " | ".join([
                _fmt(coverage["candidate_id"]),
                _fmt(coverage["role"]),
                _fmt(coverage["source_ids"]),
                _fmt(coverage["covered"]),
            ])
            + " |"
        )
    lines.extend(["", "## Missing Evidence", ""])
    for source in data["sources"]:
        lines.append(f"### {source['source_id']}")
        if source["missing_evidence"]:
            lines.extend(f"- {item}" for item in source["missing_evidence"])
        else:
            lines.append("- none")
        lines.append("")
    lines.extend([
        "## Recommendation",
        "",
        data["recommendation"] or "Keep this packet in evidence-gathering mode until claim gates are ready.",
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


def write_application_evidence_packet_markdown(packet: ApplicationEvidencePacket | dict, path: str | Path) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(application_evidence_packet_markdown(packet), encoding="utf-8")


def write_application_evidence_packet_json(packet: ApplicationEvidencePacket | dict, path: str | Path) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    data = packet if isinstance(packet, dict) else application_evidence_packet_dict(packet)
    out.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
