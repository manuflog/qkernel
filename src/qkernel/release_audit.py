from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path

from .adapters.qiskit_lite import load_qiskit_lite_program
from .application_packet import application_evidence_packet, application_evidence_packet_dict
from .compiler import compare_compiler_pass
from .examples import peres_mermin_program
from .fiber_lift import find_even_base_fiber_lift
from .lift_pipeline import run_lift_pipeline
from .metadata import QKERNEL_VERSION
from .optimizer import compress_min_odd_q
from .rewrite_policy import assess_rewrite_candidate
from .tower import tower_law_report
from .valuation import check_zd_valuation
from .verify import verify_kernel


@dataclass(frozen=True)
class AuditCheck:
    id: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class ReleaseAuditReport:
    version: str
    passed: bool
    checks: list[AuditCheck]
    safe_positioning: str
    unsafe_positioning: list[str]
    public_repo_recommendation: str


def _check_file_exists(root: Path, rel: str) -> AuditCheck:
    path = root / rel
    return AuditCheck(
        id=f"file:{rel}",
        passed=path.exists(),
        detail="present" if path.exists() else "missing",
    )


def _contains_all(path: Path, needles: list[str]) -> bool:
    text = path.read_text(encoding="utf-8")
    return all(needle in text for needle in needles)


def run_release_audit(root: str | Path | None = None) -> ReleaseAuditReport:
    """Run Q-Kernel's release/readiness audit.

    This audit checks the key safety-critical invariants without relying on
    subprocess execution. It is complementary to the full pytest suite.
    """
    repo_root = Path(root) if root is not None else Path(__file__).resolve().parents[2]
    checks: list[AuditCheck] = []

    # Required public/research repo files.
    required_files = [
        "README.md",
        "LICENSE",
        "CITATION.cff",
        "CHANGELOG.md",
        "paper/qkernel_note.pdf",
        "docs/ZD_VALUATION_VERIFICATION.md",
        "docs/TOWER_LAW.md",
        "docs/FIBER_LIFT.md",
        "docs/LIFT_PIPELINE.md",
        "docs/REWRITE_POLICY.md",
        "docs/NOVELTY_HYGIENE.md",
        "docs/COMPILER_OPTIMIZER_PATH.md",
        "docs/RELEASE_READINESS.md",
        "docs/ADJACENT_REPO_DECISION.md",
        "docs/RESEARCH_PLAN.md",
        "docs/APPLICATION_PACKET.md",
        "docs/IMPACT_REGISTER.md",
        "docs/PRD_APPLICATION_WORKBENCH.md",
        "examples/application_packet_demo.json",
        "examples/resource_feature_pm_probe.json",
        "examples/circuit_manifest_d4_probe.json",
        "src/qkernel/application_packet.py",
    ]
    checks.extend(_check_file_exists(repo_root, rel) for rel in required_files)

    # Core PM certificate must be odd-Q and genuine Z_d contextual.
    pm = peres_mermin_program()
    pm_kernel = compress_min_odd_q(pm)
    pm_verification = verify_kernel(pm, pm_kernel)
    checks.append(
        AuditCheck(
            id="core:pm_kernel_verified",
            passed=pm_verification.valid and pm_verification.zd_contextual is True,
            detail=pm_verification.reason,
        )
    )

    pm_zd = check_zd_valuation(pm)
    checks.append(
        AuditCheck(
            id="core:pm_zd_unsat",
            passed=pm_zd.contextual and pm_zd.solvable is False,
            detail=pm_zd.reason,
        )
    )

    # Rewrite policy must block resource claims.
    forbidden = assess_rewrite_candidate("forbidden_resource_claim")
    safe_prune = assess_rewrite_candidate("safe_diagnostic_prune")
    checks.append(
        AuditCheck(
            id="policy:forbidden_resource_claim_blocked",
            passed=not forbidden.allowed_to_report and not forbidden.allowed_to_apply,
            detail=forbidden.allowed_claim,
        )
    )
    checks.append(
        AuditCheck(
            id="policy:safe_prune_reportable_not_applicable",
            passed=safe_prune.allowed_to_report and not safe_prune.allowed_to_apply,
            detail=safe_prune.allowed_claim,
        )
    )

    # Compiler playground must remain diagnostic-only.
    before = load_qiskit_lite_program(repo_root / "examples/compiler_before_qiskit_lite.json")
    after = load_qiskit_lite_program(repo_root / "examples/compiler_after_qiskit_lite.json")
    comparison = compare_compiler_pass(before, after)
    checks.append(
        AuditCheck(
            id="compiler:playground_requires_semantic_proof",
            passed=(
                comparison.requires_semantic_equivalence_proof
                and comparison.allowed_to_report
                and not comparison.allowed_to_apply
            ),
            detail=comparison.verdict,
        )
    )

    # Fiber-lift and tower pipeline.
    base_lift_program = repo_root / "examples/tower_pair_d2_base.json"
    if base_lift_program.exists():
        from .io import load_program

        base = load_program(base_lift_program)
        fiber = find_even_base_fiber_lift(base)
        checks.append(
            AuditCheck(
                id="tower:fiber_lift_constructed",
                passed=fiber.constructed and fiber.program is not None and fiber.zd_contextual is True,
                detail=fiber.reason,
            )
        )

        if fiber.program is not None:
            tower = tower_law_report(fiber.program, [1, 1], base_d=base.d)
            checks.append(
                AuditCheck(
                    id="tower:closed_formula_certified",
                    passed=tower.certified and tower.generativity_bit == 0 and tower.zd_contextual is True,
                    detail=tower.reason,
                )
            )

        pipeline = run_lift_pipeline(base)
        checks.append(
            AuditCheck(
                id="tower:pipeline_report_complete",
                passed=(
                    pipeline.constructed
                    and pipeline.zd_valuation is not None
                    and pipeline.tower_law is not None
                    and "resource advantage" in " ".join(pipeline.unsafe_claims)
                ),
                detail=pipeline.safe_claim,
            )
        )

    # Novelty hygiene files must cite finite-geometry prior art and boundaries.
    bib = repo_root / "paper" / "references.bib"
    novelty = repo_root / "docs" / "NOVELTY_HYGIENE.md"
    if bib.exists():
        checks.append(
            AuditCheck(
                id="novelty:finite_geometry_refs_in_bib",
                passed=_contains_all(
                    bib,
                    [
                        "deBoutrayHolweckGiorgettiMassonSaniga2022",
                        "MullerSanigaGiorgettiDeBoutrayHolweck2023",
                    ],
                ),
                detail="finite-geometry prior-art BibTeX keys present",
            )
        )
    if novelty.exists():
        checks.append(
            AuditCheck(
                id="novelty:linear_system_not_claimed",
                passed=_contains_all(
                    novelty,
                    [
                        "Do not claim novelty",
                        "GF(2)",
                        "binary symplectic polar-space",
                    ],
                ),
                detail="novelty hygiene document states non-novel parts",
            )
        )

    packet_path = repo_root / "examples" / "application_packet_demo.json"
    if packet_path.exists():
        packet = application_evidence_packet(packet_path)
        packet_data = application_evidence_packet_dict(packet)
        summary = packet_data["summary"]
        sources = {source["source_id"]: source for source in packet_data["sources"]}
        checks.append(
            AuditCheck(
                id="workbench:packet_claim_gates_blocked",
                passed=(
                    summary["ready_for_claims"] is False
                    and summary["uncovered_tracked_candidates"] == []
                    and sources["compiler_demo"]["claim_gate_status"] == "blocked"
                    and sources["factory_demo"]["claim_gate_status"] == "blocked"
                    and sources["resource_feature_demo"]["claim_gate_status"] == "blocked"
                    and sources["circuit_manifest_demo"]["claim_gate_status"] == "blocked"
                ),
                detail="demo evidence packet preserves blocked claim gates without uncovered candidates",
            )
        )
        checks.append(
            AuditCheck(
                id="workbench:packet_all_source_families_present",
                passed={
                    "compiler_candidate_corpus",
                    "factory_candidate_corpus",
                    "correlation_study",
                    "resource_feature_json",
                    "circuit_manifest_json",
                }.issubset({source["source_type"] for source in packet_data["sources"]}),
                detail="demo packet covers compiler, factory, correlation, resource, and circuit evidence",
            )
        )

    passed = all(check.passed for check in checks)

    return ReleaseAuditReport(
        version=QKERNEL_VERSION,
        passed=passed,
        checks=checks,
        safe_positioning=(
            "Q-Kernel is a research tool for extracting, verifying, and reporting "
            "odd-Q / Z_d contextuality kernels in Weyl/Pauli measurement programs."
        ),
        unsafe_positioning=[
            "not a magic-state optimizer",
            "not a T-count optimizer",
            "not a certified tower-compression optimizer",
            "not proof that passive embedding is free",
            "not a compiler semantic-equivalence engine",
            "not an application packet that upgrades missing evidence into resource or factory claims",
        ],
        public_repo_recommendation=(
            "ready for private/public-review repository; keep alpha label and conservative README positioning"
            if passed
            else "not ready; fix failed audit checks first"
        ),
    )


def release_audit_dict(report: ReleaseAuditReport) -> dict:
    return {
        "version": report.version,
        "passed": report.passed,
        "checks": [asdict(check) for check in report.checks],
        "safe_positioning": report.safe_positioning,
        "unsafe_positioning": report.unsafe_positioning,
        "public_repo_recommendation": report.public_repo_recommendation,
    }


def release_audit_markdown(report: ReleaseAuditReport) -> str:
    lines = [
        "# Q-Kernel Release Audit",
        "",
        f"- version: `{report.version}`",
        f"- passed: `{report.passed}`",
        f"- recommendation: {report.public_repo_recommendation}",
        "",
        "## Safe positioning",
        "",
        report.safe_positioning,
        "",
        "## Unsafe positioning",
        "",
    ]

    for item in report.unsafe_positioning:
        lines.append(f"- {item}")

    lines.extend(["", "## Checks", ""])

    for check in report.checks:
        mark = "PASS" if check.passed else "FAIL"
        lines.append(f"- `{mark}` `{check.id}` — {check.detail}")

    return "\n".join(lines) + "\n"


def write_release_audit_outputs(
    report: ReleaseAuditReport,
    *,
    json_path: str | Path | None = None,
    markdown_path: str | Path | None = None,
) -> None:
    if json_path is not None:
        json_out = Path(json_path)
        json_out.parent.mkdir(parents=True, exist_ok=True)
        json_out.write_text(json.dumps(release_audit_dict(report), indent=2) + "\n", encoding="utf-8")

    if markdown_path is not None:
        markdown_out = Path(markdown_path)
        markdown_out.parent.mkdir(parents=True, exist_ok=True)
        markdown_out.write_text(release_audit_markdown(report), encoding="utf-8")
