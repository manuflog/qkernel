# Circuit Builder Manifest

`qkernel.circuit_manifest` reports whether an input program is ready for the
currently validated circuit exporter.

It does not emit a circuit and does not bypass `export-circuit` scope guards.
The manifest is a planning artifact for circuit-builder development and PR
review.

## CLI

```bash
qkernel circuit-manifest examples/peres_mermin.json
qkernel circuit-manifest examples/peres_mermin.json --out-md circuit_manifest.md
qkernel circuit-manifest examples/activation_base_d4.json
```

## Current Export Surface

The only hardware-ready exporter today is:

```text
export_qiskit_protocol
d = 2
m = 2
3 observables per context
sequential non-destructive ancilla Hadamard-test measurements
```

This is the same protocol used by `qkernel export-circuit`.

## Unsupported Cases

For `d > 2`, `m != 2`, or non-triple contexts, the manifest reports blockers and
next actions. It does not synthesize a placeholder hardware circuit.

This matters for real-world impact: a fake circuit-builder path can create
invalid hardware claims. A manifest makes unsupported work visible while keeping
the exporter honest.

## Non-Claims

The manifest does not claim:

```text
unsupported qudit protocol synthesis
hardware success before execution
circuit-depth optimization
T-count or magic-state optimization
semantic equivalence of compiler rewrites
```
