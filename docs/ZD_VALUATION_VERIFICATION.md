# Z_d Valuation Verification

Q-Kernel v0.28 adds a genuine `Z_d` valuation-system check.

This addresses the compression trap:

```text
odd-Q / Z_2 shadow contextuality
    does not always imply
genuine AvN contextuality over Z_d
```

A compressed odd-Q kernel can pass the parity-shadow test while still admitting a
noncontextual `Z_d` valuation. Therefore verification now checks the full system:

```text
M phi = gamma mod d
```

where:

```text
M     = context-observable multiplicity matrix over Z_d
phi   = observable valuation vector
gamma = context phase/scalar vector
```

The family is genuinely `Z_d`-contextual iff this system is unsolvable.

## Phase convention

If `context_phases` is supplied in the Weyl JSON, Q-Kernel uses it.

If omitted, Q-Kernel uses a backward-compatible odd-Q phase model:

```text
gamma_i = (d/2) * b_i mod d    for even d
gamma_i = 0                    for odd d
```

For high-d AvN certificates, prefer explicit `context_phases`.

## CLI

```bash
qkernel zd-valuation examples/peres_mermin_pauli.json --input pauli
```

## Verifier hardening

`verify_kernel` now requires both:

```text
A^T lambda = 0 mod 2
Q(lambda) = 1
Z_d valuation system unsolvable on the selected kernel family
```

If a compressed family is parity-only contextual but has a valid `Z_d` valuation,
verification fails.

## Implementation

The solver uses Smith normal form over the integers. For `S = U M V`, the system
is solvable modulo `d` iff each transformed diagonal congruence is solvable:

```text
s_i y_i = (U gamma)_i mod d
```

i.e.

```text
gcd(s_i, d) divides (U gamma)_i
```
