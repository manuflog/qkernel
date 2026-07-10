from __future__ import annotations

from itertools import product
from typing import Iterable, List, Tuple


def rref(rows: List[int], ncols: int) -> Tuple[List[int], List[int]]:
    """RREF over GF(2), storing each row as an int bitset."""
    rows = rows[:]
    pivots: List[int] = []
    r = 0

    for c in range(ncols):
        pivot = None
        for i in range(r, len(rows)):
            if (rows[i] >> c) & 1:
                pivot = i
                break
        if pivot is None:
            continue

        rows[r], rows[pivot] = rows[pivot], rows[r]

        for i in range(len(rows)):
            if i != r and ((rows[i] >> c) & 1):
                rows[i] ^= rows[r]

        pivots.append(c)
        r += 1

        if r == len(rows):
            break

    return rows[:r], pivots


def nullspace(matrix_rows: List[List[int]], ncols: int) -> List[List[int]]:
    """Basis for the GF(2) nullspace of M x = 0."""
    int_rows = []
    for row in matrix_rows:
        bits = 0
        for j, val in enumerate(row):
            if val & 1:
                bits |= 1 << j
        int_rows.append(bits)

    rref_rows, pivots = rref(int_rows, ncols)
    pivot_set = set(pivots)
    free_cols = [c for c in range(ncols) if c not in pivot_set]

    basis: List[List[int]] = []
    for free_col in free_cols:
        x_bits = 1 << free_col
        for row_bits, pivot_col in zip(rref_rows, pivots):
            if (row_bits >> free_col) & 1:
                x_bits |= 1 << pivot_col
        basis.append([(x_bits >> j) & 1 for j in range(ncols)])

    return basis


def span(basis: List[List[int]], max_dim: int = 24) -> Iterable[List[int]]:
    """Enumerate nonzero vectors in a GF(2) span.

    This is suitable for small POCs. Larger systems should use MILP/CP-SAT
    or a specialized minimum-weight coset/codeword solver.
    """
    k = len(basis)

    if k == 0:
        return

    if k > max_dim:
        raise ValueError(f"cycle space dimension {k} too large for exhaustive enumeration.")

    n = len(basis[0])
    for coeffs in product([0, 1], repeat=k):
        if not any(coeffs):
            continue

        out = [0] * n
        for active, vec in zip(coeffs, basis):
            if active:
                out = [a ^ b for a, b in zip(out, vec)]
        yield out
