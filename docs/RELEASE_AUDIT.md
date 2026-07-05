# Release Audit

Q-Kernel v0.32 adds a release/readiness audit.

The audit checks:

```text
required public/research repo files
Peres-Mermin odd-Q + Z_d verification
rewrite policy guardrails
compiler playground diagnostic-only status
fiber-lift construction
closed tower-law report
lift pipeline report
finite-geometry novelty hygiene
```

## CLI

```bash
qkernel release-audit \
  --root . \
  --out-json experiments/output/release_audit.json \
  --out-md experiments/output/RELEASE_AUDIT.md
```

## Script

```bash
PYTHONPATH=src python experiments/release_audit.py
```

## Purpose

This is not a mathematical proof generator. It is a release checklist that
guards against the most important project failure modes:

```text
claiming magic/T-count optimization
dropping Z_d valuation verification
forgetting finite-geometry prior art
treating diagnostics as compiler rewrites
publishing without core examples working
```
