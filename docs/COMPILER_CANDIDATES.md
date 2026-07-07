# Compiler Candidate Corpus

`qkernel.compiler_candidates` turns before/after compiler-pass ideas into
auditable diagnostic records.

It does not certify that the rewrite is semantically valid, and it does not
claim resource improvement. It packages:

```text
before/after qkernel diagnostics
odd-Q kernel deltas
semantic-equivalence proof status
external resource-metric status
rewrite-policy guardrails
missing evidence
non-claims
```

## CLI

```bash
qkernel compiler-candidates examples/compiler_candidate_corpus.json
qkernel compiler-candidates examples/compiler_candidate_corpus.json --out-md compiler_candidates.md
```

## Corpus Schema

```json
{
  "compiler_candidates": [
    {
      "candidate_id": "pm_nonkernel_prune_qiskit_lite",
      "before": "compiler_before_qiskit_lite.json",
      "after": "compiler_after_qiskit_lite.json",
      "input_kind": "qiskit-lite",
      "semantic_equivalence_status": "not_provided",
      "resource_metrics_status": "not_provided",
      "rationale": "candidate diagnostic pruning experiment"
    }
  ]
}
```

Paths are resolved relative to the corpus file.

## Status Meaning

```text
diagnostic_only_missing_semantic_proof
semantic_proof_supplied_missing_resource_metrics
not_applicable_by_policy
externally_supported_candidate
```

Only the first status is expected for the shipped example. Later statuses require
external evidence that qkernel does not generate.

## Non-Claims

The corpus report does not claim:

```text
semantic equivalence
T-count reduction
magic-state optimization
hardware-resource advantage
valid compiler rewrite application
```

Use it as a triage surface for compiler and resource-research candidates.
