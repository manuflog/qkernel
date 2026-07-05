from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Literal

from .analyzer import analyze
from .certificate import kernel_to_dict
from .decompose import component_summary
from .ir import WeylProgram
from .optimizer import compress_min_odd_q
from .verify import verify_kernel
from .rewrite_policy import assess_rewrite_candidate


OptimizationClaim = Literal[
    "diagnostic_only",
    "candidate_pass_requires_semantic_equivalence",
]


@dataclass(frozen=True)
class CompilerDiagnosticReport:
    """Compiler-facing diagnostic report.

    This is not a resource optimizer. It packages Q-Kernel's certified facts in
    a form a compiler pass can consume.
    """

    contextual: bool
    reason: str
    contexts: int
    observables: int
    components: int
    kernel_contexts: int | None
    kernel_observables: int | None
    q_value: int | None
    verified: bool
    compression_ratio_contexts: float | None
    compression_ratio_observables: float | None
    optimization_claim: OptimizationClaim
    safe_use: list[str]
    unsafe_use: list[str]


@dataclass(frozen=True)
class CompilerPassComparison:
    """Compare two measurement programs under Q-Kernel diagnostics.

    This does not certify that `after` preserves the semantics of `before`.
    A real compiler optimization must supply that proof separately.
    """

    before: CompilerDiagnosticReport
    after: CompilerDiagnosticReport
    kernel_context_delta: int | None
    observable_delta: int
    context_delta: int
    requires_semantic_equivalence_proof: bool
    verdict: str
    rewrite_policy_id: str
    rewrite_policy_status: str
    allowed_to_report: bool
    allowed_to_apply: bool


def compiler_report(program: WeylProgram) -> CompilerDiagnosticReport:
    analysis = analyze(program)
    components = component_summary(program)

    kernel_contexts: int | None = None
    kernel_observables: int | None = None
    verified = False
    compression_ratio_contexts: float | None = None
    compression_ratio_observables: float | None = None

    if analysis.contextual:
        kernel = compress_min_odd_q(program)
        verification = verify_kernel(program, kernel)
        verified = verification.valid
        kernel_contexts = kernel.compressed_contexts
        kernel_observables = kernel.compressed_observables
        compression_ratio_contexts = kernel.compression_ratio_contexts
        compression_ratio_observables = kernel.compression_ratio_observables

    return CompilerDiagnosticReport(
        contextual=analysis.contextual,
        reason=analysis.reason,
        contexts=len(program.contexts),
        observables=len(program.observables),
        components=len(components),
        kernel_contexts=kernel_contexts,
        kernel_observables=kernel_observables,
        q_value=analysis.q_value,
        verified=verified,
        compression_ratio_contexts=compression_ratio_contexts,
        compression_ratio_observables=compression_ratio_observables,
        optimization_claim="diagnostic_only",
        safe_use=[
            "identify a small odd-Q contextuality kernel",
            "separate irrelevant disconnected components when semantics allow",
            "compare candidate compiler rewrites using verified certificates",
            "produce audit artifacts for contextuality-preserving transformations",
        ],
        unsafe_use=[
            "claim reduced T-count or magic cost without a separate bridge theorem",
            "treat kernel compression as semantic circuit optimization",
            "drop measurements without an external semantic-equivalence proof",
            "treat contextuality fraction as an additive resource gauge",
        ],
    )


def compiler_report_dict(program: WeylProgram) -> dict:
    return asdict(compiler_report(program))


def compare_compiler_pass(before: WeylProgram, after: WeylProgram) -> CompilerPassComparison:
    """Compare before/after programs as candidate compiler-pass diagnostics.

    The verdict is deliberately conservative. Q-Kernel can say a rewrite looks
    better or worse under odd-Q kernel metrics, but cannot certify the rewrite
    preserves circuit semantics.
    """
    b = compiler_report(before)
    a = compiler_report(after)

    if b.kernel_contexts is None or a.kernel_contexts is None:
        kernel_delta = None
    else:
        kernel_delta = a.kernel_contexts - b.kernel_contexts

    context_delta = a.contexts - b.contexts
    observable_delta = a.observables - b.observables

    if not b.contextual and a.contextual:
        verdict = "after introduces an odd-Q obstruction under this criterion; investigate."
    elif b.contextual and not a.contextual:
        verdict = "after removes the detected odd-Q obstruction; valid only if a separate semantic-equivalence proof exists."
    elif kernel_delta is not None and kernel_delta < 0:
        verdict = "after has a smaller odd-Q kernel; this is a promising diagnostic, not a certified resource improvement."
    elif kernel_delta is not None and kernel_delta > 0:
        verdict = "after has a larger odd-Q kernel under this diagnostic."
    elif b.contextual and a.contextual and kernel_delta == 0 and (context_delta < 0 or observable_delta < 0):
        verdict = (
            "after removes nonkernel contexts/observables while preserving the detected odd-Q kernel size; "
            "this is a promising pruning diagnostic, not a semantic optimization proof."
        )
    else:
        verdict = "no certified odd-Q kernel improvement detected."

    policy = assess_rewrite_candidate("safe_diagnostic_prune")

    return CompilerPassComparison(
        before=b,
        after=a,
        kernel_context_delta=kernel_delta,
        observable_delta=observable_delta,
        context_delta=context_delta,
        requires_semantic_equivalence_proof=True,
        verdict=verdict,
        rewrite_policy_id=policy.policy_id,
        rewrite_policy_status=policy.status,
        allowed_to_report=policy.allowed_to_report,
        allowed_to_apply=policy.allowed_to_apply,
    )


def compare_compiler_pass_dict(before: WeylProgram, after: WeylProgram) -> dict:
    return asdict(compare_compiler_pass(before, after))
