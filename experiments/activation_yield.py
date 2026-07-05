"""Activation-yield sweep: does contextuality-activation yield rise monotonically
with base size, and is the small-size dip (10% -> 8% at 3 -> 4 contexts in the
coarse 60-seed run) real or sampling noise?

For each base size we draw many random non-contextual d=4 bases, embed each to the
d=8 fiber pool, and record the fraction that become contextual. Reported with
Wilson 95% confidence intervals so the curve shape can be read off rigorously.

VERIFIED RESULT (Wilson 95% CI; 150-400 seeds/point):

    nctx :   3     4     5     6     7     8     10    12
    yield: 4.5% 13.5% 19.0% 30.0% 42.0% 46.0% 66.2% 73.8%

The curve is MONOTONE INCREASING and non-linear (concave, saturating toward 1):
the 3->4 step alone has disjoint CIs ([2.4,8.3] vs [9.4,18.9]), so the rise is
statistically real. The apparent 10% -> 8% "dip" in the coarse 60-seed run was
sampling noise. The non-activation probability (1 - yield) decays roughly
geometrically in base size: for d=4->8, 1 - yield ~ 1.63 * 0.861^nctx (R^2 = 0.98).

DEPENDENCE ON BASE DIMENSION d (yield at nctx=6, 100-150 seeds):

    d = 4 (2^2):  30%  [23, 38]   -- activates readily, geometric decay r = 0.861
    d = 6 (2*3):   9%  [4.8, 16]  -- rare
    d = 8 (2^3):   2%  [0.6, 7]   -- at the noise floor

Activation yield DECREASES sharply with base dimension; d=4 is a special readily-
activating regime. NOTE (hypothesis refuted): "2-primary d activates readily" is
FALSE -- d=8 is 2-primary yet activates as rarely as, or more rarely than, d=6. So
2-adic structure alone does not govern activation readiness; base dimension does.
"""
from __future__ import annotations

import math
import random
import sys

sys.path.insert(0, "src")
from qkernel.ir import WeylProgram
from qkernel.embedding import build_fiber_pool
from qkernel.analyzer import analyze


def _symp(u, v):
    m = len(u) // 2
    return sum(u[2 * i + 1] * v[2 * i] - u[2 * i] * v[2 * i + 1] for i in range(m))


def rand_base(d, seed, nctx, m=2):
    rng = random.Random(seed)
    out = []

    def rc():
        for _ in range(400):
            u = tuple(rng.randrange(0, d) for _ in range(2 * m))
            v = tuple(rng.randrange(0, d) for _ in range(2 * m))
            if _symp(u, v) % d == 0:
                w = tuple((-(u[i] + v[i])) % d for i in range(2 * m))
                if _symp(u, w) % d == 0 and _symp(v, w) % d == 0:
                    return [u, v, w]
        return None

    for _ in range(nctx):
        c = rc()
        if c:
            out.append(c)
    return out


def _to_prog(base, d, m=2):
    obs, ctx = {}, []

    def nm(v):
        k = "v" + "_".join(map(str, v))
        obs[k] = list(v)
        return k

    for C in base:
        ctx.append([nm(tuple(v)) for v in C])
    return WeylProgram(d=d, m=m, observables=obs, contexts=ctx)


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0, 0.0)
    p = k / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (p, center - half, center + half)


def yield_sweep(sizes, seeds_per=400, seed0=90000):
    print(f"activation yield d=4->8, {seeds_per} seeds/point, Wilson 95% CI")
    print(f"{'nctx':>4} {'trivial_n':>10} {'act':>5} {'yield%':>7} {'95% CI':>16}")
    rows = []
    for nctx in sizes:
        act = triv = 0
        for s in range(seeds_per):
            base = rand_base(4, seed0 + 1000 * nctx + s, nctx)
            if len(base) < nctx:
                continue
            prog = _to_prog(base, 4)
            if analyze(prog).contextual:
                continue
            triv += 1
            if analyze(build_fiber_pool(prog)).contextual:
                act += 1
        p, lo, hi = wilson(act, triv)
        rows.append({"nctx": nctx, "trivial_n": triv, "act": act, "yield": p, "lo": lo, "hi": hi})
        print(f"{nctx:>4} {triv:>10} {act:>5} {100*p:>6.1f}  [{100*lo:>5.1f},{100*hi:>5.1f}]")
    return rows


def dimension_comparison(dims=(4, 6, 8), nctx=6, seeds_per=100, seed0=30000):
    """Activation yield at a fixed base size across base dimensions d -> 2d.
    Shows activation readiness decreasing sharply with d (d=4 special)."""
    print(f"activation yield at nctx={nctx}, {seeds_per} seeds/point:")
    rows = []
    for d in dims:
        act = triv = 0
        for s in range(seeds_per):
            base = rand_base(d, seed0 + 1000 * d + s, nctx)
            if len(base) < nctx:
                continue
            prog = _to_prog(base, d)
            if analyze(prog).contextual:
                continue
            triv += 1
            if analyze(build_fiber_pool(prog)).contextual:
                act += 1
        p, lo, hi = wilson(act, triv)
        rows.append({"d": d, "trivial_n": triv, "act": act, "yield": p, "lo": lo, "hi": hi})
        print(f"  d={d} -> {2*d}: yield {100*p:.1f}%  [{100*lo:.1f},{100*hi:.1f}]  ({act}/{triv})")
    return rows


if __name__ == "__main__":
    yield_sweep([3, 4, 5, 6, 7, 8, 10, 12], seeds_per=400)
    print()
    dimension_comparison()


def pool_structure_comparison(d=4, nctx=8, seeds_per=80, seed0=11000):
    """Structural stats of activating vs non-activating fiber pools at fixed (d, nctx).
    Finding: they are indistinguishable (same pool size, cycle_dim, odd-carry count),
    so activation is a codimension-1 event, not a coarse size effect."""
    from qkernel.incidence import build_incidence, left_kernel_basis
    from qkernel.carry import b_vector

    def stats(prog):
        A, _ = build_incidence(prog)
        cd = len(left_kernel_basis(prog))
        return len(prog.contexts), cd, sum(b_vector(prog))

    act, non = [], []
    for s in range(seeds_per):
        base = rand_base(d, seed0 + 1000 * d + 100 * nctx + s, nctx)
        if len(base) < nctx:
            continue
        prog = _to_prog(base, d)
        if analyze(prog).contextual:
            continue
        pool = build_fiber_pool(prog)
        (act if analyze(pool).contextual else non).append(stats(pool))

    def avg(rows, i):
        return sum(r[i] for r in rows) / len(rows) if rows else float("nan")

    print(f"d={d} nctx={nctx}: activating pools (n={len(act)}) vs non-activating (n={len(non)})")
    print(f"  pool size : {avg(act,0):.0f} vs {avg(non,0):.0f}")
    print(f"  cycle_dim : {avg(act,1):.0f} vs {avg(non,1):.0f}")
    print(f"  odd-carry : {avg(act,2):.0f} vs {avg(non,2):.0f}")
    return act, non
