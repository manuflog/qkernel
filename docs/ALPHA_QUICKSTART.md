# Alpha Quickstart

## Install

```bash
python -m pip install -e .[dev]
```

## Smoke test

```bash
qkernel self-test
```

## Core contextuality demo

```bash
qkernel compress-pauli examples/peres_mermin_pauli.json --json
qkernel zd-valuation examples/peres_mermin_pauli.json --input pauli
```

## Compiler diagnostic demo

```bash
qkernel compare-pass \
  examples/compiler_before_qiskit_lite.json \
  examples/compiler_after_qiskit_lite.json \
  --input qiskit-lite
```

## Tower/lift demo

```bash
qkernel lift-pipeline examples/tower_pair_d2_base.json \
  --input weyl \
  --out-json experiments/output/lift_pipeline_demo_report.json \
  --out-md experiments/output/lift_pipeline_demo_report.md
```

## Release audit

```bash
qkernel release-audit --root .
```
