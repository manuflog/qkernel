# Research Plan

This document turns the application-workbench direction into a paper and
research scaffold. It is a planning artifact, not a claim that the results below
already exist.

## Research Thesis

QKernel can act as a claim-disciplined front end for contextuality-kernel
evidence. Its useful near-term role is not to optimize circuits or construct
magic-state factories, but to produce auditable packets that decide what
external evidence is still missing.

## Paper Tracks

### Paper A: QKernel Software Artifact

Scope:

- odd-Q and Z_d contextuality-kernel extraction
- solver stack and certificates
- benchmark zoo and kernel census
- release audit and claim boundaries

Status: existing software note and package infrastructure.

Primary artifact:

- `paper/qkernel_note.pdf`
- `paper/PAPER_SCAFFOLD.md`
- `docs/PROPOSITION_MAP.md`
- `docs/PAPER_BENCHMARK_TABLES.md`

### Paper B: Application Workbench And Evidence Packets

Scope:

- compiler-candidate evidence packets
- factory-candidate evidence packets
- resource-feature and correlation-study joins
- circuit-manifest readiness gates
- CI-style claim gating with `application-packet --fail-on-blocked`

Status: scaffolded in qkernel; needs real external evidence rows before stronger
claims.

Primary artifacts:

- `docs/APPLICATION_PACKET.md`
- `docs/PRD_APPLICATION_WORKBENCH.md`
- `docs/RELEASE_READINESS.md`
- `examples/application_packet_demo.json`

### Paper C: Resource Correlation Study

Scope:

- qkernel feature extraction over a benchmark corpus
- external resource-oracle metrics
- negative controls
- statistical analysis outside qkernel

Status: not ready for claims. The harness exists, but the validated external
corpus does not.

Primary artifacts:

- `docs/RESOURCE_ORACLE.md`
- `docs/CORRELATION_STUDY.md`
- `examples/resource_correlation_study.json`

### Paper D: MagicScout And Factory-Adjacent Triage

Scope:

- contextuality motif ranking
- MagicScout reports
- factory-template compatibility
- missing factory evidence and non-claims

Status: suitable for a research workflow note, not a factory-performance paper.

Primary artifacts:

- `docs/MAGICSCOUT.md`
- `docs/MAGIC_SEARCH.md`
- `docs/FACTORY_CANDIDATES.md`

## Research Questions

- Which qkernel features, if any, correlate with externally computed resource
  metrics?
- Which compiler-candidate deltas remain interesting after semantic-equivalence
  proof requirements are enforced?
- Which MagicScout motifs recur across benchmark families without becoming
  overclaimed as factories?
- Which K(d,m) target cells deserve proof work or new witness searches?
- Which circuit-manifest blockers are engineering gaps versus true protocol
  gaps?

## Minimum Evidence Gates

No paper should claim resource or factory impact until these are attached:

- source-attributed external metrics
- negative controls
- reproducible packet JSON
- explicit missing-evidence ledger
- independent semantic-equivalence proof for compiler claims
- external simulator or hardware assumptions for factory/circuit claims

## Near-Term Work Plan

1. Keep qkernel as the source of record for schemas, examples, claim gates, and
   release audits.
2. Build a larger external-resource corpus only when real compiler/resource
   metrics are available.
3. Use `application-packet --out-json` as the reproducibility input to any
   future paper bundle.
4. Revisit an independent repo after a real corpus, notebook suite, UI, or
   simulator bridge exists.
5. Keep `paper/PAPER_SCAFFOLD.md` updated as the authoritative map from paper
   tracks to current artifacts and missing evidence.

## Non-Claims

This research plan does not claim:

- qkernel predicts T-count, T-depth, or magic injections
- qkernel constructs valid magic-state factories
- qkernel emits hardware-ready circuits for unsupported qudit cases
- qkernel proves semantic equivalence of compiler rewrites
- an adjacent repo is already necessary
