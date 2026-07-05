# Qiskit-lite Adapter

Q-Kernel v0.25 adds a dependency-free Qiskit-lite JSON adapter.

This is not a hard dependency on Qiskit. It is a bridge format that can be
emitted from Qiskit objects such as `SparsePauliOp`, `PauliList`, or custom pass
managers.

## Qubit order

Qiskit Pauli strings are normally displayed with the highest qubit on the left.
Q-Kernel's simple Pauli frontend interprets the leftmost character as the first
coordinate block. Therefore the adapter defaults to:

```json
"qubit_order": "qiskit"
```

which reverses labels before analysis.

Use:

```json
"qubit_order": "qkernel"
```

when labels are already in Q-Kernel convention.

## Supported layered form

```json
{
  "type": "qiskit_pauli_layers",
  "qubit_order": "qiskit",
  "layers": [
    {"name": "row_0", "paulis": ["IZ", "ZI", "ZZ"]},
    ["XI", "IX", "XX"]
  ]
}
```

## Supported flat term form

```json
{
  "type": "qiskit_sparse_pauli_terms",
  "terms": [
    {"pauli": "IZ", "layer": "r0", "coeff": 1.0},
    {"pauli": "ZI", "layer": "r0", "coeff": -1.0}
  ]
}
```

Coefficients are recorded as ignored metadata. Q-Kernel analyzes Pauli labels
and contexts, not Hamiltonian weights.

## CLI

```bash
qkernel inspect-qiskit-lite examples/peres_mermin_qiskit_lite.json
qkernel analyze-qiskit-lite examples/peres_mermin_qiskit_lite.json
qkernel compress-qiskit-lite examples/peres_mermin_qiskit_lite.json --json
qkernel certify examples/peres_mermin_qiskit_lite.json --input qiskit-lite --out pm_qiskit.cert.json
```

## Scope

Safe:

```text
Qiskit-exported Pauli family bridge
pass-manager diagnostic artifact
explicit context/layer analysis
```

Unsafe:

```text
automatic arbitrary circuit optimization
resource estimation from Hamiltonian coefficients
T-count/magic optimization
semantic rewrite proof
```
