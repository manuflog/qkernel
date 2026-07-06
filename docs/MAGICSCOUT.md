# MagicScout

MagicScout is Q-Kernel's conservative magic-state-adjacent application layer.

It does **not** construct, distill, or improve magic states. It analyzes candidate
stabilizer/Pauli/Weyl measurement protocols and reports whether their
contextuality structure makes them worth studying as possible magic-state
injection, cultivation, verification, or factory subroutines.

## What it answers

```text
Does this candidate protocol contain a small contextual core?
Is the core independently verified?
Does it pass the stronger Z_d/AvN valuation verifier?
How many distinct minimal kernels does it have?
Was minimality certified?
Can a backend readout model plausibly certify it?
What evidence is still missing before any magic-factory claim?
```

## What it does not answer

```text
distillation threshold
output fidelity
acceptance probability
logical-code distance
decoder behavior
space-time volume
magic-state overhead improvement
```

## Protocol schema

```json
{
  "type": "qkernel.magic_protocol.v1",
  "protocol_id": "pm_magic_probe",
  "target": "T",
  "role": "candidate_magic_verification_subroutine",
  "input_kind": "schedule",
  "claim_scope": "diagnostic_only",
  "schedule": {
    "layers": [
      ["ZI", "IZ", "ZZ"],
      ["IX", "XI", "XX"],
      ["ZX", "XZ", "YY"],
      ["ZI", "IX", "ZX"],
      ["IZ", "XI", "XZ"],
      ["ZZ", "XX", "YY"]
    ]
  },
  "factory_metadata": {
    "input_magic_states": null,
    "output_magic_states": null,
    "acceptance_probability": null,
    "distance": null,
    "decoder": null
  }
}
```

## Main workflows

```bash
qkernel magic-analyze examples/magic_toy_protocol.json --input schedule --target T
qkernel magic-protocol examples/magic_protocol_pm_probe.json
qkernel magic-portfolio examples/magic_portfolio.json
qkernel magic-zoo
qkernel magic-zoo --include-noncontextual
qkernel magic-generate XI IX XX IY YI YY XY YX ZZ
qkernel magic-search XI IX XX IY YI YY XY YX ZZ --top 5
qkernel magic-templates
qkernel magic-template-assess examples/magic_protocol_pm_probe.json --template contextuality_witness
qkernel magic-report examples/magic_protocol_pm_probe.json --out magic_report.md
qkernel magic-audit
```

## Score interpretation

`interest_score` is a research-prioritization score. It is not a magic yield,
not a threshold estimate, not an output fidelity estimate, and not a factory
resource metric.

Positive signals include:

```text
odd-Q contextuality present
independently verified kernel
passes stronger Z_d/AvN verifier
small contextual core
many equivalent minimal kernels / routing alternatives
CP-SAT certified minimality
backend model predicts certifiable contextuality witness
```

Missing evidence is always reported, even for high-scoring candidates.

## Claim scope

Every report carries a criterion ledger:

```text
criterion_id
verifier_used
claim_scope
stronger_verifier_available
stronger_verifier_passed
```

MagicScout's claim scope is:

```text
magic-state-adjacent contextuality diagnostic
```

not:

```text
valid magic-state factory
lower magic-state overhead
threshold improvement
```

## Research program

MagicScout is designed as a staged bridge:

```text
1. contextuality diagnostic
2. portfolio ranking
3. backend-aware witness feasibility
4. generated candidate motifs from available Paulis
5. only later: connect motifs to actual distillation/cultivation templates
```
