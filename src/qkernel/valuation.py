from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from math import gcd
from typing import Literal

from .carry import b_vector
from .incidence import build_incidence
from .ir import KernelResult, WeylProgram
from .validate import validate_program


ValuationStatus = Literal["contextual", "noncontextual", "unknown"]


@dataclass(frozen=True)
class ZDValuationResult:
    """Result of the genuine Z_d valuation-system check.

    The AvN valuation system is

        M phi = gamma mod d

    where M is the integer context-observable incidence matrix and gamma is the
    context scalar/phase vector. If this system has no solution, the family is
    genuinely Z_d-contextual under the supplied phase model.
    """

    contextual: bool
    status: ValuationStatus
    solvable: bool | None
    modulus: int
    phases: list[int]
    observable_order: list[str]
    reason: str


def context_phase_vector(program: WeylProgram) -> list[int]:
    """Return gamma, the Z_d context phase vector.

    If `program.context_phases` is supplied, it is treated as the authoritative
    phase vector.

    Backward-compatible default:
      - for even d, gamma_i = (d/2) * b_i mod d, where b_i is the integer-carry
        parity used by the odd-Q criterion;
      - for odd d, gamma_i = 0.

    For high-d AvN work, callers should prefer explicit `context_phases` when
    they know the actual operator product scalars.
    """
    validate_program(program)

    if program.context_phases is not None:
        return [phase % program.d for phase in program.context_phases]

    if program.d % 2 == 0:
        half = program.d // 2
        return [(half * bit) % program.d for bit in b_vector(program)]

    return [0 for _ in program.contexts]


def valuation_matrix(program: WeylProgram) -> tuple[list[list[int]], list[str]]:
    """Build integer M for the Z_d valuation system.

    Entries are context multiplicities modulo d, not only GF(2) incidence bits.
    """
    validate_program(program)
    _, observable_order = build_incidence(program)

    name_to_col = {name: j for j, name in enumerate(observable_order)}
    matrix: list[list[int]] = []

    for context in program.contexts:
        row = [0] * len(observable_order)
        for name in context:
            row[name_to_col[name]] = (row[name_to_col[name]] + 1) % program.d
        matrix.append(row)

    return matrix, observable_order


def selected_subprogram(program: WeylProgram, selected_contexts: list[int]) -> WeylProgram:
    """Return the subprogram induced by selected context indices."""
    n = len(program.contexts)
    for idx in selected_contexts:
        if idx < 0 or idx >= n:
            raise ValueError(f"context index out of range: {idx}")

    selected_observables = sorted({name for idx in selected_contexts for name in program.contexts[idx]})
    sub_observables = {name: program.observables[name] for name in selected_observables}
    sub_metadata = {
        name: program.observable_metadata[name]
        for name in selected_observables
        if name in program.observable_metadata
    }
    sub_contexts = [list(program.contexts[idx]) for idx in selected_contexts]
    sub_phases = (
        [program.context_phases[idx] for idx in selected_contexts]
        if program.context_phases is not None
        else None
    )

    return WeylProgram(
        d=program.d,
        m=program.m,
        observables=sub_observables,
        contexts=sub_contexts,
        observable_metadata=sub_metadata,
        context_phases=sub_phases,
    )


def _bruteforce_solvable(matrix: list[list[int]], rhs: list[int], modulus: int) -> bool | None:
    """Small fallback solver when SymPy is unavailable.

    Returns None if the search space is too large.
    """
    rows = len(matrix)
    cols = len(matrix[0]) if matrix else 0
    max_states = 200_000
    states = modulus ** cols
    if states > max_states:
        return None

    for candidate in product(range(modulus), repeat=cols):
        ok = True
        for i in range(rows):
            total = sum(matrix[i][j] * candidate[j] for j in range(cols)) % modulus
            if total != rhs[i] % modulus:
                ok = False
                break
        if ok:
            return True

    return False


def linear_system_solvable_mod_n(matrix: list[list[int]], rhs: list[int], modulus: int) -> bool:
    """Exact solvability of A x = rhs mod n using Smith normal form.

    For S = U A V, the transformed system is S y = U rhs mod n. Each diagonal
    equation s_i y_i = c_i mod n is solvable iff gcd(s_i,n) divides c_i.
    Zero rows require c_i = 0 mod n.
    """
    if modulus < 2:
        raise ValueError("modulus must be >= 2.")

    if len(matrix) != len(rhs):
        raise ValueError("rhs length must match matrix row count.")

    if not matrix:
        return all((x % modulus) == 0 for x in rhs)

    cols = len(matrix[0])
    if any(len(row) != cols for row in matrix):
        raise ValueError("matrix rows must have equal length.")

    try:
        from sympy import Matrix, ZZ
        from sympy.matrices.normalforms import smith_normal_decomp
    except Exception:
        brute = _bruteforce_solvable(matrix, rhs, modulus)
        if brute is None:
            raise RuntimeError(
                "SymPy is required for large Z_d valuation checks. Install qkernel with sympy support."
            )
        return brute

    A = Matrix(matrix)
    D, U, _V = smith_normal_decomp(A, domain=ZZ)
    b = Matrix(rhs)
    transformed = U * b

    rows = len(matrix)
    rank_diag = min(rows, cols)

    for i in range(rows):
        c = int(transformed[i]) % modulus
        diag = abs(int(D[i, i])) if i < rank_diag else 0

        if diag == 0:
            if c % modulus != 0:
                return False
        else:
            if c % gcd(diag, modulus) != 0:
                return False

    return True


def check_zd_valuation(program: WeylProgram) -> ZDValuationResult:
    """Check whether the supplied family is genuinely Z_d-contextual."""
    validate_program(program)
    matrix, order = valuation_matrix(program)
    phases = context_phase_vector(program)

    solvable = linear_system_solvable_mod_n(matrix, phases, program.d)
    contextual = not solvable

    return ZDValuationResult(
        contextual=contextual,
        status="contextual" if contextual else "noncontextual",
        solvable=solvable,
        modulus=program.d,
        phases=phases,
        observable_order=order,
        reason=(
            "Z_d valuation system is unsolvable; genuine AvN contextual family"
            if contextual
            else "Z_d valuation system has a solution; not a genuine AvN certificate under this phase model"
        ),
    )


def check_kernel_zd_valuation(program: WeylProgram, kernel: KernelResult) -> ZDValuationResult:
    """Run Z_d valuation unsolvability on the compressed kernel family."""
    if not kernel.contextual:
        return ZDValuationResult(
            contextual=False,
            status="noncontextual",
            solvable=True,
            modulus=program.d,
            phases=[],
            observable_order=[],
            reason="kernel is noncontextual; no Z_d valuation obstruction claimed",
        )

    sub = selected_subprogram(program, kernel.selected_contexts)
    return check_zd_valuation(sub)


@dataclass(frozen=True)
class TwoPrimaryReport:
    """Report on the 2-primary structure of the achievable obstruction value.

    Corollary (deductive from the Obstruction Spectrum Theorem, H(d) = {0, d/2}
    for even d): write d = 2^k * m with m odd. Under the CRT isomorphism
    Z_d ~= Z_{2^k} x Z_m, the value d/2 = 2^{k-1} m maps to
    (2^{k-1} m mod 2^k, 0): it is the order-two element of the 2-primary factor
    and is identically zero in the odd factor Z_m, for every even d. Hence any
    achievable Weyl obstruction value is 2-primary, and the mod-2 carry shadow
    detects the full obstruction *value* at every even d -- not only 2-power
    dimensions. (This concerns the value; incidence-minimality can still require
    a Z_d cycle search.)
    """

    modulus: int
    two_adic_valuation: int
    odd_part: int
    value_dover2: int
    value_odd_component: int
    is_two_primary: bool
    shadow_value_faithful: bool
    reason: str


def two_primary_report(modulus: int) -> TwoPrimaryReport:
    """Return the 2-primary / value-faithfulness report for local dimension d."""
    d = int(modulus)
    if d <= 0:
        raise ValueError("modulus must be positive")
    m = d
    k = 0
    while m % 2 == 0:
        m //= 2
        k += 1
    if k == 0:
        return TwoPrimaryReport(
            modulus=d,
            two_adic_valuation=0,
            odd_part=m,
            value_dover2=0,
            value_odd_component=0,
            is_two_primary=True,
            shadow_value_faithful=True,
            reason="odd d: H(d) = {0}; no obstruction, shadow trivially value-faithful",
        )
    half = d // 2
    odd_component = half % m  # image of d/2 in the odd factor Z_m
    is_two_primary = odd_component == 0
    return TwoPrimaryReport(
        modulus=d,
        two_adic_valuation=k,
        odd_part=m,
        value_dover2=half,
        value_odd_component=odd_component,
        is_two_primary=is_two_primary,
        shadow_value_faithful=is_two_primary,
        reason=(
            "even d = 2^%d * %d: value d/2 = %d is 2-primary "
            "(odd-part component %d); mod-2 shadow is value-faithful"
            % (k, m, half, odd_component)
        ),
    )


@dataclass(frozen=True)
class SpectrumSummary:
    """One-call summary of the obstruction spectrum at local dimension d.

    Encodes the Obstruction Spectrum Theorem H(d) = {0, d/2} for even d (and
    H(d) = {0} for odd d), together with the 2-primary structure of the nonzero
    value. This is a pure dimension-level lookup: it depends only on d, not on
    any particular measurement program.
    """

    modulus: int
    is_even: bool
    achievable_values: list[int]
    nonzero_value: int | None
    value_order: int | None
    two_primary: TwoPrimaryReport
    reason: str


def spectrum_summary(modulus: int) -> SpectrumSummary:
    """Return the obstruction spectrum summary for local dimension d."""
    d = int(modulus)
    if d <= 1:
        raise ValueError("modulus must be >= 2")
    tp = two_primary_report(d)
    if d % 2 == 1:
        return SpectrumSummary(
            modulus=d,
            is_even=False,
            achievable_values=[0],
            nonzero_value=None,
            value_order=None,
            two_primary=tp,
            reason=(
                "odd d: H(d) = {0}; odd-dimensional Weyl stabilizer families are "
                "noncontextual (no state-independent parity obstruction)"
            ),
        )
    half = d // 2
    # order of d/2 in Z_d: d / gcd(d, d/2) = d / (d/2) = 2
    return SpectrumSummary(
        modulus=d,
        is_even=True,
        achievable_values=[0, half],
        nonzero_value=half,
        value_order=2,
        two_primary=tp,
        reason=(
            "even d: H(d) = {0, d/2}; the nonzero value d/2 is the order-two "
            "element of Z_d and is 2-primary (mod-2 shadow value-faithful)"
        ),
    )
