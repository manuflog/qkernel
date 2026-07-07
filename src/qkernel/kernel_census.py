from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .zoo import ZOO, ZooInstance, run_instance


SCHEMA_VERSION = "qkernel.kernel_census.v1"


@dataclass(frozen=True)
class CensusEntry:
    name: str
    d: int
    m: int
    contexts: int
    observables: int
    contextual: bool
    passed_zoo_expectation: bool
    kernel_weight: int | None
    n_minimal_kernels: int | None
    obstruction_value: int | None
    zd_avn_contextual: bool | None
    claim_scope: str
    note: str
    evidence_level: str


@dataclass(frozen=True)
class CensusSummary:
    d: int
    m: int
    contextual_instances: int
    noncontextual_instances: int
    witnessed_min_kernel_weight: int | None
    witness_names: list[str]
    global_K_proven: bool
    global_K_value: int | None
    proof_obligations: list[str]
    claim_scope: str


@dataclass(frozen=True)
class KernelTheoremPin:
    d: int
    m: int
    K: int
    theorem_id: str
    source: str
    proof_method: str
    verifier: str | None = None
    notes: str = ""


@dataclass(frozen=True)
class KernelTheoremPinAudit:
    d: int
    m: int
    K: int
    theorem_id: str
    status: str
    witnessed_min_kernel_weight: int | None
    witness_names: list[str]
    detail: str


@dataclass(frozen=True)
class KernelCensusTargetSpec:
    d: int
    m: int
    target_id: str = ""
    priority: str = ""
    source: str = ""
    rationale: str = ""


@dataclass(frozen=True)
class KernelCensusTarget:
    d: int
    m: int
    target_id: str
    priority: str
    source: str
    rationale: str
    status: str
    witnessed_min_kernel_weight: int | None
    witness_names: list[str]
    global_K_proven: bool
    global_K_value: int | None
    theorem_id: str | None
    proof_obligations: list[str]
    next_actions: list[str]
    claim_scope: str


@dataclass(frozen=True)
class KernelCensusReport:
    schema: str
    entries: list[CensusEntry]
    summaries: list[CensusSummary]
    theorem_pins: list[KernelTheoremPin]
    theorem_pin_audits: list[KernelTheoremPinAudit]
    research_targets: list[KernelCensusTarget]
    claim_scope: str
    non_claims: list[str]


def _entry(inst: ZooInstance) -> CensusEntry:
    program = inst.builder()
    result = run_instance(inst)
    sub = result.result
    ledger = sub.criterion_ledger or {}
    return CensusEntry(
        name=inst.name,
        d=program.d,
        m=program.m,
        contexts=len(program.contexts),
        observables=len(program.observables),
        contextual=sub.contextual,
        passed_zoo_expectation=result.passed,
        kernel_weight=sub.kernel_weight,
        n_minimal_kernels=sub.n_minimal_kernels,
        obstruction_value=sub.obstruction_value,
        zd_avn_contextual=ledger.get("stronger_verifier_passed"),
        claim_scope=inst.claim_scope,
        note=inst.note,
        evidence_level="zoo_pinned_instance",
    )


def _global_proof_obligations() -> list[str]:
    return [
        "exhaust all relevant Weyl/context-family shapes or cite a checked classification",
        "prove no contextual family exists below the witnessed kernel weight",
        "attach machine-checkable MILP/CP-SAT certificates or a mathematical lower-bound proof",
        "pin the theorem source before reporting a global K(d,m) value",
    ]


def _witnessed_minima(entries: list[CensusEntry]) -> dict[tuple[int, int], tuple[int, list[str]]]:
    witnessed: dict[tuple[int, int], tuple[int, list[str]]] = {}
    for entry in entries:
        if not entry.contextual or entry.kernel_weight is None:
            continue
        key = (entry.d, entry.m)
        if key not in witnessed or entry.kernel_weight < witnessed[key][0]:
            witnessed[key] = (entry.kernel_weight, [entry.name])
        elif entry.kernel_weight == witnessed[key][0]:
            witnessed[key][1].append(entry.name)
    return {key: (weight, sorted(names)) for key, (weight, names) in witnessed.items()}


def _summaries(entries: list[CensusEntry], theorem_pins: list[KernelTheoremPin]) -> list[CensusSummary]:
    grouped: dict[tuple[int, int], list[CensusEntry]] = {}
    for entry in entries:
        grouped.setdefault((entry.d, entry.m), []).append(entry)
    pins_by_dm = {(pin.d, pin.m): pin for pin in theorem_pins}

    out: list[CensusSummary] = []
    for (d, m), group in sorted(grouped.items()):
        contextual = [e for e in group if e.contextual]
        noncontextual = [e for e in group if not e.contextual]
        weights = [e.kernel_weight for e in contextual if e.kernel_weight is not None]
        min_weight = min(weights) if weights else None
        witnesses = sorted(e.name for e in contextual if e.kernel_weight == min_weight)
        pin = pins_by_dm.get((d, m))
        if pin is None:
            global_K_proven = False
            global_K_value = None
            proof_obligations = _global_proof_obligations()
            claim_scope = (
                "witnessed minimum among registered zoo instances only; "
                "not a proof of global K(d,m) unless supplied by an external theorem"
            )
        else:
            global_K_proven = True
            global_K_value = pin.K
            proof_obligations = []
            claim_scope = (
                f"global K({d},{m})={pin.K} pinned by theorem {pin.theorem_id}; "
                f"source={pin.source}; proof_method={pin.proof_method}"
            )
        out.append(CensusSummary(
            d=d,
            m=m,
            contextual_instances=len(contextual),
            noncontextual_instances=len(noncontextual),
            witnessed_min_kernel_weight=min_weight,
            witness_names=witnesses,
            global_K_proven=global_K_proven,
            global_K_value=global_K_value,
            proof_obligations=proof_obligations,
            claim_scope=claim_scope,
        ))
    return out


def _theorem_pin_from_dict(item: dict[str, Any]) -> KernelTheoremPin:
    required = ["d", "m", "K", "theorem_id", "source", "proof_method"]
    missing = [key for key in required if key not in item]
    if missing:
        raise ValueError(f"kernel theorem pin missing required field(s): {', '.join(missing)}")
    pin = KernelTheoremPin(
        d=int(item["d"]),
        m=int(item["m"]),
        K=int(item["K"]),
        theorem_id=str(item["theorem_id"]),
        source=str(item["source"]),
        proof_method=str(item["proof_method"]),
        verifier=str(item["verifier"]) if item.get("verifier") is not None else None,
        notes=str(item.get("notes", "")),
    )
    if pin.d <= 0 or pin.m <= 0 or pin.K <= 0:
        raise ValueError("kernel theorem pins require positive d, m, and K")
    return pin


def load_kernel_theorem_pins(path: str | Path) -> list[KernelTheoremPin]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    pins_data = data.get("theorem_pins", data)
    if not isinstance(pins_data, list):
        raise ValueError("kernel theorem pin file must be a list or contain a `theorem_pins` list")
    pins = [_theorem_pin_from_dict(item) for item in pins_data]
    seen: set[tuple[int, int]] = set()
    for pin in pins:
        key = (pin.d, pin.m)
        if key in seen:
            raise ValueError(f"duplicate theorem pin for d={pin.d}, m={pin.m}")
        seen.add(key)
    return pins


def _target_spec_from_dict(item: dict[str, Any]) -> KernelCensusTargetSpec:
    required = ["d", "m"]
    missing = [key for key in required if key not in item]
    if missing:
        raise ValueError(f"kernel census target missing required field(s): {', '.join(missing)}")
    spec = KernelCensusTargetSpec(
        d=int(item["d"]),
        m=int(item["m"]),
        target_id=str(item.get("target_id", "")),
        priority=str(item.get("priority", "")),
        source=str(item.get("source", "")),
        rationale=str(item.get("rationale", "")),
    )
    if spec.d <= 0 or spec.m <= 0:
        raise ValueError("kernel census targets require positive d and m")
    return spec


def load_kernel_census_targets(path: str | Path) -> list[KernelCensusTargetSpec]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    targets_data = data.get("research_targets", data.get("targets", data))
    if not isinstance(targets_data, list):
        raise ValueError("kernel census target file must be a list or contain a `research_targets` list")
    targets = [_target_spec_from_dict(item) for item in targets_data]
    seen: set[tuple[int, int]] = set()
    for target in targets:
        key = (target.d, target.m)
        if key in seen:
            raise ValueError(f"duplicate kernel census target for d={target.d}, m={target.m}")
        seen.add(key)
    return targets


def _audit_theorem_pins_against_entries(
    pins: list[KernelTheoremPin],
    entries: list[CensusEntry],
) -> list[KernelTheoremPinAudit]:
    witnessed = _witnessed_minima(entries)
    audits: list[KernelTheoremPinAudit] = []
    for pin in pins:
        witness = witnessed.get((pin.d, pin.m))
        if witness is None:
            audits.append(KernelTheoremPinAudit(
                d=pin.d,
                m=pin.m,
                K=pin.K,
                theorem_id=pin.theorem_id,
                status="no_registered_witness",
                witnessed_min_kernel_weight=None,
                witness_names=[],
                detail=(
                    f"no contextual zoo witness is registered for d={pin.d}, m={pin.m}; "
                    "the theorem pin is recorded as external metadata"
                ),
            ))
            continue
        witnessed_weight, names = witness
        if pin.K > witnessed_weight:
            raise ValueError(
                f"theorem pin {pin.theorem_id} claims K({pin.d},{pin.m})={pin.K}, "
                f"but zoo witness(es) {names} have kernel weight {witnessed_weight}"
            )
        if pin.K == witnessed_weight:
            status = "matches_registered_witness"
            detail = (
                f"theorem K matches registered witness kernel weight {witnessed_weight}: "
                f"{', '.join(names)}"
            )
        else:
            status = "stronger_than_registered_witnesses"
            detail = (
                f"external theorem claims K={pin.K}, below the registered witnessed "
                f"minimum {witnessed_weight}; qkernel has no registered witness at K={pin.K}"
            )
        audits.append(KernelTheoremPinAudit(
            d=pin.d,
            m=pin.m,
            K=pin.K,
            theorem_id=pin.theorem_id,
            status=status,
            witnessed_min_kernel_weight=witnessed_weight,
            witness_names=names,
            detail=detail,
        ))
    return audits


def _research_target_records(
    entries: list[CensusEntry],
    theorem_pins: list[KernelTheoremPin],
    targets: list[tuple[int, int] | KernelCensusTargetSpec],
) -> list[KernelCensusTarget]:
    witnessed = _witnessed_minima(entries)
    pins_by_dm = {(pin.d, pin.m): pin for pin in theorem_pins}
    specs: dict[tuple[int, int], KernelCensusTargetSpec] = {}
    for target in targets:
        if isinstance(target, KernelCensusTargetSpec):
            spec = target
        else:
            d, m = target
            spec = KernelCensusTargetSpec(d=d, m=m)
        if spec.d <= 0 or spec.m <= 0:
            raise ValueError("kernel census targets require positive d and m")
        specs[(spec.d, spec.m)] = spec

    out: list[KernelCensusTarget] = []
    for d, m in sorted(specs):
        spec = specs[(d, m)]
        witness = witnessed.get((d, m))
        pin = pins_by_dm.get((d, m))
        witnessed_weight = witness[0] if witness else None
        witness_names = witness[1] if witness else []
        global_K_proven = pin is not None
        global_K_value = pin.K if pin is not None else None
        theorem_id = pin.theorem_id if pin is not None else None
        proof_obligations = [] if pin is not None else _global_proof_obligations()

        if pin is not None and witness is not None:
            status = "pinned_with_registered_witness"
            next_actions = [
                "keep theorem source and verifier metadata current",
                "add independent verifier artifacts when available",
            ]
            claim_scope = (
                f"global K({d},{m})={pin.K} is externally pinned; "
                "qkernel also has registered zoo witness evidence"
            )
        elif pin is not None:
            status = "pinned_without_registered_witness"
            next_actions = [
                "register a contextual zoo witness or certificate for this target",
                "add independent verifier artifacts when available",
            ]
            claim_scope = (
                f"global K({d},{m})={pin.K} is externally pinned; "
                "qkernel has no registered zoo witness for this target"
            )
        elif witness is not None:
            status = "witnessed_unpinned"
            next_actions = [
                "prove no contextual family exists below the witnessed kernel weight",
                "attach an external theorem pin once the global proof is checked",
            ]
            claim_scope = "registered zoo witness only; not a global K(d,m) theorem"
        else:
            status = "open_no_registered_witness"
            next_actions = [
                "construct or import a contextual witness for this target",
                "run kernel extraction and Z_d valuation verification on the witness",
                "attach classification or solver certificates before pinning global K(d,m)",
            ]
            claim_scope = (
                "open research target; no qkernel witness and no external theorem pin supplied"
            )

        out.append(KernelCensusTarget(
            d=d,
            m=m,
            target_id=spec.target_id,
            priority=spec.priority,
            source=spec.source,
            rationale=spec.rationale,
            status=status,
            witnessed_min_kernel_weight=witnessed_weight,
            witness_names=witness_names,
            global_K_proven=global_K_proven,
            global_K_value=global_K_value,
            theorem_id=theorem_id,
            proof_obligations=proof_obligations,
            next_actions=next_actions,
            claim_scope=claim_scope,
        ))
    return out


def run_kernel_census(
    *,
    include_noncontextual: bool = True,
    theorem_pins: list[KernelTheoremPin] | None = None,
    research_targets: list[tuple[int, int] | KernelCensusTargetSpec] | None = None,
) -> KernelCensusReport:
    """Run a conservative minimal-kernel census over the benchmark zoo.

    This pins known small examples and their minimal-kernel statistics. It does
    not prove a universal K(d,m) lower bound over all possible Weyl families.
    """
    entries = [_entry(inst) for inst in ZOO]
    if not include_noncontextual:
        entries = [entry for entry in entries if entry.contextual]
    pins = list(theorem_pins or [])
    theorem_pin_audits = _audit_theorem_pins_against_entries(pins, entries)
    targets = list(research_targets or [])

    return KernelCensusReport(
        schema=SCHEMA_VERSION,
        entries=entries,
        summaries=_summaries(entries, pins),
        theorem_pins=pins,
        theorem_pin_audits=theorem_pin_audits,
        research_targets=_research_target_records(entries, pins, targets),
        claim_scope=(
            "registered-instance census for qkernel's benchmark zoo; "
            "safe input to K(d,m) theorem/proof work, not a full-family classification"
        ),
        non_claims=[
            "does not prove global K(d,m) lower bounds",
            "does not exhaust all Weyl families at a given d,m",
            "does not replace external shape classifications or MILP/CP-SAT proofs",
            "does not claim a resource monotone",
        ],
    )


def kernel_census_report_dict(
    *,
    include_noncontextual: bool = True,
    theorem_pins: list[KernelTheoremPin] | None = None,
    research_targets: list[tuple[int, int] | KernelCensusTargetSpec] | None = None,
) -> dict:
    return asdict(run_kernel_census(
        include_noncontextual=include_noncontextual,
        theorem_pins=theorem_pins,
        research_targets=research_targets,
    ))


def _fmt(value: object) -> str:
    if value is None:
        return "-"
    if value is True:
        return "yes"
    if value is False:
        return "no"
    return str(value)


def _table(headers: list[str], rows: list[list[object]]) -> str:
    if not rows:
        return ""
    head = "| " + " | ".join(headers) + " |"
    sep = "| " + " | ".join("---" for _ in headers) + " |"
    body = ["| " + " | ".join(_fmt(cell) for cell in row) + " |" for row in rows]
    return "\n".join([head, sep, *body])


def kernel_census_markdown(report: KernelCensusReport | dict) -> str:
    """Render a kernel census report as Markdown."""
    data = asdict(report) if isinstance(report, KernelCensusReport) else report
    entries = data.get("entries", [])
    summaries = data.get("summaries", [])
    theorem_pins = data.get("theorem_pins", [])
    theorem_pin_audits = data.get("theorem_pin_audits", [])
    research_targets = data.get("research_targets", [])

    entry_rows = [
        [
            e.get("name"),
            e.get("d"),
            e.get("m"),
            e.get("contextual"),
            e.get("kernel_weight"),
            e.get("n_minimal_kernels"),
            e.get("obstruction_value"),
            e.get("zd_avn_contextual"),
        ]
        for e in entries
    ]
    summary_rows = [
        [
            f"({s.get('d')},{s.get('m')})",
            s.get("contextual_instances"),
            s.get("noncontextual_instances"),
            s.get("witnessed_min_kernel_weight"),
            s.get("global_K_proven"),
            ", ".join(s.get("witness_names", []) or []),
        ]
        for s in summaries
    ]

    lines = [
        "# Kernel Census",
        "",
        "## Scope",
        "",
        data.get("claim_scope", "-"),
        "",
        "## By `(d,m)`",
        "",
        _table(
            ["d,m", "contextual", "non-contextual", "witnessed min K", "global K proven", "witnesses"],
            summary_rows,
        ),
        "",
        "## Proof Obligations",
        "",
        "\n".join(
            f"- ({s.get('d')},{s.get('m')}): " + "; ".join(s.get("proof_obligations", []) or [])
            for s in summaries
        ) or "-",
        "",
        "## Theorem Pins",
        "",
        _table(
            ["d,m", "K", "theorem", "source", "method", "verifier"],
            [
                [
                    f"({pin.get('d')},{pin.get('m')})",
                    pin.get("K"),
                    pin.get("theorem_id"),
                    pin.get("source"),
                    pin.get("proof_method"),
                    pin.get("verifier"),
                ]
                for pin in theorem_pins
            ],
        ) or "No global K(d,m) theorem pins supplied.",
        "",
        "## Theorem Pin Audit",
        "",
        _table(
            ["d,m", "K", "theorem", "status", "witnessed K", "witnesses", "detail"],
            [
                [
                    f"({audit.get('d')},{audit.get('m')})",
                    audit.get("K"),
                    audit.get("theorem_id"),
                    audit.get("status"),
                    audit.get("witnessed_min_kernel_weight"),
                    ", ".join(audit.get("witness_names", []) or []),
                    audit.get("detail"),
                ]
                for audit in theorem_pin_audits
            ],
        ) or "No theorem pins to audit.",
        "",
        "## Research Targets",
        "",
        _table(
            ["d,m", "target", "priority", "source", "status", "witnessed K", "global K", "theorem", "next actions"],
            [
                [
                    f"({target.get('d')},{target.get('m')})",
                    target.get("target_id"),
                    target.get("priority"),
                    target.get("source"),
                    target.get("status"),
                    target.get("witnessed_min_kernel_weight"),
                    target.get("global_K_value"),
                    target.get("theorem_id"),
                    "; ".join(target.get("next_actions", []) or []),
                ]
                for target in research_targets
            ],
        ) or "No explicit research targets supplied.",
        "",
        "## Research Target Rationale",
        "",
        "\n".join(
            f"- ({target.get('d')},{target.get('m')}) {target.get('target_id') or '-'}: "
            f"{target.get('rationale') or '-'}"
            for target in research_targets
        ) or "-",
        "",
        "## Instances",
        "",
        _table(
            ["instance", "d", "m", "contextual", "K", "# min kernels", "value", "Z_d/AvN"],
            entry_rows,
        ),
        "",
        "## Non-Claims",
        "",
        "\n".join(f"- {item}" for item in data.get("non_claims", [])),
        "",
    ]
    return "\n".join(lines)


def write_kernel_census_markdown(report: KernelCensusReport | dict, path: str | Path) -> None:
    Path(path).write_text(kernel_census_markdown(report), encoding="utf-8")
