# Roadmap

## Phase 1: Core library

- [x] JSON WeylProgram format.
- [x] validator.
- [x] carry engine.
- [x] incidence and cycle engine.
- [x] odd-Q analyzer.
- [x] contextuality compressor.
- [x] tests for Peres-Mermin and integer-carry bug.
- [x] CI green on GitHub.
- [x] package metadata cleanup.

## Phase 2: Compiler-facing adapters  — complete

_All four adapters implemented and correctness-tested: Peres–Mermin round-trips to a
contextual verdict through every adapter, a single row does not, and the observable-identity
semantics (shared `observable` vs independent `event` scope) are verified
(`tests/test_adapter_roundtrips.py`, plus the qiskit-lite suite)._


- [x] Pauli-string schedule importer.
- [x] Qiskit Pauli observable importer.
- [x] Stim-like measurement/check importer.
- [x] certificate renderer for compiler logs.

## Phase 3: Optimization algorithms

- [ ] branch-and-bound minimum odd-Q cycle solver.
- [ ] MILP/CP-SAT backend.
- [ ] sparse-cycle heuristics.
- [ ] benchmark suite.

## Phase 4: Applications

- [ ] contextuality-aware resource-estimator experiment.
- [ ] qudit d=4,6,8 examples.
- [ ] d -> 2d generativity experiments.
- [ ] comparison with T-count, T-depth, magic injections, stabilizer rank.
