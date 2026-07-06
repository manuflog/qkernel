from __future__ import annotations

from dataclasses import asdict, dataclass

from .analyzer import analyze
from .certificate import kernel_to_dict
from .decompose import component_summary
from .incidence import build_incidence
from .ir import WeylProgram
from .metadata import criterion_ledger
from .optimizer import compress_min_odd_q
from .subroutine import analyze_contextuality
from .verify import verify_kernel


SCHEMA_VERSION = "qkernel.resource_features.v1"


@dataclass(frozen=True)
class ResourceFeatureReport:
    """Conservative feature vector for external resource-estimation studies.

    This report is intentionally not a resource estimate. It exports verified
    contextuality/kernel features that an external oracle can correlate with
    T-count, magic injections, stabilizer rank, depth, or backend costs.
    """

    schema: str
    contextual: bool
    modulus: int
    qudits: int
    contexts: int
    observables: int
    components: int
    cycle_basis_dimension: int
    odd_carry_contexts: int
    kernel_contexts: int | None
    kernel_observables: int | None
    kernel_context_fraction: float | None
    kernel_observable_fraction: float | None
    obstruction_value: int | None
    n_minimal_kernels: int | None
    verified: bool
    zd_avn_contextual: bool | None
    candidate_features: dict
    required_external_oracles: list[str]
    safe_use: list[str]
    unsafe_claims: list[str]
    criterion_ledger: dict


def _fraction(part: int | None, whole: int) -> float | None:
    if part is None or whole == 0:
        return None
    return part / whole


def resource_feature_report(
    program: WeylProgram,
    *,
    enumerate_all_kernels: bool = False,
    certify_minimal: bool = False,
    include_certificate_features: bool = False,
) -> ResourceFeatureReport:
    """Return a resource-estimator-facing feature vector.

    The result deliberately stops at feature export. It does not infer T-count,
    magic overhead, depth, stabilizer rank, or backend resource advantage.
    """
    analysis = analyze(program)
    components = component_summary(program)
    A, _ = build_incidence(program)
    sub = analyze_contextuality(
        program,
        verify=True,
        enumerate_all_kernels=enumerate_all_kernels,
        certify_minimal=certify_minimal,
    )

    kernel_contexts: int | None = None
    kernel_observables: int | None = None
    zd_avn_contextual: bool | None = None
    verified = sub.verified
    certificate_features: dict = {}

    if analysis.contextual:
        kernel = compress_min_odd_q(program)
        verification = verify_kernel(program, kernel)
        verified = verification.valid
        zd_avn_contextual = verification.zd_contextual
        kernel_contexts = kernel.compressed_contexts
        kernel_observables = kernel.compressed_observables
        if include_certificate_features:
            cert = kernel_to_dict(program, kernel)
            certificate_features = {
                "program_sha256": cert["program_sha256"],
                "selected_contexts": cert["kernel"]["selected_contexts"],
                "selected_observables": cert["kernel"]["selected_observables"],
                "q_value": cert["kernel"]["q_value"],
            }

    ledger = criterion_ledger(
        criterion_id="odd_Q_even_d_v1",
        verifier_used="analyze_contextuality + verify_kernel; resource_features is feature export only",
        claim_scope="resource-estimator feature export; not a T-count, magic-overhead, depth, or backend-cost estimate",
        stronger_verifier_available="zd_avn_valuation_v1",
        stronger_verifier_passed=zd_avn_contextual,
    )

    candidate_features = {
        "context_count": len(program.contexts),
        "observable_count": len(program.observables),
        "component_count": len(components),
        "cycle_basis_dimension": len(analysis.cycle_basis),
        "odd_carry_context_count": sum(analysis.b_vector),
        "kernel_context_count": kernel_contexts,
        "kernel_observable_count": kernel_observables,
        "kernel_context_fraction": _fraction(kernel_contexts, len(program.contexts)),
        "kernel_observable_fraction": _fraction(kernel_observables, len(program.observables)),
        "obstruction_value": sub.obstruction_value,
        "n_minimal_kernels": sub.n_minimal_kernels,
        "incidence_rows": len(A),
        "incidence_cols": len(A[0]) if A else 0,
    }
    if certificate_features:
        candidate_features["certificate"] = certificate_features

    return ResourceFeatureReport(
        schema=SCHEMA_VERSION,
        contextual=analysis.contextual,
        modulus=program.d,
        qudits=program.m,
        contexts=len(program.contexts),
        observables=len(program.observables),
        components=len(components),
        cycle_basis_dimension=len(analysis.cycle_basis),
        odd_carry_contexts=sum(analysis.b_vector),
        kernel_contexts=kernel_contexts,
        kernel_observables=kernel_observables,
        kernel_context_fraction=_fraction(kernel_contexts, len(program.contexts)),
        kernel_observable_fraction=_fraction(kernel_observables, len(program.observables)),
        obstruction_value=sub.obstruction_value,
        n_minimal_kernels=sub.n_minimal_kernels,
        verified=verified,
        zd_avn_contextual=zd_avn_contextual,
        candidate_features=candidate_features,
        required_external_oracles=[
            "semantic-equivalence proof for any compiler rewrite",
            "validated T-count/T-depth or magic-injection oracle",
            "stabilizer-rank or simulator-cost oracle when claimed",
            "backend-specific hardware cost model for architecture claims",
        ],
        safe_use=[
            "export contextuality/kernel features for correlation studies",
            "compare candidate programs under a verified odd-Q diagnostic",
            "feed an external resource oracle with explicit claim boundaries",
        ],
        unsafe_claims=[
            "Q-Kernel predicts T-count",
            "Q-Kernel predicts magic-state overhead",
            "kernel compression is a resource monotone",
            "contextuality fraction is an additive resource gauge",
            "a smaller kernel proves a semantics-preserving compiler optimization",
            "this feature vector proves backend resource advantage",
        ],
        criterion_ledger=ledger,
    )


def resource_feature_report_dict(
    program: WeylProgram,
    *,
    enumerate_all_kernels: bool = False,
    certify_minimal: bool = False,
    include_certificate_features: bool = False,
) -> dict:
    return asdict(resource_feature_report(
        program,
        enumerate_all_kernels=enumerate_all_kernels,
        certify_minimal=certify_minimal,
        include_certificate_features=include_certificate_features,
    ))
