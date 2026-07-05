# MaxSAT / WCNF Export

Q-Kernel v0.14 adds dependency-free WCNF export for the exact minimum odd-Q kernel problem.

## Problem encoded

Hard clauses:

```text
A^T lambda = 0 mod 2
b^T lambda = 1 mod 2
```

Soft clauses:

```text
-lambda_i    weight 1
```

Violating soft clause `-lambda_i` means selecting context `i`. Therefore minimizing total soft cost minimizes:

```text
sum(lambda_i)
```

This is the minimum contextual kernel objective.

## CLI

```bash
qkernel export-maxsat examples/peres_mermin_pauli.json \
  --input pauli \
  --out pm.wcnf
```

## Why WCNF matters

SAT export answers:

```text
is there a solution with |lambda| <= k?
```

WCNF/MaxSAT asks directly:

```text
what is the minimum |lambda|?
```

This is exactly the optimization problem Q-Kernel solves internally.

## External solvers

The WCNF file can be passed to any compatible MaxSAT solver. The solver output should be converted back into a lambda vector and independently checked with Q-Kernel's verifier.

## Caveat

This is export only. Q-Kernel does not yet parse MaxSAT solver output or invoke external solvers. That is deliberate: the core package remains dependency-light and reproducible.
