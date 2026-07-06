# MagicScout factory-template bridge

MagicScout templates are conservative checklists. They map a contextuality motif
to a possible research role inside a magic-state-adjacent workflow without
claiming that the motif is a valid factory or improves overhead.

Built-in templates:

```text
contextuality_witness
magic_verification_subroutine
hardware_ready_magic_probe
distillation_check_motif
cultivation_motif
```

Each template declares required contextuality evidence, optional backend
certifiability, factory metadata requirements, claim scope, and non-claims.

## CLI concept

```bash
qkernel magic-templates
qkernel magic-template-assess examples/magic_protocol_pm_probe.json
```

## Interpretation

A compatible template means:

```text
this report satisfies a conservative checklist for that research role
```

It does not mean:

```text
valid magic-state factory
lower overhead
threshold improvement
output fidelity bound
space-time-volume advantage
```
