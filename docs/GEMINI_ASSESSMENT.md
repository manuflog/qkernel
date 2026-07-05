# Gemini Assessment — Triage

This document records the useful parts of the Gemini assessment and the parts that should not be accepted as stated.

## What Gemini got right

### 1. The project is computationally well posed

The odd-Q note reduces the Weyl-family obstruction to finite data:

```text
A^T lambda = 0 mod 2
b^T lambda = 1 mod 2
```

This is exactly the kind of object that belongs in software: incidence matrices, GF(2) cycles, carry bits, and certificate verification.

### 2. SAT / SMT is a serious next direction

The minimum-kernel problem is naturally constraint-based. A SAT/SMT/MILP backend could search for odd-Q cycles without enumerating the whole cycle space.

However, the right first target is not vague "SMT for everything." The precise target is:

```text
find lambda in {0,1}^r
such that A^T lambda = 0
and b^T lambda = 1
minimizing |lambda|
```

For fixed A and b, this is already a Boolean cardinality/parity optimization problem. Z3, CP-SAT, or MILP can all attack it.

### 3. The verification pipeline should be unified

Gemini correctly identified that scattered scripts should become a coherent pipeline. Q-Kernel is now moving in that direction:

- analyzers;
- solvers;
- independent verifier;
- decomposition;
- canonicalization;
- metadata-aware IR;
- experiments.

## What Gemini overstated or got wrong

### 1. "Passive dimension embedding is a free operation" is not safe

Gemini says passive dimension embedding `Z_d -> Z_2d` is a free operation requiring no entanglement or magic. That is too strong.

Even if the algebraic label embedding is formally simple, a physical qudit compiler must implement:

- a larger Hilbert space;
- hardware-supported control in dimension `2d`;
- compatible gates and measurements;
- error correction / calibration in the lifted space;
- state preparation and readout in the higher-dimensional system.

That is not automatically free.

Safe wording:

> The d -> 2d lift may be an algebraically simple transformation that activates the obstruction in some families. Whether it is operationally cheap or useful for hardware is a separate compiler/hardware question.

### 2. "Intentionally trigger contextuality to optimize magic-state distillation" is not proven

This is the biggest overreach.

The odd-Q kernel is a contextuality certificate. It is not yet a theorem-level resource lower bound or optimizer for:

- T-count;
- T-depth;
- magic-state injections;
- distillation cost;
- stabilizer rank.

Safe wording:

> The odd-Q kernel can be tested as a compiler feature and compared empirically with resource metrics. A bridge theorem is future work.

### 3. "Use Gemini API to orchestrate verification" is not the core scientific need

An LLM/API orchestration layer may help workflow automation, but it should not be central to the research claim. The core must be deterministic and reproducible.

Safe priority:

1. deterministic Python package;
2. exact verifier;
3. reproducible benchmark scripts;
4. optional LLM assistance only for report generation or experiment planning.

### 4. SAT/SMT should not replace proofs

SAT/SMT can find certificates and disprove bounded searches. It does not automatically prove the general 2-adic tower statements unless the quantified theorem is encoded correctly. For general theorems, use solver output as evidence or proof assistant input, not as a substitute for a mathematical proof.

## Decision

Gemini's best contribution is this:

> add SAT/SMT/MILP-style solver backends and automated benchmarks.

Gemini's weak contribution is the resource/compilers overclaim.

Immediate project direction remains:

```text
exact kernel extractor
+ scalable solvers
+ reproducible experiments
+ conservative compiler positioning
```

not:

```text
magic-state optimizer
```
