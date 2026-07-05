# Experiments

These scripts are intentionally modest. They are not quantum-supremacy or magic-state claims.

Their purpose is to measure whether Q-Kernel's engineering choices help on synthetic structured instances:

- component decomposition;
- solver backend choice;
- certificate verification overhead;
- behavior under irrelevant disconnected noise.

Run from the repository root:

```bash
PYTHONPATH=src python experiments/benchmark_decomposition.py
PYTHONPATH=src python experiments/compare_solvers.py
```

Outputs are written to `experiments/output/`.
