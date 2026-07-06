"""Contextuality as a composable subroutine.

qkernel's value in a larger quantum-compilation / resource-estimation / experiment-
design pipeline is not as a monolithic solver but as a *subroutine* it calls: given a
measurement program, return the contextuality verdict, the cheapest certificate, and a
resource quantification, in one stable-contract call. This module is that entry point;
it composes the analyzer, the min-odd-cycle solvers, the verifier, and (optionally) the
all-kernels enumerator, the CP-SAT optimality certifier, and the obstruction value.

This is a classical analysis subroutine (no quantum speedup is claimed); the point is
composability -- it is designed to be dropped into a classical control loop that a
quantum compiler or resource estimator runs.
"""
from __future__ import annotations

from dataclasses import dataclass

from .analyzer import analyze
from .metadata import criterion_ledger
from .ir import WeylProgram
from .optimizer import compress_min_odd_q
from .solvers import find_min_odd_cycle, find_all_min_odd_cycles, hamming_weight
from .verify import verify_kernel


@dataclass
class ContextualitySubroutineResult:
    contextual: bool
    min_kernel_contexts: list[int] | None   # indices of the cheapest contextuality test
    kernel_weight: int | None               # number of contexts in that test
    verified: bool                          # kernel re-checked independently
    certified_minimal: bool | None          # CP-SAT proved minimality (None if not requested)
    n_minimal_kernels: int | None           # count of distinct cheapest tests (None if not requested)
    obstruction_value: int | None           # resource value d/2 for even d (0 if non-contextual)
    modulus: int
    reason: str
    criterion_ledger: dict | None = None


def analyze_contextuality(
    program: WeylProgram,
    *,
    verify: bool = True,
    enumerate_all_kernels: bool = False,
    certify_minimal: bool = False,
    max_cycle_dim_enumerate: int = 20,
) -> ContextualitySubroutineResult:
    """One-call contextuality subroutine.

    - decision: is the family contextual (odd-Q)?
    - certificate: the minimal contextuality kernel (cheapest test) and its size;
    - verification: the kernel re-checked independently (``verify=True``);
    - structure (opt): the number of distinct minimal kernels (``enumerate_all_kernels``);
    - certified minimality (opt): CP-SAT proof that the kernel is truly minimal
      (``certify_minimal``, needs OR-Tools);
    - resource value: the obstruction value ``d/2`` for even ``d`` when contextual, else 0.
    """
    result = analyze(program)
    d = program.d

    if not result.contextual:
        return ContextualitySubroutineResult(
            contextual=False,
            min_kernel_contexts=None,
            kernel_weight=None,
            verified=True,
            certified_minimal=None,
            n_minimal_kernels=0 if enumerate_all_kernels else None,
            obstruction_value=0,
            modulus=d,
            reason="non-contextual: no odd-Q obstruction",
            criterion_ledger=criterion_ledger(
                criterion_id="odd_Q_even_d_v1",
                verifier_used="analyze (odd-Q cycle obstruction)",
                claim_scope="state_independent_parity_obstruction",
                stronger_verifier_available="zd_avn_valuation_v1",
                stronger_verifier_passed=None,
            ),
        )

    lam = find_min_odd_cycle(program)
    selected = [i for i, bit in enumerate(lam) if bit] if lam else None
    weight = hamming_weight(lam) if lam else None

    verified = True
    zd_passed: bool | None = None
    if verify and lam is not None:
        kernel = compress_min_odd_q(program)
        vr = verify_kernel(program, kernel)
        verified = vr.valid
        zd_passed = vr.zd_contextual

    certified_minimal: bool | None = None
    if certify_minimal:
        from .solvers_milp import find_min_odd_cycle_cpsat

        cyc, certified = find_min_odd_cycle_cpsat(program)
        certified_minimal = bool(certified and cyc is not None
                                 and hamming_weight(cyc) == weight)

    n_minimal: int | None = None
    if enumerate_all_kernels:
        try:
            n_minimal = len(find_all_min_odd_cycles(program, max_cycle_dim=max_cycle_dim_enumerate))
        except ValueError:
            n_minimal = None  # cycle space too large to enumerate all

    obstruction_value = d // 2 if d % 2 == 0 else None

    return ContextualitySubroutineResult(
        contextual=True,
        min_kernel_contexts=selected,
        kernel_weight=weight,
        verified=verified,
        certified_minimal=certified_minimal,
        n_minimal_kernels=n_minimal,
        obstruction_value=obstruction_value,
        modulus=d,
        reason="contextual: minimal odd-Q kernel found",
        criterion_ledger=criterion_ledger(
            criterion_id="odd_Q_even_d_v1",
            verifier_used=("verify_kernel (independent odd-Q re-check + Z_d/AvN valuation)"
                           if verify else "find_min_odd_cycle (odd-Q, unverified)"),
            claim_scope="state_independent_parity_obstruction; minimal contextuality kernel",
            stronger_verifier_available="zd_avn_valuation_v1",
            stronger_verifier_passed=zd_passed,
        ),
    )
