"""MagicScout candidate-search engine.

The search layer turns MagicScout from a passive analyzer into a conservative
candidate-discovery workflow. Given a set of available Pauli measurements, it
constructs contextuality motifs, runs the full MagicScout diagnostic stack on
each motif, checks optional template compatibility, and ranks candidates by a
transparent research-prioritization rule.

It does not claim to synthesize a physical magic-state factory. Search results
are contextuality-resource hypotheses that still require external distillation,
logical-code, decoder, and hardware validation.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .metadata import criterion_ledger
from .magic import (
    MAGIC_PROTOCOL_TYPE,
    GeneratedMagicCandidate,
    MagicProtocol,
    MagicScoutReport,
    analyze_magic_protocol,
)
from .pauli import pauli_program


@dataclass(frozen=True)
class MagicSearchConfig:
    """Configuration for candidate search over available Pauli labels."""

    paulis: list[str]
    target: str = "generic_non_clifford"
    role: str = "generated_contextuality_motif"
    top: int = 10
    candidates: int = 50
    backend_model: dict[str, Any] | None = None
    required_templates: list[str] = field(default_factory=list)
    certify_minimal: bool = False
    search_id: str = "magic_search"


@dataclass(frozen=True)
class MagicSearchCandidate:
    """Ranked candidate produced by MagicScout search."""

    rank: int
    protocol: MagicProtocol
    report: MagicScoutReport
    template_compatible_ids: list[str]
    required_templates_satisfied: bool
    backend_certifiable: bool | None
    ranking_score: float
    ranking_explanation: list[str]


@dataclass(frozen=True)
class MagicSearchReport:
    """Full MagicScout search report."""

    search_id: str
    target: str
    available_paulis: list[str]
    candidates_considered: int
    candidates_returned: int
    required_templates: list[str]
    ranking_rule: str
    results: list[MagicSearchCandidate]
    not_claimed: list[str]
    criterion_ledger: dict


SEARCH_NONCLAIMS = [
    "magic-state factory synthesis",
    "lower magic-state overhead",
    "distillation threshold",
    "output fidelity bound",
    "acceptance probability",
    "logical-code-distance claim",
    "decoder performance claim",
    "space-time-volume advantage",
]


def _compatible_template_ids(report: MagicScoutReport) -> list[str]:
    ids: list[str] = []
    for item in report.template_assessments or []:
        try:
            if item.get("compatible"):
                ids.append(str(item.get("template_id")))
        except AttributeError:
            continue
    return ids


def _backend_certifiable(report: MagicScoutReport) -> bool | None:
    if report.backend_estimate is None:
        return None
    return bool(report.backend_estimate.certifiable)


def _ranking_score(
    report: MagicScoutReport,
    *,
    required_templates: list[str],
) -> tuple[float, list[str], bool, list[str], bool | None]:
    compatible_ids = _compatible_template_ids(report)
    compatible = set(compatible_ids)
    required = set(required_templates)
    required_ok = required.issubset(compatible)
    backend_ok = _backend_certifiable(report)

    score = float(report.interest_score)
    why = [f"base MagicScout interest_score={report.interest_score}"]

    if compatible_ids:
        bump = min(0.15, 0.05 * len(compatible_ids))
        score += bump
        why.append(f"+{bump:.2f} template compatibility bonus ({', '.join(compatible_ids)})")
    else:
        why.append("+0.00 no compatible factory-template checklist")

    if required_templates:
        if required_ok:
            score += 0.10
            why.append("+0.10 all required templates satisfied")
        else:
            score -= 0.25
            missing = sorted(required - compatible)
            why.append(f"-0.25 required templates not satisfied: {missing}")

    if backend_ok is True:
        score += 0.10
        why.append("+0.10 backend estimate certifiable")
    elif backend_ok is False:
        score -= 0.05
        why.append("-0.05 backend estimate not certifiable")
    else:
        why.append("+0.00 no backend estimate")

    if not report.contextual:
        score -= 0.50
        why.append("-0.50 non-contextual candidate")

    return round(max(0.0, min(score, 1.0)), 3), why, required_ok, compatible_ids, backend_ok


def _protocol_from_test_contexts(
    contexts: list[list[str]],
    *,
    protocol_id: str,
    target: str,
    role: str,
    backend_model: dict[str, Any] | None,
    source: str,
) -> MagicProtocol:
    return MagicProtocol(
        protocol_id=protocol_id,
        target=target,
        role=role,
        input_kind="pauli",
        claim_scope="diagnostic_only",
        payload={
            "type": MAGIC_PROTOCOL_TYPE,
            "protocol_id": protocol_id,
            "target": target,
            "role": role,
            "input_kind": "pauli",
            "claim_scope": "diagnostic_only",
            "pauli_contexts": {"contexts": contexts},
        },
        factory_metadata={"source": source},
        backend_model=backend_model,
    )


def search_magic_candidates(config: MagicSearchConfig) -> MagicSearchReport:
    """Search available Pauli measurements for MagicScout candidate motifs.

    The search uses qkernel's existing experiment-design layer to enumerate cheap
    contextuality tests from the available Pauli set, then runs each candidate
    through MagicScout + template checklists + optional backend estimates.
    """
    from .experiment_design import minimal_contextuality_tests

    tests = minimal_contextuality_tests(config.paulis, top=config.candidates)
    ranked: list[MagicSearchCandidate] = []
    for i, test in enumerate(tests, start=1):
        protocol_id = f"{config.search_id}_candidate_{i}"
        proto = _protocol_from_test_contexts(
            test.contexts,
            protocol_id=protocol_id,
            target=config.target,
            role=config.role,
            backend_model=config.backend_model,
            source="magic_search_available_paulis",
        )
        report = analyze_magic_protocol(
            pauli_program(test.contexts),
            protocol_id=protocol_id,
            target=config.target,
            role=config.role,
            factory_metadata=proto.factory_metadata,
            backend_model=config.backend_model,
            enumerate_all_kernels=True,
            certify_minimal=config.certify_minimal,
        )
        score, why, required_ok, compatible_ids, backend_ok = _ranking_score(
            report,
            required_templates=config.required_templates,
        )
        ranked.append(MagicSearchCandidate(
            rank=0,
            protocol=proto,
            report=report,
            template_compatible_ids=compatible_ids,
            required_templates_satisfied=required_ok,
            backend_certifiable=backend_ok,
            ranking_score=score,
            ranking_explanation=why,
        ))

    ranked.sort(
        key=lambda c: (
            -c.ranking_score,
            c.report.backend_estimate.shots_total if c.report.backend_estimate and c.report.backend_estimate.shots_total is not None else 10**12,
            c.report.kernel_weight if c.report.kernel_weight is not None else 10**9,
            c.protocol.protocol_id,
        )
    )
    limited = ranked[: config.top]
    results = [
        MagicSearchCandidate(
            rank=i + 1,
            protocol=c.protocol,
            report=c.report,
            template_compatible_ids=c.template_compatible_ids,
            required_templates_satisfied=c.required_templates_satisfied,
            backend_certifiable=c.backend_certifiable,
            ranking_score=c.ranking_score,
            ranking_explanation=c.ranking_explanation,
        )
        for i, c in enumerate(limited)
    ]
    ledger = criterion_ledger(
        criterion_id="odd_Q_even_d_v1",
        verifier_used="MagicScout search over experiment-design contextuality candidates",
        claim_scope="candidate-search diagnostic; no factory-performance claim",
        stronger_verifier_available="zd_avn_valuation_v1",
        stronger_verifier_passed=None,
    )
    return MagicSearchReport(
        search_id=config.search_id,
        target=config.target,
        available_paulis=[p.upper() for p in config.paulis],
        candidates_considered=len(tests),
        candidates_returned=len(results),
        required_templates=list(config.required_templates),
        ranking_rule=(
            "ranking_score descending; backend shots ascending; kernel weight ascending; protocol id. "
            "ranking_score = MagicScout interest + template bonuses + backend bonus - required-template/noncontextual penalties"
        ),
        results=results,
        not_claimed=SEARCH_NONCLAIMS,
        criterion_ledger=ledger,
    )


def search_magic_candidates_from_paulis(
    paulis: list[str],
    *,
    target: str = "generic_non_clifford",
    top: int = 10,
    candidates: int = 50,
    backend_model: dict[str, Any] | None = None,
    required_templates: list[str] | None = None,
    certify_minimal: bool = False,
    search_id: str = "magic_search",
) -> MagicSearchReport:
    """Convenience wrapper for simple CLI/API use."""
    return search_magic_candidates(MagicSearchConfig(
        paulis=paulis,
        target=target,
        top=top,
        candidates=candidates,
        backend_model=backend_model,
        required_templates=list(required_templates or []),
        certify_minimal=certify_minimal,
        search_id=search_id,
    ))


def search_two_qubit_magic_candidates(
    *,
    target: str = "generic_non_clifford",
    top: int = 10,
    backend_model: dict[str, Any] | None = None,
) -> MagicSearchReport:
    """Search all 15 non-identity two-qubit Paulis as a standard demo universe."""
    from .zoo import TWO_QUBIT_PAULIS

    return search_magic_candidates_from_paulis(
        list(TWO_QUBIT_PAULIS),
        target=target,
        top=top,
        candidates=50,
        backend_model=backend_model,
        search_id="two_qubit_pauli_search",
    )


def magic_search_report_dict(report: MagicSearchReport) -> dict:
    return asdict(report)
