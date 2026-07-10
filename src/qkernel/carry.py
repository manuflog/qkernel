from __future__ import annotations

from itertools import combinations

from .ir import Context, WeylProgram
from .symplectic import symplectic_int


def compute_b(program: WeylProgram, context: Context) -> int:
    """Compute the commutator-carry bit b(C).

    b(C) = sum_{i<j} <c_i,c_j>/d mod 2

    The pairing must be the integer lift. Reducing modulo d first destroys
    the carry and gives the wrong answer.
    """
    total = 0
    for a, b in combinations(context, 2):
        s = symplectic_int(program.observables[a], program.observables[b])
        if s % program.d != 0:
            raise ValueError(f"context contains noncommuting pair {a}, {b}: pairing={s}")
        total += s // program.d
    return total % 2


def b_vector(program: WeylProgram) -> list[int]:
    return [compute_b(program, context) for context in program.contexts]
