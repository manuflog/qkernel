# Challenges / Things Not Yet Proven

This document is deliberately adversarial. It exists to prevent the project from overclaiming.

## 1. Context extraction is not automatic from a raw observable set

A list of Pauli strings is not a measurement program.

Contextuality depends on actual contexts: which observables are co-measured, jointly constrained, or grouped by the protocol. If the tool infers all possible compatible triples from a raw observable set, it may create contextuality that was not present in the actual schedule.

Safe input:

```json
{
  "type": "pauli_schedule",
  "layers": [
    ["ZI", "IZ", "ZZ"],
    ["IX", "XI", "XX"]
  ]
}
```

Unsafe input:

```json
{
  "observables": ["ZI", "IZ", "ZZ", "IX", "XI", "XX", "..."]
}
```

The second format lacks context semantics.

## 2. Minimum odd-Q kernel search may become hard

The core optimization

```text
minimize |lambda|
subject to A^T lambda = 0 mod 2
           b^T lambda = 1 mod 2
```

is structurally a minimum-weight coset/codeword-style problem over GF(2). The current brute-force cycle-basis enumeration is correct for small examples, not a scalable solver.

Next backends:

- branch and bound;
- MILP / CP-SAT;
- sparse-cycle heuristics;
- certificate-first verification.

## 3. This is not a T-count theorem

The odd-Q kernel is a contextuality certificate. It is not yet a proven lower bound on:

- T-count;
- T-depth;
- magic-state injections;
- distillation overhead;
- stabilizer rank.

The bridge theorem is future work.

## 4. The anomaly language must stay narrow

The Q-criterion note reads the obstruction as the support/indicator of a Pontryagin anomaly, not the additive anomaly charge. Therefore the software should not expose an additive "contextual fuel gauge" unless a new theorem justifies it.

## 5. Odd local dimension is not "classical forever"

The current state-independent Weyl obstruction vanishes in odd d. That does not mean all odd-dimensional quantum computation is classically trivial. It only means this specific Weyl/AvN obstruction is zero.

## 6. Novelty must be phrased carefully

Known, do not claim:

- even-d cohomological obstruction exists;
- even/odd dichotomy in stabilizer/Weyl settings;
- Peres-Mermin contextuality;
- symplectic commutator form.

Candidate-new core to protect:

- value-spectrum classification `{0, d/2}`;
- 2-adic carry and tower formulas;
- depth rigidity / value-bit formula;
- explicit d=8, d=16 certificates;
- compiler/kernelization use of the odd-Q criterion.


## 7. Observable identity vs observable names

Current decomposition treats observable names as graph nodes. Two different names with identical Weyl vectors are treated as different observables.

This is conservative for protocol analysis, because two equal labels in different schedule locations may be operationally distinct. But for algebraic compression, optional canonicalization by Weyl vector may be useful.

Future option:

```text
canonicalize_observables=True
```

This must be explicit, not automatic.


Q-Kernel now supports `--canonicalize by-vector`, but this is deliberately opt-in. The default remains `none`.


## Tower/doubling scope

Do not certify tower compression or embedding advantage yet. Claude-side feedback indicates the repeat-free subclass has a closed lift-induced carry formula, but repeat-observable corrections remain open. Any tower/doubling feature must remain experimental.

Also do not describe passive embedding as free. Algebraic lifting may be simple, but operationally the activated resource can be dilute and hardware/compiler overhead is not settled.


## Novelty hygiene: finite geometry prior art

Do not claim novelty for the GF(2) linear-system framing or the binary symplectic polar-space view of multi-qubit Pauli contextuality. Cite the Saniga/Holweck/de Boutray/Muller finite-geometric work.

The safer novelty target is the closed odd-Q carry/kernel/certificate implementation, qudit-aware scope, and software architecture.
