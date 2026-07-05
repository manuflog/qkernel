# Application Strategy

This repository should stay narrow at first. The best application is not a universal quantum compiler and not a vague claim that contextuality is "free fuel."

The strongest application is:

> contextuality kernel extraction for Weyl/Pauli measurement programs.

## Core product

Given a context family:

1. validate commuting Weyl/Pauli contexts;
2. compute the commutator-carry vector `b`;
3. build the context-observable incidence matrix `A`;
4. find cycles `lambda` with `A^T lambda = 0`;
5. find a minimum odd-Q cycle with `b^T lambda = 1`;
6. return the smallest obstruction-carrying kernel.

## Why this is the right first product

The uploaded Q-criterion note gives an exact finite test:

```text
F is contextual iff some cycle lambda has lambda · b = Q(lambda) = 1.
```

The same note also shows why this should not be marketed as an additive resource meter: the obstruction saturates under stacking. It is a support/indicator of the anomaly, not the additive anomaly charge.

Therefore Q-Kernel should expose:

```text
large measurement program -> minimal contextual kernel
```

not:

```text
large measurement program -> scalar magic fuel amount
```

## Near-term applications

1. Certificate compression.
2. Compiler diagnostics.
3. Benchmark generation.
4. Qudit d=4,6,8 certificate exploration.
5. Later: resource-estimation experiments comparing kernel features with T-count, T-depth, magic injections, and stabilizer rank.

## Novelty-safe positioning

The novelty ledger says to treat these as known:

- basic even-d cohomological obstruction;
- even/odd dichotomy;
- existence of KS/AvN obstruction;
- symplectic commutator form.

It flags these as stronger candidate-new cores:

- exact value spectrum `{0, d/2}`;
- 2-adic carry/tower formulas;
- depth rigidity and value-bit formula;
- explicit high-d certificates.

So the software claim should be:

> We implement a finite, exact, kernelizing compiler-analysis pass for the odd-Q Weyl contextuality criterion.

Avoid claiming:

> first contextuality software;
> exact T-count optimization;
> universal magic-state lower bound.

Those require later bridge theorems.
