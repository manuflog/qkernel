# Spectrum — Obstruction Values by Dimension

`qkernel spectrum --d D` reports the obstruction spectrum at local dimension `D`
in one call. It is a pure dimension-level lookup encoding the Obstruction
Spectrum Theorem; it needs no program file.

## What it reports

For **even d**: `H(d) = {0, d/2}`. The only achievable state-independent
obstruction value is `d/2`, which is the order-two element of `Z_d` and is
2-primary (so the mod-2 carry shadow is value-faithful).

For **odd d**: `H(d) = {0}`. Odd-dimensional Weyl stabilizer families are
noncontextual — there is no state-independent parity obstruction.

## Usage

```bash
qkernel spectrum --d 4    # -> {0, 2}, order 2, 2-primary
qkernel spectrum --d 6    # -> {0, 3}, order 2, 2-primary
qkernel spectrum --d 3    # -> {0}  (odd: noncontextual)
```

Fields: `achievable_values`, `nonzero_value` (d/2 or null), `value_order`
(always 2 for even d), `two_primary`, `shadow_value_faithful`.

## Relationship to the other commands

- `zd-valuation` / `analyze` decide contextuality for a *specific* program.
- `two-primary` reports the 2-primary structure for a program's modulus.
- `spectrum` gives the dimension-level classification directly from `d`, with no
  program — useful for reasoning about what values are even possible before
  building a family.
