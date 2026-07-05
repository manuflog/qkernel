from __future__ import annotations

from dataclasses import asdict, dataclass
from itertools import combinations
from typing import Literal

from .ir import WeylProgram
from .symplectic import symplectic_int
from .validate import validate_program
from .valuation import check_zd_valuation, context_phase_vector


FiberLiftStatus = Literal[
    "constructed",
    "no_linear_lift",
    "unsupported_odd_base",
    "invalid_base",
]


@dataclass(frozen=True)
class FiberLiftResult:
    status: FiberLiftStatus
    constructed: bool
    reason: str
    base_d: int
    lifted_d: int
    lift_bits: dict[str, list[int]]
    program: WeylProgram | None
    zd_contextual: bool | None
    zd_reason: str | None


def _gf2_solve(equations: list[tuple[list[int], int]], n_vars: int) -> list[int] | None:
    """Solve a GF(2) linear system and return one solution with free vars zero."""
    rows: list[list[int]] = []

    for inds, rhs in equations:
        mask = 0
        for idx in inds:
            if idx < 0 or idx >= n_vars:
                raise ValueError(f"variable index out of range: {idx}")
            mask ^= 1 << idx
        rows.append([mask, rhs & 1])

    rank = 0
    pivots: list[int] = []

    for col in range(n_vars):
        pivot = None
        for r in range(rank, len(rows)):
            if (rows[r][0] >> col) & 1:
                pivot = r
                break

        if pivot is None:
            continue

        rows[rank], rows[pivot] = rows[pivot], rows[rank]

        for r in range(len(rows)):
            if r != rank and ((rows[r][0] >> col) & 1):
                rows[r][0] ^= rows[rank][0]
                rows[r][1] ^= rows[rank][1]

        pivots.append(col)
        rank += 1

    for mask, rhs in rows:
        if mask == 0 and rhs:
            return None

    solution = [0] * n_vars
    for row_idx, col in enumerate(pivots):
        solution[col] = rows[row_idx][1]

    return solution


def _symplectic_linear_coeffs(
    *,
    obs_a: str,
    obs_b: str,
    u_a: tuple[int, ...],
    u_b: tuple[int, ...],
    var_index: dict[tuple[str, int], int],
) -> list[int]:
    """Coefficients of <u_a,x_b> + <x_a,u_b> modulo 2."""
    inds: list[int] = []
    m = len(u_a) // 2

    for k in range(m):
        z = 2 * k
        x = 2 * k + 1

        # <u_a, x_b> = u_a[x] * x_b[z] - u_a[z] * x_b[x].
        # Over GF(2), subtraction is addition.
        if u_a[x] % 2:
            inds.append(var_index[(obs_b, z)])
        if u_a[z] % 2:
            inds.append(var_index[(obs_b, x)])

        # <x_a, u_b> = x_a[x] * u_b[z] - x_a[z] * u_b[x].
        if u_b[z] % 2:
            inds.append(var_index[(obs_a, x)])
        if u_b[x] % 2:
            inds.append(var_index[(obs_a, z)])

    return inds


def build_even_base_fiber_lift_constraints(program: WeylProgram) -> tuple[list[tuple[list[int], int]], dict[tuple[str, int], int]]:
    """Build GF(2) constraints for a valid d -> 2d fiber lift when base d is even.

    For each lifted coordinate:

        v_tilde = u + d x,  x in {0,1}

    The constraints enforce:
      1. every lifted context sums to zero modulo 2d;
      2. every lifted context remains pairwise commuting modulo 2d.

    When base d is even, the commutation constraints are linear in the lift bits.
    """
    validate_program(program)

    if program.d % 2 != 0:
        raise ValueError("linear fiber-lift constructor currently supports even base d only.")

    observable_names = sorted(program.observables)
    width = 2 * program.m
    var_index = {
        (name, coord): i
        for i, (name, coord) in enumerate(
            (name, coord)
            for name in observable_names
            for coord in range(width)
        )
    }

    equations: list[tuple[list[int], int]] = []

    # Context closure constraints:
    # sum(u) + d sum(x) = 0 mod 2d.
    # Since sum(u)=d*t, require sum(x)=t mod 2.
    for context in program.contexts:
        for coord in range(width):
            total = sum(program.observables[name][coord] for name in context)
            if total % program.d != 0:
                raise ValueError("base context is not closed modulo d.")
            rhs = (total // program.d) % 2
            equations.append(([var_index[(name, coord)] for name in context], rhs))

    # Pairwise commutation constraints:
    # <u_a,u_b> + d(<u_a,x_b>+<x_a,u_b>) + d^2<x_a,x_b> = 0 mod 2d.
    # For even d, d^2<x_a,x_b> is automatically 0 mod 2d after division by d,
    # so this is linear:
    # (<u_a,u_b>/d) + <u_a,x_b> + <x_a,u_b> = 0 mod 2.
    for context in program.contexts:
        for a, b in combinations(context, 2):
            u_a = program.observables[a]
            u_b = program.observables[b]
            pairing = symplectic_int(u_a, u_b)
            if pairing % program.d != 0:
                raise ValueError("base context is not commuting modulo d.")

            rhs = (pairing // program.d) % 2
            inds = _symplectic_linear_coeffs(
                obs_a=a,
                obs_b=b,
                u_a=u_a,
                u_b=u_b,
                var_index=var_index,
            )
            equations.append((inds, rhs))

    return equations, var_index


def lift_program_with_bits(
    program: WeylProgram,
    lift_bits: dict[str, list[int]],
    *,
    lifted_context_phases: list[int] | None = None,
) -> WeylProgram:
    """Construct the d -> 2d lifted program from explicit binary lift bits."""
    validate_program(program)

    width = 2 * program.m
    lifted_d = 2 * program.d
    lifted_observables: dict[str, tuple[int, ...]] = {}

    for name, vec in program.observables.items():
        bits = lift_bits.get(name)
        if bits is None:
            raise ValueError(f"missing lift bits for observable {name!r}.")
        if len(bits) != width:
            raise ValueError(f"lift bits for {name!r} have length {len(bits)}; expected {width}.")
        if any(bit not in {0, 1} for bit in bits):
            raise ValueError(f"lift bits for {name!r} must be binary.")

        lifted_observables[name] = tuple(
            int(coord) + program.d * int(bit)
            for coord, bit in zip(vec, bits)
        )

    if lifted_context_phases is None:
        # Lift phases by the natural inclusion Z_d -> Z_{2d}: gamma |-> 2 gamma.
        lifted_context_phases = [(2 * phase) % lifted_d for phase in context_phase_vector(program)]

    lifted = WeylProgram(
        d=lifted_d,
        m=program.m,
        observables=lifted_observables,
        contexts=[list(context) for context in program.contexts],
        observable_metadata=program.observable_metadata,
        context_phases=lifted_context_phases,
    )

    validate_program(lifted)
    return lifted


def find_even_base_fiber_lift(program: WeylProgram) -> FiberLiftResult:
    """Find one valid d -> 2d fiber lift for even base d, if one exists."""
    try:
        validate_program(program)
    except Exception as exc:
        return FiberLiftResult(
            status="invalid_base",
            constructed=False,
            reason=f"base program is invalid: {exc}",
            base_d=getattr(program, "d", -1),
            lifted_d=-1,
            lift_bits={},
            program=None,
            zd_contextual=None,
            zd_reason=None,
        )

    if program.d % 2 != 0:
        return FiberLiftResult(
            status="unsupported_odd_base",
            constructed=False,
            reason="linear constructor currently supports even base d only; odd base d has quadratic x-x terms.",
            base_d=program.d,
            lifted_d=2 * program.d,
            lift_bits={},
            program=None,
            zd_contextual=None,
            zd_reason=None,
        )

    equations, var_index = build_even_base_fiber_lift_constraints(program)
    solution = _gf2_solve(equations, n_vars=len(var_index))

    if solution is None:
        return FiberLiftResult(
            status="no_linear_lift",
            constructed=False,
            reason="no valid even-base linear fiber lift satisfies closure and commutation constraints.",
            base_d=program.d,
            lifted_d=2 * program.d,
            lift_bits={},
            program=None,
            zd_contextual=None,
            zd_reason=None,
        )

    lift_bits: dict[str, list[int]] = {
        name: [0] * (2 * program.m)
        for name in sorted(program.observables)
    }
    for (name, coord), idx in var_index.items():
        lift_bits[name][coord] = int(solution[idx])

    lifted = lift_program_with_bits(program, lift_bits)
    zd = check_zd_valuation(lifted)

    return FiberLiftResult(
        status="constructed",
        constructed=True,
        reason="valid d -> 2d fiber lift constructed and validated.",
        base_d=program.d,
        lifted_d=lifted.d,
        lift_bits=lift_bits,
        program=lifted,
        zd_contextual=zd.contextual,
        zd_reason=zd.reason,
    )


def fiber_lift_result_dict(result: FiberLiftResult, *, include_program: bool = False) -> dict:
    out = {
        "status": result.status,
        "constructed": result.constructed,
        "reason": result.reason,
        "base_d": result.base_d,
        "lifted_d": result.lifted_d,
        "lift_bits": result.lift_bits,
        "zd_contextual": result.zd_contextual,
        "zd_reason": result.zd_reason,
    }

    if include_program and result.program is not None:
        out["program"] = {
            "d": result.program.d,
            "m": result.program.m,
            "observables": {name: list(vec) for name, vec in result.program.observables.items()},
            "contexts": result.program.contexts,
            "context_phases": result.program.context_phases,
        }

    return out
