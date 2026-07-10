from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal


RewritePolicyId = Literal[
    "safe_diagnostic_prune",
    "requires_external_semantics",
    "experimental_resource_probe",
    "forbidden_resource_claim",
]


@dataclass(frozen=True)
class RewritePolicy:
    id: RewritePolicyId
    name: str
    status: Literal["allowed", "requires_proof", "experimental", "forbidden"]
    description: str
    required_evidence: list[str]
    forbidden_claims: list[str]


@dataclass(frozen=True)
class RewriteCandidateAssessment:
    policy_id: RewritePolicyId
    status: str
    allowed_to_report: bool
    allowed_to_apply: bool
    requires_semantic_equivalence_proof: bool
    allowed_claim: str
    forbidden_claims: list[str]
    required_evidence: list[str]


_POLICIES: dict[RewritePolicyId, RewritePolicy] = {
    "safe_diagnostic_prune": RewritePolicy(
        id="safe_diagnostic_prune",
        name="Safe diagnostic pruning report",
        status="requires_proof",
        description=(
            "A candidate rewrite removes contexts/observables that are outside the "
            "verified odd-Q kernel. Q-Kernel may report this as a diagnostic pruning "
            "opportunity, but applying it in a compiler still requires external "
            "semantic-equivalence proof."
        ),
        required_evidence=[
            "verified odd-Q kernel before",
            "verified odd-Q kernel after",
            "kernel preserved or intentionally changed",
            "external proof that removed measurements/contexts are semantically irrelevant",
        ],
        forbidden_claims=[
            "resource optimization is certified",
            "T-count is reduced",
            "magic cost is reduced",
            "measurements can be dropped unconditionally",
        ],
    ),
    "requires_external_semantics": RewritePolicy(
        id="requires_external_semantics",
        name="Candidate rewrite requiring external semantics",
        status="requires_proof",
        description=(
            "A candidate rewrite changes the diagnostic program in a way Q-Kernel can "
            "compare but not validate semantically."
        ),
        required_evidence=[
            "before/after Q-Kernel diagnostic report",
            "external circuit or measurement-semantics equivalence proof",
            "backend-specific cost model if resource claims are made",
        ],
        forbidden_claims=[
            "Q-Kernel proves the rewrite is legal",
            "Q-Kernel proves resource improvement",
        ],
    ),
    "experimental_resource_probe": RewritePolicy(
        id="experimental_resource_probe",
        name="Experimental resource-correlation probe",
        status="experimental",
        description=(
            "A study comparing Q-Kernel metrics against resource metrics such as T-count, "
            "magic injections, or stabilizer rank. This is exploratory until a theorem "
            "or validated empirical model exists."
        ),
        required_evidence=[
            "dataset definition",
            "resource metric definition",
            "statistical protocol",
            "negative controls",
            "statement that correlation is not theorem",
        ],
        forbidden_claims=[
            "odd-Q kernel size is a resource monotone",
            "correlation proves optimization",
            "contextuality fraction is additive fuel",
        ],
    ),
    "forbidden_resource_claim": RewritePolicy(
        id="forbidden_resource_claim",
        name="Forbidden resource claim",
        status="forbidden",
        description=(
            "Any claim that Q-Kernel alone certifies T-count, magic-state, hardware, "
            "tower/doubling, or embedding-resource advantage."
        ),
        required_evidence=[],
        forbidden_claims=[
            "Q-Kernel reduces T-count",
            "Q-Kernel optimizes magic states",
            "passive embedding is free",
            "tower compression is certified",
            "contextuality fraction is an additive resource gauge",
        ],
    ),
}


def list_rewrite_policies() -> list[RewritePolicy]:
    return list(_POLICIES.values())


def get_rewrite_policy(policy_id: RewritePolicyId) -> RewritePolicy:
    return _POLICIES[policy_id]


def assess_rewrite_candidate(policy_id: RewritePolicyId) -> RewriteCandidateAssessment:
    policy = get_rewrite_policy(policy_id)

    if policy.status == "allowed":
        allowed_to_report = True
        allowed_to_apply = True
        requires_semantic_equivalence_proof = False
        allowed_claim = "certified under Q-Kernel policy"
    elif policy.status == "requires_proof":
        allowed_to_report = True
        allowed_to_apply = False
        requires_semantic_equivalence_proof = True
        allowed_claim = "diagnostic only until external semantic-equivalence proof is supplied"
    elif policy.status == "experimental":
        allowed_to_report = True
        allowed_to_apply = False
        requires_semantic_equivalence_proof = True
        allowed_claim = "experimental correlation/probe only; not a compiler optimization claim"
    else:
        allowed_to_report = False
        allowed_to_apply = False
        requires_semantic_equivalence_proof = True
        allowed_claim = "forbidden claim; do not report as Q-Kernel result"

    return RewriteCandidateAssessment(
        policy_id=policy.id,
        status=policy.status,
        allowed_to_report=allowed_to_report,
        allowed_to_apply=allowed_to_apply,
        requires_semantic_equivalence_proof=requires_semantic_equivalence_proof,
        allowed_claim=allowed_claim,
        forbidden_claims=policy.forbidden_claims,
        required_evidence=policy.required_evidence,
    )


def list_rewrite_policies_dict() -> list[dict]:
    return [asdict(policy) for policy in list_rewrite_policies()]


def assess_rewrite_candidate_dict(policy_id: RewritePolicyId) -> dict:
    return asdict(assess_rewrite_candidate(policy_id))
