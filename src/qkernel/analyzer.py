from __future__ import annotations

from .carry import b_vector
from .closed_form import q_from_context_carries, q_from_observable_multiset
from .gf2 import span
from .incidence import left_kernel_basis
from .ir import AnalysisResult, WeylProgram
from .validate import validate_program


def q_of_cycle(program: WeylProgram, lam: list[int]) -> int:
    """Backward-compatible Q(lambda) API.

    Uses the closed observable-multiset symplectic form:

        Q(lambda) = (sum_{a<b} <v_a, v_b> / d) mod 2

    for even d. The analyzer cross-checks this against lambda·b on cycles.
    """
    return q_from_observable_multiset(program, lam)


def analyze(program: WeylProgram) -> AnalysisResult:
    """Analyze contextuality using the odd-Q criterion.

    Implements the even-d state-independent Weyl-family criterion.
    """
    validate_program(program)

    if program.d % 2 != 0:
        return AnalysisResult(
            contextual=False,
            reason="Odd local dimension: this state-independent Weyl obstruction is zero in this criterion.",
            b_vector=[],
            cycle_basis=[],
            odd_cycle=None,
            q_value=None,
            selected_contexts=[],
        )

    b = b_vector(program)
    cycle_basis = left_kernel_basis(program)

    for lam in span(cycle_basis):
        q_carry = q_from_context_carries(program, lam)
        q_closed = q_from_observable_multiset(program, lam)

        if q_carry != q_closed:
            raise AssertionError("internal check failed: lambda·b != closed symplectic Q(lambda).")

        if q_closed == 1:
            selected = [i for i, bit in enumerate(lam) if bit]
            return AnalysisResult(
                contextual=True,
                reason="odd-Q cycle found",
                b_vector=b,
                cycle_basis=cycle_basis,
                odd_cycle=lam,
                q_value=q_closed,
                selected_contexts=selected,
            )

    return AnalysisResult(
        contextual=False,
        reason="no odd-Q cycle found",
        b_vector=b,
        cycle_basis=cycle_basis,
        odd_cycle=None,
        q_value=None,
        selected_contexts=[],
    )
