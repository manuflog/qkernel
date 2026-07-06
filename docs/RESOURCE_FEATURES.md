# Resource Feature Export

`qkernel.resource_features` exports conservative contextuality feature vectors
for external resource-estimation studies.

It is intentionally not a resource estimator. The report can be used as input to
a separate oracle for T-count, T-depth, magic injections, stabilizer rank, or
backend hardware cost, but it does not infer any of those quantities.

## CLI

```bash
qkernel resource-features examples/peres_mermin_pauli.json --input pauli --enumerate
```

Optional certificate-facing fields:

```bash
qkernel resource-features examples/peres_mermin_pauli.json \
  --input pauli \
  --enumerate \
  --include-certificate-features
```

## Python API

```python
from qkernel.io import load_program
from qkernel.resource_features import resource_feature_report_dict

program = load_program("examples/peres_mermin.json")
features = resource_feature_report_dict(program, enumerate_all_kernels=True)
```

## Exported Signals

The report includes:

```text
context count
observable count
component count
cycle-basis dimension
odd-carry context count
minimal kernel context/observable counts
kernel fractions
obstruction value
minimal-kernel multiplicity, when requested and tractable
criterion ledger
```

## Required External Oracles

Any resource claim still needs an external model or proof, such as:

```text
semantic-equivalence proof for compiler rewrites
validated T-count/T-depth or magic-injection oracle
stabilizer-rank or simulator-cost oracle
backend-specific hardware cost model
```

## Non-Claims

The resource-feature report must not be read as saying:

```text
Q-Kernel predicts T-count.
Q-Kernel predicts magic-state overhead.
Kernel compression is a resource monotone.
Contextuality fraction is an additive resource gauge.
A smaller kernel proves a semantics-preserving compiler optimization.
This feature vector proves backend resource advantage.
```
