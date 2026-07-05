# Fiber-Lift Constructor

Q-Kernel v0.30 adds a validated constructor for even-base fiber lifts:

```text
d -> 2d
v_tilde = u + d x,  x in {0,1}
```

The constructor solves for binary lift bits that preserve:

```text
context closure modulo 2d
pairwise commutation modulo 2d
```

For even base `d`, these constraints are linear over GF(2).

## CLI

```bash
qkernel fiber-lift examples/tower_pair_d2_base.json \
  --input weyl \
  --out experiments/output/tower_pair_d4_lifted.json
```

Then verify:

```bash
qkernel zd-valuation experiments/output/tower_pair_d4_lifted.json --input weyl

qkernel tower-scope experiments/output/tower_pair_d4_lifted.json \
  --input weyl \
  --contexts 0,1 \
  --base-d 2
```

## Phase lift

The default phase lift is:

```text
gamma in Z_d  ->  2 gamma in Z_{2d}
```

This matches the sign lift in the simple `d=2 -> d=4` examples. For external
operator data, explicit `context_phases` should be supplied and audited.

## Scope

Certified:

```text
validity of constructed d -> 2d WeylProgram
closure and commutation checks
Z_d valuation check on output
compatibility with tower-scope
```

Unsupported for now:

```text
odd base d, because x-x terms make the lift constraints quadratic
resource or compiler optimization claims
```
