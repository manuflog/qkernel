from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from itertools import combinations
from typing import Literal

from .closed_form import is_cycle, validate_lambda_length
from .ir import WeylProgram
from .symplectic import symplectic_int
from .validate import validate_program
from .valuation import check_zd_valuation


TowerStatus = Literal[
    "certified_generative",
    "certified_nongenerative",
    "invalid_fiber_lift",
    "not_a_cycle",
]


@dataclass(frozen=True)
class FiberObservable:
    name: str
    lifted_vector: tuple[int, ...]
    base_residue: tuple[int, ...]
    lift_bits: tuple[int, ...]


@dataclass(frozen=True)
class TowerLawReport:
    """Certified closed-form tower/doubling-law report.

    For a fiber lift d -> 2d, each lifted observable is written as

        v_tilde = u + d x

    with u in Z_d and x in {0,1}. For the selected cycle, define

        M_ab = <u_a, x_b> + <x_a, u_b>

    over the flattened selected observable multiset. The exact generativity bit is

        G = floor(sum M_ab / 2) XOR floor(K / 2) mod 2

    where K is the number of odd M_ab terms. A cycle is non-generative iff G=0.
    """

    status: TowerStatus
    certified: bool
    reason: str
    selected_contexts: list[int]
    base_d: int
    lifted_d: int
    flattened_observables: list[str]
    repeated_observables: dict[str, int]
    sum_m: int | None
    odd_m_count: int | None
    floor_sum_m_over_2: int | None
    floor_odd_m_count_over_2: int | None
    generativity_bit: int | None
    non_generative: bool | None
    zd_contextual: bool | None
    zd_reason: str | None


def infer_base_d(program: WeylProgram, base_d: int | None = None) -> int:
    if base_d is not None:
        if base_d < 2:
            raise ValueError("base_d must be >= 2.")
        if program.d != 2 * base_d:
            raise ValueError(f"program modulus d={program.d} is not 2*base_d={2*base_d}.")
        return base_d

    if program.d % 2 != 0:
        raise ValueError("cannot infer base_d: lifted modulus must be even.")
    return program.d // 2


def split_fiber_vector(vec: tuple[int, ...], *, base_d: int, lifted_d: int) -> tuple[tuple[int, ...], tuple[int, ...]]:
    """Split a lifted vector into base residue u and binary lift bits x."""
    if lifted_d != 2 * base_d:
        raise ValueError("lifted_d must equal 2*base_d.")

    u: list[int] = []
    x: list[int] = []

    for coord in vec:
        residue = coord % base_d
        delta = (coord - residue) % lifted_d

        if delta not in {0, base_d}:
            raise ValueError(
                f"coordinate {coord} is not a valid fiber coordinate over base_d={base_d}."
            )

        u.append(residue)
        x.append(delta // base_d)

    return tuple(u), tuple(x)


def flatten_selected_fiber_observables(
    program: WeylProgram,
    lam: list[int],
    *,
    base_d: int | None = None,
) -> list[FiberObservable]:
    """Flatten selected contexts and split each lifted observable into (u,x)."""
    validate_program(program)
    validate_lambda_length(program, lam)
    bd = infer_base_d(program, base_d)

    out: list[FiberObservable] = []
    for bit, context in zip(lam, program.contexts):
        if bit:
            for name in context:
                lifted = tuple(program.observables[name])
                u, x = split_fiber_vector(lifted, base_d=bd, lifted_d=program.d)
                out.append(
                    FiberObservable(
                        name=name,
                        lifted_vector=lifted,
                        base_residue=u,
                        lift_bits=x,
                    )
                )

    return out


def direct_m_ab(a: FiberObservable, b: FiberObservable) -> int:
    """Compute M_ab directly as <u_a,x_b> + <x_a,u_b>."""
    return symplectic_int(a.base_residue, b.lift_bits) + symplectic_int(a.lift_bits, b.base_residue)


def tower_generativity_bit_from_fibers(fibers: list[FiberObservable]) -> tuple[int, int, int, int, int]:
    """Return (G, sum_m, K, floor(sum_m/2), floor(K/2))."""
    sum_m = 0
    odd_count = 0

    for a, b in combinations(fibers, 2):
        m_ab = direct_m_ab(a, b)
        sum_m += m_ab
        if m_ab % 2:
            odd_count += 1

    floor_sum = sum_m // 2
    floor_odd = odd_count // 2
    g = (floor_sum ^ floor_odd) & 1
    return g, sum_m, odd_count, floor_sum, floor_odd


def tower_law_report(
    program: WeylProgram,
    lam: list[int],
    *,
    base_d: int | None = None,
    require_zd_contextual: bool = True,
) -> TowerLawReport:
    """Return the certified closed-form tower/doubling-law report.

    The formula itself is certified for valid fiber cycles. This is still not a
    resource optimizer and not a tower-compression certificate.
    """
    validate_program(program)
    validate_lambda_length(program, lam)
    bd = infer_base_d(program, base_d)

    selected = [idx for idx, bit in enumerate(lam) if bit]
    counts: Counter[str] = Counter()
    for idx in selected:
        counts.update(program.contexts[idx])
    repeated = {name: count for name, count in sorted(counts.items()) if count > 1}

    if not is_cycle(program, lam):
        return TowerLawReport(
            status="not_a_cycle",
            certified=False,
            reason="selected contexts are not a closed GF(2) cycle.",
            selected_contexts=selected,
            base_d=bd,
            lifted_d=program.d,
            flattened_observables=[],
            repeated_observables=repeated,
            sum_m=None,
            odd_m_count=None,
            floor_sum_m_over_2=None,
            floor_odd_m_count_over_2=None,
            generativity_bit=None,
            non_generative=None,
            zd_contextual=None,
            zd_reason=None,
        )

    try:
        fibers = flatten_selected_fiber_observables(program, lam, base_d=bd)
    except ValueError as exc:
        return TowerLawReport(
            status="invalid_fiber_lift",
            certified=False,
            reason=str(exc),
            selected_contexts=selected,
            base_d=bd,
            lifted_d=program.d,
            flattened_observables=[],
            repeated_observables=repeated,
            sum_m=None,
            odd_m_count=None,
            floor_sum_m_over_2=None,
            floor_odd_m_count_over_2=None,
            generativity_bit=None,
            non_generative=None,
            zd_contextual=None,
            zd_reason=None,
        )

    g, sum_m, odd_count, floor_sum, floor_odd = tower_generativity_bit_from_fibers(fibers)
    zd_contextual = None
    zd_reason = None

    if require_zd_contextual:
        zd = check_zd_valuation(program)
        zd_contextual = zd.contextual
        zd_reason = zd.reason

    status: TowerStatus = "certified_nongenerative" if g == 0 else "certified_generative"
    reason = (
        "certified closed tower/doubling formula; cycle is non-generative iff G=0"
    )
    if require_zd_contextual and not zd_contextual:
        reason += "; warning: selected program is not Z_d contextual under its phase model"

    return TowerLawReport(
        status=status,
        certified=True,
        reason=reason,
        selected_contexts=selected,
        base_d=bd,
        lifted_d=program.d,
        flattened_observables=[fiber.name for fiber in fibers],
        repeated_observables=repeated,
        sum_m=sum_m,
        odd_m_count=odd_count,
        floor_sum_m_over_2=floor_sum,
        floor_odd_m_count_over_2=floor_odd,
        generativity_bit=g,
        non_generative=(g == 0),
        zd_contextual=zd_contextual,
        zd_reason=zd_reason,
    )


# Backward-compatible name for old experimental API.
def tower_doubling_scope_report(program: WeylProgram, lam: list[int]) -> TowerLawReport:
    return tower_law_report(program, lam)
