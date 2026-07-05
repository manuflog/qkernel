# Optional PySAT / RC2 Backend

Q-Kernel v0.23 adds an optional PySAT backend interface.

The core package remains dependency-free. Install the SAT extra only when wanted:

```bash
pip install 'qkernel[sat]'
```

## Fixed-k SAT

```bash
qkernel solve-pysat examples/peres_mermin_pauli.json \
  --input pauli \
  --max-weight 6
```

This uses the same CNF encoding as:

```bash
qkernel export-sat ...
```

## RC2 MaxSAT

```bash
qkernel solve-rc2 examples/peres_mermin_pauli.json --input pauli
```

This uses the same WCNF encoding as:

```bash
qkernel export-maxsat ...
```

## Trust model

PySAT and RC2 are not trusted. They return candidate assignments.

Q-Kernel then recomputes and verifies:

```text
A^T lambda = 0
Q(lambda) = 1
```

before accepting a certificate.

## Why optional?

The base Q-Kernel package should stay pure Python and easy to audit. External solvers are useful for scale, but the dependency-free export/import loop remains the stable interface.
