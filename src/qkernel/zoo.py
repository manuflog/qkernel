"""Contextuality Benchmark Zoo (v0.41).

A curated registry of small contextuality instances with *expected* verdicts,
so that qkernel's behavior is pinned as a research artifact: every instance
declares what the correct answer is, under which criterion, and what claim
scope that answer supports. ``run_zoo()`` executes the full registry through
``analyze_contextuality`` and reports pass/fail per instance; the test suite
asserts every expectation, making the zoo a permanent regression harness.

Instances (all dependency-free, built in code):

- ``peres_mermin``            the PM square (d=2, m=2): contextual, kernel 6,
                              exactly 1 minimal kernel, Z_d/AvN passes.
- ``noisy_peres_mermin``      PM plus 40 irrelevant commuting contexts:
                              same verdict; exercises kernel extraction in noise.
- ``doily_two_qubit``         all 15 two-qubit Pauli triples (GQ(2,2) doily):
                              contextual, kernel 6, exactly 10 minimal kernels
                              (the 10 Mermin squares of the doily).
- ``single_context``          one commuting triple: non-contextual (no cycle).
- ``odd_d_qutrit``            a d=3 Weyl family: non-contextual under the
                              odd-Q criterion (odd d — criterion is zero), the
                              canonical odd-Q *shadow trap*: no parity claim may
                              be made here regardless of other notions.
- ``cert4_d4``                the verified minimal d=4 certificate: contextual
                              with obstruction value d/2 = 2 (naive 2x-scaled
                              PM is non-contextual and is *not* used).

Claim-scope discipline: expectations are stated per criterion. The zoo pins
the odd-Q verdict and, where the subroutine runs ``verify_kernel``, the
Z_d/AvN outcome recorded in the criterion ledger.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Callable

from .examples import noisy_peres_mermin_program, peres_mermin_program
from .ir import WeylProgram
from .subroutine import ContextualitySubroutineResult, analyze_contextuality

TWO_QUBIT_PAULIS = {
    "IZ": (1, 0, 0, 0), "ZI": (0, 0, 1, 0), "ZZ": (1, 0, 1, 0),
    "IX": (0, 1, 0, 0), "XI": (0, 0, 0, 1), "XX": (0, 1, 0, 1),
    "IY": (1, 1, 0, 0), "YI": (0, 0, 1, 1), "YY": (1, 1, 1, 1),
    "ZX": (1, 0, 0, 1), "XZ": (0, 1, 1, 0),
    "ZY": (1, 0, 1, 1), "YZ": (1, 1, 1, 0),
    "XY": (1, 1, 0, 1), "YX": (0, 1, 1, 1),
}


def _symp2(a, b):
    return (a[0] * b[1] + a[1] * b[0] + a[2] * b[3] + a[3] * b[2]) % 2


def doily_two_qubit_program() -> WeylProgram:
    """All 15 commuting two-qubit Pauli triples: the GQ(2,2) doily."""
    names = list(TWO_QUBIT_PAULIS)
    vec = TWO_QUBIT_PAULIS
    contexts, seen = [], set()
    for a, b in combinations(names, 2):
        if _symp2(vec[a], vec[b]):
            continue
        c = tuple(x ^ y for x, y in zip(vec[a], vec[b]))
        if not any(c):
            continue
        cname = next((n for n, v in vec.items() if v == c), None)
        if cname is None:
            continue
        key = frozenset((a, b, cname))
        if key in seen:
            continue
        seen.add(key)
        contexts.append(sorted(key))
    obs = {n: list(v) for n, v in vec.items()}
    return WeylProgram(d=2, m=2, observables=obs, contexts=contexts)


def single_context_program() -> WeylProgram:
    obs = {"ZI": [0, 0, 1, 0], "IZ": [1, 0, 0, 0], "ZZ": [1, 0, 1, 0]}
    return WeylProgram(d=2, m=2, observables=obs, contexts=[["ZI", "IZ", "ZZ"]])


def odd_d_qutrit_program() -> WeylProgram:
    """A small d=3 Weyl family: the odd-Q criterion is identically zero for odd d."""
    obs = {"Z": [1, 0], "X": [0, 1], "XZ": [1, 1], "X2Z2": [2, 2], "Z2": [2, 0], "X2": [0, 2]}
    contexts = [["Z", "Z2"], ["X", "X2"], ["XZ", "X2Z2"]]
    return WeylProgram(d=3, m=1, observables=obs, contexts=contexts)


CERT4_CONTEXTS = [
    [[0, 0, 2, 0], [2, 0, 0, 0], [2, 0, 2, 0]],
    [[0, 0, 2, 0], [2, 1, 0, 0], [2, 3, 2, 0]],
    [[0, 0, 2, 1], [2, 0, 0, 0], [2, 0, 2, 3]],
    [[0, 0, 2, 1], [2, 1, 0, 0], [2, 3, 2, 3]],
    [[0, 1, 0, 1], [2, 0, 2, 0], [2, 3, 2, 3]],
    [[0, 1, 0, 1], [2, 0, 2, 3], [2, 3, 2, 0]],
]


def cert4_d4_program() -> WeylProgram:
    """The verified minimal d=4 (m=2) certificate with obstruction value d/2 = 2.

    Note: this is *not* a rescaled PM square — naive 2x scaling of PM into d=4
    is non-contextual under the odd-Q criterion (the carry structure does not
    survive scaling); genuine d=4 value-2 contextuality needs this family.
    """
    v2n: dict[tuple, str] = {}
    obs: dict[str, list[int]] = {}
    contexts: list[list[str]] = []
    for C in CERT4_CONTEXTS:
        row = []
        for v in C:
            t = tuple(v)
            if t not in v2n:
                nm = f"w{len(v2n)}"
                v2n[t] = nm
                obs[nm] = list(v)
            row.append(v2n[t])
        contexts.append(row)
    return WeylProgram(d=4, m=2, observables=obs, contexts=contexts)


@dataclass(frozen=True)
class ZooInstance:
    name: str
    builder: Callable[[], WeylProgram]
    expect_contextual: bool
    expect_kernel_weight: int | None          # None when non-contextual
    expect_n_minimal_kernels: int | None      # None when not asserted
    expect_zd_passed: bool | None             # ledger stronger_verifier_passed
    expect_obstruction_value: int | None
    claim_scope: str
    note: str = ""


ZOO: list[ZooInstance] = [
    ZooInstance(
        name="peres_mermin",
        builder=peres_mermin_program,
        expect_contextual=True,
        expect_kernel_weight=6,
        expect_n_minimal_kernels=1,
        expect_zd_passed=True,
        expect_obstruction_value=1,
        claim_scope="state_independent_parity_obstruction; AvN-grade (Z_d verified)",
    ),
    ZooInstance(
        name="noisy_peres_mermin",
        builder=noisy_peres_mermin_program,
        expect_contextual=True,
        expect_kernel_weight=6,
        expect_n_minimal_kernels=None,   # noise contexts may admit extra kernels; not pinned
        expect_zd_passed=True,
        expect_obstruction_value=1,
        claim_scope="state_independent_parity_obstruction; AvN-grade (Z_d verified)",
        note="kernel extraction from 40 irrelevant commuting contexts",
    ),
    ZooInstance(
        name="doily_two_qubit",
        builder=doily_two_qubit_program,
        expect_contextual=True,
        expect_kernel_weight=6,
        expect_n_minimal_kernels=10,     # the 10 Mermin squares of GQ(2,2)
        expect_zd_passed=True,
        expect_obstruction_value=1,
        claim_scope="state_independent_parity_obstruction; AvN-grade (Z_d verified)",
    ),
    ZooInstance(
        name="single_context",
        builder=single_context_program,
        expect_contextual=False,
        expect_kernel_weight=None,
        expect_n_minimal_kernels=0,
        expect_zd_passed=None,
        expect_obstruction_value=0,
        claim_scope="no parity obstruction (cycle space trivial)",
    ),
    ZooInstance(
        name="odd_d_qutrit",
        builder=odd_d_qutrit_program,
        expect_contextual=False,
        expect_kernel_weight=None,
        expect_n_minimal_kernels=0,
        expect_zd_passed=None,
        expect_obstruction_value=0,
        claim_scope=(
            "odd-Q shadow trap: criterion is identically zero for odd d; "
            "no parity claim of any kind is licensed here"
        ),
    ),
    ZooInstance(
        name="cert4_d4",
        builder=cert4_d4_program,
        expect_contextual=True,
        expect_kernel_weight=6,
        expect_n_minimal_kernels=1,
        expect_zd_passed=True,
        expect_obstruction_value=2,
        claim_scope="state_independent_parity_obstruction at d=4; AvN-grade (Z_d verified); value d/2 = 2",
        note="genuine d=4 certificate; naive 2x-scaled PM is non-contextual (see builder docstring)",
    ),
]


@dataclass
class ZooResult:
    name: str
    passed: bool
    result: ContextualitySubroutineResult
    failures: list[str]


def run_instance(inst: ZooInstance) -> ZooResult:
    res = analyze_contextuality(inst.builder(), enumerate_all_kernels=True)
    fails: list[str] = []
    if res.contextual != inst.expect_contextual:
        fails.append(f"contextual={res.contextual}, expected {inst.expect_contextual}")
    if inst.expect_kernel_weight is not None and res.kernel_weight != inst.expect_kernel_weight:
        fails.append(f"kernel_weight={res.kernel_weight}, expected {inst.expect_kernel_weight}")
    if inst.expect_n_minimal_kernels is not None and res.n_minimal_kernels != inst.expect_n_minimal_kernels:
        fails.append(f"n_minimal_kernels={res.n_minimal_kernels}, expected {inst.expect_n_minimal_kernels}")
    if inst.expect_obstruction_value is not None and res.obstruction_value != inst.expect_obstruction_value:
        fails.append(f"obstruction_value={res.obstruction_value}, expected {inst.expect_obstruction_value}")
    if inst.expect_zd_passed is not None:
        led = res.criterion_ledger or {}
        if led.get("stronger_verifier_passed") != inst.expect_zd_passed:
            fails.append(
                f"zd stronger_verifier_passed={led.get('stronger_verifier_passed')}, "
                f"expected {inst.expect_zd_passed}"
            )
    if not res.verified:
        fails.append("kernel failed independent verification")
    return ZooResult(name=inst.name, passed=not fails, result=res, failures=fails)


def run_zoo() -> list[ZooResult]:
    """Run every registered instance; the zoo is green iff all pass."""
    return [run_instance(inst) for inst in ZOO]
