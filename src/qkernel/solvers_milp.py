"""Independent exact backend for the minimum odd-Q cycle, via CP-SAT (OR-Tools).

This is a completely separate code path from the GF(2) span / branch-and-bound
solvers: it models the problem as an integer program and lets CP-SAT's
branch-and-bound + LP relaxation find (and *certify*) the optimum. The value is
twofold: an independent cross-check of the native solvers, and — because the LP
relaxation prunes by weight rather than enumerating the 2^dim cycle space — the
ability to certify minimality on high cycle-dimension families where exhaustive
span enumeration is infeasible.

OR-Tools is an optional dependency; import errors surface a clear message.
"""
from __future__ import annotations

from .carry import b_vector
from .incidence import build_incidence
from .ir import WeylProgram


class ORToolsUnavailable(RuntimeError):
    """Raised when the CP-SAT backend is requested but OR-Tools is not installed."""


def _require_cpsat():
    try:
        from ortools.sat.python import cp_model  # noqa: WPS433
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise ORToolsUnavailable(
            "the CP-SAT backend requires OR-Tools; install with `pip install ortools`."
        ) from exc
    return cp_model


def find_min_odd_cycle_cpsat(
    program: WeylProgram,
    *,
    max_time_seconds: float = 30.0,
) -> tuple[list[int] | None, bool]:
    """Exact minimum odd-Q cycle via CP-SAT.

    Returns ``(cycle, certified_optimal)``. ``cycle`` is ``None`` when the family is
    non-contextual (the IP is infeasible) or when the solver returns nothing within
    the budget. ``certified_optimal`` is True only when CP-SAT proves optimality.

    The model: binary ``lambda_i`` per context; for each observable column the
    incidence sum is forced even (``= 2 k_j``); the carry inner product is forced
    odd (``= 2 k_b + 1``); minimize ``sum lambda_i``.
    """
    cp_model = _require_cpsat()

    A, _names = build_incidence(program)
    b = b_vector(program)
    n = len(program.contexts)
    ncols = len(A[0]) if A else 0

    model = cp_model.CpModel()
    lam = [model.NewBoolVar(f"lam_{i}") for i in range(n)]

    for j in range(ncols):
        terms = [lam[i] for i in range(n) if A[i][j] & 1]
        if terms:
            k_j = model.NewIntVar(0, n // 2, f"k_{j}")
            model.Add(sum(terms) == 2 * k_j)

    carry_terms = [lam[i] for i in range(n) if b[i] & 1]
    if not carry_terms:
        return None, True  # no odd-carry context: provably non-contextual
    k_b = model.NewIntVar(0, n // 2, "k_b")
    model.Add(sum(carry_terms) == 2 * k_b + 1)

    model.Minimize(sum(lam))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = max_time_seconds
    solver.parameters.num_search_workers = 8
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL:
        return [int(solver.Value(lam[i])) for i in range(n)], True
    if status == cp_model.FEASIBLE:
        return [int(solver.Value(lam[i])) for i in range(n)], False
    if status == cp_model.INFEASIBLE:
        return None, True  # non-contextual, certified
    return None, False  # UNKNOWN within budget
