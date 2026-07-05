# SAT / SMT Backend Plan

Gemini's strongest useful suggestion was to add a solver backend based on SAT/SMT/MILP-style optimization.

## Exact problem

Given incidence matrix `A` and carry vector `b`, solve:

```text
minimize sum(lambda_i)
subject to:
    for each observable j:
        XOR_i A[i,j] * lambda_i = 0
    XOR_i b[i] * lambda_i = 1
    lambda_i in {0,1}
```

This is the minimum odd-carry cycle problem.

## Implemented in v0.13

Q-Kernel now exports DIMACS CNF for the odd-Q feasibility problem using Tseitin parity encodings. Q-Kernel v0.14 adds WCNF/MaxSAT export for the direct minimum-kernel objective. These are external-solver bridges, not hard dependencies.

## Baseline before external solvers

Q-Kernel v0.9 adds a pure-Python branch-and-bound solver with suffix-span feasibility pruning. This is the baseline that any future SAT/SMT/MILP backend must beat on structured instances.

## Candidate encodings

### SAT

Use XOR clauses if the backend supports them, or Tseitin-encode parity constraints.

Pros:
- direct Boolean encoding;
- fast for parity-heavy problems if XOR-aware.

Cons:
- cardinality minimization requires iterative deepening or MaxSAT.

### SMT / Z3

Use Bool variables and parity expressed with `Xor`.

Pros:
- easy prototype;
- good for theorem-search workflows.

Cons:
- may be slower than specialized SAT/MaxSAT for large parity instances.

### MILP / CP-SAT

Use binary variables and integer equalities:

```text
sum_i A[i,j] lambda_i = 2 k_j
sum_i b[i] lambda_i = 2 t + 1
```

Pros:
- native objective minimization;
- easy minimum-weight formulation.

Cons:
- dependency footprint; solver availability.

## Implementation plan

Add:

```text
src/qkernel/solver_milp.py
src/qkernel/solver_z3.py
```

but keep them optional extras:

```toml
[project.optional-dependencies]
solvers = ["z3-solver", "ortools"]
```

The core package must remain pure Python and dependency-light.

## Verification rule

Every external solver output remains untrusted until passed through:

```python
qkernel.verify.verify_kernel(program, kernel)
```

## Scientific warning

Solver-backed certificate search is not a proof of the general 2-adic tower theorem. It is evidence, certificate generation, and bounded search. General claims still need mathematical proof.
