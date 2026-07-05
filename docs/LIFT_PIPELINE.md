# Lift Pipeline

Q-Kernel v0.31 adds an end-to-end reproducibility pipeline:

```text
fiber-lift -> Z_d valuation -> tower-law report
```

This is a certification/reporting workflow, not an optimizer.

## CLI

```bash
qkernel lift-pipeline examples/tower_pair_d2_base.json \
  --input weyl \
  --out-program experiments/output/lift_pipeline_demo_lifted.json \
  --out-json experiments/output/lift_pipeline_demo_report.json \
  --out-md experiments/output/lift_pipeline_demo_report.md
```

## Outputs

The pipeline report includes:

```text
fiber-lift construction status
lift bits
Z_d valuation result
tower/doubling generativity bit
safe claim
unsafe claims
```

## Safe claim

```text
validated fiber lift plus Z_d valuation result plus closed tower-law generativity report
```

## Unsafe claims

```text
resource advantage
T-count or magic-cost improvement
compiler rewrite legality
tower compression as optimization
```

## Demo

```bash
PYTHONPATH=src python experiments/lift_pipeline_demo.py
```
