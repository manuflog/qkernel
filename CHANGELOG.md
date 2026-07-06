# Changelog

## v0.39.0 — Criterion Ledger / Semantic Firewall

- **Criterion ledger.** New `metadata.CRITERIA` registry (`odd_Q_even_d_v1`,
  `zd_avn_valuation_v1`) and `metadata.criterion_ledger(...)` helper. Every
  user-facing result now carries a machine-readable `criterion_ledger` declaring
  `criterion_id`, `verifier_used`, `claim_scope`, `stronger_verifier_available`,
  and `stronger_verifier_passed`, so odd-Q parity verdicts can never silently be
  read as Z_d/AvN valuation verdicts (or vice versa).
- Ledger threaded through: `ActivationReport`, `ActivatedResource` (which now
  additionally *runs* `check_kernel_zd_valuation` on the activated kernel and
  records the outcome), `ContextualityTest` (experiment design; populated from
  `verify_kernel`'s `zd_contextual`), and `ContextualitySubroutineResult`.
- **Wording firewall.** `docs/ACTIVATION.md` and `embedding.py` no longer call
  lifting a "free, passive operation"; the embedding is described as a
  label-level passive embedding in the mathematical model, with an explicit
  disclaimer that no physical/compiler resource-freeness is claimed (this
  resolves the contradiction with the README scope box).
- Fixed stale `metadata.QKERNEL_VERSION` (was 0.37.0).

## [0.38.0] - 2026-07-05
### Added
- Activation as resource generation (`qkernel.embedding.activated_resource`, `activation-resource` CLI):
  extracts the cheapest contextuality test activated by d->2d embedding of a non-contextual base, verified
  on the odd-Q criterion (consistent with the activation definition; not the stricter Z_d verifier).
- Stim interoperability check (`tests/test_stim_oracle.py`, optional `[stim]` extra): cross-validates the
  stim-lite adapter and qkernel's Pauli algebra against real Stim (v1.16+) as an independent oracle --
  Stim parses the .stim examples and confirms every context pairwise-commutes and products to +/-I.
- Experiment-design layer (`qkernel.experiment_design`): given a device's measurable Paulis, returns
  the cheapest state-independent contextuality test(s) as concrete measurement settings, ranked by
  fewest settings then fewest observables. New `minimal-test` CLI command.
- Composable **contextuality subroutine** (`qkernel.subroutine.analyze_contextuality`): one stable-
  contract call returning the decision, the minimal certificate, independent verification, optional
  CP-SAT certified-minimality and minimal-kernel count, and the obstruction value -- designed to plug
  into a larger quantum-compilation / resource-estimation loop (subroutine-oriented design). See docs/SUBROUTINE.md.
- CP-SAT exact backend (`qkernel.solvers_milp`, optional OR-Tools): independent integer-programming
  solver, `solver="cpsat"`. Cross-validates the native solvers and **certifies** minimality on
  high-cycle-dimension families where exhaustive span enumeration is infeasible (m=3, cycle_dim 259).
- Contextuality **activation by dimension embedding** (`qkernel.embedding`): `build_fiber_pool`
  (d->2d fiber pool) and `activation_report`; a non-contextual base can become contextual under
  passive embedding. New `activation` CLI command; example `activation_base_d4.json`. Reproduces the
  verified research activation-yield curve exactly.
- Sparse-cycle heuristic solver (`find_min_odd_cycle_heuristic`): minimum-weight coset-leader local
  search; scales to cycle-dimension >5000 where exact span enumeration is infeasible. Selectable via
  `find_min_odd_cycle(solver="heuristic")`; `analyze` and `compress_min_odd_q` auto-fall-back to it.
- `find_all_min_odd_cycles`: enumerates all distinct minimal contextual kernels (reproduces the 10
  Mermin squares of the two-qubit doily). New `enumerate-kernels` CLI command.
- Benchmark suite (`experiments/benchmark_suite.py`) and dense-Pauli generator
  (`experiments/dense_pauli.py`) for solver scaling and the exact-vs-heuristic crossover.
### Fixed
- `analyze` no longer raises on high cycle-dimension families; contextuality is decided by odd-carry
  parity (exact) with a heuristic witness.

## [0.37.0] - 2026-07-05

### Repo hygiene (public-release prep)
- Removed development scratch from the tree (32 `DEV_OUTPUT_*.txt`, `TEST_OUTPUT.txt`,
  AI-handoff notes, internal status/manifest files, LaTeX build temp); git history retains them.
- Fixed version drift (pyproject / CITATION now 0.37.0) and corrected the CITATION repository URL
  to `github.com/manuflog/qkernel`.
- Fixed README math to render on GitHub (`$...$` / `$$...$$`); added CI/license/python/status badges
  and a prominent scope callout.
- Release-audit and github-ready checks updated to require genuine public files, not internal scratch.
- Software note is now shipped as **PDF only** (`paper/qkernel_note.pdf`); LaTeX source and build
  artifacts are not distributed. Maintainer contact set to `manuel.flores@columbia.edu`.

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
