from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

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
            global_K_proven=False,
            global_K_value=None,
            proof_obligations=[
                "exhaust all relevant Weyl/context-family shapes or cite a checked classification",
                "prove no contextual family exists below the witnessed kernel weight",
                "attach machine-checkable MILP/CP-SAT certificates or a mathematical lower-bound proof",
                "pin the theorem source before reporting a global K(d,m) value",
            ],
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
