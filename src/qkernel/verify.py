from __future__ import annotations

from dataclasses import dataclass

from .analyzer import q_of_cycle
from .incidence import build_incidence
from .ir import KernelResult, WeylProgram
from .validate import validate_program
from .valuation import check_kernel_zd_valuation


@dataclass(frozen=True)
class VerificationResult:
    valid: bool
    reason: str
    lambda_vector: list[int]
    q_value: int | None
    zd_contextual: bool | None = None
    zd_reason: str | None = None


def verify_kernel(program: WeylProgram, kernel: KernelResult) -> VerificationResult:
    """Verify a contextual kernel certificate.

    This is intentionally independent of the optimizer. A future solver may be
    heuristic or external; verification should remain cheap and exact.
    """
    validate_program(program)

    if not kernel.contextual:
        return VerificationResult(
            valid=False,
            reason="kernel result is noncontextual; no odd-Q certificate to verify",
            lambda_vector=[],
            q_value=None,
        )

    n = len(program.contexts)
    lam = [0] * n

    for idx in kernel.selected_contexts:
        if idx < 0 or idx >= n:
            return VerificationResult(
                valid=False,
                reason=f"context index out of range: {idx}",
                lambda_vector=lam,
                q_value=None,
            )
        lam[idx] ^= 1

    A, names = build_incidence(program)

    # Check A^T lambda = 0.
    for col, name in enumerate(names):
        parity = 0
        for row_idx, bit in enumerate(lam):
            if bit:
                parity ^= A[row_idx][col]
        if parity:
            return VerificationResult(
                valid=False,
                reason=f"observable {name!r} appears with odd multiplicity",
                lambda_vector=lam,
                q_value=None,
            )

    q = q_of_cycle(program, lam)
    if q != 1:
        return VerificationResult(
            valid=False,
            reason=f"cycle is closed but Q={q}, not odd",
            lambda_vector=lam,
            q_value=q,
        )

    zd = check_kernel_zd_valuation(program, kernel)
    if not zd.contextual:
        return VerificationResult(
            valid=False,
            reason="odd-Q cycle is valid but compressed family is not Z_d-contextual",
            lambda_vector=lam,
            q_value=q,
            zd_contextual=False,
            zd_reason=zd.reason,
        )

    return VerificationResult(
        valid=True,
        reason="valid odd-Q and genuine Z_d contextual kernel",
        lambda_vector=lam,
        q_value=q,
        zd_contextual=True,
        zd_reason=zd.reason,
    )
