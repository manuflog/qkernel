# External Solver Output Import

Q-Kernel v0.15 completes the dependency-free external solver loop.

## Workflow

```bash
qkernel export-maxsat examples/peres_mermin_pauli.json --input pauli --out pm.wcnf

# Run external MaxSAT solver separately:
# maxsat_solver pm.wcnf > pm.out

qkernel import-solver-output examples/peres_mermin_pauli.json \
  --input pauli \
  --model pm.wcnf \
  --solution pm.out \
  --out pm_external.cert.json
```

## Supported assignment styles

Signed DIMACS literals:

```text
s SATISFIABLE
v 1 -2 3 0
```

Bitstring:

```text
s OPTIMUM FOUND
v 101001
```

## Trust model

External solvers are treated as untrusted candidate generators.

Q-Kernel imports only the lambda variables identified by comments in the model file:

```text
c lambda_var 1 context_index 0
```

Then it independently verifies:

```text
A^T lambda = 0
Q(lambda) = 1
```

Only verified assignments can be written as Q-Kernel certificates.

## Limitation

Q-Kernel does not currently check that the external assignment satisfies every auxiliary Tseitin clause. It does not need to for trust: it recomputes the actual mathematical certificate from the lambda vector and the original program.
