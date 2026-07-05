"""Dense Pauli families: high cycle-dimension stress inputs.

The full set of commuting Pauli triples on ``m`` qubits (the lines of the
symplectic space) shares observables heavily, so the cycle space grows fast:

    m=2 -> cycle_dim 5      (exact enumeration fine)
    m=3 -> cycle_dim 259    (2^259 -- exact enumeration infeasible)
    m=4 -> cycle_dim 5109   (2^5109)

These families are state-independent contextual (they contain Peres-Mermin
squares), so they are exactly the regime where exhaustive cycle enumeration is
impossible but the sparse-cycle heuristic still finds the minimal odd-Q kernel.
"""
from __future__ import annotations

import itertools

from qkernel.ir import WeylProgram


def _symplectic(a: tuple[int, ...], b: tuple[int, ...], m: int) -> int:
    s = 0
    for i in range(m):
        s ^= a[2 * i] * b[2 * i + 1] ^ a[2 * i + 1] * b[2 * i]
    return s & 1


def dense_pauli_triples(m: int) -> WeylProgram:
    """All commuting Pauli triples {a, b, a+b} on m qubits (d=2), interleaved
    coordinates [z1, x1, ..., zm, xm]. Cycle dimension grows super-linearly in m."""
    dim = 2 * m
    vecs = [tuple((k >> i) & 1 for i in range(dim)) for k in range(1, 1 << dim)]
    observables: dict[str, list[int]] = {}

    def name(v: tuple[int, ...]) -> str:
        key = "".join(map(str, v))
        observables[key] = list(v)
        return key

    contexts: list[list[str]] = []
    seen: set = set()
    for a, b in itertools.combinations(vecs, 2):
        if _symplectic(a, b, m):
            continue
        c = tuple(a[i] ^ b[i] for i in range(dim))
        if not any(c):
            continue
        triple = frozenset([a, b, c])
        if len(triple) == 3 and triple not in seen:
            seen.add(triple)
            contexts.append([name(a), name(b), name(c)])

    return WeylProgram(d=2, m=m, observables=observables, contexts=contexts)
