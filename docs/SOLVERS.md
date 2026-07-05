# Solver Backends

The kernelization problem is:

```text
minimize |lambda|
subject to A^T lambda = 0 mod 2
           b^T lambda = 1 mod 2
```

This is a minimum-weight odd-carry cycle problem over GF(2).

## Current backends

### `span`

Enumerates the span of a cycle-space basis.

Strengths:

- exact;
- fast when cycle dimension is small;
- works well on Peres-Mermin and noisy examples where irrelevant disconnected contexts do not enlarge the cycle space much.

Weakness:

- exponential in cycle-space dimension.

### `bounded-weight`

Searches context subsets by increasing Hamming weight up to a bound.

Strengths:

- exact up to `max_weight`;
- good when the expected certificate is very small.

Weakness:

- combinatorial in number of contexts;
- not safe as an unbounded large-instance solver.

### `auto`

Current policy:

1. use `span` if cycle dimension <= `max_cycle_dim`;
2. otherwise try `bounded-weight`, then `branch-bound`;
3. if the exact backends exhaust their budget (return nothing or raise), fall back to
   the `heuristic` — so `auto` never crashes on high cycle-dimension families.

## Delivered since this doc was first written

- branch and bound over GF(2) — **done** (`branch-bound`, below);
- sparse-cycle heuristics — **done** (`heuristic`, below);
- MILP / CP-SAT — **done** (`cpsat`, below).

Still future: meet-in-the-middle for moderate cycle dimension.

### `heuristic`

Minimum-weight coset-leader local search. The odd cycles form an affine coset
`c0 + <even cycles>` in the GF(2) cycle space; starting from an odd representative,
the search greedily XORs even-cycle basis directions to lower the Hamming weight, with
random restarts to escape local minima.

Strengths:

- polynomial per restart — no `2^dim` enumeration;
- scales to cycle dimension in the thousands (verified to ~5000, dense m=4 Pauli);
- empirically finds the optimum (weight 6) on every dense family tested.

Weakness:

- approximate: returns a low-weight odd cycle without a built-in optimality certificate
  (pair with `cpsat` when a certificate is needed).

### `cpsat`

Independent exact backend via OR-Tools CP-SAT (optional dependency, `pip install
qkernel[cpsat]`). Models the problem as an integer program: binary `lambda_i`, each
observable column forced even (`= 2 k_j`), the carry forced odd (`= 2 k_b + 1`),
minimize `sum lambda_i`. `find_min_odd_cycle_cpsat` returns `(cycle, certified)`.

Strengths:

- a completely separate code path (integer programming vs GF(2) linear algebra) — an
  independent cross-check of the native solvers;
- the LP relaxation prunes by weight rather than enumerating `2^dim`, so it **certifies**
  minimality on high cycle-dimension families where `span` is infeasible: on dense m=3
  (cycle_dim 259) it proves the minimum is weight 6 in ~45s.

Weakness:

- certification has a size ceiling: at m=4 (cycle_dim ~5109) it finds weight 6 but may not
  prove optimality within a short budget.

## Choosing a backend

| need | use |
|---|---|
| small family, exact + internal cross-check | `span` (or `auto`) |
| large family, fast witness | `heuristic` |
| large family, *certified* minimum | `cpsat` |
| independent verification of an answer | `cpsat` vs native |
| every minimal kernel (structure invariant) | `find_all_min_odd_cycles` |
| contextuality yes/no only, never crashes | `analyze` (odd-carry parity) |

## Verification principle

Solver output should be treated as untrusted until verified. Q-Kernel therefore provides:

```python
from qkernel.verify import verify_kernel
```

Verification checks:

1. selected contexts are in range;
2. every selected observable appears with even multiplicity;
3. aggregate Q is odd.

This is cheap and exact, even if the future solver is heuristic.


## Decomposition first

Before invoking a solver, Q-Kernel can split the context-observable bipartite graph into connected components. This is enabled by default in `compress_min_odd_q`.

Reason:

```text
minimum odd certificate of a disconnected union lives inside one component
```

This is the first real scalability improvement. It prevents irrelevant disconnected blocks from inflating the search problem.


### `branch-bound`

Exact pure-Python branch-and-bound with suffix-span feasibility pruning.

It encodes each context as:

```text
state_i = incidence_row_i || carry_bit_i
```

and searches for a subset whose XOR equals:

```text
0...01
```

At every DFS node, it checks whether the remaining suffix span can still reach the residual target. If not, the branch is pruned.

Strengths:

- exact;
- no external dependencies;
- better feasibility pruning than naive subset enumeration.

Weaknesses:

- still exponential in hard cases;
- not a replacement for SAT/MaxSAT/MILP on large difficult instances.
