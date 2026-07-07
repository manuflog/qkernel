# Resource Oracle Bridge

`qkernel.resource_oracle` exports Q-Kernel features for comparison against an
external compiler or resource-estimation oracle.

It closes a practical gap in the roadmap: comparing kernel features against
T-count, T-depth, magic injections, or stabilizer rank requires those resource
metrics to come from outside qkernel. This bridge keeps the columns together
without claiming qkernel computed or predicted the resource values.

## CLI

```bash
qkernel resource-features examples/peres_mermin.json
qkernel resource-features examples/peres_mermin.json \
  --program-id peres_mermin_probe \
  --resource-metrics examples/resource_metrics_stub.json \
  --out-md resource_features.md
```

## External Metrics Schema

```json
{
  "external_resource_metrics": {
    "program_id": "peres_mermin_probe",
    "source": "external compiler/resource oracle name",
    "t_count": 7,
    "t_depth": 3,
    "magic_injections": 7,
    "stabilizer_rank": null,
    "notes": "computed outside qkernel"
  }
}
```

All metric fields are optional non-negative integers. Missing metrics remain
`null`; qkernel does not fill them in.

## What Q-Kernel Exports

```text
contexts
observables
contextual verdict
minimal kernel weight
minimal-kernel multiplicity
obstruction value
Z_d / AvN verifier result
criterion ledger
```

## Non-Claims

The bridge does not claim:

```text
T-count prediction
T-depth prediction
magic-injection prediction
stabilizer-rank prediction
resource advantage
```

Use the output as a row in an external benchmark table. Any resource theorem,
correlation model, or optimization claim must be established outside this
module and then cited explicitly.
