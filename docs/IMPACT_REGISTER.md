# QKernel Application Impact Register

The impact register is a conservative map from qkernel capabilities to possible
real-world application tracks. It exists because compiler work, optimizers,
circuit builders, magic-state workflows, and factory hypotheses are easy to
overstate. The register keeps each track explicit:

- what qkernel can do today
- which commands and docs support it
- what evidence is still missing
- what the next development actions are
- what this project does not claim

Run:

```bash
qkernel impact-register --out-md impact-register.md
```

The command prints a JSON report and can also write a Markdown planning artifact.

## Application Tracks

The current register covers:

- kernel census and K(d,m) target planning
- compiler and optimizer candidate corpora
- MagicScout motif triage
- magic-state factory candidate ledgers
- circuit-builder readiness manifests
- resource-oracle feature export
- correlation-study JSON, Markdown, and CSV handoff
- a planned PRD track for new applications

## Claim Boundaries

The register is a planning and evidence artifact. It does not claim qkernel is a
production compiler, does not claim qkernel builds validated magic-state
factories, and does not claim resource improvements without external resource
evidence. Mathematical proof, hardware validation, and statistical analysis
remain separate obligations.

## Development Use

Use the register when deciding what to build next. A track is ready for stronger
claims only when its missing-evidence list is cleared by external proof,
measured resource data, validated circuit execution, or an independently
reviewed analysis artifact.
