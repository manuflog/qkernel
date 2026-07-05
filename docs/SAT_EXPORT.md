# SAT / DIMACS Export

Q-Kernel v0.13 adds a dependency-free SAT export for the odd-Q feasibility problem.

## Problem encoded

For context-selection bits `lambda_i`, Q-Kernel exports CNF constraints for:

```text
A^T lambda = 0 mod 2
b^T lambda = 1 mod 2
```

Optional:

```text
sum(lambda_i) <= k
```

This gives an external SAT workflow for minimum-kernel search:

```text
for k = 1,2,3,...
    export CNF with --max-weight k
    run external SAT solver
    first SAT k is the minimum weight
```

## CLI

```bash
qkernel export-sat examples/peres_mermin_pauli.json \
  --input pauli \
  --max-weight 6 \
  --out pm_k6.cnf
```

## Why SAT export before a hard solver dependency?

This lets us integrate with any external solver without adding package dependencies:

- CaDiCaL
- Kissat
- CryptoMiniSat
- PySAT/RC2
- MaxSAT tools
- custom SAT infrastructure

The core package remains pure Python.

## Encoding

Every context becomes a variable:

```text
lambda_i = context i selected
```

Every parity condition is Tseitin-encoded into CNF.

The exported DIMACS file includes comments:

```text
c qkernel_dimacs_v1
c criterion odd_Q_even_d_v1
c coordinate_convention interleaved_zx_v1
c lambda_var 1 context_index 0
```

## Caveat

The cardinality constraint currently uses a naive at-most-k encoding. This is acceptable for small exports and tests, but a real MaxSAT or cardinality-network backend is needed for large instances.


## See also

For direct minimization instead of fixed-k feasibility, use WCNF export:

```bash
qkernel export-maxsat examples/peres_mermin_pauli.json --input pauli --out pm.wcnf
```
