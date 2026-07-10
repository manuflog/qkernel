"""Export a contextuality kernel to a runnable Qiskit measurement protocol.

This bridges theory -> certificate -> runnable hardware test. Given a two-qubit
(d=2, m=2) Weyl/Pauli program and a selection of contexts, it synthesises, for
each context, a *sequential non-destructive* measurement of the three commuting
observables: each observable is measured into its own classical bit via an
ancilla Hadamard-test (H, controlled-P, H, measure, reset), and the context
statistic is the shot-by-shot product of the three measured eigenvalues.

Why sequential and not a single joint measurement.  The three observables of a
context multiply to the scalar sign*I, so if one diagonalises the context and
reads all three eigenvalues from a *single* basis label, the product is
sign*(o0*o1)^2 = sign on *every* shot -- an algebraic identity independent of the
device.  Such a statistic returns the ideal value even on random counts and
therefore certifies nothing.  Measuring the three observables in *physically
separate* operations (this protocol) is what lets device error genuinely pull the
correlator below the ideal, so that S > NC-bound is a real certification.  (This
is the pinned-statistic pitfall; the emitted protocol avoids it by construction,
and the test-suite guards against regressions to it.)

Scope guard.  Synthesis here is for two-qubit Pauli contexts (d=2, m=2).  For
d>2 or m>2 the function refuses rather than emit an unverified circuit: a genuine
qudit (d>=4) protocol needs a Z_d phase readout whose depth is validated
separately (and is impractical on current hardware -- see the papers).

The emitted artifact is a standalone Python script depending only on ``qiskit``
and ``qiskit_ibm_runtime`` at run time, so it runs on IBM hardware without
qkernel installed.  It pins every context to one low-error qubit triple, enables
dynamical decoupling and twirling, and reports per-context values with error
bars and the significance of S above the noncontextual bound.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .ir import WeylProgram
from .valuation import context_phase_vector


# ---- symplectic vector <-> Pauli label (interleaved [z1,x1,z2,x2] convention) ----

_PAULI_FROM_ZX = {(0, 0): "I", (1, 0): "Z", (0, 1): "X", (1, 1): "Y"}


def vector_to_pauli_label(vec: tuple[int, ...], m: int) -> str:
    """Map an interleaved [z1,x1,...,zm,xm] mod-2 vector to an m-qubit Pauli label."""
    if len(vec) != 2 * m:
        raise ValueError(f"vector length {len(vec)} != 2*m ({2 * m})")
    label = []
    for i in range(m):
        z = vec[2 * i] % 2
        x = vec[2 * i + 1] % 2
        label.append(_PAULI_FROM_ZX[(z, x)])
    return "".join(label)


def _context_product_sign(labels: list[str]) -> int | None:
    """Return s in {+1,-1} if the 3 Paulis pairwise commute and multiply to s*I;
    None otherwise.  Uses qiskit.quantum_info.Pauli (lazily imported)."""
    from qiskit.quantum_info import Pauli
    import numpy as np

    ps = [Pauli(l) for l in labels]
    for i in range(len(ps)):
        for j in range(i + 1, len(ps)):
            if not ps[i].commutes(ps[j]):
                return None
    prod = ps[0]
    for p in ps[1:]:
        prod = prod.compose(p)
    # prod must be +-I (no X/Z support), phase encodes the sign
    if prod.x.any() or prod.z.any():
        return None
    # Pauli.phase: group phase in units of -i; for a real +-I it is 0 (=> +I) or 2 (=> -I)
    ph = int(prod.phase) % 4
    if ph == 0:
        return 1
    if ph == 2:
        return -1
    return None  # +-iI should not occur for a genuine commuting real context


@dataclass(frozen=True)
class ExportedProtocol:
    n_contexts: int
    context_labels: list[list[str]]
    context_signs: list[int]
    script: str


def tight_nc_bound(labels, signs):
    """Exact noncontextual bound of S = sum_i sign_i*<prod_i> over deterministic +/-1
    assignments (exhaustive for <=20 observables; loose nc-1 fallback above that).
    A violated constraint contributes -1, so the exact bound is typically nc-2*k_min."""
    names = sorted({o for C in labels for o in C})
    if len(names) > 20:
        return float(len(labels) - 1)
    import itertools
    best = -float("inf")
    for bits in itertools.product((1, -1), repeat=len(names)):
        val = dict(zip(names, bits))
        s = 0
        for C, sg in zip(labels, signs):
            p = 1
            for o in C:
                p *= val[o]
            s += sg * p
        best = max(best, s)
    return float(best)


def export_qiskit_protocol(
    program: WeylProgram,
    selected_contexts: list[int] | None = None,
    verify: bool = True,
) -> ExportedProtocol:
    """Synthesise a runnable Qiskit *sequential-measurement* protocol for a 2-qubit
    Weyl program.

    Raises ValueError (scope guard) if d != 2 or m != 2, if any context is not a
    genuine 3-element commuting Pauli context multiplying to +-I, or (when
    ``verify``) if the derived sign disagrees with the program's phase vector.
    """
    if program.d != 2:
        raise ValueError(
            f"export_qiskit_protocol: d=2 required (got d={program.d}); "
            "qudit (d>=4) protocols need a validated Z_d phase readout, not emitted here."
        )
    if program.m != 2:
        raise ValueError(f"export_qiskit_protocol: m=2 required (got m={program.m}).")

    phases = context_phase_vector(program)
    ctx_indices = selected_contexts if selected_contexts is not None else list(range(len(program.contexts)))

    context_labels: list[list[str]] = []
    context_signs: list[int] = []
    for ci in ctx_indices:
        ctx = program.contexts[ci]
        if len(ctx) != 3:
            raise ValueError(f"context {ci} has {len(ctx)} observables; 2-qubit synthesis expects 3.")
        labels = [vector_to_pauli_label(tuple(program.observables[name]), program.m) for name in ctx]
        derived = _context_product_sign(labels)
        if derived is None:
            raise ValueError(
                f"context {ci} {labels} is not a commuting triple multiplying to +-I; refusing to emit."
            )
        phase_sign = -1 if phases[ci] % 2 == 1 else 1
        if verify and derived != phase_sign:
            raise ValueError(
                f"context {ci} {labels}: product sign {derived} disagrees with phase-derived "
                f"sign {phase_sign}; refusing to emit."
            )
        context_labels.append(labels)
        context_signs.append(derived)

    script = _render_script(context_labels, context_signs)
    return ExportedProtocol(
        n_contexts=len(ctx_indices),
        context_labels=context_labels,
        context_signs=context_signs,
        script=script,
    )


def _render_script(labels: list[list[str]], signs: list[int]) -> str:
    """Render a standalone runnable IBM Qiskit script emitting the sequential
    non-destructive protocol (genuine, noise-sensitive)."""
    contexts = {f"C{i}": (labels[i], signs[i]) for i in range(len(labels))}
    nc = len(labels)
    nc_bound = tight_nc_bound(labels, signs)  # exact deterministic bound (loose fallback inside)
    return (
        '"""Runnable IBM contextuality protocol, exported by qkernel export-circuit.\n'
        "Sequential non-destructive (ancilla Hadamard-test) measurement of each context's\n"
        "three commuting observables -- a genuine, noise-sensitive statistic (NOT the\n"
        "algebraically-pinned single-joint-measurement, which returns the ideal value on any\n"
        'data).  2 data qubits + 1 ancilla; DD + twirling; pinned to one low-error triple.\n"""\n'
        "import math\n"
        "from qiskit import QuantumCircuit, transpile, QuantumRegister, ClassicalRegister\n"
        "from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler\n\n"
        f"CONTEXTS = {contexts!r}\n"
        f"NC_BOUND = {nc_bound}\n"
        f"IDEAL = {float(nc)}\n\n"
        "def _ctrl(qc, anc, q, P):\n"
        "    if P == 'I': return\n"
        "    if P == 'X': qc.cx(anc, q)\n"
        "    elif P == 'Z': qc.cz(anc, q)\n"
        "    elif P == 'Y': qc.sdg(q); qc.cx(anc, q); qc.s(q)\n\n"
        "def _measure_obs(qc, data, anc, cbit, label):\n"
        "    qc.h(anc); _ctrl(qc, anc, data[0], label[0]); _ctrl(qc, anc, data[1], label[1])\n"
        "    qc.h(anc); qc.measure(anc, cbit); qc.reset(anc)\n\n"
        "def build(name):\n"
        "    data = QuantumRegister(2, 'd'); anc = QuantumRegister(1, 'a'); c = ClassicalRegister(3, 'c')\n"
        "    qc = QuantumCircuit(data, anc, c)\n"
        "    labels, _ = CONTEXTS[name]\n"
        "    for j, lab in enumerate(labels):\n"
        "        _measure_obs(qc, data, anc[0], c[j], lab)\n"
        "    return qc\n\n"
        "def product_expectation(name, counts):\n"
        "    # shot-by-shot product of the THREE separately-measured ancilla parities\n"
        "    tot = sum(counts.values()); acc = 0.0\n"
        "    for bits, cnt in counts.items():\n"
        "        b = bits.replace(' ', ''); o = [(-1)**int(b[-1-j]) for j in range(3)]\n"
        "        acc += o[0]*o[1]*o[2] * cnt\n"
        "    return acc / tot\n\n"
        "def _se(counts):\n"
        "    tot = sum(counts.values()); even = sum(c for b,c in counts.items() if b.replace(' ','').count('1')%2==0)\n"
        "    p = even/tot; return math.sqrt(max(4*p*(1-p)/tot, 0.0))\n\n"
        "def _best_triple(backend):\n"
        "    t = backend.target; edges = set(t.build_coupling_map().get_edges()); nq = t.num_qubits\n"
        "    def ro(q):\n"
        "        try: return t['measure'][(q,)].error or 0.05\n"
        "        except Exception: return 0.05\n"
        "    tw = [g for g in ['cz','ecr','cx'] if g in t.operation_names]\n"
        "    def ee(a,b):\n"
        "        for g in tw:\n"
        "            for pr in [(a,b),(b,a)]:\n"
        "                try:\n"
        "                    e = t[g][pr].error\n"
        "                    if e is not None: return e\n"
        "                except Exception: pass\n"
        "        return 0.05\n"
        "    nbr = {q:set() for q in range(nq)}\n"
        "    for a,b in edges: nbr[a].add(b); nbr[b].add(a)\n"
        "    best=None; bs=1e9\n"
        "    for anc in range(nq):\n"
        "        nb=list(nbr[anc])\n"
        "        for i in range(len(nb)):\n"
        "            for j in range(i+1,len(nb)):\n"
        "                d0,d1=nb[i],nb[j]; s=ro(anc)+ro(d0)+ro(d1)+ee(anc,d0)+ee(anc,d1)\n"
        "                if s<bs: bs=s; best=[d0,d1,anc]\n"
        "    return best\n\n"
        "if __name__ == '__main__':\n"
        "    import os\n"
        "    service = QiskitRuntimeService(token=os.environ.get('QISKIT_IBM_TOKEN'))\n"
        "    backend = service.least_busy(operational=True, simulator=False, min_num_qubits=3)\n"
        "    print('Backend:', backend.name)\n"
        "    layout = _best_triple(backend); print('Qubit triple [d0,d1,anc]:', layout)\n"
        "    sampler = Sampler(mode=backend)\n"
        "    sampler.options.dynamical_decoupling.enable = True\n"
        "    sampler.options.dynamical_decoupling.sequence_type = 'XpXm'\n"
        "    sampler.options.twirling.enable_gates = True\n"
        "    sampler.options.twirling.enable_measure = True\n"
        "    S = 0.0; Svar = 0.0\n"
        "    for name, (obs, sgn) in CONTEXTS.items():\n"
        "        qc = transpile(build(name), backend, initial_layout=layout, optimization_level=1)\n"
        "        counts = sampler.run([qc], shots=8192).result()[0].data.c.get_counts()\n"
        "        val = product_expectation(name, counts); se = _se(counts); S += sgn*val; Svar += se*se\n"
        "        print(f'{name} {obs}: <prod>={val:+.3f} +/- {se:.3f} (ideal {sgn:+d})')\n"
        "    SE = Svar**0.5\n"
        "    print(f'\\nS = {S:.4f} +/- {SE:.4f}   NC bound = {NC_BOUND}   ideal = {IDEAL}')\n"
        "    print(f'({(S-NC_BOUND)/SE:.1f} sigma above bound)' if SE>0 else '')\n"
        "    print('CONTEXTUALITY CERTIFIED' if S - 2*SE > NC_BOUND else 'no clean violation - check calibration/backend')\n"
    )
