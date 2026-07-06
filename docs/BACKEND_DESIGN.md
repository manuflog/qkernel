# Backend-Aware Experiment Design (v0.40)

`minimal_contextuality_tests` ranks state-independent contextuality tests by
*cost* (fewest settings/observables). `qkernel.backend_design` re-ranks them by
*expected experimental significance* under an explicit readout-noise model.

## Model

Context operators of a parity test are scalars, so the correlators are exactly
+/-1 for every input state: **state-preparation noise does not degrade the
signal**; readout does. With per-context correlator visibility `eta_c`:

- expected functional `S = sum_c eta_c` (ideal `n` = number of contexts)
- noncontextual bound `S_NC = n - 2`
- certification threshold: mean visibility `> (n-2)/n` (= 2/3 for the 6-context minimal test)
- shots to certify at `k` sigma (uniform per-context budget):
  `total = n * k^2 * sum_c (1 - eta_c^2) / (S - (n-2))^2`

Readout: an observable's visibility is `prod_{q in support} (1 - 2 e_q)`;
independent-reads contexts multiply their observables' visibilities;
`joint_basis=True` reads the context's shared eigenbasis once instead.

## Usage

```python
from qkernel.backend_design import BackendModel, backend_aware_tests

backend = BackendModel(readout_error={0: 0.005, 1: 0.03}, default_readout_error=0.02)
ranked = backend_aware_tests(["XI","IX","XX","IY","YI","YY","XY","YX","ZZ"], backend, top=3)
best = ranked[0]
best.test.contexts            # measurement settings
best.estimate.expected_S      # e.g. 4.8 vs NC bound 4
best.estimate.shots_total     # total shots to certify at 5 sigma
```

## Claim scope

This is a **planning estimate** under uncorrelated readout errors, not a
hardware measurement; every estimate carries a `criterion_ledger` saying so.
The underlying tests remain odd-Q kernels independently re-checked by
`verify_kernel` (odd-Q + Z_d/AvN), inheriting `stronger_verifier_passed`.
