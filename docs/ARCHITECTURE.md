# Architecture

Q-Kernel is organized around one narrow compiler-analysis task:

> compress a Weyl/Pauli measurement family to its minimum odd-Q contextual kernel.

## Pipeline

```text
Circuit / measurement schedule
        ↓
Weyl context extractor
        ↓
WeylProgram IR
        ↓
validator
        ↓
carry engine b(C)
        ↓
incidence matrix A
        ↓
cycle solver A^T lambda = 0
        ↓
minimum odd-Q optimizer
        ↓
contextuality kernel certificate
```

## Modules

- `ir.py`: typed dataclasses.
- `symplectic.py`: integer symplectic arithmetic.
- `validate.py`: context constraints.
- `carry.py`: commutator-carry bits.
- `incidence.py`: GF(2) incidence matrix and left-kernel cycles.
- `gf2.py`: small exact GF(2) linear algebra.
- `analyzer.py`: yes/no contextuality detection.
- `optimizer.py`: minimum odd-Q kernel extraction.
- `certificate.py`: JSON and Markdown certificates.
- `io.py`: JSON program format.
- `cli.py`: command-line interface.

## Critical implementation rule

The carry bit is an integer-lift invariant. Never reduce the symplectic pairing modulo `d` before dividing by `d`.

Correct:

```python
s = symplectic_int(u, v)
assert s % d == 0
carry += s // d
```

Wrong:

```python
s = symplectic_int(u, v) % d
carry += s // d
```

The second version silently destroys the obstruction.
