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
- `ADJACENT_REPO_DECISION.md`: decision record for when adjacent work should
  split into an independent repo
- `RESEARCH_PLAN.md`: paper/research scaffold and evidence gates
- `paper/PAPER_SCAFFOLD.md`: track-by-track map from planned papers to current
  artifacts and missing evidence
- `paper/repro_manifest_template.json`: reproducibility manifest template for
  future paper bundles

## Release Checks

Before tagging or merging a release PR, run:

```bash
pytest -q
qkernel self-test
qkernel application-packet examples/application_packet_demo.json \
  --out-md experiments/output/application_packet.md \
  --out-json experiments/output/application_packet.json
qkernel application-packet examples/application_packet_demo.json --fail-on-blocked
qkernel release-audit --root . \
  --out-json experiments/output/release_audit.json \
  --out-md experiments/output/RELEASE_AUDIT.md
```

The final command is expected to exit nonzero for the demo packet because the
demo intentionally preserves blocked claim gates for missing compiler,
factory, resource-bridge, and qudit-circuit evidence.

The release audit checks the workbench docs/examples, verifies that the demo
packet covers all current source families, and confirms that blocked claim gates
remain blocked rather than being reported as release claims.

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
