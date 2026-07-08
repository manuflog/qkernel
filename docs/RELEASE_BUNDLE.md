# Release Bundle

This is the ordered review map for the current application-workbench release.
It keeps the release auditable without turning blocked research hypotheses into
shipping claims.

## Review Order

1. Read `README.md` and `ALPHA_README.md` for public positioning.
2. Read `CHANGELOG.md` for release-scope changes.
3. Read `docs/RELEASE_READINESS.md` for required checks and claim boundaries.
4. Inspect `examples/application_packet_demo.json` and generated
   `application-packet` JSON/Markdown outputs.
5. Inspect `paper/PAPER_SCAFFOLD.md` and
   `paper/repro_manifest_template.json` before making any paper or resource
   claim.
6. Read `docs/ADJACENT_REPO_DECISION.md` before moving work into an adjacent
   repository.

## Required Commands

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

`application-packet --fail-on-blocked` is expected to exit nonzero for the demo
packet because the demo preserves missing-evidence gates.

## Must Ship

- `README.md`
- `ALPHA_README.md`
- `CHANGELOG.md`
- `LICENSE`
- `CITATION.cff`
- `docs/RELEASE_READINESS.md`
- `docs/RELEASE_BUNDLE.md`
- `docs/APPLICATION_PACKET.md`
- `docs/IMPACT_REGISTER.md`
- `docs/PRD_APPLICATION_WORKBENCH.md`
- `docs/ADJACENT_REPO_DECISION.md`
- `docs/RESEARCH_PLAN.md`
- `paper/PAPER_SCAFFOLD.md`
- `paper/repro_manifest_template.json`
- `paper/qkernel_note.pdf`
- `examples/application_packet_demo.json`

## Claim Boundaries

This release does not claim:

- qkernel is a production compiler
- compiler rewrites are semantically equivalent
- qkernel optimizes T-count, T-depth, or magic-state injections
- MagicScout motifs are validated magic-state factories
- unsupported circuit manifests are hardware-ready circuits
- external resource correlations are causal or validated

## Packaging Notes

`MANIFEST.in` must include paper Markdown, TeX, BibTeX, JSON manifests, and the
current PDF note. The release audit must fail if required release-bundle files
are missing.
