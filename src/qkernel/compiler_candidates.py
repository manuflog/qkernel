from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

from .adapters.pauli_table import load_pauli_table
from .adapters.qiskit_lite import load_qiskit_lite_program
from .adapters.stim_lite import load_stim_lite_program
from .compiler import CompilerPassComparison, compare_compiler_pass
from .io import load_program
from .pauli import load_pauli_program
from .pauli_schedule import load_pauli_schedule
from .rewrite_policy import assess_rewrite_candidate


SCHEMA_VERSION = "qkernel.compiler_candidates.v1"
InputKind = Literal["weyl", "pauli", "schedule", "table", "stim-lite", "qiskit-lite"]


@dataclass(frozen=True)
class CompilerCandidateSpec:
    candidate_id: str
    before: str
    after: str
    input_kind: InputKind
    semantic_equivalence_status: str = "not_provided"
    semantic_equivalence_ref: str = ""
    resource_metrics_status: str = "not_provided"
    resource_metrics_ref: str = ""
    rationale: str = ""


@dataclass(frozen=True)
class CompilerCandidateReport:
    candidate_id: str
    input_kind: InputKind
    before: str
    after: str
    comparison: CompilerPassComparison
    semantic_equivalence_status: str
    semantic_equivalence_ref: str
    resource_metrics_status: str
    resource_metrics_ref: str
    policy_id: str
    policy_status: str
    candidate_status: str
    allowed_to_report: bool
    allowed_to_apply: bool
    rationale: str
    missing_evidence: list[str]
    not_claimed: list[str]
    next_actions: list[str]


@dataclass(frozen=True)
class CompilerCandidateCorpusReport:
    schema: str
    corpus_id: str
    candidates: list[CompilerCandidateReport]
    claim_scope: str
    not_claimed: list[str]


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


def _candidate_spec_from_dict(item: dict) -> CompilerCandidateSpec:
    required = ["candidate_id", "before", "after", "input_kind"]
    missing = [key for key in required if key not in item]
    if missing:
        raise ValueError(f"compiler candidate missing required field(s): {', '.join(missing)}")
    kind = str(item["input_kind"])
    if kind not in {"weyl", "pauli", "schedule", "table", "stim-lite", "qiskit-lite"}:
        raise ValueError(f"unknown compiler candidate input_kind {kind!r}")
    return CompilerCandidateSpec(
        candidate_id=str(item["candidate_id"]),
        before=str(item["before"]),
        after=str(item["after"]),
        input_kind=kind,  # type: ignore[arg-type]
        semantic_equivalence_status=str(item.get("semantic_equivalence_status", "not_provided")),
        semantic_equivalence_ref=str(item.get("semantic_equivalence_ref", "")),
        resource_metrics_status=str(item.get("resource_metrics_status", "not_provided")),
        resource_metrics_ref=str(item.get("resource_metrics_ref", "")),
        rationale=str(item.get("rationale", "")),
    )


def load_compiler_candidate_specs(path: str | Path) -> tuple[str, list[CompilerCandidateSpec]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    specs_data = data.get("compiler_candidates", data.get("candidates", data))
    if not isinstance(specs_data, list):
        raise ValueError("compiler candidate file must be a list or contain a `compiler_candidates` list")
    corpus_id = str(data.get("corpus_id", "compiler_candidate_corpus")) if isinstance(data, dict) else "compiler_candidate_corpus"
    specs = [_candidate_spec_from_dict(item) for item in specs_data]
    seen: set[str] = set()
    for spec in specs:
        if spec.candidate_id in seen:
            raise ValueError(f"duplicate compiler candidate id {spec.candidate_id!r}")
        seen.add(spec.candidate_id)
    return corpus_id, specs


def _candidate_status(spec: CompilerCandidateSpec, comparison: CompilerPassComparison) -> str:
    if spec.semantic_equivalence_status != "provided":
        return "diagnostic_only_missing_semantic_proof"
    if spec.resource_metrics_status != "provided":
        return "semantic_proof_supplied_missing_resource_metrics"
    if not comparison.allowed_to_apply:
        return "not_applicable_by_policy"
    return "externally_supported_candidate"


def compiler_candidate_report(spec: CompilerCandidateSpec, *, root: str | Path = ".") -> CompilerCandidateReport:
    root_path = Path(root)
    before_path = root_path / spec.before
    after_path = root_path / spec.after
    before = _load_by_kind(before_path, spec.input_kind)
    after = _load_by_kind(after_path, spec.input_kind)
    comparison = compare_compiler_pass(before, after)
    policy = assess_rewrite_candidate("experimental_resource_probe")

    missing_evidence: list[str] = []
    if spec.semantic_equivalence_status != "provided":
        missing_evidence.append("external semantic-equivalence proof is not attached")
    if spec.resource_metrics_status != "provided":
        missing_evidence.append("external before/after resource metrics are not attached")
    if comparison.requires_semantic_equivalence_proof:
        missing_evidence.append("qkernel comparison itself cannot authorize applying this compiler rewrite")

    next_actions = [
        "attach or cite a semantic-equivalence proof before treating the candidate as a compiler pass",
        "attach external resource metrics before discussing T-count, depth, magic, or hardware cost",
        "keep qkernel diagnostic deltas separate from compiler resource deltas",
    ]

    return CompilerCandidateReport(
        candidate_id=spec.candidate_id,
        input_kind=spec.input_kind,
        before=spec.before,
        after=spec.after,
        comparison=comparison,
        semantic_equivalence_status=spec.semantic_equivalence_status,
        semantic_equivalence_ref=spec.semantic_equivalence_ref,
        resource_metrics_status=spec.resource_metrics_status,
        resource_metrics_ref=spec.resource_metrics_ref,
        policy_id=policy.policy_id,
        policy_status=policy.status,
        candidate_status=_candidate_status(spec, comparison),
        allowed_to_report=policy.allowed_to_report and comparison.allowed_to_report,
        allowed_to_apply=False,
        rationale=spec.rationale,
        missing_evidence=missing_evidence,
        not_claimed=[
            "does not prove semantic equivalence",
            "does not reduce T-count",
            "does not optimize magic states",
            "does not prove hardware-resource advantage",
        ],
        next_actions=next_actions,
    )


def compiler_candidate_corpus_report(path: str | Path) -> CompilerCandidateCorpusReport:
    corpus_path = Path(path)
    corpus_id, specs = load_compiler_candidate_specs(corpus_path)
    reports = [compiler_candidate_report(spec, root=corpus_path.parent) for spec in specs]
    return CompilerCandidateCorpusReport(
        schema=SCHEMA_VERSION,
        corpus_id=corpus_id,
        candidates=reports,
        claim_scope=(
            "compiler-candidate diagnostic corpus; qkernel compares odd-Q kernel features, "
            "but semantic equivalence and resource metrics must come from external evidence"
        ),
        not_claimed=[
            "does not certify compiler rewrites",
            "does not optimize T-count",
            "does not construct magic-state factories",
            "does not prove resource advantage",
        ],
    )


def compiler_candidate_corpus_report_dict(report: CompilerCandidateCorpusReport) -> dict:
    return asdict(report)


def _fmt(value: object) -> str:
    if value is None:
        return "-"
    if value is True:
        return "yes"
    if value is False:
        return "no"
    return str(value)


def compiler_candidate_markdown(report: CompilerCandidateCorpusReport | dict) -> str:
    data = asdict(report) if isinstance(report, CompilerCandidateCorpusReport) else report
    rows = []
    for cand in data["candidates"]:
        comp = cand["comparison"]
        rows.append([
            cand["candidate_id"],
            cand["candidate_status"],
            comp["kernel_context_delta"],
            comp["context_delta"],
            comp["observable_delta"],
            cand["semantic_equivalence_status"],
            cand["resource_metrics_status"],
            cand["allowed_to_report"],
            cand["allowed_to_apply"],
        ])
    lines = [
        "# Compiler Candidate Corpus",
        "",
        "## Scope",
        "",
        data["claim_scope"],
        "",
        "## Candidates",
        "",
        "| candidate | status | kernel delta | context delta | observable delta | semantic proof | resource metrics | report | apply |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    lines.extend("| " + " | ".join(_fmt(cell) for cell in row) + " |" for row in rows)
    lines.extend([
        "",
        "## Missing Evidence",
        "",
    ])
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


def write_compiler_candidate_markdown(report: CompilerCandidateCorpusReport | dict, path: str | Path) -> None:
    Path(path).write_text(compiler_candidate_markdown(report), encoding="utf-8")
