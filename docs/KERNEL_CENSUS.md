# Kernel Census

`qkernel.kernel_census` runs a conservative minimal-kernel census over the
registered Contextuality Benchmark Zoo.

The census is a bridge toward K(d,m) work. It pins known examples and their
minimal-kernel statistics, but it does not exhaust all Weyl families and does
not prove a global K(d,m) lower bound.

## CLI

```bash
qkernel kernel-census
qkernel kernel-census --contextual-only
qkernel kernel-census --theorem-pins examples/kernel_theorem_pins.json
qkernel kernel-census --target-file examples/kernel_census_targets.json
qkernel kernel-census --target-dm 8,2 --target-dm 16,2
qkernel kernel-census --out-md kernel_census.md
```

## Python API

```python
from qkernel.kernel_census import kernel_census_report_dict

report = kernel_census_report_dict()
```

## What It Reports

Each entry records:

```text
zoo instance name
d, m
context / observable counts
contextual verdict
minimal kernel weight
minimal-kernel multiplicity, when pinned
obstruction value
Z_d / AvN verifier outcome
claim scope
```

The summary groups entries by `(d,m)` and reports the witnessed minimum among
registered zoo instances. Every summary also carries:

```text
global_K_proven
global_K_value
proof_obligations
```

These fields are deliberately unset until a theorem source, exhaustive
classification, or machine-checkable certificate proves a full-family K(d,m)
claim.

Explicit research targets can also be tracked with `--target-dm D,M`. Targets
are useful for atlas work such as `K(8,2)` and `K(16,2)`, where qkernel should
preserve a visible TODO even before a contextual zoo witness exists. Target
records are emitted under `research_targets` and classify each target as:

```text
pinned_with_registered_witness
pinned_without_registered_witness
witnessed_unpinned
open_no_registered_witness
```

Targets do not create evidence. They only connect current qkernel witnesses,
optional theorem pins, proof obligations, and next actions in one auditable
record.

Reusable target plans can be loaded from JSON with `--target-file`:

```json
{
  "research_targets": [
    {
      "d": 8,
      "m": 2,
      "target_id": "K82",
      "priority": "next",
      "source": "research-atlas-v7/KC",
      "rationale": "Next even-dimension K(d,m) census target after the d=4 certificate."
    }
  ]
}
```

`target_id`, `priority`, `source`, and `rationale` are metadata only. They help
reviewers connect a census run to an atlas or research plan, but they do not
change witnessed minima, theorem-pin validation, or claim scope.

## Theorem Pins

External K(d,m) proofs can be recorded in a JSON file and merged into the census:

```json
{
  "theorem_pins": [
    {
      "d": 4,
      "m": 2,
      "K": 6,
      "theorem_id": "K42_MINIMAL_CERTIFICATE",
      "source": "research-atlas-v7/FKC",
      "proof_method": "odd-K parity lemma + K=4 shape classification + exhaustive K4-configuration search",
      "verifier": "external proof record",
      "notes": "qkernel records but does not derive this theorem"
    }
  ]
}
```

Supplying a theorem pin sets `global_K_proven=true` for that `(d,m)` summary and
records the theorem metadata. Pins are externally sourced: qkernel validates the
metadata shape and keeps the claim boundary visible, but it does not turn a pin
into an internal proof.

Pins are also checked against registered zoo witnesses. A pin claiming
`K(d,m)` larger than an already witnessed contextual kernel weight is rejected
as inconsistent with current qkernel evidence.

Every accepted pin also receives a `theorem_pin_audits` record:

```text
matches_registered_witness
stronger_than_registered_witnesses
no_registered_witness
```

`matches_registered_witness` means the theorem's `K` equals the best registered
zoo witness for that `(d,m)`. `stronger_than_registered_witnesses` means the
external theorem claims a smaller global `K` than qkernel currently witnesses;
the pin is kept, but the audit makes the gap explicit. `no_registered_witness`
means qkernel has no contextual zoo instance for that `(d,m)` and is only
recording external theorem metadata.

## Non-Claims

The census does not claim:

```text
global K(d,m) lower bounds
exhaustive search over all Weyl families
replacement for shape-classification proofs
resource monotonicity
```

Full K(d,m) theorems still require external proof machinery such as exhaustive
shape classification, CP-SAT/MILP certificates, or mathematical lower-bound
arguments. The census gives qkernel a stable place to pin those results once
they are verified.
