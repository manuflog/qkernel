# Quick Summary for Gemini

We are building **Q-Kernel**, a conservative research-software implementation of an odd-Q contextuality criterion for Weyl/Pauli measurement families.

## Core mathematical object

Given a family of Weyl/Pauli contexts, build:

```text
A = context-observable incidence matrix over GF(2)
b = commutator-carry vector
```

A contextuality certificate is a vector `lambda` such that:

```text
A^T lambda = 0 mod 2
b^T lambda = 1 mod 2
```

For even local dimension `d`, the uploaded Q-criterion note identifies this with odd `Q(lambda)`.

## What Q-Kernel does

Q-Kernel turns that theorem into a compiler-style analysis primitive:

```text
large Weyl/Pauli measurement family
        -> smallest odd-Q contextual kernel
        -> standalone verifiable certificate
```

## Current software state

Implemented:

- Weyl JSON input;
- Pauli-string context input;
- grouped Pauli schedule input;
- dependency-free Pauli table adapter for future Qiskit/Stim frontends;
- metadata-aware IR distinguishing `identity_scope="observable"` from `identity_scope="event"`;
- safe and force canonicalization;
- context-observable component decomposition;
- DIMACS SAT export for fixed-weight external solver workflows;
- WCNF/MaxSAT export for direct minimum-kernel optimization;
- external solver-output import with independent verification;
- exact solvers:
  - cycle-span enumeration;
  - bounded-weight search;
  - branch-and-bound with suffix-span pruning;
- independent certificate verifier;
- stable JSON certificate format bound to program SHA-256;
- certificate metadata:
  - qkernel version;
  - coordinate convention;
  - integer carry rule;
  - criterion ID;
- synthetic benchmarks for decomposition and solver comparison;
- arXiv-style software/application note.

Current test count: 36+ tests, all passing in the local runtime.

## Positioning

Safe claim:

> Q-Kernel is an exact contextuality kernel extractor for Weyl/Pauli measurement programs.

Unsafe claim:

> Q-Kernel is already a magic-state or T-count optimizer.

Why unsafe: the odd-Q obstruction is a contextuality certificate. The bridge to T-count, T-depth, stabilizer rank, magic injections, or distillation cost is not yet proved.

## Best next technical directions

1. Optional SAT/MaxSAT/MILP backend for minimum odd-Q kernel search.
2. Qiskit/Stim adapters with explicit identity semantics.
3. More realistic benchmark families.
4. Empirical resource-correlation experiments only after the compiler input semantics are clean.
