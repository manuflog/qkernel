# Compiler Pass Playground

Q-Kernel v0.26 adds a concrete before/after compiler diagnostic example.

The example is deliberately conservative:

```text
before = Peres-Mermin odd-Q core + disconnected noncontextual checks
after  = Peres-Mermin odd-Q core only
```

Files:

```text
examples/compiler_before_qiskit_lite.json
examples/compiler_after_qiskit_lite.json
experiments/compiler_pass_playground.py
```

Run:

```bash
qkernel compare-pass \
  examples/compiler_before_qiskit_lite.json \
  examples/compiler_after_qiskit_lite.json \
  --input qiskit-lite
```

or generate the report files:

```bash
PYTHONPATH=src python experiments/compiler_pass_playground.py
```

Outputs:

```text
experiments/output/compiler_pass_playground.json
experiments/output/compiler_pass_playground.md
```

## Interpretation

The after-program removes nonkernel contexts and observables while preserving the
detected odd-Q kernel. This is a useful compiler diagnostic.

It is not a semantic circuit proof. A real compiler pass must separately prove
that dropping or rewriting those measurements is legal in the surrounding
program.
