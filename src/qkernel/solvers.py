from __future__ import annotations

from itertools import combinations
from typing import Literal

from .carry import b_vector
from .gf2 import span
from .incidence import build_incidence, left_kernel_basis
from .ir import WeylProgram


SolverName = Literal["auto", "span", "bounded-weight", "branch-bound"]


def hamming_weight(vec: list[int]) -> int:
    return sum(1 for x in vec if x)


def _row_bitsets(program: WeylProgram) -> tuple[list[int], list[int], int]:
    """Return incidence rows as integer bitsets, carry vector, and column count."""
    A, _ = build_incidence(program)
    rows: list[int] = []
    for row in A:
        bits = 0
        for j, val in enumerate(row):
            if val & 1:
                bits |= 1 << j
        rows.append(bits)
    return rows, b_vector(program), (len(A[0]) if A else 0)


def _basis_insert(basis: dict[int, int], x: int) -> None:
    """Insert x into a GF(2) row-echelon basis represented by pivot bit."""
    y = x
    while y:
        pivot = y.bit_length() - 1
        if pivot not in basis:
            basis[pivot] = y
            return
        y ^= basis[pivot]


def _basis_reduce(basis: dict[int, int], x: int) -> int:
    """Reduce x by basis; returns zero iff x is in the span."""
    y = x
    while y:
        pivot = y.bit_length() - 1
        if pivot not in basis:
            return y
        y ^= basis[pivot]
    return 0


def _suffix_span_bases(states: list[int]) -> list[dict[int, int]]:
    """suffix_bases[i] spans states[i:]."""
    suffix: list[dict[int, int]] = [dict() for _ in range(len(states) + 1)]

    for i in range(len(states) - 1, -1, -1):
        basis = dict(suffix[i + 1])
        _basis_insert(basis, states[i])
        suffix[i] = basis

    return suffix


def find_min_odd_cycle_span(
    program: WeylProgram,
    *,
    max_cycle_dim: int = 24,
) -> list[int] | None:
    """Exact minimum odd-cycle search by enumerating the cycle-basis span."""
    basis = left_kernel_basis(program)

    best: list[int] | None = None
    best_weight: int | None = None
    b = b_vector(program)

    for lam in span(basis, max_dim=max_cycle_dim):
        if sum(x * y for x, y in zip(lam, b)) % 2 != 1:
            continue

        weight = hamming_weight(lam)
        if best is None or weight < best_weight:  # type: ignore[operator]
            best = lam
            best_weight = weight

    return best


def find_min_odd_cycle_bounded_weight(
    program: WeylProgram,
    *,
    max_weight: int = 8,
    max_checks: int = 2_000_000,
) -> list[int] | None:
    """Exact increasing-weight search over context subsets up to max_weight."""
    row_bits, b, _ = _row_bitsets(program)
    n = len(row_bits)
    checks = 0

    for weight in range(1, min(max_weight, n) + 1):
        for combo in combinations(range(n), weight):
            checks += 1
            if checks > max_checks:
                raise RuntimeError(
                    f"bounded-weight solver exceeded max_checks={max_checks}; "
                    "increase max_checks or use another solver."
                )

            incidence_xor = 0
            carry_xor = 0
            for idx in combo:
                incidence_xor ^= row_bits[idx]
                carry_xor ^= b[idx]

            if incidence_xor == 0 and carry_xor == 1:
                lam = [0] * n
                for idx in combo:
                    lam[idx] = 1
                return lam

    return None


def find_min_odd_cycle_branch_bound(
    program: WeylProgram,
    *,
    max_nodes: int = 1_000_000,
    initial_max_weight: int | None = None,
) -> list[int] | None:
    """Exact branch-and-bound solver with suffix-span feasibility pruning.

    Each context row is encoded as a single GF(2) state vector:

        state_i = incidence_row_i || carry_bit_i

    A partial selection has state:

        current = XOR selected state_i

    A complete odd-Q cycle is exactly:

        current == target = 0...01

    where the last bit is the carry parity.

    At DFS position i, if target XOR current is not in the span of the
    remaining suffix states, no continuation can solve the instance, so the
    branch is pruned.

    This remains exponential in hard cases, but it is an exact pure-Python
    baseline with a meaningful feasibility oracle.
    """
    row_bits, b, n_cols = _row_bitsets(program)
    n = len(row_bits)

    states = [
        row_bits[i] | (b[i] << n_cols)
        for i in range(n)
    ]
    target = 1 << n_cols

    suffix_bases = _suffix_span_bases(states)

    if _basis_reduce(suffix_bases[0], target) != 0:
        return None

    order = sorted(range(n), key=lambda i: (b[i], row_bits[i].bit_count()), reverse=True)
    ordered_states = [states[i] for i in order]

    suffix_bases = _suffix_span_bases(ordered_states)

    best: list[int] | None = None
    best_weight = initial_max_weight if initial_max_weight is not None else n + 1
    nodes = 0
    selected_order_positions: list[int] = []

    def dfs(pos: int, current_state: int) -> None:
        nonlocal best, best_weight, nodes

        nodes += 1
        if nodes > max_nodes:
            raise RuntimeError(
                f"branch-bound solver exceeded max_nodes={max_nodes}; "
                "increase max_nodes or use another solver."
            )

        current_weight = len(selected_order_positions)
        if current_weight >= best_weight:
            return

        residual = target ^ current_state
        if _basis_reduce(suffix_bases[pos], residual) != 0:
            return

        if current_state == target:
            lam = [0] * n
            for ordered_pos in selected_order_positions:
                original_idx = order[ordered_pos]
                lam[original_idx] = 1
            best = lam
            best_weight = current_weight
            return

        if pos >= n:
            return

        # Include branch first. This tends to find a feasible certificate early,
        # giving a useful upper bound for subsequent pruning.
        selected_order_positions.append(pos)
        dfs(pos + 1, current_state ^ ordered_states[pos])
        selected_order_positions.pop()

        # Exclude branch.
        dfs(pos + 1, current_state)

    dfs(0, 0)
    return best


def find_min_odd_cycle(
    program: WeylProgram,
    *,
    solver: SolverName = "auto",
    max_cycle_dim: int = 24,
    max_weight: int = 8,
    max_checks: int = 2_000_000,
    max_nodes: int = 1_000_000,
) -> list[int] | None:
    """Find a minimum odd-Q cycle using one of the available backends."""
    if solver == "span":
        return find_min_odd_cycle_span(program, max_cycle_dim=max_cycle_dim)

    if solver == "bounded-weight":
        return find_min_odd_cycle_bounded_weight(
            program,
            max_weight=max_weight,
            max_checks=max_checks,
        )

    if solver == "branch-bound":
        return find_min_odd_cycle_branch_bound(
            program,
            max_nodes=max_nodes,
            initial_max_weight=max_weight + 1 if max_weight else None,
        )

    if solver != "auto":
        raise ValueError(f"unknown solver {solver!r}.")

    basis = left_kernel_basis(program)
    if len(basis) <= max_cycle_dim:
        return find_min_odd_cycle_span(program, max_cycle_dim=max_cycle_dim)

    # Try exact bounded search for small certificates, then branch-bound.
    candidate = find_min_odd_cycle_bounded_weight(
        program,
        max_weight=max_weight,
        max_checks=max_checks,
    )
    if candidate is not None:
        return candidate

    return find_min_odd_cycle_branch_bound(
        program,
        max_nodes=max_nodes,
    )
