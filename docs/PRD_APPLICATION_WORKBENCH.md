# PRD: QKernel Application Workbench

## Status

Draft for incremental development. This PRD chooses a narrow v1 direction from
the broader compiler, magic-state, optimizer, circuit-builder, and factory
application space.

## Problem Statement

QKernel now has separate compiler, MagicScout, factory-candidate,
circuit-manifest, resource-oracle, impact-register, and correlation-study
surfaces. Researchers need one application workflow that turns those pieces into
reviewable decisions without pretending qkernel is already a production
compiler, circuit builder, or magic-state factory.

## Recommended V1

Build a CLI-first application workbench that assembles existing reports by
candidate ID, then produces a single evidence packet for compiler-pass and
magic/factory triage.

This is the highest-leverage v1 because it reuses existing versioned artifacts:

- compiler candidate corpora
- MagicScout and factory-candidate reports
- circuit-builder readiness manifests
- resource-oracle feature rows
- correlation-study JSON, Markdown, and CSV output
- impact-register claim boundaries

## Goals

- Reduce manual evidence-gathering across compiler, circuit, magic, factory, and
  resource reports.
- Make every recommendation traceable to source commands, docs, missing evidence,
  and explicit non-claims.
- Support at least one end-to-end candidate packet that joins qkernel features
  with external metrics.
- Keep forbidden claims visible in every generated artifact.

## Non-Goals

- Production optimizer or transpiler integration in v1.
- Interactive circuit-builder UI in v1.
- Validated magic-state factory construction in v1.
- Statistical model fitting or causal resource claims inside qkernel.
- Hardware execution or backend calibration inside qkernel.

## User Stories

- As a quantum compiler researcher, I want a single evidence packet for a
  compiler-pass candidate so that I can see semantic-proof status, qkernel
  diagnostics, and resource metrics before deciding whether to investigate the
  pass.
- As a magic-state researcher, I want MagicScout motifs linked to
  factory-candidate evidence gates so that promising motifs are not mistaken for
  validated factories.
- As a hardware benchmarking researcher, I want circuit-builder readiness and
  blockers attached to a candidate so that unsupported protocols do not become
  fake hardware claims.
- As a qkernel maintainer, I want generated PR-ready claim boundaries so that
  releases can describe application progress without overstating results.

## Application Options

### Compiler/resource evidence workbench

- Target user: quantum compiler researcher
- User value: combines compiler candidates, qkernel diagnostics, and external
  resource rows
- Implementation risk: low; mostly composes existing JSON reports
- Evidence gate: semantic-equivalence proof status plus externally sourced
  resource metrics
- Why now: highest reuse of current compiler-candidate, resource-oracle, and
  correlation-study code

### Circuit-builder readiness UI

- Target user: hardware benchmarking researcher
- User value: shows which kernels can become validated circuit exports and which
  are blocked
- Implementation risk: medium; frontend and hardware-capability modeling add new
  surface area
- Evidence gate: validated exporter support and backend capability records
- Why later: valuable, but better after the CLI evidence packet stabilizes

### Magic-state factory simulator bridge

- Target user: fault-tolerance and magic-state researcher
- User value: links MagicScout motifs to external factory simulation metrics
- Implementation risk: medium-high; requires careful external simulator/source
  integration
- Evidence gate: acceptance probability, output fidelity, code distance, decoder,
  and volume evidence
- Why later: important once candidate IDs and external metric contracts are stable

## Requirements

### P0: Candidate packet schema

Define a JSON packet that references compiler candidates, factory candidates,
circuit manifests, qkernel feature rows, and external resource rows by stable
IDs.

Acceptance criteria:

- Packet rejects duplicate candidate IDs.
- Packet preserves source paths for every referenced report.
- Packet includes `missing_evidence` and `not_claimed` sections.

### P0: Evidence packet renderer

Render a Markdown packet suitable for PR review or research logs.

Acceptance criteria:

- Renderer groups compiler, circuit, magic, factory, and resource evidence
  separately.
- Renderer prints claim boundaries before recommendations.
- Renderer works without external network access.

### P0: Claim-boundary gate

Block resource-positive or factory-positive language unless required evidence is
present.

Acceptance criteria:

- Missing semantic-equivalence proof blocks optimizer claims.
- Missing factory metrics blocks factory viability claims.
- Missing backend readiness blocks hardware-ready circuit claims.

### P1: Example packet corpus

Add examples that connect current compiler and factory candidate corpora to
resource rows.

Status: initial demo packet implemented. It now covers compiler candidates,
factory candidates, correlation rows, resource-feature JSON, and
circuit-manifest JSON.

Acceptance criteria:

- Example includes at least one negative control.
- Example can be rendered from JSON only.
- Example is covered by CLI smoke tests.

### P2: Interactive application frontend

Design a future UI after the CLI packet format has stabilized.

Acceptance criteria:

- UI consumes the same packet JSON as the CLI.
- UI does not introduce new claim semantics.

## Success Metrics

- One command can produce a complete evidence packet from versioned JSON inputs.
- Every packet contains at least one explicit non-claim and one next action.
- Full test suite preserves negative-control language.
- External resource metrics remain source-attributed and optional.

## Open Questions

- Which external compiler/resource oracle should supply the first real metric
  dataset?
- Which candidate ID convention should be shared by compiler, factory, and
  correlation manifests?
- Should packet validation require all referenced source files to exist locally?
- Which future UI surface matters most after the CLI packet proves useful?

## Phased Timeline

- Phase 1: document the workbench PRD and claim gates.
- Phase 2: add candidate packet schema and Markdown renderer.
- Phase 3: add example packets joining compiler, factory, circuit, and resource
  artifacts.
- Phase 4: evaluate whether a UI, plugin, or simulator bridge is the next best
  application.

## Claim Boundaries

- Does not claim qkernel is a production compiler.
- Does not claim qkernel optimizes T-count or T-depth by itself.
- Does not claim MagicScout motifs are validated magic-state factories.
- Does not claim unsupported circuit manifests are hardware-ready circuits.
- Does not claim external resource correlations are causal.
