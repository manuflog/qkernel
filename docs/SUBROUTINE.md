# Contextuality as a subroutine

## Design stance: subroutine, not solver
Practical quantum utility in optimization is increasingly expected to come from
quantum **subroutines** that accelerate a specific bottleneck inside an otherwise
classical pipeline (the canonical example: quantum amplitude estimation giving a
quadratic speedup on the Monte-Carlo *estimation* step), rather than from monolithic
quantum **solvers** that replace a classical optimizer wholesale. Classical solvers
are extremely good; provable speedups live on well-defined primitives; and a small,
composable subroutine integrates with existing infrastructure and is individually
benchmarkable.

qkernel adopts the same stance for contextuality analysis. It is not sold as a
monolithic "contextuality solver"; it exposes a **subroutine** that a larger quantum-
compilation, resource-estimation, or experiment-design loop calls. (qkernel itself is
classical -- no quantum speedup is claimed; the point is composability.)

## The entry point
```python
from qkernel.subroutine import analyze_contextuality

r = analyze_contextuality(program,
                          verify=True,              # re-check the kernel independently
                          enumerate_all_kernels=True,  # count distinct minimal tests
                          certify_minimal=True)     # CP-SAT optimality proof (OR-Tools)
```
`ContextualitySubroutineResult` fields: `contextual`, `min_kernel_contexts` (the cheapest
contextuality test), `kernel_weight`, `verified`, `certified_minimal`, `n_minimal_kernels`,
`obstruction_value` (resource value `d/2` for even `d`), `modulus`, `reason`.

## Why one call
The subroutine composes the analyzer, the min-odd-cycle solver, the verifier, and
(optionally) the all-kernels enumerator and the CP-SAT certifier behind a single stable
contract, so a pipeline gets the decision, the cheapest certificate, an independent
verification, and a resource quantification in one place -- the natural unit at which a
host workflow measures the value of the contextuality step.

## Where it plugs in
- **Experiment design:** the minimal kernel is the cheapest state-independent
  contextuality test on a device's measurable operators; `n_minimal_kernels` gives the
  alternatives to pick from by connectivity / gate cost.
- **Compiler / verification pass:** flag whether a measurement schedule contains an
  unavoidable contextual obstruction and localize the minimal core.
- **Resource estimation:** `obstruction_value` quantifies the resource; combined with the
  activation subroutine (`qkernel.embedding`) this locates or generates contextuality as a
  resource in a magic-state / MBQC pipeline.

## Worked example: experiment design (`minimal-test`)
The first pipeline-facing layer over the subroutine. Given the Pauli operators a device
can measure, `qkernel.experiment_design.minimal_contextuality_tests` returns the cheapest
state-independent contextuality test(s) -- concrete commuting measurement groups -- ranked
by fewest settings, then fewest distinct observables:

```
qkernel minimal-test XI IX XX IY YI YY XY YX ZZ
  -> 1 cheapest test(s); each 6 settings, 9 observables.
     test 1 (value d/2 = 1, verified=True):
       measure together: [XI, IX, XX]
       ... (the Peres-Mermin square)
```

A device that can measure all 15 two-qubit Paulis yields 10 distinct cheapest tests (the
Mermin squares of the doily); a single commuting row yields none (non-contextual).
