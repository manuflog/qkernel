# Changelog

## Unreleased — Kernel census report

- Added `qkernel.kernel_census`: a conservative minimal-kernel census over the
  Contextuality Benchmark Zoo.
- New `kernel-census` CLI command reports per-instance kernel weights,
  multiplicities, obstruction values, and by-`(d,m)` witnessed minima.
- Markdown rendering is available through `qkernel kernel-census --out-md`.
- Summaries include explicit `global_K_proven`, `global_K_value`, and
  `proof_obligations` fields so witnessed zoo minima cannot be confused with
  full K(d,m) theorems.
- Optional theorem-pin JSON files can merge externally proven K(d,m) values into
  the census with source, proof method, verifier, and notes preserved.
- Theorem pins are rejected if they claim a K(d,m) value larger than an already
  witnessed zoo kernel for the same `(d,m)`.
- Theorem pins now receive explicit audit records, and `kernel-census --target-dm
  D,M` tracks open or pinned K(d,m) research targets such as `(8,2)` and `(16,2)`.
- Added `kernel-census --target-file` plus `examples/kernel_census_targets.json`
  so atlas target plans can carry target IDs, priority, source, and rationale.
- Added `qkernel.resource_oracle` and the `resource-features` CLI to export
  qkernel kernel features alongside externally supplied T-count/T-depth/magic
  metrics without claiming qkernel predicts those resources.
- Added `docs/PRD_COMPILER_MAGIC_FACTORY_BRIDGE.md`, a staged plan for compiler,
  magic-state, optimizer, circuit-builder, and factory-candidate development.
- Added `qkernel.compiler_candidates` and the `compiler-candidates` CLI for
  before/after compiler-candidate corpora with semantic-proof and resource-metric
  status tracked separately from qkernel diagnostics.
- Added `qkernel.factory_candidates` and the `factory-candidates` CLI for
  MagicScout factory-adjacent candidate corpora with template compatibility,
  missing factory metrics, and non-claims tracked.
- Added `qkernel.circuit_manifest` and the `circuit-manifest` CLI for
  circuit-builder readiness reports that expose supported Qiskit export cases
  and blockers for unsupported qudit/protocol cases.
- Added `qkernel.correlation_study` and the `correlation-study` CLI for joining
  qkernel features with externally supplied resource metrics and negative
  controls under explicit correlation-only language.
- `correlation-study` can now write a joined CSV table via `--out-csv` for
  external notebooks, spreadsheets, or statistical tooling.
- Added `qkernel.impact_register` and the `impact-register` CLI to keep
  compiler, optimizer, circuit-builder, magic-state, factory, resource, and PRD
  application tracks tied to current capability, missing evidence, next actions,
  and claim boundaries.
- Added `qkernel.application_prd` and the `application-prd` CLI for a scoped
  next-application PRD that recommends a CLI-first evidence workbench before UI,
  optimizer, or factory-simulator expansion.
- Added `qkernel.application_packet` and the `application-packet` CLI to compose
  compiler, factory, correlation, resource, and circuit-manifest evidence into a
  single claim-gated review packet.
- The development extra includes `numpy>=1.26`, matching test paths that import
  the Qiskit protocol exporter.
- Added `docs/KERNEL_CENSUS.md` and `tests/test_kernel_census.py`.

## v0.52.0 — MagicScout research report generator

- New `qkernel.magic_report`: Markdown report generator for single MagicScout
  reports, portfolios, and search results.
- Reports preserve the semantic firewall: criterion ledger, backend-planning
  estimates, template compatibility, missing evidence, safe language, forbidden
  language, and next-experiment checklist.
- Added `docs/MAGIC_REPORTS.md` and `tests/test_magic_report.py`.

## v0.51.0 — MagicScout candidate-search engine

- New `qkernel.magic_search`: candidate discovery over available Pauli measurements.
  It uses the existing experiment-design layer to generate contextuality motifs,
  runs each candidate through MagicScout, checks factory-template compatibility,
  optionally incorporates backend estimates, and ranks candidates by a transparent
  research-prioritization rule.
- New standard two-qubit search helper over the doily / all 15 two-qubit Paulis.
- New `docs/MAGIC_SEARCH.md` and tests for ranking, required-template filtering,
  negative/non-claim guardrails, and JSON serializability.
- Scope discipline: search outputs are research hypotheses, not generated physical
  magic-state factories or overhead improvements.

## v0.50.0 — MagicScout factory-template bridge

- Added `qkernel.magic_templates`: conservative checklist templates for mapping
  MagicScout reports to possible research roles: contextuality witness,
  verification subroutine, hardware-ready probe, distillation-check motif, and
  cultivation/activation motif.
- MagicScout reports now carry template assessments as diagnostic metadata.
- Added a distillation-stub example that deliberately remains blocked because
  acceptance probability / real factory evidence is missing.
- Added template tests to ensure the bridge never claims a valid factory,
  threshold, fidelity, or overhead improvement.

## v0.49.0 — MagicScout application workflow

- MagicScout matured from a single diagnostic into an application workflow:
  protocol schema, portfolio ranking, benchmark-zoo bridge, backend-aware
  significance estimates, candidate generation from available Pauli sets, and
  a dedicated MagicScout claim-scope audit.
- New protocol type: `qkernel.magic_protocol.v1`.
- New portfolio type: `qkernel.magic_portfolio.v1`.
- New workflows: `magic-protocol`, `magic-portfolio`, `magic-zoo`,
  `magic-generate`, and `magic-audit`.
- Still no magic-factory overclaim: reports list missing factory evidence and
  explicit non-claims for overhead, thresholds, fidelity, acceptance probability,
  code distance, decoder behavior, and space-time volume.

## v0.43.0 — Paper-ready software artifact release

- `CITATION.cff` (CFF 1.2.0; Apache-2.0, matching the repository license).
- README: "Theory-to-hardware artifact pipeline" section documenting the
  v0.39-v0.43 bridge — decide & certify (criterion ledger), design (cost- and
  backend-aware), pin (benchmark zoo), run (sequential protocol), record
  (hardware result registry).
- Tagged release v0.43.0.

## v0.42.0 — Hardware Result Registry

- New `qkernel.hardware_registry`: dependency-free, schema-validated JSON-lines
  records (`qkernel.hardware_result.v1`) closing the loop
  theory -> certificate -> protocol -> **measured result**. Each record links
  the measured contexts + constraint signs, the pre-run v0.40 backend-model
  prediction (or an explicit None), per-context +/-1 product-statistic counts,
  and a computed verdict: measured S, standard error, significance z above the
  noncontextual bound n-2, certified at k sigma.
- `compute_verdict` (counts -> S, sigma_S, z, certified), `new_record`,
  `append_record`/`load_registry` (JSONL, validated on both write and read),
  `prediction_gap` (measured minus predicted S).
- Discipline: no bare "certified" flag without the numbers that produced it,
  and every record carries a criterion ledger scoping the claim to a measured
  odd-Q parity violation on the recorded device.

## v0.41.0 — Contextuality Benchmark Zoo

- New `qkernel.zoo`: a curated registry of small contextuality instances with
  *expected* verdicts, pinned per criterion and enforced by the test suite —
  a permanent regression harness and research artifact. Instances:
  `peres_mermin` (kernel 6, exactly 1 minimal kernel, Z_d verified),
  `noisy_peres_mermin` (kernel extraction from 40 irrelevant contexts),
  `doily_two_qubit` (GQ(2,2): kernel 6, exactly **10** minimal kernels — the
  doily's 10 Mermin squares), `single_context` (non-contextual),
  `odd_d_qutrit` (the odd-Q *shadow trap*: criterion identically zero for odd
  d; no parity claim licensed), and `cert4_d4` (the verified minimal d=4
  certificate, obstruction value 2, Z_d verified).
- Recorded fact worth pinning: naive 2x scaling of the PM square into d=4 is
  **non-contextual** under the odd-Q criterion — genuine d=4 value-2
  contextuality requires the cert4 family, not a rescaled PM.
- Each instance declares its `claim_scope`; zoo checks include the criterion
  ledger's `stronger_verifier_passed` where pinned.

## v0.40.0 — Backend-Aware Experiment Design

- New `qkernel.backend_design`: rank contextuality tests by **expected
  experimental significance** under a device readout-noise model
  (`BackendModel`: per-qubit assignment errors; independent-reads or
  joint-basis readout). `estimate_significance` returns expected S, the
  noncontextual bound `n-2`, the margin, and the closed-form total shots to
  certify at `k` sigma; `backend_aware_tests` re-ranks the minimal tests by
  shots-to-certify (cost-minimal and significance-optimal tests need not
  coincide once qubit errors are uneven).
- Physics note encoded in the model: context operators are scalars, so
  state-preparation noise does not degrade the signal — readout visibility is
  the binding resource; certification threshold is mean visibility > (n-2)/n.
- Estimates carry a criterion ledger with claim scope "planning estimate",
  inheriting `stronger_verifier_passed` from the underlying verified test.
- `docs/BACKEND_DESIGN.md`; tests incl. closed-form cross-check and
  threshold/monotonicity behavior.

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
