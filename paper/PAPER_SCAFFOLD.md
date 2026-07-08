# Paper Scaffold

This scaffold maps planned research papers to current qkernel artifacts. It is
not a manuscript source tree. The current repository ships a software note PDF
and planning artifacts; future paper bundles should only move into an adjacent
repo when the split triggers in `docs/ADJACENT_REPO_DECISION.md` are met.

## Track A: QKernel Software Artifact

Working claim:

QKernel extracts and verifies odd-Q / Z_d contextuality kernels in Weyl/Pauli
measurement programs with conservative certificate and release-audit discipline.

Current artifacts:

- `paper/qkernel_note.pdf`
- `paper/generated_benchmark_tables.md`
- `docs/PROPOSITION_MAP.md`
- `docs/PAPER_BENCHMARK_TABLES.md`
- `docs/RELEASE_AUDIT.md`

Missing before a new paper bundle:

- refreshed generated benchmark tables for the current release branch
- explicit version/commit manifest for regenerated outputs
- review of all theorem/proposition labels against the shipped code

## Track B: Application Workbench Evidence Packets

Working claim:

QKernel can package compiler, factory, resource, correlation, and circuit
readiness evidence into auditable packets that preserve missing-evidence gates.

Current artifacts:

- `docs/APPLICATION_PACKET.md`
- `docs/PRD_APPLICATION_WORKBENCH.md`
- `docs/RELEASE_READINESS.md`
- `examples/application_packet_demo.json`
- `examples/resource_feature_pm_probe.json`
- `examples/circuit_manifest_d4_probe.json`

Missing before a paper claim:

- at least one non-demo packet tied to external evidence
- archived packet JSON emitted with `application-packet --out-json`
- clear statement that blocked gates are research blockers, not negative
  results about the underlying science

## Track C: Resource Correlation Study

Working claim:

QKernel features can be joined with external resource-oracle measurements under
correlation-only language.

Current artifacts:

- `docs/RESOURCE_ORACLE.md`
- `docs/CORRELATION_STUDY.md`
- `examples/resource_correlation_study.json`

Missing before a paper claim:

- real external resource-oracle corpus
- negative controls beyond the demo row
- statistical model and validation outside qkernel
- provenance for every external resource metric

## Track D: MagicScout And Factory-Adjacent Triage

Working claim:

MagicScout can prioritize contextuality motifs and factory-adjacent candidates
without claiming factory validity, overhead, thresholds, or fidelity.

Current artifacts:

- `docs/MAGICSCOUT.md`
- `docs/MAGIC_SEARCH.md`
- `docs/MAGIC_REPORTS.md`
- `docs/FACTORY_CANDIDATES.md`
- `examples/factory_candidate_corpus.json`

Missing before a paper claim:

- external factory metrics or simulator outputs
- acceptance probability and output fidelity evidence
- code-distance, decoder, and space-time-volume assumptions
- comparison against known factory constructions

## Reproducibility Manifest Shape

Every future paper bundle should record:

- qkernel git commit
- qkernel version
- input artifact paths
- generated packet JSON paths
- external metric sources
- blocked claim gates
- non-claims copied into the paper appendix

## Current Repo Decision

Keep this scaffold inside `qkernel` for now. Create an adjacent paper/research
repo only when paper source, figures, notebooks, external datasets, or simulator
outputs become too large or dependency-heavy for the package repository.
