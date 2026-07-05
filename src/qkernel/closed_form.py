from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

from .carry import b_vector
from .incidence import build_incidence
from .ir import WeylProgram
from .symplectic import symplectic_int


@dataclass(frozen=True)
class QFormComparison:
    """Comparison of two equivalent Q computations on a closed cycle."""

    lambda_vector: list[int]
    q_from_context_carries: int
    q_from_observable_multiset: int
    numerator: int
    valid: bool


def validate_lambda_length(program: WeylProgram, lam: list[int]) -> None:
    if len(lam) != len(program.contexts):
        raise ValueError(
            f"lambda length {len(lam)} does not match context count {len(program.contexts)}."
        )
    if any(bit not in {0, 1} for bit in lam):
        raise ValueError("lambda must be a binary vector.")


def is_cycle(program: WeylProgram, lam: list[int]) -> bool:
    """Return True iff A^T lambda = 0 over GF(2)."""
    validate_lambda_length(program, lam)
    A, _ = build_incidence(program)

    if not A:
        return False

    for col in range(len(A[0])):
        parity = 0
        for row_idx, bit in enumerate(lam):
            if bit:
                parity ^= A[row_idx][col]
        if parity:
            return False

    return True


def q_from_context_carries(program: WeylProgram, lam: list[int]) -> int:
    """Compute lambda · b mod 2 using per-context carry bits."""
    validate_lambda_length(program, lam)
    b = b_vector(program)
    return sum(bit * carry for bit, carry in zip(lam, b)) % 2


def observable_multiset_for_cycle(program: WeylProgram, lam: list[int]) -> list[tuple[int, ...]]:
    """Flatten selected contexts into an ordered observable multiset."""
    validate_lambda_length(program, lam)

    multiset: list[tuple[int, ...]] = []
    for bit, context in zip(lam, program.contexts):
        if bit:
            multiset.extend(program.observables[name] for name in context)

    return multiset


def observable_multiset_pairing_numerator(program: WeylProgram, lam: list[int]) -> int:
    """Return sum_{a<b} <v_a, v_b> over the selected observable multiset."""
    multiset = observable_multiset_for_cycle(program, lam)

    total = 0
    for u, v in combinations(multiset, 2):
        total += symplectic_int(u, v)
    return total


def q_from_observable_multiset(program: WeylProgram, lam: list[int]) -> int:
    """Compute Q(lambda) from the closed symplectic observable-multiset form.

    For a closed cycle in even dimension:

        Q(lambda) = (sum_{a<b} <v_a, v_b> / d) mod 2

    The division by d is applied to the aggregate integer numerator. Individual
    inter-context pairings need not be divisible by d.

    This function is intentionally defined only for cycles. Non-cycles do not
    represent contextuality certificates and may have a non-divisible aggregate.
    """
    validate_lambda_length(program, lam)

    if program.d % 2 != 0:
        return 0

    numerator = observable_multiset_pairing_numerator(program, lam)

    if numerator % program.d != 0:
        raise ValueError(
            "observable-multiset pairing numerator is not divisible by d; "
            "lambda may not be a closed cycle."
        )

    return (numerator // program.d) % 2


def compare_q_forms(program: WeylProgram, lam: list[int]) -> QFormComparison:
    """Compare lambda·b with the closed observable-multiset Q form."""
    validate_lambda_length(program, lam)

    q_carry = q_from_context_carries(program, lam)
    numerator = observable_multiset_pairing_numerator(program, lam)
    q_closed = q_from_observable_multiset(program, lam)

    return QFormComparison(
        lambda_vector=list(lam),
        q_from_context_carries=q_carry,
        q_from_observable_multiset=q_closed,
        numerator=numerator,
        valid=(q_carry == q_closed),
    )
