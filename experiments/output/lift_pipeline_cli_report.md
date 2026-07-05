# Q-Kernel Lift Pipeline Report

- constructed: `True`
- base d: `2`
- lifted d: `4`
- selected contexts: `[0, 1]`

## Safe claim

validated fiber lift plus Z_d valuation result plus closed tower-law generativity report

## Unsafe claims

- does not prove resource advantage
- does not prove T-count or magic-cost improvement
- does not certify compiler rewrite legality
- does not certify tower compression as an optimization

## Fiber lift

```json
{
  "status": "constructed",
  "constructed": true,
  "reason": "valid d -> 2d fiber lift constructed and validated.",
  "base_d": 2,
  "lifted_d": 4,
  "lift_bits": {
    "A": [
      1,
      0
    ],
    "A_inv": [
      0,
      0
    ]
  },
  "zd_contextual": true,
  "zd_reason": "Z_d valuation system is unsolvable; genuine AvN contextual family"
}
```

## Z_d valuation

```json
{
  "contextual": true,
  "status": "contextual",
  "solvable": false,
  "modulus": 4,
  "phases": [
    0,
    2
  ],
  "observable_order": [
    "A",
    "A_inv"
  ],
  "reason": "Z_d valuation system is unsolvable; genuine AvN contextual family"
}
```

## Tower law

```json
{
  "status": "certified_nongenerative",
  "certified": true,
  "reason": "certified closed tower/doubling formula; cycle is non-generative iff G=0",
  "selected_contexts": [
    0,
    1
  ],
  "base_d": 2,
  "lifted_d": 4,
  "flattened_observables": [
    "A",
    "A_inv",
    "A",
    "A_inv"
  ],
  "repeated_observables": {
    "A": 2,
    "A_inv": 2
  },
  "sum_m": 0,
  "odd_m_count": 0,
  "floor_sum_m_over_2": 0,
  "floor_odd_m_count_over_2": 0,
  "generativity_bit": 0,
  "non_generative": true,
  "zd_contextual": true,
  "zd_reason": "Z_d valuation system is unsolvable; genuine AvN contextual family"
}
```
