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

- [x] branch-and-bound minimum odd-Q cycle solver.
- [x] MILP/CP-SAT backend (`solvers_milp.find_min_odd_cycle_cpsat`, OR-Tools; independent exact cross-check; **certifies** minimality on dense high-cycle-dim families where span is infeasible, e.g. m=3 cycle_dim 259).
- [x] sparse-cycle heuristics (`find_min_odd_cycle_heuristic`; min-weight coset-leader local search; scales to cycle-dim >5000 where exact enumeration is infeasible; analyzer/compressor auto-fall-back to it).
- [x] benchmark suite (`experiments/benchmark_suite.py`; validates correctness at scale, records ~O(n^2) exact-solver scaling).

## Phase 4: Applications

- [x] qudit d=4,6,8 examples and obstruction-spectrum machinery (H(d)={0,d/2}, 2-primary tower, Z_d valuation).
- [x] d -> 2d activation experiments (`qkernel.embedding`; reproduces the verified activation-yield curve;
      yield falls sharply with base dimension -- d=4 special).
- [x] composable contextuality subroutine (`qkernel.subroutine.analyze_contextuality`) for pipeline integration.
- [x] experiment-design application (`minimal-test`): device Paulis -> cheapest contextuality test.
- [x] activation-as-resource-generation (`activation-resource`): cheapest test activated by embedding.
- [ ] comparison with T-count, T-depth, magic injections, stabilizer rank (open; needs an external resource oracle).

## Status

Phases 1-3 complete; Phase 4 applications delivered (the resource-overhead comparison remains open).
Solver stack: span / bounded-weight / branch-bound / heuristic / CP-SAT (see docs/SOLVERS.md).
