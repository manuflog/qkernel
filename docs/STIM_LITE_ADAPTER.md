# Stim-lite Adapter

Q-Kernel v0.22 adds a dependency-free Stim-lite adapter.

This is **not** a full Stim parser. It supports a small, explicit subset:

```text
TICK
MPP X0 Z1 X0*Z1
```

Each TICK-delimited block becomes one Pauli schedule layer. Each MPP product token becomes one Pauli observable.

## Why Stim-lite first?

A real Stim dependency should be optional. Before adding that dependency, Q-Kernel needs a stable semantic contract:

```text
Stim / circuit layer
        -> explicit Pauli-product measurement layer
        -> Q-Kernel schedule frontend
```

## Supported syntax

```text
MPP X0
MPP Z0*Z1
MPP X0*Y2*Z5
TICK
```

Signs such as `!X0` are ignored at this boundary because Q-Kernel tracks Weyl labels, not measurement outcome signs.

Unsupported lines are ignored by default and rejected with `--strict`.

## CLI

Inspect parsing:

```bash
qkernel inspect-stim-lite examples/peres_mermin_mpp.stim
```

Analyze:

```bash
qkernel analyze-stim-lite examples/peres_mermin_mpp.stim
```

Compress:

```bash
qkernel compress-stim-lite examples/peres_mermin_mpp.stim --json
```

Use as generic input:

```bash
qkernel certify examples/peres_mermin_mpp.stim --input stim-lite --out pm_stim.cert.json
```

## Scope

Safe:

```text
explicit MPP-family adapter
schedule-layer extraction
research bridge toward real Stim support
```

Unsafe:

```text
full stabilizer circuit semantics
detector-error-model contextuality analysis
automatic extraction from arbitrary Clifford circuits
resource claims
```
