# Claude Handoff — Q-Kernel Session Summary

## One-line description

Q-Kernel is an exact contextuality kernel extractor for Weyl/Pauli measurement programs. It converts the odd-Q contextuality criterion into software: detect and compress a large context family into a minimal verifiable odd-Q kernel.

## Mathematical core

Given a Weyl/Pauli context family:

```text
A = context-observable incidence matrix over GF(2)
b = commutator-carry vector
```

A contextuality certificate is a binary context-selection vector `lambda` satisfying:

```text
A^T lambda = 0 mod 2
b^T lambda = 1 mod 2
```

For even local dimension `d`, the uploaded Q-criterion note identifies this with odd `Q(lambda)`.

The software is intentionally conservative: it does not claim T-count, T-depth, stabilizer-rank, magic-injection, or distillation lower bounds.

## Why the package exists

The theorem gives an exact finite criterion. Q-Kernel turns it into:

```text
large Weyl/Pauli measurement family
        -> minimum odd-Q contextual kernel
        -> standalone certificate
        -> independent verifier
```

This is a foundations-to-software bridge, not yet a resource-estimation theorem.

## Major modules built in this session

### Inputs / IR

- `src/qkernel/ir.py`
  - `WeylProgram`
  - `ObservableMetadata`
  - `identity_scope="observable" | "event"`

- `src/qkernel/io.py`
  - Weyl JSON read/write with metadata.

- `src/qkernel/pauli.py`
  - Pauli-string frontend.

- `src/qkernel/pauli_schedule.py`
  - grouped schedule frontend.

- `src/qkernel/adapters/pauli_table.py`
  - dependency-free row-oriented CSV/JSON table adapter.
  - intended bridge format for future Qiskit/Stim importers.

### Core math

- `src/qkernel/symplectic.py`
  - integer symplectic arithmetic.
  - crucial rule: do not reduce pairing modulo `d` before dividing by `d`.

- `src/qkernel/carry.py`
  - context carry bits.

- `src/qkernel/incidence.py`
  - incidence matrices and left-kernel cycles.

- `src/qkernel/analyzer.py`
  - odd-Q contextuality detection.

- `src/qkernel/optimizer.py`
  - minimum odd-Q kernel extraction.

### Scaling / preprocessing

- `src/qkernel/decompose.py`
  - context-observable connected component decomposition.
  - solves disconnected blocks independently.

- `src/qkernel/canonicalize.py`
  - explicit canonicalization:
    - `none`
    - `by-vector`
    - `by-vector-force`
  - respects event-vs-observable identity semantics.

### Solvers

- `src/qkernel/solvers.py`
  - `span`
  - `bounded-weight`
  - `branch-bound`

`branch-bound` encodes each context as:

```text
state_i = incidence_row_i || carry_bit_i
```

and searches for XOR target:

```text
0...01
```

with suffix-span feasibility pruning.

### External solver bridge

- `src/qkernel/sat_export.py`
  - DIMACS CNF export for fixed-k feasibility.

- `src/qkernel/maxsat_export.py`
  - WCNF MaxSAT export for direct minimization.

- `src/qkernel/solver_output.py`
  - imports SAT/MaxSAT assignments back into Q-Kernel.
  - extracts lambda variables from model comments.
  - independently verifies imported lambda.
  - can write a Q-Kernel certificate.

### Certificates

- `src/qkernel/hashing.py`
  - canonical program hash.

- `src/qkernel/metadata.py`
  - software version, criterion, coordinate convention, integer-carry rule.

- `src/qkernel/certificate.py`
  - stable certificate schema:
    - program SHA-256
    - lambda
    - selected contexts
    - b-vector
    - q-value
    - criterion/convention metadata
    - independent verification result.

### Experiments

- `experiments/generate_noisy_pm.py`
- `experiments/benchmark_decomposition.py`
- `experiments/compare_solvers.py`

Synthetic only. Purpose is to test decomposition and solver behavior, not resource claims.

### Docs

Important docs:

- `docs/CLAUDE_HANDOFF.md`
- `docs/GEMINI_SUMMARY.md`
- `docs/GEMINI_ASSESSMENT.md`
- `docs/CHALLENGES.md`
- `docs/SOLVERS.md`
- `docs/SAT_EXPORT.md`
- `docs/MAXSAT_EXPORT.md`
- `docs/SOLVER_OUTPUT_IMPORT.md`
- `docs/CERTIFICATES.md`
- `docs/PAULI_TABLE_ADAPTER.md`
- `docs/IR_METADATA.md`
- `docs/CANONICALIZATION.md`
- `docs/DECOMPOSITION.md`

## Current test state

As of v0.15:

```text
53 passing tests
```

The exact number may change if new tests are added, but the local suite passes.

## Current CLI capabilities

Analyze:

```bash
qkernel analyze examples/peres_mermin.json
qkernel analyze-pauli examples/peres_mermin_pauli.json
qkernel analyze-schedule examples/peres_mermin_schedule.json
qkernel analyze-table examples/peres_mermin_table.json
```

Compress:

```bash
qkernel compress-pauli examples/peres_mermin_pauli.json --solver branch-bound --json
```

Inspect components:

```bash
qkernel components examples/peres_mermin_with_noise_schedule.json --input schedule
```

Canonicalization report:

```bash
qkernel canonicalize-report examples/duplicate_vectors_events_weyl.json
```

Certificates:

```bash
qkernel certify examples/peres_mermin_pauli.json --input pauli --out pm.cert.json
qkernel verify-certificate examples/peres_mermin_pauli.json --input pauli --certificate pm.cert.json
qkernel inspect-certificate pm.cert.json
```

SAT / MaxSAT export:

```bash
qkernel export-sat examples/peres_mermin_pauli.json --input pauli --max-weight 6 --out pm.cnf
qkernel export-maxsat examples/peres_mermin_pauli.json --input pauli --out pm.wcnf
```

Import external solver output:

```bash
qkernel import-solver-output examples/peres_mermin_pauli.json \
  --input pauli \
  --model pm.wcnf \
  --solution solver.out \
  --out external.cert.json
```

## Important conceptual choices

### 1. Do not overclaim

Safe claim:

```text
Exact contextuality kernel extractor for Weyl/Pauli measurement families.
```

Unsafe claim:

```text
Magic-state optimizer / T-count lower-bound tool.
```

The latter requires a bridge theorem or strong empirical evidence.

### 2. Identity semantics matter

Repeated equal Pauli/Weyl labels may mean:

```text
same observable
```

or:

```text
distinct measurement events
```

That is why the IR has `identity_scope`.

Frontends must not guess silently.

### 3. External solvers are untrusted

SAT/MaxSAT/MILP solvers propose lambda vectors. Q-Kernel verifies the actual math independently.

### 4. Q-Kernel should stay dependency-light

The core should remain pure Python. External solvers and quantum SDKs should be optional bridges.

## Gemini assessment triage

Gemini was useful on:

- SAT/MaxSAT/MILP direction;
- Stim/Qiskit adapter direction;
- empirical correlation direction.

Gemini overstated:

- passive dimension embedding as "free";
- magic-state optimization implications.

Use Gemini-style ideas as roadmap prompts, not as claim support.

## Suggested next development paths

### Path A — Real external solver bridge

Add optional PySAT support:

```text
[project.optional-dependencies]
sat = ["python-sat"]
```

Functions:

```python
solve_with_pysat(program, max_weight=None)
solve_with_rc2(program)
```

But keep it optional.

### Path B — Stim-lite adapter

Before a real Stim dependency, define a simple detector/measurement-event table:

```text
measurement_id, pauli, tick, identity_scope
```

Then later parse actual `.stim` files.

### Path C — Qiskit bridge

Do not hard-depend on Qiskit. Add optional adapter that accepts `SparsePauliOp`, `PauliList`, or pre-exported tables only if Qiskit is installed.

### Path D — Paper polish

The arXiv note should now be reorganized into:

1. mathematical criterion;
2. software architecture;
3. algorithms and solvers;
4. certificates;
5. benchmarks;
6. limitations;
7. roadmap.

### Path E — Real benchmarks

Use known Clifford+T or stabilizer measurement examples, but frame results as empirical only.

Metrics to compare:

- kernel context count;
- kernel observable count;
- solver runtime;
- decomposition ratio;
- known T-count or injection count, if available.

Do not call it a theorem yet.


## v0.16 closed Q form and tower scope update

Added:

```text
src/qkernel/closed_form.py
docs/CLOSED_Q_FORM.md
docs/TOWER_SCOPE.md
src/qkernel/experimental/tower.py
```

The analyzer now explicitly cross-checks:

```text
lambda · b mod 2
```

against:

```text
(sum_{a<b}<v_a,v_b> / d) mod 2
```

on cycle-space elements.

Tower/doubling features remain experimental only. Repeat-observable corrections are open, so do not certify embedding/tower resource claims.


## v0.17 paper restructuring

The arXiv-style note was rewritten into a cleaner software/research paper structure:

```text
paper/qkernel_note.tex
paper/EDITOR_NOTES.md
tests/test_paper_structure.py
```

The paper now explicitly separates:
- proved odd-Q kernel criterion;
- implementation architecture;
- solvers and external solver workflows;
- certificate trust model;
- experimental tower/doubling scope;
- limitations and safe claims.


## v0.18 benchmark table generation

Added:

```text
experiments/render_paper_tables.py
docs/PAPER_BENCHMARK_TABLES.md
paper/generated_benchmark_tables.tex
paper/generated_benchmark_tables.md
```

The paper now includes generated synthetic benchmark tables with `\input{generated_benchmark_tables}`. These are diagnostics only, not resource/advantage claims.


## v0.19 proposition map

Added explicit proposition labels in the paper and a code-to-proposition map:

```text
docs/PROPOSITION_MAP.md
```

The main certified claims are now traceable to implementation modules and tests:
- integer carry rule;
- odd-Q criterion;
- closed Q form;
- component decomposition;
- certificate verification soundness.


## v0.20 novelty hygiene

Incorporated Claude's citation warning.

Added:

```text
docs/NOVELTY_HYGIENE.md
```

Updated:

```text
paper/references.bib
paper/qkernel_note.tex
docs/CHALLENGES.md
docs/PROPOSITION_MAP.md
```

The paper now explicitly cites Saniga/Holweck/de Boutray/Muller finite-geometric work for GF(2) linear systems and binary symplectic polar-space contextuality. Q-Kernel does not claim novelty for that framing. The safer contribution statement is the odd-Q carry/kernel/certificate implementation, closed symplectic Q form, qudit-aware scope, identity-aware IR, and solver/certificate architecture.


## v0.21 release manifest and note discoverability

Added:

```text
MANIFEST_QKERNEL.md
QKERNEL_NOTE_LOCATION.md
paper/NOTE_LOCATION.md
paper/qkernel_note.pdf
```

The note is now available both as LaTeX and compiled PDF:

```text
paper/qkernel_note.tex
paper/qkernel_note.pdf
```


## v0.22 Stim-lite adapter

Added dependency-free Stim-lite MPP adapter:

```text
src/qkernel/adapters/stim_lite.py
docs/STIM_LITE_ADAPTER.md
examples/peres_mermin_mpp.stim
tests/test_stim_lite_adapter.py
```

CLI:

```bash
qkernel inspect-stim-lite examples/peres_mermin_mpp.stim
qkernel analyze-stim-lite examples/peres_mermin_mpp.stim
qkernel compress-stim-lite examples/peres_mermin_mpp.stim --json
qkernel certify examples/peres_mermin_mpp.stim --input stim-lite --out pm_stim.cert.json
```

Scope: explicit MPP-family adapter only, not a full Stim circuit semantics engine.


## v0.23 optional PySAT backend

Added:

```text
src/qkernel/backends/pysat_backend.py
docs/PYSAT_BACKEND.md
tests/test_pysat_backend.py
```

Optional dependency:

```toml
[project.optional-dependencies]
sat = ["python-sat[pblib,aiger]>=1.8.dev0"]
```

CLI:

```bash
qkernel solve-pysat examples/peres_mermin_pauli.json --input pauli --max-weight 6
qkernel solve-rc2 examples/peres_mermin_pauli.json --input pauli
```

If PySAT is not installed, these commands fail cleanly with an install hint. Solvers remain untrusted; Q-Kernel verifies returned lambda vectors independently.


## v0.24 compiler diagnostics and package polish

Added:

```text
src/qkernel/compiler.py
docs/COMPILER_OPTIMIZER_PATH.md
tests/test_compiler_diagnostics.py
tests/test_package_metadata.py
LICENSE
CITATION.cff
MANIFEST.in
CHANGELOG.md
src/qkernel/py.typed
```

New CLI:

```bash
qkernel compiler-report examples/peres_mermin_pauli.json --input pauli
qkernel compare-pass before.json after.json --input pauli
```

Important boundary: this is a compiler diagnostic contract, not yet a resource optimizer.


## v0.25 Qiskit-lite adapter and self-test

Added:

```text
src/qkernel/adapters/qiskit_lite.py
src/qkernel/selftest.py
docs/QISKIT_LITE_ADAPTER.md
docs/INSTALL_SMOKE.md
examples/peres_mermin_qiskit_lite.json
tests/test_qiskit_lite_adapter.py
tests/test_selftest_cli.py
```

CLI:

```bash
qkernel self-test
qkernel inspect-qiskit-lite examples/peres_mermin_qiskit_lite.json
qkernel analyze-qiskit-lite examples/peres_mermin_qiskit_lite.json
qkernel compress-qiskit-lite examples/peres_mermin_qiskit_lite.json --json
```

The adapter defaults to Qiskit label order and reverses strings into Q-Kernel convention.


## v0.26 compiler pass playground

Added concrete before/after diagnostic examples:

```text
examples/compiler_before_qiskit_lite.json
examples/compiler_after_qiskit_lite.json
experiments/compiler_pass_playground.py
docs/COMPILER_PASS_PLAYGROUND.md
tests/test_compiler_pass_playground.py
```

The example shows a Qiskit-lite schedule where after removes disconnected nonkernel checks while preserving the detected odd-Q kernel. The verdict explicitly still requires a semantic-equivalence proof.


## v0.27 rewrite policy registry

Added:

```text
src/qkernel/rewrite_policy.py
docs/REWRITE_POLICY.md
tests/test_rewrite_policy.py
```

CLI:

```bash
qkernel rewrite-policies
qkernel assess-rewrite safe_diagnostic_prune
qkernel assess-rewrite forbidden_resource_claim
```

Compiler-pass comparisons now include policy fields:
- rewrite_policy_id
- rewrite_policy_status
- allowed_to_report
- allowed_to_apply

The default compiler-pass playground is reportable but not directly applicable without external semantic-equivalence proof.


## v0.28 Z_d valuation verification

Incorporated Claude correctness flag.

Added:

```text
src/qkernel/valuation.py
docs/ZD_VALUATION_VERIFICATION.md
tests/test_zd_valuation.py
```

Changes:
- `WeylProgram` now supports optional `context_phases`.
- Weyl JSON load/dump/hash/decompose/canonicalize preserve context phases.
- `verify_kernel` now requires both odd-Q and genuine `Z_d` valuation-system unsolvability on the selected kernel.
- Certificates include context phases and Z_d valuation verification result.
- New CLI: `qkernel zd-valuation`.

This closes the parity-only compression trap operationally: a compressed family that is odd-Q but admits a Z_d valuation is rejected by verification.


## v0.29 closed tower law

Incorporated Claude's tower formula.

Added:

```text
src/qkernel/tower.py
docs/TOWER_LAW.md
examples/tower_pair_d4_nongenerative.json
tests/test_tower_law.py
```

Replaced old experimental tower scope implementation with a compatibility shim.

Formula:

```text
M_ab = <u_a,x_b> + <x_a,u_b>
G = floor(sum M_ab / 2) XOR floor(K/2) mod 2
K = number of odd M_ab
non-generative iff G = 0
```

Direct pairwise sum is used. No intrinsic reconstruction. Repeat cycles are supported.


## v0.30 fiber-lift constructor

Added:

```text
src/qkernel/fiber_lift.py
docs/FIBER_LIFT.md
examples/tower_pair_d2_base.json
tests/test_fiber_lift.py
```

New CLI:

```bash
qkernel fiber-lift examples/tower_pair_d2_base.json --input weyl --out experiments/output/tower_pair_d4_lifted.json
```

Supports even base d. It solves linear GF(2) constraints for lift bits preserving closure and commutation modulo 2d, validates the lifted program, lifts phases by gamma -> 2 gamma, and runs Z_d valuation check.


## v0.31 lift pipeline

Added:

```text
src/qkernel/lift_pipeline.py
docs/LIFT_PIPELINE.md
experiments/lift_pipeline_demo.py
tests/test_lift_pipeline.py
```

New CLI:

```bash
qkernel lift-pipeline examples/tower_pair_d2_base.json --input weyl --out-program experiments/output/lift_pipeline_demo_lifted.json --out-json experiments/output/lift_pipeline_demo_report.json --out-md experiments/output/lift_pipeline_demo_report.md
```

Pipeline: fiber-lift -> Z_d valuation -> tower-law report. It emits safe/unsafe claim boundaries and remains a reproducibility/certification workflow, not an optimizer.


## v0.32 release audit

Added:

```text
src/qkernel/release_audit.py
docs/RELEASE_AUDIT.md
experiments/release_audit.py
tests/test_release_audit.py
```

New CLI:

```bash
qkernel release-audit --root . --out-json experiments/output/release_audit.json --out-md experiments/output/RELEASE_AUDIT.md
```

The audit checks core odd-Q + Z_d verification, policy guardrails, compiler diagnostic-only status, fiber-lift/tower pipeline, and novelty hygiene.


## v0.33 GitHub alpha readiness

Added public-repo alpha scaffolding:

```text
ALPHA_README.md
CONTRIBUTING.md
SECURITY.md
CODE_OF_CONDUCT.md
SUPPORT.md
docs/ALPHA_QUICKSTART.md
docs/PUBLIC_REPO_STATUS.md
.github/ISSUE_TEMPLATE/*
.github/PULL_REQUEST_TEMPLATE.md
.github/workflows/release-audit.yml
.github/dependabot.yml
src/qkernel/github_ready.py
tests/test_github_ready.py
```

New CLI:

```bash
qkernel github-ready --root . --out-json experiments/output/github_ready.json --out-md experiments/output/GITHUB_READY.md
```
