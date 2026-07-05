"""Experiment design: cheapest contextuality test from a device's measurable Paulis.

Given the Pauli operators a device can measure, this returns the cheapest state-
independent contextuality test(s) to run: the minimal set of measurement contexts
(commuting groups) whose carries cannot be consistently assigned. It is a thin,
pipeline-facing layer over the contextuality subroutine -- the concrete "call qkernel
as a subroutine" use case for experiment design.

Tests are ranked by what an experimentalist pays for: fewer measurement settings
(contexts) first, then fewer distinct observables to calibrate.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

from .analyzer import analyze
from .ir import WeylProgram
from .pauli import pauli_string_to_vector
from .solvers import find_all_min_odd_cycles, find_min_odd_cycle, hamming_weight
from .verify import verify_kernel
from .optimizer import compress_min_odd_q


def _symplectic(a: tuple[int, ...], b: tuple[int, ...]) -> int:
    m = len(a) // 2
    return sum(a[2 * i] * b[2 * i + 1] + a[2 * i + 1] * b[2 * i] for i in range(m)) % 2


@dataclass
class ContextualityTest:
    contexts: list[list[str]]   # measurement settings; each a commuting Pauli triple
    n_contexts: int             # number of measurement settings
    n_observables: int          # distinct Paulis to calibrate
    obstruction_value: int      # resource value d/2
    verified: bool


def _build_context_program(paulis: list[str]):
    """All commuting triples {a, b, a*b} drawable from the measurable Pauli set."""
    vecs = {p: tuple(pauli_string_to_vector(p)) for p in paulis}
    vec_to_name = {v: p for p, v in vecs.items()}
    observables = {p: list(v) for p, v in vecs.items()}
    contexts: list[list[str]] = []
    seen = set()
    names = list(paulis)
    for pa, pb in combinations(names, 2):
        a, b = vecs[pa], vecs[pb]
        if _symplectic(a, b):
            continue  # only commuting pairs form a joint measurement
        c = tuple(a[i] ^ b[i] for i in range(len(a)))
        if not any(c):
            continue
        pc = vec_to_name.get(c)
        if pc is None:
            continue  # product not measurable on this device
        triple = frozenset([pa, pb, pc])
        if len(triple) == 3 and triple not in seen:
            seen.add(triple)
            contexts.append([pa, pb, pc])
    return WeylProgram(d=2, m=len(paulis[0]), observables=observables, contexts=contexts), contexts


def minimal_contextuality_tests(paulis: list[str], *, top: int = 3) -> list[ContextualityTest]:
    """Cheapest state-independent contextuality tests from a device's measurable Paulis.

    Returns up to ``top`` tests ranked by (fewest contexts, fewest distinct observables).
    Empty list if the measurable set supports no contextuality test.
    """
    if not paulis:
        return []
    program, all_contexts = _build_context_program(paulis)
    if not program.contexts or not analyze(program).contextual:
        return []

    cycle_dim_ok = True
    try:
        kernels = find_all_min_odd_cycles(program)
    except ValueError:
        cycle_dim_ok = False
        one = find_min_odd_cycle(program)
        kernels = [one] if one else []

    d = program.d
    tests: list[ContextualityTest] = []
    for lam in kernels:
        sel = [all_contexts[i] for i, bit in enumerate(lam) if bit]
        obs = {p for ctx in sel for p in ctx}
        kernel = compress_min_odd_q(
            WeylProgram(d=d, m=program.m, observables=program.observables, contexts=sel)
        )
        verified = verify_kernel(
            WeylProgram(d=d, m=program.m, observables=program.observables, contexts=sel), kernel
        ).valid
        tests.append(ContextualityTest(
            contexts=sel,
            n_contexts=len(sel),
            n_observables=len(obs),
            obstruction_value=d // 2,
            verified=verified,
        ))

    tests.sort(key=lambda t: (t.n_contexts, t.n_observables))
    return tests[:top]
