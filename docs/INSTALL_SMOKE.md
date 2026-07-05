# Install / Smoke Test

Q-Kernel v0.25 adds package-polish files and a built-in self-test.

From a clean checkout:

```bash
python -m pip install .
qkernel self-test
```

Expected:

```json
{
  "ok": true,
  "contextual": true,
  "selected_contexts": [0, 1, 2, 3, 4, 5],
  "q_value": 1
}
```

Optional SAT backend:

```bash
python -m pip install '.[sat]'
qkernel solve-rc2 examples/peres_mermin_pauli.json --input pauli
```
