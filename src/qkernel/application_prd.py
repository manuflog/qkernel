from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal


SCHEMA_VERSION = "qkernel.application_prd.v1"
Priority = Literal["P0", "P1", "P2"]


@dataclass(frozen=True)
class ApplicationRequirement:
    priority: Priority
    name: str
    description: str
    acceptance_criteria: list[str]


@dataclass(frozen=True)
class ApplicationOption:
    option_id: str
    name: str
    target_user: str
    user_value: str
    implementation_risk: str
    evidence_gate: str
    why_now: str


@dataclass(frozen=True)
class ApplicationPRD:
    schema: str
    title: str
    status: str
    problem_statement: str
    recommended_v1: str
    goals: list[str]
    non_goals: list[str]
    user_stories: list[str]
    options: list[ApplicationOption]
    requirements: list[ApplicationRequirement]
    success_metrics: list[str]
    open_questions: list[str]
    phased_timeline: list[str]
    claim_boundaries: list[str]


def next_application_prd() -> ApplicationPRD:
    return ApplicationPRD(
        schema=SCHEMA_VERSION,
        title="PRD: QKernel Application Workbench",
        status=(
            "draft; implementation should proceed incrementally and only promote claims "
            "when evidence gates are cleared"
        ),
        problem_statement=(
            "QKernel now has separate compiler, MagicScout, factory-candidate, circuit-manifest, "
            "resource-oracle, and correlation-study surfaces. Researchers need one application "
            "workflow that turns those pieces into reviewable decisions without pretending that "
            "qkernel is already a production compiler, circuit builder, or magic-state factory."
        ),
        recommended_v1=(
            "Build a CLI-first application workbench that assembles existing reports by candidate ID, "
            "then produces a single evidence packet for compiler-pass and magic/factory triage."
        ),
        goals=[
            "reduce manual evidence-gathering across compiler, circuit, magic, factory, and resource reports",
            "make every application recommendation traceable to source commands, docs, and missing evidence",
            "support at least one end-to-end candidate packet that joins qkernel features with external metrics",
            "keep forbidden claims visible in every generated artifact",
        ],
        non_goals=[
            "production optimizer or transpiler integration in v1",
            "interactive circuit-builder UI in v1",
            "validated magic-state factory construction in v1",
            "statistical model fitting or causal resource claims inside qkernel",
            "hardware execution or backend calibration inside qkernel",
        ],
        user_stories=[
            (
                "As a quantum compiler researcher, I want a single evidence packet for a compiler-pass "
                "candidate so that I can see semantic-proof status, qkernel diagnostics, and resource "
                "metrics before deciding whether to investigate the pass."
            ),
            (
                "As a magic-state researcher, I want MagicScout motifs linked to factory-candidate "
                "evidence gates so that promising motifs are not mistaken for validated factories."
            ),
            (
                "As a hardware benchmarking researcher, I want circuit-builder readiness and blockers "
                "attached to a candidate so that unsupported protocols do not become fake hardware claims."
            ),
            (
                "As a qkernel maintainer, I want generated PR-ready claim boundaries so that releases "
                "can describe application progress without overstating results."
            ),
        ],
        options=[
            ApplicationOption(
                option_id="compiler_resource_workbench",
                name="Compiler/resource evidence workbench",
                target_user="quantum compiler researcher",
                user_value="combines compiler candidates, qkernel diagnostics, and external resource rows",
                implementation_risk="low; mostly composes existing JSON reports",
                evidence_gate="semantic-equivalence proof status plus externally sourced resource metrics",
                why_now="highest reuse of current compiler-candidate, resource-oracle, and correlation-study code",
            ),
            ApplicationOption(
                option_id="circuit_builder_ui",
                name="Circuit-builder readiness UI",
                target_user="hardware benchmarking researcher",
                user_value="shows which kernels can become validated circuit exports and which are blocked",
                implementation_risk="medium; frontend and hardware-capability modeling add new surface area",
                evidence_gate="validated exporter support and backend capability records",
                why_now="valuable, but better after the CLI evidence packet stabilizes",
            ),
            ApplicationOption(
                option_id="factory_simulator_bridge",
                name="Magic-state factory simulator bridge",
                target_user="fault-tolerance and magic-state researcher",
                user_value="links MagicScout motifs to external factory simulation metrics",
                implementation_risk="medium-high; requires careful external simulator/source integration",
                evidence_gate="acceptance probability, output fidelity, code distance, decoder, and volume evidence",
                why_now="important once candidate IDs and external metric contracts are stable",
            ),
        ],
        requirements=[
            ApplicationRequirement(
                priority="P0",
                name="Candidate packet schema",
                description=(
                    "Define a JSON packet that references compiler candidates, factory candidates, "
                    "circuit manifests, qkernel feature rows, and external resource rows by stable IDs."
                ),
                acceptance_criteria=[
                    "packet rejects duplicate candidate IDs",
                    "packet preserves source paths for every referenced report",
                    "packet includes missing_evidence and not_claimed sections",
                ],
            ),
            ApplicationRequirement(
                priority="P0",
                name="Evidence packet renderer",
                description="Render a Markdown packet suitable for PR review or research logs.",
                acceptance_criteria=[
                    "renderer groups compiler, circuit, magic, factory, and resource evidence separately",
                    "renderer prints claim boundaries before recommendations",
                    "renderer works without external network access",
                ],
            ),
            ApplicationRequirement(
                priority="P0",
                name="Claim-boundary gate",
                description="Block resource-positive or factory-positive language unless required evidence is present.",
                acceptance_criteria=[
                    "missing semantic-equivalence proof blocks optimizer claims",
                    "missing factory metrics blocks factory viability claims",
                    "missing backend readiness blocks hardware-ready circuit claims",
                ],
            ),
            ApplicationRequirement(
                priority="P1",
                name="Example packet corpus",
                description="Add examples that connect current compiler and factory candidate corpora to resource rows.",
                acceptance_criteria=[
                    "example includes at least one negative control",
                    "example can be rendered from JSON only",
                    "example is covered by CLI smoke tests",
                ],
            ),
            ApplicationRequirement(
                priority="P2",
                name="Interactive application frontend",
                description="Design a future UI after the CLI packet format has stabilized.",
                acceptance_criteria=[
                    "UI consumes the same packet JSON as the CLI",
                    "UI does not introduce new claim semantics",
                ],
            ),
        ],
        success_metrics=[
            "one command can produce a complete evidence packet from versioned JSON inputs",
            "every packet contains at least one explicit non-claim and one next action",
            "full test suite preserves negative-control language",
            "external resource metrics remain source-attributed and optional",
        ],
        open_questions=[
            "Which external compiler/resource oracle should supply the first real metric dataset?",
            "Which candidate ID convention should be shared by compiler, factory, and correlation manifests?",
            "Should packet validation require all referenced source files to exist locally?",
            "Which future UI surface matters most after the CLI packet proves useful?",
        ],
        phased_timeline=[
            "Phase 1: document the workbench PRD and claim gates",
            "Phase 2: add candidate packet schema and Markdown renderer",
            "Phase 3: add example packets joining compiler, factory, circuit, and resource artifacts",
            "Phase 4: evaluate whether a UI, plugin, or simulator bridge is the next best application",
        ],
        claim_boundaries=[
            "does not claim qkernel is a production compiler",
            "does not claim qkernel optimizes T-count or T-depth by itself",
            "does not claim MagicScout motifs are validated magic-state factories",
            "does not claim unsupported circuit manifests are hardware-ready circuits",
            "does not claim external resource correlations are causal",
        ],
    )


def application_prd_dict(prd: ApplicationPRD) -> dict:
    return asdict(prd)


def _list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def application_prd_markdown(prd: ApplicationPRD | dict) -> str:
    data = asdict(prd) if isinstance(prd, ApplicationPRD) else prd
    lines = [
        "# PRD: QKernel Application Workbench",
        "",
        f"Status: {data['status']}",
        "",
        "## Problem Statement",
        "",
        data["problem_statement"],
        "",
        "## Recommended V1",
        "",
        data["recommended_v1"],
        "",
        "## Goals",
        "",
        _list(data["goals"]),
        "",
        "## Non-Goals",
        "",
        _list(data["non_goals"]),
        "",
        "## User Stories",
        "",
        _list(data["user_stories"]),
        "",
        "## Application Options",
        "",
    ]
    for option in data["options"]:
        lines.extend([
            f"### {option['name']}",
            "",
            f"- id: `{option['option_id']}`",
            f"- target user: {option['target_user']}",
            f"- user value: {option['user_value']}",
            f"- implementation risk: {option['implementation_risk']}",
            f"- evidence gate: {option['evidence_gate']}",
            f"- why now: {option['why_now']}",
            "",
        ])
    lines.extend([
        "## Requirements",
        "",
    ])
    for req in data["requirements"]:
        lines.extend([
            f"### {req['priority']}: {req['name']}",
            "",
            req["description"],
            "",
            "Acceptance criteria:",
            "",
            _list(req["acceptance_criteria"]),
            "",
        ])
    lines.extend([
        "## Success Metrics",
        "",
        _list(data["success_metrics"]),
        "",
        "## Open Questions",
        "",
        _list(data["open_questions"]),
        "",
        "## Phased Timeline",
        "",
        _list(data["phased_timeline"]),
        "",
        "## Claim Boundaries",
        "",
        _list(data["claim_boundaries"]),
        "",
    ])
    return "\n".join(lines)


def write_application_prd_markdown(prd: ApplicationPRD | dict, path: str | Path) -> None:
    Path(path).write_text(application_prd_markdown(prd), encoding="utf-8")
