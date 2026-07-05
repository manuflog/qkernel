# Changelog
## [0.37.0] - 2026-07-05

### Fixed (correctness)
- **`export-circuit` no longer emits a pinned (vacuous) statistic.** The previous
  emitter measured each context with a single joint measurement and reconstructed
  the third observable as `sign * o0 * o1`, making the product `sign` on every shot
  regardless of the device — it certified nothing. The emitter now produces a
  **sequential non-destructive (ancilla Hadamard-test) protocol** whose statistic
  is genuinely data-dependent (validated on IBM hardware: 37.8σ single-device,
  replicated multi-device). Regression test `test_emitted_statistic_is_data_dependent_not_pinned`
  guards against reintroducing the pinned form.
- Emitted script uses token-based auth (`QISKIT_IBM_TOKEN`) instead of the retired
  `channel='ibm_quantum'`, and adds best-qubit-triple pinning, dynamical decoupling,
  twirling, error bars, and σ-above-bound reporting.



## 0.36.0

- Added `qkernel spectrum --d D`: one-call obstruction spectrum for a local
  dimension (H(d)={0,d/2} even, {0} odd) with value order and 2-primary
  structure; a pure dimension-level lookup, no program file needed.
- Added `spectrum_summary` in valuation, `docs/SPECTRUM.md`, and
  `tests/test_spectrum.py`.

## 0.35.0

- Added `qkernel export-circuit`: synthesise a runnable Qiskit measurement
  protocol from a two-qubit kernel (theory -> certificate -> runnable hardware
  test). Clifford diagonaliser per context, baked-in readout tables, emitted as
  a standalone IBM script.
- Every synthesised circuit is exact-sim verified (state-independent) before
  emission; scope-guarded to d=2, m=2 (refuses higher d rather than emit
  unverified circuits).
- Added `qiskit`/`qiskit-ibm-runtime` as an optional `[hardware]` extra
  (imported lazily; core package has no new hard dependency).
- Added `docs/EXPORT_CIRCUIT.md` and `tests/test_export_circuit.py`.

## 0.34.0

- Added 2-primary obstruction-value corollary: value d/2 is always 2-primary
  (zero in the odd CRT factor), so the mod-2 carry shadow is value-faithful at
  every even d, not just 2-powers.
- Added `qkernel two-primary` CLI and `two_primary_report` in valuation.
- Added `docs/TWO_PRIMARY.md` and `tests/test_two_primary.py`.

## 0.33.0

- Added GitHub alpha-readiness scaffolding.
- Added issue templates, PR template, contributing/security/support docs.
- Added `qkernel github-ready` CLI and checks.

## 0.32.0

- Added release/readiness audit module and CLI.
- Added release audit docs and experiment script.
- Added generated audit outputs under experiments/output.

## 0.31.0

- Added end-to-end lift pipeline report.
- Added `qkernel lift-pipeline` CLI.
- Added lift pipeline demo script and docs.

## 0.30.0

- Added validated even-base d -> 2d fiber-lift constructor.
- Added `qkernel fiber-lift` CLI.
- Added fiber-lift docs and examples.

## 0.29.0

- Added certified closed tower/doubling generativity formula.
- Replaced experimental tower scope implementation with compatibility shim.
- Added direct pairwise M_ab computation including repeat-observable cycles.

## 0.28.0

- Added genuine Z_d valuation-system verification using Smith normal form.
- Hardened `verify_kernel` and certificates against parity-only compressed kernels.
- Added optional `context_phases` support to WeylProgram and JSON IO.

## 0.27.0

- Added rewrite-candidate policy registry.
- Added optimizer-claim guardrail CLI commands.
- Added policy fields to compiler pass comparison reports.

## 0.26.0

- Added compiler-pass playground with before/after Qiskit-lite examples.
- Improved compiler pass comparison verdict for nonkernel pruning diagnostics.

## 0.25.0

- Added dependency-free Qiskit-lite JSON adapter.
- Added built-in `qkernel self-test` smoke test.
- Added install smoke documentation.

## 0.24.0

- Added compiler diagnostic report and before/after pass comparison contract.
- Added conservative quantum-compiler optimizer roadmap and claim boundaries.
- Added package polish: Apache-2.0 license, CITATION.cff, MANIFEST.in, py.typed, package metadata.
- Added install/package smoke tests.

## 0.23.0

- Added optional PySAT/RC2 backend wrappers behind `qkernel[sat]`.

## 0.22.0

- Added dependency-free Stim-lite MPP adapter.

## 0.21.0

- Added release manifest and note-location files.

## 0.20.0

- Added Saniga/Holweck/de Boutray/Muller finite-geometry novelty hygiene.

Earlier versions built the core odd-Q analyzer, solvers, certificate system, SAT/MaxSAT export, external solver import, closed Q form, and paper scaffolding.
