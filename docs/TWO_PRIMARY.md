# Two-Primary Obstruction Value / Shadow Value-Faithfulness

## Statement

Corollary of the Obstruction Spectrum Theorem (`H(d) = {0, d/2}` for even `d`).

Write `d = 2^k * m` with `m` odd. Under the CRT isomorphism
`Z_d ~= Z_{2^k} x Z_m`, the achievable value `d/2 = 2^{k-1} m` maps to

```text
( 2^{k-1} m  mod 2^k ,  0 )
```

It is the order-two element of the 2-primary factor `Z_{2^k}` and is
**identically zero in the odd factor `Z_m`, for every even d**.

Since the spectrum theorem says the only achievable state-independent
obstruction value is `d/2`, the Weyl obstruction is always 2-primary: the odd
part of the local dimension never carries contextuality.

## Practical consequence

The mod-2 carry shadow (the odd-`Q` criterion) detects the full obstruction
**value** at every even `d` — not only 2-power dimensions. So the cheap
GF(2) check is guaranteed complete at the level of values for any even local
dimension, including `d` with a nontrivial odd part (`d = 6, 10, 12, ...`).

This is a value-level statement. Certificate **minimization** (finding the
smallest support) can still require a `Z_d`-cycle search, since minimality is
where the mod-2 shadow can under-report (see `TOWER_SCOPE.md`,
`ZD_VALUATION_VERIFICATION.md`).

## CLI

```bash
qkernel two-primary examples/peres_mermin.json --input weyl
```

Output fields: `two_adic_valuation` (k), `odd_part` (m), `value_dover2` (d/2),
`value_odd_component` (image of d/2 in Z_m; always 0 for even d),
`is_two_primary`, `shadow_value_faithful`.

## Verification

`two_primary_report` is checked for all even `d <= 200`
(`tests/test_two_primary.py`), and against the `d=4` and `d=8` certificates
(values 2 and 4). The claim is deductive from the spectrum theorem, so the
check is a structural report, not a search.
