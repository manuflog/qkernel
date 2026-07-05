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
2. otherwise use `bounded-weight`.

This is a baseline policy, not a final research-grade solver.

## Future backends

- branch and bound over GF(2);
- MILP / CP-SAT;
- sparse-cycle heuristics;
- meet-in-the-middle for moderate cycle dimension;
- external solver with independent certificate verification.

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
