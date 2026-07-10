"""MagicScout factory-template bridge.

This module maps MagicScout reports to conservative protocol-template roles. A
"template" is not a physical factory. It is a checklist for whether a candidate
contextuality motif has enough evidence to be treated as a possible component of
some magic-state-adjacent workflow: witness, verification subroutine, injection
probe, distillation-check motif, or cultivation motif.

The bridge is intentionally asymmetric: it can say "compatible as a research
motif" or "missing required evidence"; it never says "valid factory".
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .metadata import criterion_ledger


@dataclass(frozen=True)
class MagicFactoryTemplate:
    """Conservative template checklist for a MagicScout report."""

    template_id: str
    name: str
    purpose: str
    compatible_targets: list[str]
    requires_contextual: bool = True
    requires_verified: bool = True
    requires_zd_avn: bool | None = None
    max_kernel_weight: int | None = None
    min_minimal_kernels: int | None = None
    requires_backend_certifiable: bool = False
    required_factory_metadata: list[str] = field(default_factory=list)
    claim_scope: str = "diagnostic_template_compatibility"
    not_claimed: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class MagicTemplateAssessment:
    """Result of checking one MagicScout report against one template."""

    protocol_id: str
    target: str
    template_id: str
    template_name: str
    compatible: bool
    template_score: float
    positive_signals: list[str]
    missing_evidence: list[str]
    not_claimed: list[str]
    criterion_ledger: dict


DEFAULT_TEMPLATE_NONCLAIMS = [
    "valid magic-state factory",
    "lower magic-state overhead",
    "distillation threshold",
    "output fidelity bound",
    "acceptance probability guarantee",
    "logical-code-distance guarantee",
    "decoder performance guarantee",
    "space-time-volume advantage",
]


MAGIC_FACTORY_TEMPLATES: list[MagicFactoryTemplate] = [
    MagicFactoryTemplate(
        template_id="contextuality_witness",
        name="Contextuality witness motif",
        purpose="A state-independent contextuality witness usable as a diagnostic or benchmark subroutine.",
        compatible_targets=["generic_non_clifford", "T", "H", "benchmark_zoo_contextuality_resource"],
        requires_contextual=True,
        requires_verified=True,
        requires_zd_avn=None,
        max_kernel_weight=10,
        claim_scope="state-independent contextuality witness motif",
        not_claimed=DEFAULT_TEMPLATE_NONCLAIMS,
    ),
    MagicFactoryTemplate(
        template_id="magic_verification_subroutine",
        name="Magic verification subroutine motif",
        purpose="A contextuality-based verification/check subroutine candidate for a magic-state workflow.",
        compatible_targets=["generic_non_clifford", "T", "H"],
        requires_contextual=True,
        requires_verified=True,
        requires_zd_avn=True,
        max_kernel_weight=10,
        requires_backend_certifiable=False,
        claim_scope="candidate verification subroutine; no fidelity or threshold claim",
        not_claimed=DEFAULT_TEMPLATE_NONCLAIMS,
    ),
    MagicFactoryTemplate(
        template_id="hardware_ready_magic_probe",
        name="Hardware-ready magic probe motif",
        purpose="A candidate motif with a backend model predicting certifiable contextuality under readout assumptions.",
        compatible_targets=["generic_non_clifford", "T", "H"],
        requires_contextual=True,
        requires_verified=True,
        requires_zd_avn=True,
        max_kernel_weight=10,
        requires_backend_certifiable=True,
        claim_scope="backend-planning estimate for a contextuality probe; not measured hardware evidence",
        not_claimed=DEFAULT_TEMPLATE_NONCLAIMS,
    ),
    MagicFactoryTemplate(
        template_id="distillation_check_motif",
        name="Distillation-check motif",
        purpose="A contextuality motif with enough protocol metadata to begin comparing against a distillation/check schedule.",
        compatible_targets=["T", "H", "generic_non_clifford"],
        requires_contextual=True,
        requires_verified=True,
        requires_zd_avn=True,
        max_kernel_weight=20,
        required_factory_metadata=["input_magic_states", "output_magic_states", "acceptance_probability"],
        claim_scope="candidate distillation-check motif; not a distillation protocol proof",
        not_claimed=DEFAULT_TEMPLATE_NONCLAIMS,
    ),
    MagicFactoryTemplate(
        template_id="cultivation_motif",
        name="Cultivation / activation motif",
        purpose="A contextuality motif worth studying as a cultivation or activation subroutine candidate.",
        compatible_targets=["generic_non_clifford", "T", "H", "benchmark_zoo_contextuality_resource"],
        requires_contextual=True,
        requires_verified=True,
        requires_zd_avn=None,
        max_kernel_weight=20,
        min_minimal_kernels=1,
        claim_scope="candidate cultivation/activation motif; no physical resource-freeness claim",
        not_claimed=DEFAULT_TEMPLATE_NONCLAIMS + ["free physical embedding"],
    ),
]


def list_magic_templates() -> list[MagicFactoryTemplate]:
    """Return built-in MagicScout template checklists."""
    return MAGIC_FACTORY_TEMPLATES[:]


def _target_compatible(target: str, compatible_targets: list[str]) -> bool:
    return target in compatible_targets or "generic_non_clifford" in compatible_targets


def _metadata_present(value: Any) -> bool:
    return value is not None and value != "" and value != [] and value != {}


def assess_magic_template(report: Any, template: MagicFactoryTemplate) -> MagicTemplateAssessment:
    """Assess a MagicScout report against one conservative factory template."""
    missing: list[str] = []
    positive: list[str] = []
    score = 0.0

    if _target_compatible(report.target, template.compatible_targets):
        positive.append(f"target {report.target!r} compatible with template")
        score += 0.10
    else:
        missing.append(f"target {report.target!r} not listed for template")

    if template.requires_contextual:
        if report.contextual:
            positive.append("odd-Q contextuality present")
            score += 0.20
        else:
            missing.append("requires odd-Q contextuality")

    if template.requires_verified:
        if report.verified:
            positive.append("independent kernel verification passed")
            score += 0.15
        else:
            missing.append("requires independent kernel verification")

    if template.requires_zd_avn is True:
        if report.zd_avn_contextual is True:
            positive.append("stronger Z_d/AvN verifier passed")
            score += 0.15
        else:
            missing.append("requires stronger Z_d/AvN verifier to pass")
    elif template.requires_zd_avn is False and report.zd_avn_contextual is False:
        positive.append("template accepts odd-Q-only scope")
        score += 0.05

    if template.max_kernel_weight is not None:
        if report.kernel_weight is not None and report.kernel_weight <= template.max_kernel_weight:
            positive.append(f"kernel weight {report.kernel_weight} within template bound {template.max_kernel_weight}")
            score += 0.15
        else:
            missing.append(f"requires kernel weight <= {template.max_kernel_weight}")

    if template.min_minimal_kernels is not None:
        if report.n_minimal_kernels is not None and report.n_minimal_kernels >= template.min_minimal_kernels:
            positive.append(f"minimal-kernel count {report.n_minimal_kernels} meets template requirement")
            score += 0.10
        else:
            missing.append(f"requires at least {template.min_minimal_kernels} minimal kernel(s)")

    if template.requires_backend_certifiable:
        be = report.backend_estimate
        if be is not None and be.certifiable is True:
            positive.append("backend estimate predicts certifiability")
            score += 0.15
        else:
            missing.append("requires backend estimate with certifiable=True")

    metadata = dict(getattr(report, "factory_metadata", {}) or {})
    for field_name in template.required_factory_metadata:
        if _metadata_present(metadata.get(field_name)):
            positive.append(f"factory metadata field present: {field_name}")
            score += 0.05
        else:
            missing.append(f"missing factory metadata field: {field_name}")

    compatible = len(missing) == 0
    ledger = criterion_ledger(
        criterion_id="odd_Q_even_d_v1",
        verifier_used="MagicScout template checklist over an already-generated MagicScout report",
        claim_scope=template.claim_scope,
        stronger_verifier_available="zd_avn_valuation_v1",
        stronger_verifier_passed=getattr(report, "zd_avn_contextual", None),
    )

    return MagicTemplateAssessment(
        protocol_id=report.protocol_id,
        target=report.target,
        template_id=template.template_id,
        template_name=template.name,
        compatible=compatible,
        template_score=round(min(score, 1.0), 3),
        positive_signals=positive,
        missing_evidence=missing,
        not_claimed=template.not_claimed or DEFAULT_TEMPLATE_NONCLAIMS,
        criterion_ledger=ledger,
    )


def assess_magic_templates(
    report: Any,
    *,
    template_ids: list[str] | None = None,
) -> list[MagicTemplateAssessment]:
    """Assess a MagicScout report against selected or all built-in templates."""
    templates = list_magic_templates()
    if template_ids is not None:
        wanted = set(template_ids)
        templates = [t for t in templates if t.template_id in wanted]
        missing = wanted - {t.template_id for t in templates}
        if missing:
            raise ValueError(f"unknown MagicScout template id(s): {sorted(missing)}")
    assessments = [assess_magic_template(report, template) for template in templates]
    assessments.sort(key=lambda a: (not a.compatible, -a.template_score, a.template_id))
    return assessments


def magic_template_assessments_dict(assessments: list[MagicTemplateAssessment]) -> dict:
    return {
        "assessments": [asdict(a) for a in assessments],
        "count": len(assessments),
        "compatible_count": sum(1 for a in assessments if a.compatible),
    }


def magic_templates_catalog_dict() -> dict:
    return {
        "templates": [asdict(t) for t in list_magic_templates()],
        "count": len(MAGIC_FACTORY_TEMPLATES),
        "claim_scope": "template compatibility only; no factory-performance claim",
    }
