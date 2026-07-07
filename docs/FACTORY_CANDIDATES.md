# Factory Candidate Corpus

`qkernel.factory_candidates` packages MagicScout protocol reports as
factory-adjacent research candidates.

It does not construct or validate magic-state factories. It combines:

```text
MagicScout contextuality report
factory-template compatibility
factory metric status
resource metric status
missing evidence
non-claims
```

## CLI

```bash
qkernel factory-candidates examples/factory_candidate_corpus.json
qkernel factory-candidates examples/factory_candidate_corpus.json --out-md factory_candidates.md
```

## Corpus Schema

```json
{
  "factory_candidates": [
    {
      "candidate_id": "pm_magic_verification_candidate",
      "protocol": "magic_protocol_pm_probe.json",
      "required_templates": ["contextuality_witness", "magic_verification_subroutine"],
      "factory_metrics_status": "not_provided",
      "resource_metrics_status": "not_provided",
      "rationale": "compact contextuality verification motif"
    }
  ]
}
```

Paths are resolved relative to the corpus file.

## Status Meaning

```text
template_evidence_incomplete
template_compatible_missing_factory_metrics
factory_metrics_supplied_missing_resource_metrics
externally_supported_factory_candidate
```

The shipped example is intentionally not a factory. It is expected to be
`template_compatible_missing_factory_metrics` when MagicScout template checks
pass.

## Non-Claims

The corpus report does not claim:

```text
valid magic-state factory
distillation threshold
output fidelity
acceptance probability
space-time-volume advantage
lower magic-state overhead
```

Use this as a triage surface for deciding which MagicScout motifs deserve
external factory analysis.
