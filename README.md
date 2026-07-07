# Q-Kernel

[![tests](https://github.com/manuflog/qkernel/actions/workflows/tests.yml/badge.svg)](https://github.com/manuflog/qkernel/actions/workflows/tests.yml)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](pyproject.toml)
![status: alpha](https://img.shields.io/badge/status-alpha-orange.svg)

> **Scope (read first).** Q-Kernel finds small, independently verifiable contextuality
> kernels in Weyl/Pauli measurement programs. It is **not** a magic-state optimizer, a
> T-count optimizer, a tower-compression optimizer, or a compiler semantic-equivalence
> engine, and it does **not** claim passive dimension embedding is free. Every
> user-facing result carries a machine-readable `criterion_ledger` declaring the
> criterion it was verified under (`odd_Q_even_d_v1` vs `zd_avn_valuation_v1`),
> the verifier used, the claim scope, and whether the stronger verifier passed. See
> [`ALPHA_README.md`](ALPHA_README.md) for the full positioning.

## Theory-to-hardware artifact pipeline (v0.39–v0.43)

Q-Kernel is a research artifact with a complete, criterion-disciplined bridge
from theory to measured hardware results:

1. **Decide & certify** — `analyze_contextuality`: odd-Q verdict, minimal
   kernel, independent re-verification (odd-Q + Z_d/AvN), optional CP-SAT
   minimality proof. Every result carries a `criterion_ledger` (v0.39).
2. **Design** — `minimal_contextuality_tests` (cheapest settings) and
   `backend_design.backend_aware_tests` (ranked by expected significance and
   shots-to-certify under a per-qubit readout-noise model; v0.40).
3. **Pin** — `zoo.run_zoo()`: curated instances with expected verdicts per
   criterion, enforced by the test suite as a permanent regression harness
   (v0.41).
4. **Run** — `export_circuit.export_qiskit_protocol`: sequential
   non-destructive measurement protocol (avoids the pinned-statistic pitfall).
5. **Record** — `hardware_registry`: schema-validated JSONL records linking
   prediction, per-context counts, and the computed verdict (S, z above the
   noncontextual bound, certified at k sigma; v0.42).

Cite via `CITATION.cff` (v0.43).


> **Part of a larger program.** Q-Kernel is the software component of a research program on
> contextuality as cohomological obstructions. Papers, machine-checkable verifications, and hardware
> results: [`manuflog/contextuality-obstructions`](https://github.com/manuflog/contextuality-obstructions).
**Q-Kernel** is an experimental Python library for contextuality kernel extraction in Weyl/Pauli measurement programs.

It implements the binary-linear-algebra core behind the odd-$Q$ criterion:


$$F \text{ contextual}
\iff
\exists \lambda,\quad A^T\lambda=0 \pmod 2,\quad b^T\lambda=1 \pmod 2.$$


Engineering interpretation:

> Given a large Weyl/Pauli measurement program, find the smallest closed parity cycle of contexts carrying an odd commutator-carry obstruction — the irreducible contextual kernel.

## What this is

A narrow, testable compiler-analysis backend:

- validate Weyl/Pauli context families;
- compute commutator-carry bits $b(C)$;
- build the context-observable incidence matrix $A$;
- find parity cycles $A^T\lambda=0$;
- detect odd-$Q$ contextuality (polynomial decision, never enumerates);
- compress a large program to a minimal odd-$Q$ certificate, via five solver backends
  (span / bounded-weight / branch-bound / heuristic / CP-SAT) — the heuristic scales past
  cycle-dimension 5000, and CP-SAT *certifies* minimality where enumeration is infeasible;
- enumerate **all** minimal kernels (contextuality-structure invariant);
- expose all of the above as one composable **subroutine** for pipeline integration
  (`qkernel.subroutine`), with two applications built on it: cheapest-contextuality-test
  **experiment design** (`minimal-test`) and **activation-by-embedding** as resource
  generation (`activation`, `activation-resource`).

## What this is not yet

This is **not yet** a T-count optimizer or a full quantum compiler. The first target is a rigorous contextuality kernelizer. Later modules can connect the kernel size/rank to magic-state overhead, resource estimation, and qudit compiler passes.

## Install locally

```bash
pip install -e ".[dev]"
```

## CLI examples

```bash
qkernel analyze examples/peres_mermin.json
qkernel compress examples/noisy_pm.json
qkernel enumerate-kernels examples/peres_mermin.json          # all minimal kernels
qkernel kernel-census                                         # zoo minimal-kernel census
qkernel kernel-census --target-dm 8,2 --target-dm 16,2        # track open K(d,m) targets
qkernel kernel-census --target-file examples/kernel_census_targets.json
qkernel resource-features examples/peres_mermin.json          # export features for an external resource oracle
qkernel minimal-test XI IX XX IY YI YY XY YX ZZ               # cheapest test from device Paulis
qkernel activation examples/activation_base_d4.json           # does d->2d embedding activate?
qkernel activation-resource examples/activation_base_d4.json  # cheapest activated test
```

Expected behavior:

- `peres_mermin.json` is contextual;
- `noisy_pm.json` compresses many irrelevant contexts to the six-context Peres-Mermin kernel;
- the nine Peres-Mermin Paulis yield exactly one cheapest test (the PM square); all 15 two-qubit
  Paulis yield the 10 Mermin squares of the doily.

## Python API

```python
from qkernel.io import load_program
from qkernel.analyzer import analyze
from qkernel.optimizer import compress_min_odd_q

program = load_program("examples/peres_mermin.json")
result = analyze(program)
kernel = compress_min_odd_q(program)

print(result.contextual)
print(kernel.selected_contexts)
```

## Composable subroutine and applications

Q-Kernel exposes contextuality analysis as a single composable **subroutine** — the natural
unit at which a host quantum-compilation / resource-estimation loop measures the value of the
contextuality step (see [`docs/SUBROUTINE.md`](docs/SUBROUTINE.md)):

```python
from qkernel.subroutine import analyze_contextuality

r = analyze_contextuality(program, enumerate_all_kernels=True, certify_minimal=True)
# r.contextual, r.min_kernel_contexts, r.kernel_weight, r.verified,
# r.certified_minimal (CP-SAT), r.n_minimal_kernels, r.obstruction_value
```

Two applications are built on it:

- **Experiment design** (`qkernel.experiment_design`, `minimal-test` CLI): given a device's
  measurable Paulis, return the cheapest state-independent contextuality test(s) as concrete
  measurement settings, ranked by fewest settings then fewest observables.
- **Kernel census** (`qkernel.kernel_census`, `kernel-census` CLI): run a conservative
  minimal-kernel census over the benchmark zoo, grouped by `(d,m)`. This is a bridge toward
  K(d,m) work, not a proof of global lower bounds. Explicit `--target-dm D,M`
  entries or `--target-file` target plans keep open targets such as `K(8,2)`
  visible even before qkernel has a registered zoo witness. See
  [`docs/KERNEL_CENSUS.md`](docs/KERNEL_CENSUS.md).
- **Activation by embedding** (`qkernel.embedding`, `activation` / `activation-resource` CLI):
  a non-contextual base can become contextual under passive `d -> 2d` embedding (the *fiber
  pool*); the yield reproduces the verified research curve and falls sharply with base dimension.
  See [`docs/ACTIVATION.md`](docs/ACTIVATION.md).
- **MagicScout** (`qkernel.magic`, `magic-protocol` / `magic-search` / `magic-report` CLI):
  a conservative magic-state-adjacent triage layer that ranks contextuality motifs, checks
  factory-template compatibility, renders research reports, and explicitly preserves non-claims
  around overhead, thresholds, fidelity, acceptance probability, code distance, decoder behavior,
  and space-time volume. See [`docs/MAGICSCOUT.md`](docs/MAGICSCOUT.md).
- **Resource oracle bridge** (`qkernel.resource_oracle`, `resource-features` CLI):
  export qkernel kernel features next to externally supplied T-count, T-depth,
  magic-injection, or stabilizer-rank metrics. This is a correlation-study
  bridge, not a resource predictor. See [`docs/RESOURCE_ORACLE.md`](docs/RESOURCE_ORACLE.md).

The staged plan for compiler, magic-state, circuit-builder, optimizer, and
factory-candidate development is tracked in
[`docs/PRD_COMPILER_MAGIC_FACTORY_BRIDGE.md`](docs/PRD_COMPILER_MAGIC_FACTORY_BRIDGE.md).

This is classical analysis (no quantum speedup is claimed); the design value is composability.

## Core theorem implemented

For even local dimension $d$, contexts are finite commuting Weyl families whose labels sum to zero mod $d$. For each context,


$$b(C)=\sum_{i<j}\langle c_i,c_j\rangle/d \pmod 2.$$


For a cycle $\lambda$ in the left kernel of the incidence matrix,


$$A^T\lambda=0,$$


the odd-$Q$ obstruction is detected by


$$b^T\lambda = Q(\lambda) = 1.$$


The key implementation rule is:

> Do **not** reduce the symplectic pairing modulo $d$ before dividing by $d$. The carry is an integer lift.

## Roadmap

1. Core library and CLI. **done**
2. Certificate renderer. **done**
3. Qiskit / Stim / Pauli-string adapters. **done** (Stim adapter cross-validated against real Stim v1.16)
4. Minimum-weight odd-$Q$ optimization beyond brute-force enumeration. **done** — five backends
   (span / bounded-weight / branch-bound / heuristic / CP-SAT); the heuristic scales past cycle-dim 5000
   and CP-SAT *certifies* minimality where enumeration is infeasible. See [`docs/SOLVERS.md`](docs/SOLVERS.md).
5. Resource-estimator experiments (kernel features vs T-count, magic, stabilizer rank). **bridge added** — `resource-features` accepts external oracle metrics; validated correlation studies remain open.
6. Qudit demos for even $d=4,6,8$. **done** — obstruction spectrum $H(d)=\{0,d/2\}$, 2-primary tower, and d→2d activation.

See [`docs/ROADMAP.md`](docs/ROADMAP.md) for the phase-by-phase status (Phases 1–3 complete, Phase 4 applications delivered).


## Pauli frontend

Version 0.2 adds a human-readable qubit Pauli frontend:

```bash
qkernel analyze-pauli examples/peres_mermin_pauli.json
qkernel compress-pauli examples/peres_mermin_pauli.json --json
```

This lets users write contexts as Pauli strings:

```json
{
  "type": "pauli_contexts",
  "contexts": [
    ["ZI", "IZ", "ZZ"],
    ["IX", "XI", "XX"],
    ["ZX", "XZ", "YY"]
  ]
}
```

The frontend converts `I, X, Y, Z` into Weyl vectors over `d=2` using interleaved `[z1,x1,z2,x2,...]` coordinates.


## Pauli schedule frontend

Version 0.3 adds a grouped Pauli schedule frontend:

```bash
qkernel analyze-schedule examples/peres_mermin_schedule.json
qkernel compress-schedule examples/peres_mermin_schedule.json --json
```

A schedule uses `layers` because contextuality depends on actual co-measurement/context structure, not merely on which Pauli strings appear somewhere.

```json
{
  "type": "pauli_schedule",
  "layers": [
    ["ZI", "IZ", "ZZ"],
    ["IX", "XI", "XX"]
  ]
}
```

This design is intentionally conservative: Q-Kernel does not infer contexts across unrelated layers.


## Solver backends

Compression commands support solver selection:

```bash
qkernel compress examples/peres_mermin.json --solver span
qkernel compress-pauli examples/peres_mermin_pauli.json --solver bounded-weight --max-weight 6
qkernel verify-demo examples/peres_mermin_schedule.json --input schedule
```

Available backends:

- `span`: exact cycle-basis span enumeration;
- `bounded-weight`: exact increasing-context-weight search up to a bound;
- `auto`: current default.

Every solver result can be independently checked with `qkernel.verify.verify_kernel`.


## Component decomposition

Version 0.5 adds connected-component decomposition of the context-observable bipartite graph. Compression uses this by default.

```bash
qkernel components examples/peres_mermin_with_noise_schedule.json --input schedule
qkernel compress-schedule examples/peres_mermin_with_noise_schedule.json --json
```

Disconnected irrelevant blocks no longer enlarge the hard kernel-search problem.


## Observable canonicalization

Version 0.6 adds opt-in canonicalization:

```bash
qkernel canonicalize-report examples/duplicate_vectors_weyl.json
qkernel compress examples/duplicate_vectors_weyl.json --canonicalize by-vector --json
```

Default is conservative:

```text
--canonicalize none
```

Use `by-vector` only when identical Weyl labels should be treated as the same observable.


## IR metadata

Version 0.7 adds optional observable metadata:

```json
"observable_metadata": {
  "ZI_round_1": {"identity_scope": "event", "round": 1},
  "ZI_round_2": {"identity_scope": "event", "round": 2}
}
```

Safe canonicalization respects event identity:

```bash
qkernel canonicalize-report examples/duplicate_vectors_events_weyl.json
qkernel compress examples/duplicate_vectors_events_weyl.json --canonicalize by-vector
qkernel compress examples/duplicate_vectors_events_weyl.json --canonicalize by-vector-force
```

This prevents the tool from confusing algebraic equality with protocol identity.


## Experiments

Version 0.8 adds synthetic benchmark scripts:

```bash
PYTHONPATH=src python experiments/benchmark_decomposition.py
PYTHONPATH=src python experiments/compare_solvers.py
```

These are regression and scaling probes, not quantum-resource claims.

Gemini assessment triage is recorded in:

```text
docs/GEMINI_ASSESSMENT.md
```

The SAT/SMT backend plan is recorded in:

```text
docs/SAT_SMT_BACKEND_PLAN.md
```


## Branch-and-bound solver

Version 0.9 adds an exact pure-Python branch-and-bound backend:

```bash
qkernel compress-pauli examples/peres_mermin_pauli.json --solver branch-bound --json
```

It uses suffix-span feasibility pruning and remains independently verified by `qkernel.verify.verify_kernel`.


## Standalone certificates

Version 0.10 adds stable JSON certificates:

```bash
qkernel certify examples/peres_mermin_pauli.json --input pauli --out pm_certificate.json
qkernel verify-certificate examples/peres_mermin_pauli.json --input pauli --certificate pm_certificate.json
```

A certificate binds the selected odd-Q kernel to the input program by SHA-256 hash and is independently verified.


## Certificate metadata

Version 0.11 adds formal certificate metadata:

```text
qkernel_version = 0.11.0
coordinate_convention = interleaved_zx_v1
criterion = odd_Q_even_d_v1
integer_carry_rule = integer_lift_before_mod_v1
```

Inspect without verifying:

```bash
qkernel inspect-certificate pm_certificate.json
```

A quick summary for Gemini or another reviewer is in:

```text
docs/GEMINI_SUMMARY.md
```


## Pauli table adapter

Version 0.12 adds a dependency-free Qiskit-lite table adapter:

```bash
qkernel analyze-table examples/peres_mermin_table.json
qkernel compress-table examples/peres_mermin_table.csv --json
qkernel certify examples/peres_mermin_table.json --input table --out pm_table_cert.json
```

This is the stable contract future Qiskit/Stim adapters should emit before calling the Q-Kernel core.


## SAT export

Version 0.13 adds dependency-free DIMACS CNF export:

```bash
qkernel export-sat examples/peres_mermin_pauli.json --input pauli --max-weight 6 --out pm_k6.cnf
```

The CNF encodes:

```text
A^T lambda = 0 mod 2
b^T lambda = 1 mod 2
sum(lambda_i) <= k   # optional
```

This is the bridge to external SAT/MaxSAT tooling without adding hard dependencies.


## MaxSAT export

Version 0.14 adds dependency-free WCNF export:

```bash
qkernel export-maxsat examples/peres_mermin_pauli.json --input pauli --out pm.wcnf
```

Hard clauses encode the odd-Q feasibility constraints. Unit soft clauses `-lambda_i` minimize selected contexts.


## External solver output import

Version 0.15 completes the external-solver loop:

```bash
qkernel export-maxsat examples/peres_mermin_pauli.json --input pauli --out pm.wcnf
# run external MaxSAT solver, save output to pm.out
qkernel import-solver-output examples/peres_mermin_pauli.json --input pauli --model pm.wcnf --solution pm.out --out pm_external.cert.json
```

External solvers are treated as untrusted candidate generators. Q-Kernel imports the lambda vector and independently verifies it.

Claude handoff summary:

```text
docs/CLAUDE_HANDOFF.md
```


## Closed Q form

Version 0.16 exposes the equivalent closed observable-multiset form:

```bash
qkernel q-forms examples/peres_mermin_pauli.json --input pauli --contexts 0,1,2,3,4,5
```

It cross-checks `lambda·b` against the aggregate symplectic form.

## Tower scope

Tower/doubling support remains experimental:

```bash
qkernel tower-scope examples/peres_mermin_pauli.json --input pauli --contexts 0,1,2,3,4,5
```

Do not use this for certified tower-compression or resource-advantage claims.


## Paper restructuring

Version 0.17 rewrites `paper/qkernel_note.tex` into a cleaner software/research paper structure and adds paper-safety tests.

Editor notes:

```text
paper/EDITOR_NOTES.md
```


## Paper benchmark tables

Version 0.18 adds generated benchmark tables for the paper:

```bash
PYTHONPATH=src python experiments/render_paper_tables.py
```

Outputs:

```text
paper/generated_benchmark_tables.tex
paper/generated_benchmark_tables.md
```


## Proposition map

Version 0.19 adds explicit paper proposition labels and a code-to-proposition map:

```text
docs/PROPOSITION_MAP.md
```


## Novelty hygiene

Version 0.20 adds explicit Saniga/Holweck/de Boutray/Muller finite-geometry citations and novelty boundaries.

See:

```text
docs/NOVELTY_HYGIENE.md
```

Q-Kernel does not claim novelty for the GF(2) linear-system or binary symplectic polar-space framing.


## Where is the paper note?

Main note:

```text
paper/qkernel_note.tex
paper/qkernel_note.pdf
```

Top-level release guide:

```text
MANIFEST_QKERNEL.md
QKERNEL_NOTE_LOCATION.md
```


## Stim-lite adapter

Version 0.22 adds a dependency-free parser for a small explicit Stim MPP subset:

```bash
qkernel inspect-stim-lite examples/peres_mermin_mpp.stim
qkernel analyze-stim-lite examples/peres_mermin_mpp.stim
qkernel compress-stim-lite examples/peres_mermin_mpp.stim --json
```

See:

```text
docs/STIM_LITE_ADAPTER.md
```


## Optional PySAT backend

Version 0.23 adds optional PySAT/RC2 backend wrappers.

Install:

```bash
pip install 'qkernel[sat]'
```

Run:

```bash
qkernel solve-pysat examples/peres_mermin_pauli.json --input pauli --max-weight 6
qkernel solve-rc2 examples/peres_mermin_pauli.json --input pauli
```

The dependency-free SAT/WCNF export path remains the stable core interface.


## Compiler diagnostics

Version 0.24 adds conservative compiler-facing diagnostics:

```bash
qkernel compiler-report examples/peres_mermin_pauli.json --input pauli
qkernel compare-pass before.json after.json --input pauli
```

See:

```text
docs/COMPILER_OPTIMIZER_PATH.md
```


## Qiskit-lite adapter

Version 0.25 adds a dependency-free Qiskit-lite JSON bridge:

```bash
qkernel inspect-qiskit-lite examples/peres_mermin_qiskit_lite.json
qkernel analyze-qiskit-lite examples/peres_mermin_qiskit_lite.json
qkernel compress-qiskit-lite examples/peres_mermin_qiskit_lite.json --json
```

Built-in smoke test:

```bash
qkernel self-test
```

See:

```text
docs/QISKIT_LITE_ADAPTER.md
docs/INSTALL_SMOKE.md
```


## Compiler pass playground

Version 0.26 adds a concrete before/after diagnostic example:

```bash
qkernel compare-pass examples/compiler_before_qiskit_lite.json examples/compiler_after_qiskit_lite.json --input qiskit-lite
PYTHONPATH=src python experiments/compiler_pass_playground.py
```

See:

```text
docs/COMPILER_PASS_PLAYGROUND.md
```


## Rewrite policy registry

Version 0.27 adds policy guardrails for optimizer-facing claims:

```bash
qkernel rewrite-policies
qkernel assess-rewrite safe_diagnostic_prune
qkernel assess-rewrite forbidden_resource_claim
```

See:

```text
docs/REWRITE_POLICY.md
```


## Z_d valuation verification

Version 0.28 hardens verification against parity-only compression artifacts:

```bash
qkernel zd-valuation examples/peres_mermin_pauli.json --input pauli
```

Certificates now require both odd-Q and genuine `Z_d` valuation-system unsolvability on the selected kernel family.

See:

```text
docs/ZD_VALUATION_VERIFICATION.md
```


## Tower law

Version 0.29 implements the closed tower/doubling generativity formula:

```bash
qkernel tower-scope examples/tower_pair_d4_nongenerative.json --input weyl --contexts 0,1,2,3,4,5 --base-d 2
```

The formula is certified for valid fiber cycles. Tower compression/resource claims remain out of scope.

See:

```text
docs/TOWER_LAW.md
```


## Fiber-lift constructor

Version 0.30 adds a validated even-base `d -> 2d` lift constructor:

```bash
qkernel fiber-lift examples/tower_pair_d2_base.json --input weyl --out experiments/output/tower_pair_d4_lifted.json
```

See:

```text
docs/FIBER_LIFT.md
```


## Lift pipeline

Version 0.31 adds an end-to-end tower reproducibility pipeline:

```bash
qkernel lift-pipeline examples/tower_pair_d2_base.json --input weyl --out-program experiments/output/lift_pipeline_demo_lifted.json --out-json experiments/output/lift_pipeline_demo_report.json --out-md experiments/output/lift_pipeline_demo_report.md
```

See:

```text
docs/LIFT_PIPELINE.md
```


## Release audit

Version 0.32 adds a release/readiness audit:

```bash
qkernel release-audit --root . --out-json experiments/output/release_audit.json --out-md experiments/output/RELEASE_AUDIT.md
```

See:

```text
docs/RELEASE_AUDIT.md
```


## GitHub alpha readiness

Version 0.33 adds public-repo scaffolding and a GitHub readiness check:

```bash
qkernel github-ready --root . --out-json experiments/output/github_ready.json --out-md experiments/output/GITHUB_READY.md
```

See:

```text
ALPHA_README.md
CONTRIBUTING.md
SECURITY.md
docs/ALPHA_QUICKSTART.md
docs/PUBLIC_REPO_STATUS.md
```
