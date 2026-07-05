# Pauli Table Adapter

Q-Kernel v0.12 adds a dependency-free adapter for row-oriented Pauli tables.

This is the adapter contract that future Qiskit or Stim integrations should target before entering the core library.

## Why not import Qiskit immediately?

A direct Qiskit dependency would make the package heavier before the input semantics are settled. The safer architecture is:

```text
Qiskit / Stim / compiler SDK
        ↓
Pauli table
        ↓
Q-Kernel core
```

## Required columns / fields

Each row needs:

```text
context_id or layer_id
pauli
```

Optional fields:

```text
name
observable
observable_id
identity_scope  # observable | event
source
round
notes
order
```

## CSV example

```csv
context_id,pauli,order,identity_scope
r1,ZI,0,observable
r1,IZ,1,observable
r1,ZZ,2,observable
```

## JSON example

```json
{
  "type": "pauli_table",
  "rows": [
    {"context_id": "r1", "pauli": "ZI", "order": 0},
    {"context_id": "r1", "pauli": "IZ", "order": 1},
    {"context_id": "r1", "pauli": "ZZ", "order": 2}
  ]
}
```

## Identity semantics

If `identity_scope="observable"` and no name is supplied, the Pauli string is used as the observable name. Repeated `ZI` rows refer to the same observable.

If `identity_scope="event"` and no name is supplied, Q-Kernel creates unique event names such as:

```text
ZI@r1:0
ZI@c1:9
```

This prevents accidental merging of protocol-distinct measurement events.

## CLI

```bash
qkernel analyze-table examples/peres_mermin_table.json
qkernel compress-table examples/peres_mermin_table.csv --json
qkernel certify examples/peres_mermin_table.json --input table --out pm_table_cert.json
```

## Design rule

The adapter does not infer contexts from a raw Pauli set. It only groups rows by explicit `context_id` or `layer_id`.
