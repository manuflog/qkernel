# Roadmap

## Phase 1: Core library

- [x] JSON WeylProgram format.
- [x] validator.
- [x] carry engine.
- [x] incidence and cycle engine.
- [x] odd-Q analyzer.
- [x] contextuality compressor.
- [x] tests for Peres-Mermin and integer-carry bug.
- [ ] CI green on GitHub.
- [ ] package metadata cleanup.

## Phase 2: Compiler-facing adapters

- [ ] Pauli-string schedule importer.
- [ ] Qiskit Pauli observable importer.
- [ ] Stim-like measurement/check importer.
- [ ] certificate renderer for compiler logs.

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
