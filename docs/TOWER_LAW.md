# Tower / Doubling-Law Scope

Q-Kernel v0.29 promotes the tower/doubling-law diagnostic from experimental
scope reporting to a certified closed-form generativity check for valid fiber
cycles.

## Closed formula

For a fiber lift `d -> 2d`, write each lifted observable as:

```text
v_tilde = u + d x
```

where:

```text
u = base residue in Z_d
x = binary lift bit vector in {0,1}
```

For flattened selected cycle pairs define:

```text
M_ab = <u_a, x_b> + <x_a, u_b>
```

Then:

```text
G = floor(sum M_ab / 2) XOR floor(K / 2) mod 2
```

where `K` is the number of odd `M_ab` terms.

A cycle is non-generative iff:

```text
G = 0
```

## Important implementation rule

`sum M_ab` is computed directly over flattened cycle pairs.

Do **not** reconstruct it as an intrinsic `<U,X> - sum <u_i,x_i>` expression:
that reconstruction can have a mod-4 error on repeat cycles.

The direct pair sum is used and supports repeated observables.

## CLI

```bash
qkernel tower-scope examples/tower_pair_d4_nongenerative.json \
  --input weyl \
  --contexts 0,1,2,3,4,5 \
  --base-d 2
```

## Scope boundary

Certified:

```text
closed formula for tower/doubling generativity bit G on valid fiber cycles
repeat-observable cycles handled by the floor(K/2) correction
```

Not certified:

```text
resource advantage
tower compression as compiler optimization
free embedding
T-count or magic-state optimization
```

All lifted certificates should still pass the genuine `Z_d` valuation verifier.
