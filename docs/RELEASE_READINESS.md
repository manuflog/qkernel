# Release Readiness

This document summarizes the current release posture for the application
workbench branch.

## Release Theme

The release extends qkernel from contextuality-kernel extraction into a
claim-gated application workbench. The workbench composes existing evidence
surfaces instead of upgrading diagnostics into compiler, hardware, resource, or
magic-state factory claims.

## Included Surfaces

- `kernel-census`: conservative K(d,m) census and target tracking
- `resource-features`: qkernel feature export beside external resource metrics
- `compiler-candidates`: before/after compiler-pass diagnostic corpora
- `factory-candidates`: MagicScout factory-adjacent candidate corpora
- `circuit-manifest`: circuit-builder readiness and unsupported-case blockers
- `correlation-study`: correlation-only joins with negative controls and CSV
  export
- `impact-register`: application track, missing-evidence, and claim-boundary map
- `application-prd`: scoped PRD for the CLI-first application workbench
- `application-packet`: claim-gated evidence packets with Markdown, JSON, and
  `--fail-on-blocked` support

## Release Checks

Before tagging or merging a release PR, run:

```bash
pytest -q
qkernel self-test
qkernel application-packet examples/application_packet_demo.json \
  --out-md experiments/output/application_packet.md \
  --out-json experiments/output/application_packet.json
qkernel application-packet examples/application_packet_demo.json --fail-on-blocked
```

The final command is expected to exit nonzero for the demo packet because the
demo intentionally preserves blocked claim gates for missing compiler,
factory, resource-bridge, and qudit-circuit evidence.

## Claim Boundaries

This release does not claim:

- production compiler behavior
- semantic equivalence of compiler rewrites
- T-count, T-depth, or magic-state optimization
- validated magic-state factory construction
- hardware-ready circuits for unsupported qudit protocols
- causal or validated resource correlations

These remain external proof, simulator, compiler, hardware, or statistical
obligations.
