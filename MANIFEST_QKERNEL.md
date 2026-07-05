# Q-Kernel Release Manifest

Version: `0.21.0`

## What this repository is

Q-Kernel is an exact odd-Q contextuality kernel extractor for Weyl/Pauli measurement programs.

It converts:

```text
explicit context family
        -> incidence/carry representation
        -> minimum odd-Q contextual kernel
        -> independently verifiable certificate
```

## Main paper/note files

The arXiv-style note is here:

```text
paper/qkernel_note.tex
paper/qkernel_note.pdf
```

Generated paper tables:

```text
paper/generated_benchmark_tables.tex
paper/generated_benchmark_tables.md
```

Bibliography:

```text
paper/references.bib
```

Editor notes:

```text
paper/EDITOR_NOTES.md
```

## Best files to give another AI collaborator

```text
docs/CLAUDE_HANDOFF.md
docs/GEMINI_SUMMARY.md
docs/NOVELTY_HYGIENE.md
docs/PROPOSITION_MAP.md
docs/CHALLENGES.md
paper/qkernel_note.tex
paper/qkernel_note.pdf
```

## Safe claim

```text
Exact odd-Q contextuality kernel extractor for Weyl/Pauli measurement families.
```

## Unsafe claims

Do not claim Q-Kernel is already:

```text
a magic-state optimizer
a T-count or T-depth lower-bound tool
a stabilizer-rank estimator
a hardware overhead estimator
a certified tower/doubling compression tool
proof that passive embedding is free
an additive contextuality resource gauge
```

## Current test status

At v0.21, the local suite passes with:

```text
70+ tests passing
```

The exact count may increase as tests are added.

## Core CLI examples

Analyze:

```bash
qkernel analyze-pauli examples/peres_mermin_pauli.json
```

Compress:

```bash
qkernel compress-pauli examples/peres_mermin_pauli.json --solver branch-bound --json
```

Certificate:

```bash
qkernel certify examples/peres_mermin_pauli.json --input pauli --out pm.cert.json
qkernel verify-certificate examples/peres_mermin_pauli.json --input pauli --certificate pm.cert.json
```

SAT/MaxSAT:

```bash
qkernel export-sat examples/peres_mermin_pauli.json --input pauli --max-weight 6 --out pm.cnf
qkernel export-maxsat examples/peres_mermin_pauli.json --input pauli --out pm.wcnf
```

External solver output import:

```bash
qkernel import-solver-output examples/peres_mermin_pauli.json \
  --input pauli \
  --model pm.wcnf \
  --solution solver.out \
  --out external.cert.json
```

## Certified proposition map

See:

```text
docs/PROPOSITION_MAP.md
```

The certified path maps paper propositions to code and tests.

## Experimental namespace

Tower/doubling features remain experimental only:

```text
src/qkernel/experimental/
docs/TOWER_SCOPE.md
```

Do not promote experimental outputs to certified resource claims.


## Stim-lite adapter

```bash
qkernel analyze-stim-lite examples/peres_mermin_mpp.stim
qkernel certify examples/peres_mermin_mpp.stim --input stim-lite --out pm_stim.cert.json
```


## Optional PySAT backend

```bash
pip install 'qkernel[sat]'
qkernel solve-pysat examples/peres_mermin_pauli.json --input pauli --max-weight 6
qkernel solve-rc2 examples/peres_mermin_pauli.json --input pauli
```

This is optional. Core export/import remains dependency-free.


## Compiler optimizer path

Q-Kernel is not yet a quantum compiler optimizer. It now exposes compiler-facing diagnostics:

```bash
qkernel compiler-report examples/peres_mermin_pauli.json --input pauli
qkernel compare-pass before.json after.json --input pauli
```

See `docs/COMPILER_OPTIMIZER_PATH.md`.


## Qiskit-lite adapter

```bash
qkernel analyze-qiskit-lite examples/peres_mermin_qiskit_lite.json
qkernel certify examples/peres_mermin_qiskit_lite.json --input qiskit-lite --out pm_qiskit.cert.json
```

Smoke test:

```bash
qkernel self-test
```


## Compiler pass playground

```bash
qkernel compare-pass examples/compiler_before_qiskit_lite.json examples/compiler_after_qiskit_lite.json --input qiskit-lite
```

This is a diagnostic example, not a semantic rewrite proof.


## Rewrite policy registry

```bash
qkernel rewrite-policies
qkernel assess-rewrite safe_diagnostic_prune
qkernel assess-rewrite forbidden_resource_claim
```

This guards against accidentally treating diagnostics as certified optimizations.


## Z_d valuation verification

```bash
qkernel zd-valuation examples/peres_mermin_pauli.json --input pauli
```

The verifier now rejects parity-only compressed kernels that admit a noncontextual `Z_d` valuation.


## Closed tower law

```bash
qkernel tower-scope examples/tower_pair_d4_nongenerative.json --input weyl --contexts 0,1,2,3,4,5 --base-d 2
```

Certified: closed generativity bit for valid fiber cycles.
Not certified: tower compression/resource advantage.


## Fiber-lift constructor

```bash
qkernel fiber-lift examples/tower_pair_d2_base.json --input weyl --out experiments/output/tower_pair_d4_lifted.json
```

Constructs validated even-base `d -> 2d` fiber lifts when the GF(2) constraints are solvable.


## Lift pipeline

```bash
qkernel lift-pipeline examples/tower_pair_d2_base.json --input weyl --out-json experiments/output/lift_pipeline_demo_report.json
```

Runs fiber-lift -> Z_d valuation -> tower-law report.


## Release audit

```bash
qkernel release-audit --root . --out-json experiments/output/release_audit.json --out-md experiments/output/RELEASE_AUDIT.md
```

Checks core examples, Z_d hardening, tower pipeline, rewrite-policy guardrails, and novelty hygiene.


## GitHub alpha readiness

```bash
qkernel github-ready --root . --out-json experiments/output/github_ready.json --out-md experiments/output/GITHUB_READY.md
```

Includes issue templates, PR template, CONTRIBUTING, SECURITY, alpha quickstart, and public-repo status docs.
