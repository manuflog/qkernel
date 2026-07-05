# Q-Kernel Alpha Overview

Q-Kernel is an alpha-stage research package for extracting, verifying, and reporting
odd-Q / `Z_d` contextuality kernels in Weyl/Pauli measurement programs.

## One-line positioning

```text
Q-Kernel finds small, independently verifiable contextuality kernels.
```

## Not the positioning

```text
not a magic-state optimizer
not a T-count optimizer
not a certified compiler optimizer
not a proof that passive embedding is free
```

## Quick smoke test

```bash
python -m pip install -e .
qkernel self-test
```

Expected:

```json
{
  "ok": true,
  "contextual": true,
  "q_value": 1
}
```

## Core demo

```bash
qkernel compress-pauli examples/peres_mermin_pauli.json --json
qkernel zd-valuation examples/peres_mermin_pauli.json --input pauli
qkernel release-audit --root .
```

## Compiler diagnostic demo

```bash
qkernel compare-pass \
  examples/compiler_before_qiskit_lite.json \
  examples/compiler_after_qiskit_lite.json \
  --input qiskit-lite
```

This is diagnostic-only. It still requires external semantic-equivalence proof.

## Tower/lift demo

```bash
qkernel lift-pipeline examples/tower_pair_d2_base.json \
  --input weyl \
  --out-json experiments/output/lift_pipeline_demo_report.json \
  --out-md experiments/output/lift_pipeline_demo_report.md
```

## Release state

Alpha, research software. Suitable for targeted review and experiments. Not suitable for production compiler claims.
