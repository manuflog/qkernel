# Component Decomposition

Q-Kernel v0.5 adds decomposition of the context-observable bipartite graph.

## Graph

Nodes:

- context nodes `C_i`;
- observable nodes `O_name`.

Edges:

- `C_i -- O_name` when observable `O_name` appears in context `C_i`.

## Why decomposition is valid

If the graph splits into disconnected components, then any cycle decomposes as the XOR/sum of cycles inside those components.

An odd-carry global cycle must have odd carry in at least one component. Therefore a minimum odd-Q certificate of a disconnected family lives entirely inside one connected component.

So instead of solving:

```text
whole program
```

we solve:

```text
component 1
component 2
...
component k
```

and keep the smallest odd-Q certificate.

## Why this matters

This directly attacks scaling. Real compiler schedules are likely sparse and locally structured. Noise, unrelated checks, and independent measurement blocks should not enlarge the hard search problem.

## CLI

```bash
qkernel components examples/peres_mermin_with_noise_schedule.json --input schedule
qkernel compress-schedule examples/peres_mermin_with_noise_schedule.json --json
```

## Caveat

Component decomposition is based on observable names, not only Weyl vector equality. Later versions should add optional observable canonicalization so duplicate names representing the same Weyl label can be merged intentionally.
