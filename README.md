# Q-Kernel

**Q-Kernel** is an experimental Python library for contextuality kernel extraction in Weyl/Pauli measurement programs.

It implements the binary-linear-algebra core behind the odd-\(Q\) criterion:

\[
F \text{ contextual}
\iff
\exists \lambda,\quad A^T\lambda=0 \pmod 2,\quad b^T\lambda=1 \pmod 2.
\]

Engineering interpretation:

> Given a large Weyl/Pauli measurement program, find the smallest closed parity cycle of contexts carrying an odd commutator-carry obstruction — the irreducible contextual kernel.

## What this is

A narrow, testable compiler-analysis backend:

- validate Weyl/Pauli context families;
- compute commutator-carry bits \(b(C)\);
- build the context-observable incidence matrix \(A\);
- find parity cycles \(A^T\lambda=0\);
- detect odd-\(Q\) contextuality;
- compress a large program to a minimal odd-\(Q\) certificate.

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
```

Expected behavior:

- `peres_mermin.json` is contextual;
- `noisy_pm.json` compresses many irrelevant contexts to the six-context Peres-Mermin kernel.

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

## Core theorem implemented

For even local dimension \(d\), contexts are finite commuting Weyl families whose labels sum to zero mod \(d\). For each context,

\[
b(C)=\sum_{i<j}\langle c_i,c_j\rangle/d \pmod 2.
\]

For a cycle \(\lambda\) in the left kernel of the incidence matrix,

\[
A^T\lambda=0,
\]

the odd-\(Q\) obstruction is detected by

\[
b^T\lambda = Q(\lambda) = 1.
\]

The key implementation rule is:

> Do **not** reduce the symplectic pairing modulo \(d\) before dividing by \(d\). The carry is an integer lift.

## Roadmap

1. Core library and CLI.
2. Certificate renderer.
3. Qiskit / Stim / Pauli-string adapters.
4. Minimum-weight odd-\(Q\) optimization beyond brute-force cycle enumeration.
5. Resource-estimator experiments comparing kernel features to T-count, T-depth, magic injections, and stabilizer rank.
6. Qudit-specific demos for even \(d=4,6,8\).


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
