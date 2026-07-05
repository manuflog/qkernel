# `export-circuit`: theory → runnable hardware test

Exports a two-qubit (d=2, m=2) contextuality kernel to a **standalone, runnable
Qiskit script** that certifies the obstruction on IBM hardware.

## What it emits

For each context, a **sequential non-destructive measurement** of the three
commuting observables: each observable is measured into its own classical bit via
an ancilla Hadamard-test (`H · controlled-P · H · measure · reset`), and the
context statistic is the shot-by-shot product of the three measured eigenvalues.
The emitted script pins all contexts to one low-error qubit triple, enables
dynamical decoupling and measurement/gate twirling, uses 8192 shots, and reports
per-context values with error bars plus the significance of `S` above the
noncontextual bound.

## Why sequential (and not a single joint measurement)

The three observables of a context multiply to the scalar `sign·I`. If you
diagonalise the context and read all three eigenvalues from a **single** basis
label, their product is `sign·(o0·o1)² = sign` on *every shot* — an algebraic
identity independent of the device. That statistic returns the ideal value **even
on random counts**, so it certifies nothing (it is "pinned"). Measuring the three
observables in **physically separate** operations is what lets device error
genuinely pull the correlator below the ideal, so `S` above the NC bound is a real
certification. The emitted protocol avoids the pinned statistic by construction,
and the test-suite (`test_emitted_statistic_is_data_dependent_not_pinned`) guards
against regressions to it.

## Validation on real hardware

The emitted protocol is the one used for the paper's hardware section: on IBM
`ibm_marrakesh` it gave `S = 4.646 ± 0.017` (37.8σ above the NC bound of 4), and
replicated across `ibm_marrakesh`/`ibm_fez`/`ibm_kingston` (multi-device). A
noiseless simulator gives the ideal `S = 6`; a noisy simulator gives `S ≈ 4.5`,
confirming data-dependence.

## Scope guard

Synthesis is for two-qubit Pauli contexts only. For `d > 2` or `m > 2` the command
**refuses** rather than emit an unverified circuit: a genuine qudit (`d ≥ 4`)
protocol needs a `Z_d` phase readout whose depth (~2000 two-qubit gates for the
full d=4 witness) is impractical on current hardware and is validated separately.

## Usage

```bash
qkernel export-circuit kernel.weyl --out protocol.py     # all contexts
qkernel export-circuit kernel.weyl --contexts 0,2,5 --out protocol.py
```

Run the emitted script with `QISKIT_IBM_TOKEN` set in the environment.
