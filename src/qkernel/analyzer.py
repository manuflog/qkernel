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

    # For a tractable cycle space, enumerate the span: this finds a minimal odd
    # cycle and cross-checks q_carry == q_closed on every cycle.
    ENUM_LIMIT = 20
    if len(cycle_basis) <= ENUM_LIMIT:
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

    # High cycle dimension: exhaustive span enumeration (2^dim) is infeasible.
    # The odd-Q criterion is linear in lambda (Theorem Q: q_closed = lambda·b),
    # so contextuality is decided exactly by whether any basis cycle carries odd
    # b; a low-weight witness is then obtained by the heuristic solver.
    contextual = any(sum(x * y for x, y in zip(k, b)) % 2 for k in cycle_basis)
    if not contextual:
        return AnalysisResult(
            contextual=False,
            reason="no odd-Q cycle (high cycle-dim; decided by odd-carry parity)",
            b_vector=b,
            cycle_basis=cycle_basis,
            odd_cycle=None,
            q_value=None,
            selected_contexts=[],
        )

    from .solvers import find_min_odd_cycle_heuristic

    lam = find_min_odd_cycle_heuristic(program)
    selected = [i for i, bit in enumerate(lam) if bit] if lam else []
    return AnalysisResult(
        contextual=True,
        reason="odd-Q cycle found (high cycle-dim; heuristic witness)",
        b_vector=b,
        cycle_basis=cycle_basis,
        odd_cycle=lam,
        q_value=1,
        selected_contexts=selected,
    )
