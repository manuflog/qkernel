# Path Toward a Quantum Compiler Optimizer

Q-Kernel can become part of a compiler optimizer, but not by relabeling kernel
compression as resource optimization.

## What Q-Kernel can optimize today

Today Q-Kernel can optimize a *diagnostic object*:

```text
minimum odd-Q contextuality kernel
```

This is useful for:

```text
finding the smallest contextual obstruction
removing irrelevant disconnected components when semantics allow
comparing candidate rewrites
generating audit certificates
```

## What is missing for a true compiler optimizer

A true quantum compiler optimizer needs at least one of:

```text
a theorem linking odd-Q kernels to a compiler resource
an empirical resource model with validated correlation
a semantics-preserving rewrite system
a backend cost model for a specific architecture
```

Without one of those, Q-Kernel should not claim T-count, magic-state, depth, or
hardware-resource optimization.

## Recommended architecture

```text
Circuit / schedule frontend
        ↓
explicit Pauli/Weyl measurement program
        ↓
Q-Kernel diagnostic report
        ↓
candidate rewrite / decomposition / isolation pass
        ↓
external semantic-equivalence proof
        ↓
backend resource model
        ↓
compiler decision
```

## New v0.24 compiler diagnostics

```bash
qkernel compiler-report examples/peres_mermin_pauli.json --input pauli
```

Before/after pass comparison:

```bash
qkernel compare-pass before.json after.json --input pauli
```

The comparison explicitly reports:

```text
requires_semantic_equivalence_proof: true
```

## Safe optimization language

Safe:

```text
Q-Kernel identifies and verifies smaller contextuality kernels.
Q-Kernel can be used as a compiler diagnostic.
Q-Kernel can compare candidate rewrites under an odd-Q certificate metric.
```

Unsafe:

```text
Q-Kernel reduces T-count.
Q-Kernel optimizes magic states.
Q-Kernel proves a circuit rewrite is semantically valid.
Q-Kernel's compression ratio is a resource monotone.
```

## Best next steps

1. Add Qiskit-lite and full Stim adapters.
2. Build a small corpus of known Clifford+T/stabilizer examples.
3. Compare Q-Kernel metrics against known resource metrics.
4. Only then formulate a bridge theorem or empirical optimizer.
