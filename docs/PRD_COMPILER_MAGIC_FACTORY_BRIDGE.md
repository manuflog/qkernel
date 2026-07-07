# PRD: Compiler, Magic-State, Circuit-Builder, and Factory Bridge

## Status

Draft for staged development. This is a product and research plan, not a claim
that qkernel already optimizes circuits or constructs magic-state factories.

## Problem

Q-Kernel can extract small, independently verified contextuality kernels from
Weyl/Pauli measurement programs. The next application frontier is to connect
those kernels to:

```text
compiler diagnostics
candidate circuit/protocol generation
magic-state-adjacent protocol triage
external resource metrics
eventual factory/cultivation studies
```

The current gap is not kernel extraction. The gap is the evidence bridge from a
contextuality diagnostic to a resource or compiler decision. Without that bridge,
claims such as "optimizes T-count" or "builds a valid magic-state factory" would
be unsafe.

## Goals

1. Turn qkernel outputs into structured inputs for compiler and magic-state
   research workflows.
2. Keep external resource metrics separate from qkernel-computed features.
3. Build a corpus format for before/after compiler candidates, circuit-builder
   protocols, MagicScout reports, and external resource-oracle rows.
4. Support real experiments that can test whether kernel features correlate with
   T-count, T-depth, magic injections, stabilizer rank, acceptance probability,
   or hardware certification cost.
5. Preserve explicit claim boundaries at every stage.

## Non-Goals

```text
certified T-count optimizer
certified T-depth optimizer
magic-state factory constructor
distillation threshold estimator
decoder or code-distance optimizer
semantic-equivalence prover
hardware-resource advantage theorem
```

These may become future integrations, but only after external proofs, resource
oracles, or validated empirical models exist.

## Users

```text
quantum compiler researcher
fault-tolerance / magic-state researcher
hardware benchmarking researcher
contextuality / foundations researcher
qkernel maintainer preparing auditable PRs and papers
```

## Existing Building Blocks

```text
qkernel.subroutine.analyze_contextuality
qkernel.compiler.compiler_report_dict
qkernel.compiler.compare_compiler_pass_dict
qkernel.magic / MagicScout
qkernel.magic_templates
qkernel.magic_search
qkernel.export_circuit.export_qiskit_protocol
qkernel.resource_oracle.resource_feature_report
qkernel.rewrite_policy
qkernel.kernel_census
```

## Proposed Product Shape

### Layer 1: Evidence Export

Export qkernel features and claim scope for each candidate program:

```text
program_id
input kind
context count
observable count
contextual verdict
kernel weight
minimal-kernel multiplicity
obstruction value
Z_d / AvN verifier status
criterion ledger
certificate path or digest
```

This is implemented initially by `resource-features`.

### Layer 2: External Resource Oracle Attachment

Attach metrics computed outside qkernel:

```text
T-count
T-depth
magic injections
stabilizer rank
logical qubits
space-time volume
factory acceptance probability
output fidelity
code distance
decoder
backend/hardware assumptions
```

Every row must preserve `source` and `notes`. Missing values remain null.

### Layer 3: Compiler Candidate Registry

Represent before/after compiler candidates as auditable records:

```text
before program
after program
qkernel before report
qkernel after report
semantic-equivalence proof status
external resource delta, if supplied
policy class
allowed claims
forbidden claims
```

Q-Kernel can rank candidates for study, but cannot authorize a compiler rewrite
without an external semantic-equivalence proof.

### Layer 4: Circuit Builder Expansion

Extend the circuit-building surface in stages:

```text
current: d=2, m=2 hardware certification protocol
next: report-only circuit skeletons for unsupported d,m
next: Stim/Qiskit-lite protocol exports with explicit unsupported-operation records
later: backend-aware protocol templates for selected hardware families
```

The builder must refuse or mark unsupported dimensions instead of emitting fake
hardware-ready circuits.

### Layer 5: Magic-State Factory Candidate Workbench

MagicScout should become a workbench for factory hypotheses, not a factory
validator:

```text
candidate motif search
template compatibility checks
missing factory evidence
external factory metric attachment
portfolio ranking
negative controls
report generation
```

A "factory candidate" is valid only as a research object until all required
external evidence is attached.

## Requirements

### Functional

1. Export qkernel feature rows for any supported input kind.
2. Attach external resource metrics without converting them into qkernel claims.
3. Render Markdown reports for PR review and research logs.
4. Support JSON schemas for target plans, resource-oracle rows, and future
   compiler/factory candidate corpora.
5. Reuse rewrite policies to classify every optimizer-facing feature.
6. Provide negative controls in tests so non-contextual and odd-d shadow-trap
   cases do not receive resource-positive language.

### Claim-Scope

Every report must include:

```text
claim_scope
criterion_ledger
missing_evidence
not_claimed
next_actions
```

### Verification

Each increment should have:

```text
unit tests
CLI smoke test
Markdown render test
metadata/package presence check
full-suite run before merge when practical
```

## Milestones

### M1: Resource Oracle Bridge

Status: implemented on the active branch.

Deliverables:

```text
qkernel.resource_oracle
qkernel resource-features
docs/RESOURCE_ORACLE.md
examples/resource_metrics_stub.json
tests/test_resource_oracle.py
```

### M2: Compiler Candidate Corpus

Deliverables:

```text
compiler_candidate schema
before/after qkernel feature export
semantic-equivalence proof placeholder
resource-oracle delta attachment
Markdown report
negative controls for forbidden optimizer claims
```

### M3: Factory Candidate Corpus

Deliverables:

```text
factory_candidate schema
MagicScout report linkage
template compatibility snapshot
external factory metrics attachment
missing-evidence gate
portfolio report
```

### M4: Circuit Builder Roadmap Artifacts

Deliverables:

```text
unsupported-d,m skeleton reports
backend capability records
Qiskit/Stim-lite protocol export manifests
hardware-readiness gates
```

### M5: Correlation Study Harness

Deliverables:

```text
benchmark corpus loader
joined qkernel/resource table
negative controls
summary statistics
explicit "correlation only" report language
```

## Success Metrics

```text
number of benchmark rows with both qkernel features and external metrics
number of negative controls preserved without resource-positive language
number of candidate rewrites with semantic-proof status tracked
number of factory candidates with complete missing-evidence checklists
ability to reproduce reports from JSON only
```

## Real-World Impact Path

Near-term impact is not a claim of better magic factories. The realistic impact
is faster triage:

```text
find small contextual cores inside large measurement/circuit artifacts
identify which motifs deserve expensive external resource analysis
avoid wasting hardware/compiler time on non-contextual or unsupported candidates
produce auditable reports for papers and PRs
```

If correlations or bridge theorems are later validated, qkernel can become a
front-end filter for compiler optimization and fault-tolerance research.

## Open Questions

```text
Which external compiler/resource oracle should be the first integration target?
What minimal benchmark corpus covers Clifford+T, stabilizer, and MBQC examples?
Which factory metrics are mandatory before a candidate can be called viable?
What semantic-equivalence proof format should compiler candidates reference?
How should d>2 circuit-builder skeletons represent unsupported hardware actions?
```
