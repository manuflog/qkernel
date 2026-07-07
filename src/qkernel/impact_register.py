from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal


SCHEMA_VERSION = "qkernel.impact_register.v1"
ApplicationStatus = Literal["implemented", "experimental", "planned"]


@dataclass(frozen=True)
class ImpactApplication:
    application_id: str
    name: str
    status: ApplicationStatus
    impact_area: str
    real_world_impact: str
    current_capabilities: list[str]
    commands: list[str]
    docs: list[str]
    missing_evidence: list[str]
    next_actions: list[str]
    claim_scope: str
    not_claimed: list[str]


@dataclass(frozen=True)
class ImpactRegisterSummary:
    total_applications: int
    implemented: int
    experimental: int
    planned: int
    application_ids: list[str]
    highest_priority_next_actions: list[str]


@dataclass(frozen=True)
class ImpactRegisterReport:
    schema: str
    applications: list[ImpactApplication]
    summary: ImpactRegisterSummary
    claim_scope: str
    not_claimed: list[str]


def _applications() -> list[ImpactApplication]:
    return [
        ImpactApplication(
            application_id="kernel_census",
            name="Kernel census and K(d,m) target planning",
            status="implemented",
            impact_area="mathematical contextuality atlas",
            real_world_impact=(
                "Keeps witnessed minimal odd-Q kernels, theorem pins, and open K(d,m) targets "
                "in one auditable workflow for research planning."
            ),
            current_capabilities=[
                "reports zoo witnessed minima by local dimension and context size",
                "merges externally verified theorem pins without confusing them with zoo witnesses",
                "tracks target plans for open K(d,m) cells",
            ],
            commands=["kernel-census"],
            docs=["docs/KERNEL_CENSUS.md"],
            missing_evidence=[
                "global lower-bound proofs for open K(d,m) targets",
                "larger curated benchmark coverage beyond the current zoo",
            ],
            next_actions=[
                "add more target plans from the research atlas",
                "link each theorem pin to a stable proof artifact",
            ],
            claim_scope="conservative census and target ledger",
            not_claimed=[
                "does not prove unpinned global K(d,m) values",
                "does not replace independent mathematical proof",
            ],
        ),
        ImpactApplication(
            application_id="compiler_candidates",
            name="Compiler and optimizer candidate corpus",
            status="implemented",
            impact_area="compiler diagnostics and guarded optimization research",
            real_world_impact=(
                "Packages before/after compiler-pass hypotheses with qkernel diagnostics, semantic-proof "
                "status, and resource-metric status so optimization ideas can be tested without overclaiming."
            ),
            current_capabilities=[
                "records candidate compiler passes and qkernel before/after diagnostics",
                "separates semantic-equivalence evidence from resource evidence",
                "labels rewrite-policy guardrails for each candidate",
            ],
            commands=["compiler-candidates", "compiler-report", "compare-pass", "rewrite-policies", "assess-rewrite"],
            docs=["docs/COMPILER_CANDIDATES.md", "docs/COMPILER_OPTIMIZER_PATH.md"],
            missing_evidence=[
                "machine-checkable semantic equivalence proofs for every pass",
                "external T-count, T-depth, or schedule metrics on realistic circuits",
            ],
            next_actions=[
                "add corpus rows for concrete transpiler or synthesis passes",
                "connect correlation-study rows to the same candidate IDs",
            ],
            claim_scope="compiler-pass triage and evidence ledger",
            not_claimed=[
                "does not prove a rewrite is semantics-preserving",
                "does not claim qkernel alone reduces T-count or circuit depth",
            ],
        ),
        ImpactApplication(
            application_id="magic_scout",
            name="MagicScout motif triage",
            status="implemented",
            impact_area="magic-state-adjacent research triage",
            real_world_impact=(
                "Ranks contextuality motifs and preserves the evidence boundary between useful probes, "
                "factory-template compatibility, and real magic-state factory performance."
            ),
            current_capabilities=[
                "analyzes protocol motifs through conservative criterion ledgers",
                "searches available Pauli measurements for candidate motifs",
                "renders reports with missing evidence and forbidden claims",
            ],
            commands=["magic-protocol", "magic-search", "magic-report", "magic-zoo", "magic-audit"],
            docs=["docs/MAGICSCOUT.md", "docs/MAGIC_SEARCH.md", "docs/MAGIC_REPORTS.md"],
            missing_evidence=[
                "acceptance probability and fidelity data for proposed factory roles",
                "decoder, threshold, code-distance, and space-time-volume evidence",
            ],
            next_actions=[
                "promote promising motifs into factory-candidate corpus rows",
                "attach measured or simulated backend estimates where available",
            ],
            claim_scope="motif triage and report generation",
            not_claimed=[
                "does not output a working magic-state factory",
                "does not claim overhead, threshold, fidelity, or acceptance-probability improvements",
            ],
        ),
        ImpactApplication(
            application_id="factory_candidates",
            name="Magic-state factory candidate ledger",
            status="implemented",
            impact_area="factory hypothesis management",
            real_world_impact=(
                "Turns MagicScout motifs into reviewable factory-adjacent hypotheses with template "
                "compatibility, missing factory metrics, and explicit non-claims."
            ),
            current_capabilities=[
                "loads a candidate corpus and validates required evidence fields",
                "summarizes template compatibility and blockers",
                "emits Markdown reports for review",
            ],
            commands=["factory-candidates"],
            docs=["docs/FACTORY_CANDIDATES.md"],
            missing_evidence=[
                "physical factory construction for each candidate",
                "resource estimates from an external factory simulator or paper",
            ],
            next_actions=[
                "add candidate IDs that link back to MagicScout reports",
                "record external sources for any claimed factory metrics",
            ],
            claim_scope="factory-candidate tracking, not factory validation",
            not_claimed=[
                "does not validate a distillation or cultivation factory",
                "does not prove resource advantage over known factories",
            ],
        ),
        ImpactApplication(
            application_id="circuit_builder",
            name="Circuit builder readiness manifest",
            status="implemented",
            impact_area="hardware protocol preparation",
            real_world_impact=(
                "Prevents unsupported contextuality inputs from being presented as hardware-ready "
                "circuits while documenting which cases can use the validated Qiskit exporter."
            ),
            current_capabilities=[
                "reports exporter readiness and blockers for each input",
                "lists supported two-qubit protocol paths",
                "writes a Markdown manifest for review before circuit export",
            ],
            commands=["circuit-manifest", "export-circuit"],
            docs=["docs/CIRCUIT_MANIFEST.md", "docs/EXPORT_CIRCUIT.md"],
            missing_evidence=[
                "validated qudit exporter support",
                "backend-specific calibration and measurement-error evidence",
            ],
            next_actions=[
                "add manifests for atlas targets that should become hardware probes",
                "separate hardware-ready export from research-only manifest states",
            ],
            claim_scope="readiness reporting and safe circuit-export gating",
            not_claimed=[
                "does not emit hardware-ready scripts for unsupported inputs",
                "does not claim backend execution fidelity",
            ],
        ),
        ImpactApplication(
            application_id="resource_oracle",
            name="Resource oracle bridge",
            status="implemented",
            impact_area="resource-metric correlation studies",
            real_world_impact=(
                "Exports qkernel features beside externally supplied resource metrics so scientists "
                "can test whether odd-Q structure correlates with compilation or factory costs."
            ),
            current_capabilities=[
                "extracts qkernel feature rows from supported program inputs",
                "joins optional external resource metrics without prediction language",
                "renders Markdown summaries with explicit non-claims",
            ],
            commands=["resource-features"],
            docs=["docs/RESOURCE_ORACLE.md"],
            missing_evidence=[
                "large externally measured resource datasets",
                "statistical validation outside the qkernel feature exporter",
            ],
            next_actions=[
                "collect external resource rows for compiler and factory candidates",
                "keep negative controls in every dataset",
            ],
            claim_scope="feature export for external resource analysis",
            not_claimed=[
                "does not predict resource metrics",
                "does not prove resource theorems",
            ],
        ),
        ImpactApplication(
            application_id="correlation_study",
            name="Correlation study harness",
            status="implemented",
            impact_area="evidence collection and analysis handoff",
            real_world_impact=(
                "Creates joined JSON, Markdown, and CSV artifacts for exploratory analysis in notebooks, "
                "spreadsheets, or statistical tooling while preserving negative controls."
            ),
            current_capabilities=[
                "loads study manifests with candidate and negative-control rows",
                "joins qkernel features with external metrics",
                "exports joined CSV tables for downstream analysis",
            ],
            commands=["correlation-study"],
            docs=["docs/CORRELATION_STUDY.md"],
            missing_evidence=[
                "enough measured rows for meaningful statistics",
                "independent validation of any model fitted outside qkernel",
            ],
            next_actions=[
                "extend example studies with real compiler and factory rows",
                "define minimum dataset gates before any public performance claim",
            ],
            claim_scope="correlation-only study preparation",
            not_claimed=[
                "does not infer causation",
                "does not validate resource predictions",
            ],
        ),
        ImpactApplication(
            application_id="new_application_prd",
            name="New application PRD track",
            status="planned",
            impact_area="future product and research direction",
            real_world_impact=(
                "Provides a holding track for new qkernel applications such as compiler plugins, "
                "interactive circuit builders, and factory simulators before they are implemented."
            ),
            current_capabilities=[
                "records candidate directions without forcing them into the current API",
                "keeps claim boundaries visible while ideas are still speculative",
                "provides a CLI-rendered PRD for the next application workbench",
            ],
            commands=["application-prd"],
            docs=["docs/PRD_COMPILER_MAGIC_FACTORY_BRIDGE.md", "docs/PRD_APPLICATION_WORKBENCH.md"],
            missing_evidence=[
                "user workflow selection and requirements",
                "prototype success metrics for each new application",
            ],
            next_actions=[
                "write a scoped PRD for the highest-leverage next application",
                "choose one prototype path: compiler plugin, circuit builder UI, or factory simulator bridge",
            ],
            claim_scope="planning register for optional future development",
            not_claimed=[
                "does not commit every listed direction to implementation",
                "does not treat speculative product ideas as existing qkernel capabilities",
            ],
        ),
    ]


def _summary(applications: list[ImpactApplication]) -> ImpactRegisterSummary:
    status_counts = {
        "implemented": sum(1 for app in applications if app.status == "implemented"),
        "experimental": sum(1 for app in applications if app.status == "experimental"),
        "planned": sum(1 for app in applications if app.status == "planned"),
    }
    return ImpactRegisterSummary(
        total_applications=len(applications),
        implemented=status_counts["implemented"],
        experimental=status_counts["experimental"],
        planned=status_counts["planned"],
        application_ids=[app.application_id for app in applications],
        highest_priority_next_actions=[
            "connect correlation-study rows to compiler and factory candidate IDs",
            "add real external resource metrics before making performance claims",
            "write a scoped PRD for the next new application prototype",
        ],
    )


def impact_register_report() -> ImpactRegisterReport:
    applications = _applications()
    return ImpactRegisterReport(
        schema=SCHEMA_VERSION,
        applications=applications,
        summary=_summary(applications),
        claim_scope=(
            "application impact register for qkernel development planning; tracks current capabilities, "
            "evidence gaps, next actions, and claim boundaries"
        ),
        not_claimed=[
            "does not claim qkernel is a production compiler",
            "does not claim qkernel builds validated magic-state factories",
            "does not claim resource improvements without external resource evidence",
            "does not replace mathematical proofs, hardware validation, or statistical analysis",
        ],
    )


def impact_register_report_dict(report: ImpactRegisterReport) -> dict:
    return asdict(report)


def _fmt_list(items: list[str]) -> str:
    if not items:
        return "- none"
    return "\n".join(f"- {item}" for item in items)


def impact_register_markdown(report: ImpactRegisterReport | dict) -> str:
    data = asdict(report) if isinstance(report, ImpactRegisterReport) else report
    lines = [
        "# QKernel Application Impact Register",
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
        lines.append(f"| {key} | {value} |")
    lines.extend([
        "",
        "## Application Tracks",
        "",
    ])
    for app in data["applications"]:
        lines.extend([
            f"### {app['name']}",
            "",
            f"- id: `{app['application_id']}`",
            f"- status: `{app['status']}`",
            f"- impact area: {app['impact_area']}",
            f"- real-world impact: {app['real_world_impact']}",
            "",
            "Current capabilities:",
            "",
            _fmt_list(app["current_capabilities"]),
            "",
            "Commands:",
            "",
            _fmt_list([f"`{cmd}`" for cmd in app["commands"]]),
            "",
            "Docs:",
            "",
            _fmt_list([f"`{doc}`" for doc in app["docs"]]),
            "",
            "Missing evidence:",
            "",
            _fmt_list(app["missing_evidence"]),
            "",
            "Next actions:",
            "",
            _fmt_list(app["next_actions"]),
            "",
            "Not claimed:",
            "",
            _fmt_list(app["not_claimed"]),
            "",
        ])
    lines.extend([
        "## Register Non-Claims",
        "",
        _fmt_list(data["not_claimed"]),
        "",
    ])
    return "\n".join(lines)


def write_impact_register_markdown(report: ImpactRegisterReport | dict, path: str | Path) -> None:
    Path(path).write_text(impact_register_markdown(report), encoding="utf-8")
