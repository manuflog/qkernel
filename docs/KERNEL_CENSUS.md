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
registered zoo instances.

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
