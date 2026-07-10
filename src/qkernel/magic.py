"""MagicScout: contextuality diagnostics for magic-state protocol candidates.

MagicScout is deliberately conservative. It does **not** claim to construct,
distill, or improve magic states. It treats qkernel's contextuality machinery as
a research triage layer for candidate magic-state injection, cultivation,
verification, or factory *motifs*.

The module composes existing qkernel pieces:

- criterion ledger / semantic firewall;
- contextuality subroutine;
- minimal-kernel extraction;
- optional all-kernel enumeration and CP-SAT minimality;
- Z_d / AvN stronger verifier;
- backend-aware expected-significance model;
- Contextuality Benchmark Zoo.

All user-facing reports carry explicit missing evidence and non-claims.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
from pathlib import Path
from typing import Any

from .ir import WeylProgram
from .metadata import criterion_ledger
from .optimizer import compress_min_odd_q
from .subroutine import analyze_contextuality
from .valuation import check_kernel_zd_valuation
from .verify import verify_kernel


MAGIC_PROTOCOL_TYPE = "qkernel.magic_protocol.v1"
MAGIC_PORTFOLIO_TYPE = "qkernel.magic_portfolio.v1"


@dataclass(frozen=True)
class BackendMagicEstimate:
    """Backend-aware estimate attached to a MagicScout report.

    This is an expected-significance planning model, not hardware evidence.
    """

    backend_available: bool
    reason: str
    expected_S: float | None = None
    nc_bound: int | None = None
    margin: float | None = None
    certifiable: bool | None = None
    shots_total: int | None = None
    k_sigma: float | None = None
    criterion_ledger: dict | None = None


@dataclass(frozen=True)
class MagicScoutReport:
    """Conservative magic-state-adjacent protocol report.

    ``interest_score`` is a research-prioritization score, not a magic yield,
    threshold, output fidelity, or factory-overhead estimate.
    """

    protocol_id: str
    target: str
    role: str
    contextual: bool
    kernel_contexts: list[int] | None
    kernel_weight: int | None
    verified: bool
    zd_avn_contextual: bool | None
    obstruction_value: int | None
    n_minimal_kernels: int | None
    cpsat_certified_minimal: bool | None
    interest_score: float
    positive_signals: list[str] = field(default_factory=list)
    missing_evidence: list[str] = field(default_factory=list)
    not_claimed: list[str] = field(default_factory=list)
    backend_estimate: BackendMagicEstimate | None = None
    template_assessments: list[dict[str, Any]] = field(default_factory=list)
    factory_metadata: dict[str, Any] = field(default_factory=dict)
    criterion_ledger: dict | None = None


@dataclass(frozen=True)
class MagicProtocol:
    """Parsed MagicScout protocol record."""

    protocol_id: str
    target: str
    role: str
    input_kind: str
    claim_scope: str
    payload: dict[str, Any]
    factory_metadata: dict[str, Any] = field(default_factory=dict)
    backend_model: dict[str, Any] | None = None
    source_path: str | None = None


@dataclass(frozen=True)
class MagicPortfolioEntry:
    """Ranked MagicScout result for one protocol record."""

    rank: int
    protocol_id: str
    report: MagicScoutReport


@dataclass(frozen=True)
class MagicPortfolioReport:
    """Ranked portfolio of candidate magic-state-adjacent protocols."""

    portfolio_id: str
    entries: list[MagicPortfolioEntry]
    ranking_rule: str
    not_claimed: list[str]


@dataclass(frozen=True)
class MagicZooEntry:
    """MagicScout result for one benchmark-zoo instance."""

    instance_name: str
    claim_scope: str
    note: str
    report: MagicScoutReport


@dataclass(frozen=True)
class MagicAuditCheck:
    id: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class MagicAuditReport:
    passed: bool
    checks: list[MagicAuditCheck]
    recommendation: str


@dataclass(frozen=True)
class GeneratedMagicCandidate:
    """Candidate motif generated from available Pauli operators."""

    protocol: MagicProtocol
    report: MagicScoutReport


def _default_not_claimed() -> list[str]:
    return [
        "lower magic-state overhead",
        "valid magic-state distillation protocol",
        "threshold improvement",
        "output fidelity bound",
        "acceptance probability",
        "factory space-time advantage",
        "logical-code-distance claim",
        "decoder performance claim",
        "compiler semantic-equivalence proof",
    ]


def _always_missing_factory_evidence() -> list[str]:
    return [
        "no distillation map checked",
        "no output infidelity model checked",
        "no acceptance probability checked",
        "no logical-code distance or decoder model checked",
        "no space-time volume model checked",
    ]


def _score_report(
    *,
    contextual: bool,
    verified: bool,
    zd_avn_contextual: bool | None,
    kernel_weight: int | None,
    n_minimal_kernels: int | None,
    cpsat_certified_minimal: bool | None,
    obstruction_value: int | None,
    backend_estimate: BackendMagicEstimate | None = None,
) -> tuple[float, list[str], list[str]]:
    """Return (score, positive_signals, missing_evidence).

    The score is intentionally coarse and capped. It ranks which candidates are
    worth studying next; it is not a physical resource metric.
    """
    score = 0.0
    positive: list[str] = []
    missing: list[str] = []

    if contextual:
        score += 0.30
        positive.append("odd-Q contextuality present")
    else:
        missing.append("no odd-Q contextuality detected")

    if verified:
        score += 0.15
        positive.append("independently verified kernel")
    else:
        missing.append("kernel not independently verified under the requested claim scope")

    if zd_avn_contextual is True:
        score += 0.10
        positive.append("passes stronger Z_d/AvN valuation verifier")
    elif zd_avn_contextual is False:
        missing.append("stronger Z_d/AvN verifier did not pass; treat as odd-Q-only")
    else:
        missing.append("stronger Z_d/AvN verifier not run or not applicable")

    if kernel_weight is not None:
        if kernel_weight <= 6:
            score += 0.20
            positive.append("small contextual core (<=6 contexts)")
        elif kernel_weight <= 10:
            score += 0.15
            positive.append("moderate contextual core (<=10 contexts)")
        elif kernel_weight <= 20:
            score += 0.10
            positive.append("bounded contextual core (<=20 contexts)")
        else:
            missing.append("large contextual core; factory relevance may be weak")
    else:
        missing.append("no minimal kernel available")

    if n_minimal_kernels is not None:
        if n_minimal_kernels >= 5:
            score += 0.10
            positive.append("many equivalent minimal kernels / routing alternatives")
        elif n_minimal_kernels >= 2:
            score += 0.05
            positive.append("multiple minimal kernels")
    else:
        missing.append("minimal-kernel multiplicity not enumerated")

    if cpsat_certified_minimal is True:
        score += 0.10
        positive.append("CP-SAT certified minimality")
    elif cpsat_certified_minimal is False:
        missing.append("CP-SAT minimality was requested but not certified")
    else:
        missing.append("CP-SAT minimality not requested")

    if obstruction_value is not None and obstruction_value > 0:
        score += 0.05
        positive.append(f"nonzero obstruction value {obstruction_value}")

    if backend_estimate is not None:
        if backend_estimate.certifiable:
            score += 0.10
            positive.append("backend model predicts certifiable contextuality witness")
            if backend_estimate.shots_total is not None and backend_estimate.shots_total <= 100_000:
                score += 0.05
                positive.append("backend model predicts moderate shot budget")
        elif backend_estimate.backend_available:
            missing.append("backend model does not predict certification under assumptions")
        else:
            missing.append(backend_estimate.reason)

    return min(score, 1.0), positive, missing


def _is_pauli_label(label: str) -> bool:
    return bool(label) and all(ch in {"I", "X", "Y", "Z"} for ch in label.upper())


def _backend_from_dict(data: dict[str, Any]):
    from .backend_design import BackendModel

    readout_error = {
        int(k): float(v)
        for k, v in dict(data.get("readout_error", {})).items()
    }
    return BackendModel(
        readout_error=readout_error,
        default_readout_error=float(data.get("default_readout_error", 0.02)),
        joint_basis=bool(data.get("joint_basis", False)),
    )


def _backend_estimate_for_kernel(
    program: WeylProgram,
    *,
    selected_contexts: list[int] | None,
    verified: bool,
    obstruction_value: int | None,
    criterion_ledg: dict | None,
    backend_model: dict[str, Any] | None,
    k_sigma: float = 5.0,
) -> BackendMagicEstimate | None:
    if backend_model is None:
        return None
    if selected_contexts is None:
        return BackendMagicEstimate(
            backend_available=False,
            reason="no contextual kernel available for backend estimate",
        )

    contexts = [program.contexts[i] for i in selected_contexts]
    if not all(all(_is_pauli_label(label) for label in ctx) for ctx in contexts):
        return BackendMagicEstimate(
            backend_available=False,
            reason="backend estimate currently supports qubit Pauli-labeled contexts only",
        )

    from .backend_design import estimate_significance
    from .experiment_design import ContextualityTest

    obs = {label for ctx in contexts for label in ctx}
    test = ContextualityTest(
        contexts=contexts,
        n_contexts=len(contexts),
        n_observables=len(obs),
        obstruction_value=obstruction_value or 0,
        verified=verified,
        criterion_ledger=criterion_ledg,
    )
    est = estimate_significance(test, _backend_from_dict(backend_model), k_sigma=k_sigma)
    return BackendMagicEstimate(
        backend_available=True,
        reason="backend expected-significance estimate computed",
        expected_S=est.expected_S,
        nc_bound=est.nc_bound,
        margin=est.margin,
        certifiable=est.certifiable,
        shots_total=est.shots_total,
        k_sigma=est.k_sigma,
        criterion_ledger=est.criterion_ledger,
    )


def analyze_magic_protocol(
    program: WeylProgram,
    *,
    protocol_id: str = "candidate_protocol",
    target: str = "generic_non_clifford",
    role: str = "candidate_magic_protocol_diagnostic",
    factory_metadata: dict[str, Any] | None = None,
    backend_model: dict[str, Any] | None = None,
    enumerate_all_kernels: bool = True,
    certify_minimal: bool = False,
    max_cycle_dim_enumerate: int = 20,
) -> MagicScoutReport:
    """Analyze a candidate magic-state protocol measurement program.

    This is a *factory scout*, not a factory. It reports contextuality structure
    and explicitly lists evidence still missing before any distillation/factory
    performance claim could be made.
    """
    sub = analyze_contextuality(
        program,
        verify=True,
        enumerate_all_kernels=enumerate_all_kernels,
        certify_minimal=certify_minimal,
        max_cycle_dim_enumerate=max_cycle_dim_enumerate,
    )

    zd_contextual: bool | None = None
    verified = bool(sub.verified)
    selected = sub.min_kernel_contexts
    if sub.contextual:
        kernel = compress_min_odd_q(program)
        vr = verify_kernel(program, kernel)
        verified = bool(vr.valid)
        zd_contextual = vr.zd_contextual
        selected = list(kernel.selected_contexts)
        if zd_contextual is None:
            zd = check_kernel_zd_valuation(program, kernel)
            zd_contextual = zd.contextual

    ledger = criterion_ledger(
        criterion_id="odd_Q_even_d_v1",
        verifier_used="analyze_contextuality + verify_kernel; MagicScout score is a diagnostic overlay",
        claim_scope=(
            "magic-state-adjacent contextuality diagnostic; not a distillation, "
            "threshold, output-fidelity, or overhead claim"
        ),
        stronger_verifier_available="zd_avn_valuation_v1",
        stronger_verifier_passed=zd_contextual,
    )

    backend_est = _backend_estimate_for_kernel(
        program,
        selected_contexts=selected,
        verified=verified,
        obstruction_value=sub.obstruction_value,
        criterion_ledg=ledger,
        backend_model=backend_model,
    )

    score, positive, missing = _score_report(
        contextual=sub.contextual,
        verified=verified,
        zd_avn_contextual=zd_contextual,
        kernel_weight=sub.kernel_weight,
        n_minimal_kernels=sub.n_minimal_kernels,
        cpsat_certified_minimal=sub.certified_minimal,
        obstruction_value=sub.obstruction_value,
        backend_estimate=backend_est,
    )

    template_assessments = []
    # Best-effort template bridge; kept local to avoid making MagicScout depend on
    # a physical factory model. The assessments are checklists, not proof of factory
    # performance.
    try:
        from .magic_templates import assess_magic_templates

        # Construct a lightweight view with the report fields needed by the template layer.
        class _ReportView:
            pass

        view = _ReportView()
        view.protocol_id = protocol_id
        view.target = target
        view.contextual = sub.contextual
        view.verified = verified
        view.zd_avn_contextual = zd_contextual
        view.kernel_weight = sub.kernel_weight
        view.n_minimal_kernels = sub.n_minimal_kernels
        view.backend_estimate = backend_est
        view.factory_metadata = dict(factory_metadata or {})
        template_assessments = [asdict(a) for a in assess_magic_templates(view)]
    except Exception as exc:  # pragma: no cover - defensive; templates are diagnostic only
        template_assessments = [{"template_bridge_error": str(exc)}]

    return MagicScoutReport(
        protocol_id=protocol_id,
        target=target,
        role=role,
        contextual=sub.contextual,
        kernel_contexts=selected,
        kernel_weight=sub.kernel_weight,
        verified=verified,
        zd_avn_contextual=zd_contextual,
        obstruction_value=sub.obstruction_value,
        n_minimal_kernels=sub.n_minimal_kernels,
        cpsat_certified_minimal=sub.certified_minimal,
        interest_score=round(score, 3),
        positive_signals=positive,
        missing_evidence=missing + _always_missing_factory_evidence(),
        not_claimed=_default_not_claimed(),
        backend_estimate=backend_est,
        template_assessments=template_assessments,
        factory_metadata=dict(factory_metadata or {}),
        criterion_ledger=ledger,
    )


def magic_report_dict(report: MagicScoutReport) -> dict:
    return asdict(report)


def _require_type(data: dict[str, Any], expected: str) -> None:
    got = data.get("type")
    if got != expected:
        raise ValueError(f"expected JSON type {expected!r}, got {got!r}")


def parse_magic_protocol(data: dict[str, Any], *, source_path: str | None = None) -> MagicProtocol:
    _require_type(data, MAGIC_PROTOCOL_TYPE)
    return MagicProtocol(
        protocol_id=str(data.get("protocol_id", "candidate_protocol")),
        target=str(data.get("target", "generic_non_clifford")),
        role=str(data.get("role", "candidate_magic_protocol_diagnostic")),
        input_kind=str(data.get("input_kind", "schedule")),
        claim_scope=str(data.get("claim_scope", "diagnostic_only")),
        payload=dict(data),
        factory_metadata=dict(data.get("factory_metadata", {})),
        backend_model=data.get("backend_model"),
        source_path=source_path,
    )


def load_magic_protocol(path: str | Path) -> MagicProtocol:
    p = Path(path)
    data = json.loads(p.read_text(encoding="utf-8"))
    return parse_magic_protocol(data, source_path=str(p))


def program_from_magic_protocol(protocol: MagicProtocol) -> WeylProgram:
    """Convert a MagicProtocol record to a WeylProgram."""
    kind = protocol.input_kind
    payload = protocol.payload

    if "path" in payload:
        path = Path(payload["path"])
        if protocol.source_path is not None and not path.is_absolute():
            path = Path(protocol.source_path).parent / path
        from .adapters.pauli_table import load_pauli_table
        from .adapters.qiskit_lite import load_qiskit_lite_program
        from .adapters.stim_lite import load_stim_lite_program
        from .io import load_program
        from .pauli import load_pauli_program
        from .pauli_schedule import load_pauli_schedule

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
        raise ValueError(f"unsupported protocol input_kind: {kind!r}")

    if kind == "schedule":
        from .pauli_schedule import schedule_program

        schedule = payload.get("schedule", {})
        return schedule_program(
            schedule["layers"],
            include_full_layers=bool(schedule.get("include_full_layers", True)),
            include_closed_triples=bool(schedule.get("include_closed_triples", True)),
        )

    if kind == "pauli":
        from .pauli import pauli_program

        data = payload.get("pauli_contexts", {})
        return pauli_program(data["contexts"])

    if kind == "weyl":
        data = payload.get("weyl_program")
        if data is None:
            raise ValueError("weyl magic protocol requires `weyl_program` or `path`")
        return WeylProgram(
            d=int(data["d"]),
            m=int(data["m"]),
            observables={str(k): list(v) for k, v in data["observables"].items()},
            contexts=[list(ctx) for ctx in data["contexts"]],
            observable_metadata=data.get("observable_metadata", {}),
            context_phases=data.get("context_phases"),
        )

    raise ValueError(f"unsupported inline protocol input_kind: {kind!r}")


def analyze_magic_protocol_record(
    protocol: MagicProtocol,
    *,
    enumerate_all_kernels: bool = True,
    certify_minimal: bool = False,
    max_cycle_dim_enumerate: int = 20,
) -> MagicScoutReport:
    return analyze_magic_protocol(
        program_from_magic_protocol(protocol),
        protocol_id=protocol.protocol_id,
        target=protocol.target,
        role=protocol.role,
        factory_metadata=protocol.factory_metadata,
        backend_model=protocol.backend_model,
        enumerate_all_kernels=enumerate_all_kernels,
        certify_minimal=certify_minimal,
        max_cycle_dim_enumerate=max_cycle_dim_enumerate,
    )


def load_magic_portfolio(path: str | Path) -> tuple[str, list[MagicProtocol]]:
    p = Path(path)
    data = json.loads(p.read_text(encoding="utf-8"))
    _require_type(data, MAGIC_PORTFOLIO_TYPE)
    protocols: list[MagicProtocol] = []
    for item in data.get("protocols", []):
        if isinstance(item, str):
            protocols.append(load_magic_protocol(p.parent / item))
        elif isinstance(item, dict):
            protocols.append(parse_magic_protocol(item, source_path=str(p)))
        else:
            raise ValueError(f"portfolio protocol entry must be string or object, got {type(item)}")
    return str(data.get("portfolio_id", p.stem)), protocols


def analyze_magic_portfolio(
    protocols: list[MagicProtocol],
    *,
    portfolio_id: str = "magic_portfolio",
    enumerate_all_kernels: bool = True,
    certify_minimal: bool = False,
) -> MagicPortfolioReport:
    entries: list[MagicPortfolioEntry] = []
    for proto in protocols:
        report = analyze_magic_protocol_record(
            proto,
            enumerate_all_kernels=enumerate_all_kernels,
            certify_minimal=certify_minimal,
        )
        entries.append(MagicPortfolioEntry(rank=0, protocol_id=proto.protocol_id, report=report))

    entries.sort(
        key=lambda e: (
            -e.report.interest_score,
            e.report.backend_estimate.shots_total if e.report.backend_estimate and e.report.backend_estimate.shots_total is not None else 10**12,
            e.report.kernel_weight if e.report.kernel_weight is not None else 10**9,
            e.protocol_id,
        )
    )
    ranked = [
        MagicPortfolioEntry(rank=i + 1, protocol_id=e.protocol_id, report=e.report)
        for i, e in enumerate(entries)
    ]
    return MagicPortfolioReport(
        portfolio_id=portfolio_id,
        entries=ranked,
        ranking_rule=(
            "interest_score descending; backend shots ascending when present; "
            "kernel weight ascending; protocol_id"
        ),
        not_claimed=_default_not_claimed(),
    )


def magic_portfolio_report_dict(report: MagicPortfolioReport) -> dict:
    return asdict(report)


def analyze_magic_portfolio_file(path: str | Path) -> MagicPortfolioReport:
    portfolio_id, protocols = load_magic_portfolio(path)
    return analyze_magic_portfolio(protocols, portfolio_id=portfolio_id)


def run_magic_zoo(
    *,
    include_noncontextual: bool = False,
    top: int | None = None,
) -> list[MagicZooEntry]:
    """Run MagicScout over the Contextuality Benchmark Zoo."""
    from .zoo import ZOO

    entries: list[MagicZooEntry] = []
    for inst in ZOO:
        report = analyze_magic_protocol(
            inst.builder(),
            protocol_id=inst.name,
            target="benchmark_zoo_contextuality_resource",
            role="benchmark_zoo_motif",
            enumerate_all_kernels=True,
            certify_minimal=False,
        )
        if report.contextual or include_noncontextual:
            entries.append(MagicZooEntry(inst.name, inst.claim_scope, inst.note, report))

    entries.sort(
        key=lambda e: (
            -e.report.interest_score,
            e.report.kernel_weight if e.report.kernel_weight is not None else 10**9,
            e.instance_name,
        )
    )
    return entries[:top] if top is not None else entries


def magic_zoo_report_dict(entries: list[MagicZooEntry]) -> dict:
    return {"entries": [asdict(entry) for entry in entries], "count": len(entries)}


def generate_magic_candidates_from_paulis(
    paulis: list[str],
    *,
    target: str = "generic_non_clifford",
    top: int = 10,
    backend_model: dict[str, Any] | None = None,
) -> list[GeneratedMagicCandidate]:
    """Generate MagicScout candidates from an available Pauli measurement set."""
    from .experiment_design import minimal_contextuality_tests
    from .pauli import pauli_program

    tests = minimal_contextuality_tests(paulis, top=top)
    candidates: list[GeneratedMagicCandidate] = []
    for i, test in enumerate(tests, start=1):
        proto = MagicProtocol(
            protocol_id=f"generated_candidate_{i}",
            target=target,
            role="generated_contextuality_motif",
            input_kind="pauli",
            claim_scope="diagnostic_only",
            payload={
                "type": MAGIC_PROTOCOL_TYPE,
                "protocol_id": f"generated_candidate_{i}",
                "target": target,
                "role": "generated_contextuality_motif",
                "input_kind": "pauli",
                "claim_scope": "diagnostic_only",
                "pauli_contexts": {"contexts": test.contexts},
            },
            factory_metadata={"source": "generated_from_available_paulis"},
            backend_model=backend_model,
        )
        report = analyze_magic_protocol(
            pauli_program(test.contexts),
            protocol_id=proto.protocol_id,
            target=target,
            role=proto.role,
            factory_metadata=proto.factory_metadata,
            backend_model=backend_model,
            enumerate_all_kernels=True,
            certify_minimal=False,
        )
        candidates.append(GeneratedMagicCandidate(protocol=proto, report=report))

    candidates.sort(
        key=lambda c: (
            -c.report.interest_score,
            c.report.backend_estimate.shots_total if c.report.backend_estimate and c.report.backend_estimate.shots_total is not None else 10**12,
            c.report.kernel_weight if c.report.kernel_weight is not None else 10**9,
            c.protocol.protocol_id,
        )
    )
    return candidates


def generated_magic_report_dict(candidates: list[GeneratedMagicCandidate]) -> dict:
    return {"candidates": [asdict(c) for c in candidates], "count": len(candidates)}


def run_magic_audit() -> MagicAuditReport:
    """Run a lightweight safety/readiness audit for MagicScout."""
    checks: list[MagicAuditCheck] = []

    from .zoo import peres_mermin_program, single_context_program

    pm = analyze_magic_protocol(peres_mermin_program(), protocol_id="audit_pm")
    checks.append(MagicAuditCheck(
        id="magic:pm_contextual",
        passed=pm.contextual and pm.verified and pm.zd_avn_contextual is True,
        detail=f"contextual={pm.contextual}, verified={pm.verified}, zd={pm.zd_avn_contextual}",
    ))
    checks.append(MagicAuditCheck(
        id="magic:pm_has_nonclaims",
        passed=bool(pm.not_claimed) and any("overhead" in x for x in pm.not_claimed),
        detail=", ".join(pm.not_claimed),
    ))
    checks.append(MagicAuditCheck(
        id="magic:pm_lists_missing_factory_evidence",
        passed=any("distillation map" in x for x in pm.missing_evidence),
        detail=", ".join(pm.missing_evidence),
    ))
    checks.append(MagicAuditCheck(
        id="magic:criterion_ledger_present",
        passed=pm.criterion_ledger is not None and pm.criterion_ledger.get("criterion_id") == "odd_Q_even_d_v1",
        detail=str(pm.criterion_ledger),
    ))

    nc = analyze_magic_protocol(single_context_program(), protocol_id="audit_single_context")
    checks.append(MagicAuditCheck(
        id="magic:noncontextual_low_interest",
        passed=(not nc.contextual) and nc.interest_score < 0.3,
        detail=f"contextual={nc.contextual}, score={nc.interest_score}",
    ))

    zentries = run_magic_zoo()
    checks.append(MagicAuditCheck(
        id="magic:zoo_bridge_nonempty",
        passed=bool(zentries) and all(e.report.contextual for e in zentries),
        detail=f"entries={len(zentries)}",
    ))

    passed = all(c.passed for c in checks)
    return MagicAuditReport(
        passed=passed,
        checks=checks,
        recommendation=(
            "MagicScout is ready as a conservative diagnostic layer; keep factory claims disabled."
            if passed
            else "MagicScout audit failed; fix claim-scope or verifier checks before use."
        ),
    )


def magic_audit_report_dict(report: MagicAuditReport) -> dict:
    return asdict(report)
