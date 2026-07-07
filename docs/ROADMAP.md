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
- [x] resource-oracle feature bridge (`resource-features`): exports qkernel kernel
      features next to externally supplied T-count, T-depth, magic-injection, or
      stabilizer-rank metrics without claiming qkernel predicts them.
- [x] staged PRD for compiler, magic-state, optimizer, circuit-builder, and
      factory-candidate development (`docs/PRD_COMPILER_MAGIC_FACTORY_BRIDGE.md`).
- [x] compiler-candidate corpus bridge (`compiler-candidates`): before/after
      diagnostic reports with semantic-proof and resource-metric status tracked.
- [x] factory-candidate corpus bridge (`factory-candidates`): MagicScout motifs
      with template compatibility, missing factory metrics, and non-claims tracked.
- [x] circuit-builder readiness manifests (`circuit-manifest`): reports current
      exporter support and explicit blockers for unsupported d,m/protocol cases.
- [x] correlation-study harness (`correlation-study`): joins qkernel features
      with external resource metrics and negative controls for correlation-only reports.
- [x] application impact register (`impact-register`): tracks application
      surfaces, missing evidence, next actions, and claim boundaries.
- [x] application workbench PRD (`application-prd`): scopes the next application
      as a CLI-first evidence workbench before UI, optimizer, or simulator expansion.
- [x] application evidence packets (`application-packet`): compose compiler,
      factory, correlation, resource-feature, and circuit-manifest artifacts into
      claim-gated Markdown/JSON review packets with optional CI failure on blocked
      gates.
- [ ] validated correlation study over an external resource-oracle corpus.

## Status

Phases 1-3 complete; Phase 4 applications delivered through a claim-gated
application workbench. The resource-oracle bridge and packet workflow are
present; validated resource-overhead correlation remains open.
Solver stack: span / bounded-weight / branch-bound / heuristic / CP-SAT (see docs/SOLVERS.md).
