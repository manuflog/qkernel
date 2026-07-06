from __future__ import annotations

from dataclasses import asdict, dataclass

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
    claim_scope: str


@dataclass(frozen=True)
class KernelCensusReport:
    schema: str
    entries: list[CensusEntry]
    summaries: list[CensusSummary]
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


def _summaries(entries: list[CensusEntry]) -> list[CensusSummary]:
    grouped: dict[tuple[int, int], list[CensusEntry]] = {}
    for entry in entries:
        grouped.setdefault((entry.d, entry.m), []).append(entry)

    out: list[CensusSummary] = []
    for (d, m), group in sorted(grouped.items()):
        contextual = [e for e in group if e.contextual]
        noncontextual = [e for e in group if not e.contextual]
        weights = [e.kernel_weight for e in contextual if e.kernel_weight is not None]
        min_weight = min(weights) if weights else None
        witnesses = sorted(e.name for e in contextual if e.kernel_weight == min_weight)
        out.append(CensusSummary(
            d=d,
            m=m,
            contextual_instances=len(contextual),
            noncontextual_instances=len(noncontextual),
            witnessed_min_kernel_weight=min_weight,
            witness_names=witnesses,
            claim_scope=(
                "witnessed minimum among registered zoo instances only; "
                "not a proof of global K(d,m) unless supplied by an external theorem"
            ),
        ))
    return out


def run_kernel_census(*, include_noncontextual: bool = True) -> KernelCensusReport:
    """Run a conservative minimal-kernel census over the benchmark zoo.

    This pins known small examples and their minimal-kernel statistics. It does
    not prove a universal K(d,m) lower bound over all possible Weyl families.
    """
    entries = [_entry(inst) for inst in ZOO]
    if not include_noncontextual:
        entries = [entry for entry in entries if entry.contextual]

    return KernelCensusReport(
        schema=SCHEMA_VERSION,
        entries=entries,
        summaries=_summaries(entries),
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


def kernel_census_report_dict(*, include_noncontextual: bool = True) -> dict:
    return asdict(run_kernel_census(include_noncontextual=include_noncontextual))
