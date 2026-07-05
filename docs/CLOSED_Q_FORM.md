# Closed Symplectic Form for Q

Claude-side feedback supplied a useful proved simplification for even `d`.

For a closed cycle `lambda`, the odd-Q obstruction can be computed in two equivalent ways.

## Context-carry form

```text
Q(lambda) = lambda · b mod 2
```

where each context carry is:

```text
b(C) = sum_{i<j} <c_i,c_j> / d mod 2
```

## Closed observable-multiset form

Flatten the selected contexts into an ordered observable multiset:

```text
v_1, ..., v_N
```

Then:

```text
Q(lambda) = (sum_{a<b} <v_a,v_b> / d) mod 2
```

The division by `d` is applied to the aggregate integer numerator. Individual
inter-context pairings do not have to be divisible by `d`.

## Why the forms agree

For a selected cycle, each selected context sums to zero mod `d`. In integer
lifts one can write the selected context sums as:

```text
S_r = d t_r
```

The inter-context contribution between contexts `r` and `s` is:

```text
<S_r, S_s> / d = d <t_r, t_s>
```

which is even modulo 2 when `d` is even. Therefore only the intra-context carry
bits remain, giving:

```text
closed observable-multiset Q = lambda · b
```

## Implementation

Q-Kernel exposes both paths:

```python
qkernel.closed_form.q_from_context_carries(program, lam)
qkernel.closed_form.q_from_observable_multiset(program, lam)
qkernel.closed_form.compare_q_forms(program, lam)
```

The analyzer cross-checks the two forms on cycle-space elements.

## CLI

```bash
qkernel q-forms examples/peres_mermin_pauli.json \
  --input pauli \
  --contexts 0,1,2,3,4,5
```
