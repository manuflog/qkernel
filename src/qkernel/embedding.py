"""Contextuality activation by dimension embedding (d -> 2d).

A base Weyl family that is *non-contextual* under the state-independent odd-Q
criterion can become *contextual* after passive embedding into twice the local
dimension. The embedded family is the *fiber pool*: the union, over base
contexts, of every valid d -> 2d lift of that context. Lifting is a free,
passive operation (no entangling gates), so this exhibits contextuality as a
resource that is *activated* by embedding.

The activation verdict here is direct and criterion-consistent: it compares
``analyze`` (the odd-Q obstruction) on the base at d against ``analyze`` on the
fiber pool at 2d. This module ports the verified research construction
(fiber solution space + carry) into qkernel's WeylProgram framework.
"""
from __future__ import annotations

from dataclasses import dataclass

from .ir import WeylProgram
from .analyzer import analyze


def _symplectic(u: tuple[int, ...], v: tuple[int, ...]) -> int:
    m = len(u) // 2
    return sum(u[2 * i + 1] * v[2 * i] - u[2 * i] * v[2 * i + 1] for i in range(m))


def _fiber_solspace(context: list[tuple[int, ...]], d: int):
    """Affine GF(2) lift solution space (x0, kernel) for one base context, or
    (None, None) if no valid lift exists. Ported from the verified construction."""
    m = len(context[0]) // 2
    L = len(context)
    nb = 2 * m * L
    rows: list[list[int]] = []
    rhs: list[int] = []

    coord_sum = [sum(context[i][c] for i in range(L)) for c in range(2 * m)]
    for c in range(2 * m):
        row = [0] * nb
        for i in range(L):
            row[i * 2 * m + c] = 1
        rows.append(row)
        rhs.append((coord_sum[c] // d) % 2)

    for i in range(L):
        for j in range(i + 1, L):
            row = [0] * nb
            for k in range(m):
                row[j * 2 * m + 2 * k] ^= context[i][2 * k + 1] % 2
                row[j * 2 * m + 2 * k + 1] ^= context[i][2 * k] % 2
                row[i * 2 * m + 2 * k] ^= context[j][2 * k + 1] % 2
                row[i * 2 * m + 2 * k + 1] ^= context[j][2 * k] % 2
            rows.append(row)
            rhs.append((_symplectic(context[i], context[j]) // d) % 2)

    # Gaussian elimination over GF(2) on the augmented system.
    n = len(rows)
    aug = [rows[i][:] + [rhs[i]] for i in range(n)]
    pivots: list[int] = []
    r = 0
    for c in range(nb):
        pr = next((i for i in range(r, n) if aug[i][c]), None)
        if pr is None:
            continue
        aug[r], aug[pr] = aug[pr], aug[r]
        for i in range(n):
            if i != r and aug[i][c]:
                aug[i] = [(aug[i][t] ^ aug[r][t]) for t in range(nb + 1)]
        pivots.append(c)
        r += 1
        if r == n:
            break

    for i in range(r, n):
        if aug[i][nb] == 1 and not any(aug[i][:nb]):
            return None, None  # inconsistent: no lift

    # Particular solution x0 from pivots; kernel basis from free columns.
    x0 = [0] * nb
    pivot_rows = {pivots[k]: k for k in range(len(pivots))}
    for c, k in pivot_rows.items():
        x0[c] = aug[k][nb]
    free_cols = [c for c in range(nb) if c not in pivot_rows]
    kernel: list[list[int]] = []
    for fc in free_cols:
        vec = [0] * nb
        vec[fc] = 1
        for c, k in pivot_rows.items():
            vec[c] = aug[k][fc]
        kernel.append(vec)
    return x0, kernel


def _fiber_all(context: list[tuple[int, ...]], d: int) -> list[tuple[tuple[int, ...], ...]]:
    """All lifted contexts over one base context (lifting each coordinate by d*bit)."""
    x0, kernel = _fiber_solspace(context, d)
    if x0 is None:
        return []
    m = len(context[0]) // 2
    L = len(context)
    space = [tuple(x0)]
    for kvec in kernel:
        space = space + [tuple(s[t] ^ kvec[t] for t in range(len(s))) for s in space]
    lifted_set = set()
    for s in space:
        lifted = tuple(
            tuple(context[i][c] + d * s[i * 2 * m + c] for c in range(2 * m))
            for i in range(L)
        )
        lifted_set.add(lifted)
    return [tuple(map(tuple, C)) for C in lifted_set]


def _program_contexts_as_vectors(program: WeylProgram) -> list[list[tuple[int, ...]]]:
    out = []
    for ctx in program.contexts:
        out.append([tuple(program.observables[name]) for name in ctx])
    return out


def build_fiber_pool(base: WeylProgram) -> WeylProgram:
    """The d -> 2d fiber pool of a base Weyl program: union of all lifts of every
    base context, as a WeylProgram at modulus 2d."""
    d = base.d
    base_contexts = _program_contexts_as_vectors(base)
    pool_contexts_vec: list[tuple[tuple[int, ...], ...]] = []
    seen = set()
    for C in base_contexts:
        for lifted in _fiber_all(C, d):
            key = tuple(sorted(lifted))
            if key not in seen:
                seen.add(key)
                pool_contexts_vec.append(lifted)

    observables: dict[str, list[int]] = {}
    contexts: list[list[str]] = []

    def name(v: tuple[int, ...]) -> str:
        key = "v" + "_".join(map(str, v))
        observables[key] = list(v)
        return key

    for C in pool_contexts_vec:
        contexts.append([name(v) for v in C])

    return WeylProgram(d=2 * d, m=base.m, observables=observables, contexts=contexts)


@dataclass
class ActivationReport:
    base_d: int
    fiber_d: int
    base_contextual: bool
    fiber_contextual: bool
    activated: bool
    base_contexts: int
    fiber_contexts: int
    reason: str


def activation_report(base: WeylProgram) -> ActivationReport:
    """Report whether embedding d -> 2d activates contextuality: base non-contextual
    (odd-Q) but fiber pool contextual (odd-Q), under the same criterion."""
    base_ctx = analyze(base).contextual
    pool = build_fiber_pool(base)
    fiber_ctx = analyze(pool).contextual
    activated = (not base_ctx) and fiber_ctx
    if activated:
        reason = "activation: non-contextual base becomes contextual under d->2d embedding"
    elif base_ctx:
        reason = "base already contextual; embedding does not activate (nothing to activate)"
    else:
        reason = "no activation: base and fiber pool both non-contextual"
    return ActivationReport(
        base_d=base.d,
        fiber_d=2 * base.d,
        base_contextual=base_ctx,
        fiber_contextual=fiber_ctx,
        activated=activated,
        base_contexts=len(base.contexts),
        fiber_contexts=len(pool.contexts),
        reason=reason,
    )


@dataclass
class ActivatedResource:
    activated: bool
    base_d: int
    fiber_d: int
    base_contextual: bool
    fiber_contextual: bool
    test_contexts: list[list[str]] | None   # fiber contexts of the cheapest activated test
    test_weight: int | None                 # number of fiber measurement settings
    obstruction_value: int | None           # resource value (fiber d)/2
    verified: bool
    reason: str


def activated_resource(base: WeylProgram) -> ActivatedResource:
    """Contextuality-as-a-resource via embedding: if a non-contextual base activates
    under d -> 2d embedding, extract the cheapest activated contextuality test (the
    minimal odd-Q kernel of the fiber pool) as concrete fiber measurement settings."""
    from .optimizer import compress_min_odd_q

    base_ctx = analyze(base).contextual
    pool = build_fiber_pool(base)
    fiber_ctx = analyze(pool).contextual
    activated = (not base_ctx) and fiber_ctx

    if not activated:
        reason = ("base already contextual; nothing to activate" if base_ctx
                  else "no activation: fiber pool is non-contextual")
        return ActivatedResource(
            activated=False, base_d=base.d, fiber_d=2 * base.d,
            base_contextual=base_ctx, fiber_contextual=fiber_ctx,
            test_contexts=None, test_weight=None, obstruction_value=None,
            verified=True, reason=reason,
        )

    from .incidence import build_incidence
    from .carry import b_vector

    kernel = compress_min_odd_q(pool)
    selected_idx = list(kernel.selected_contexts)
    selected = [pool.contexts[i] for i in selected_idx]
    weight = len(selected_idx)

    # Verify on the odd-Q criterion that activation is defined on (state-independent
    # parity): the selected contexts use every observable an even number of times and
    # carry an odd total. (This is intentionally *not* verify_kernel, which additionally
    # demands Z_d/AvN valuation-contextuality -- a stricter, different criterion that the
    # minimal activated sub-family need not satisfy.)
    A, _ = build_incidence(pool)
    b = b_vector(pool)
    sel = set(selected_idx)
    lam = [1 if i in sel else 0 for i in range(len(pool.contexts))]
    even = all(sum(A[r][c] * lam[r] for r in range(len(A))) % 2 == 0 for c in range(len(A[0])))
    odd_carry = sum(b[i] * lam[i] for i in range(len(pool.contexts))) % 2 == 1
    verified = bool(even and odd_carry)

    return ActivatedResource(
        activated=True, base_d=base.d, fiber_d=2 * base.d,
        base_contextual=False, fiber_contextual=True,
        test_contexts=selected, test_weight=weight,
        obstruction_value=pool.d // 2, verified=verified,
        reason="activated: non-contextual base yields an odd-Q contextuality resource under d->2d embedding",
    )
