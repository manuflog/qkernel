from __future__ import annotations

from .gf2 import nullspace
from .ir import WeylProgram


def build_incidence(program: WeylProgram) -> tuple[list[list[int]], list[str]]:
    """Build context-observable incidence matrix over GF(2)."""
    names = sorted(program.observables)
    col = {name: i for i, name in enumerate(names)}

    rows: list[list[int]] = []
    for context in program.contexts:
        row = [0] * len(names)
        for name in context:
            row[col[name]] ^= 1
        rows.append(row)

    return rows, names


def left_kernel_basis(program: WeylProgram) -> list[list[int]]:
    """Basis for cycles lambda satisfying A^T lambda = 0."""
    A, names = build_incidence(program)
    AT = [[A[r][c] for r in range(len(A))] for c in range(len(names))]
    return nullspace(AT, ncols=len(program.contexts))
