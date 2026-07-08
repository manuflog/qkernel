# Adjacent Repository Decision

This document decides whether the application-workbench and research-planning
work should stay inside `qkernel` or move into an independent repository.

## Recommendation

Do not split the repository yet.

Keep the current application-workbench artifacts inside `qkernel` until at
least one adjacent line of work needs independent dependencies, data, release
cadence, or audience. The current workbench is mostly schema, reporting, claim
gating, and examples; those are still part of qkernel's release contract.

## Why Keep It Here For Now

- The workbench composes qkernel-native artifacts: compiler candidates, factory
  candidates, resource features, circuit manifests, correlation studies, and
  kernel census outputs.
- The strongest safety property is local: claim boundaries should be tested next
  to the code that produces the diagnostics.
- The demo evidence packet is intentionally blocked. Splitting it now could make
  blocked research hypotheses look like a separate product.
- The current dependency profile is still lightweight and compatible with the
  qkernel package.

## When To Create An Independent Repo

Create a separate repo only when one of these gates is crossed:

- **External datasets**: resource-oracle corpora, hardware runs, or benchmark
  tables become large enough that they should not ship with the Python package.
- **Notebook-heavy analysis**: correlation studies require exploratory notebooks,
  statistical models, plots, or provenance records beyond static examples.
- **Frontend or UI**: a circuit-builder UI, reviewer dashboard, or packet
  browser needs a web stack or design assets.
- **Simulator integration**: magic-state factory simulators, compiler plugins,
  or hardware backends introduce optional dependencies and external toolchain
  assumptions.
- **Paper bundle**: a reproducible paper artifact needs source, figures,
  generated tables, and frozen outputs independent of package releases.

## Candidate Future Repos

| repo | purpose | split trigger |
| --- | --- | --- |
| `qkernel-research-atlas` | external datasets, theorem pins, K(d,m) target plans, and paper figures | atlas data grows beyond examples |
| `qkernel-workbench` | packet browser, review dashboard, and workflow UI | application packet review needs an interactive surface |
| `qkernel-resource-studies` | notebooks and statistical analyses for resource correlations | real external resource-oracle corpus is available |
| `qkernel-factory-lab` | MagicScout-to-factory simulator bridge experiments | external factory simulator metrics are attached |

## Migration Shape

If a split becomes justified:

1. Keep core schemas and claim-gate tests in `qkernel`.
2. Move bulky data, notebooks, UI, or simulator integrations to the adjacent
   repo.
3. Treat qkernel outputs as immutable inputs to the adjacent repo.
4. Preserve non-claims in both repos; the adjacent repo must not weaken qkernel's
   safety language.
5. Add a reproducibility manifest that records qkernel commit, input artifacts,
   generated packet JSON, and external evidence sources.

## Current Decision

Status: **stay in qkernel**.

Next review point: after the first real external resource-oracle corpus or after
the first interactive packet/circuit-builder prototype is proposed.
