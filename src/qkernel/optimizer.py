from __future__ import annotations

from .analyzer import q_of_cycle
from .canonicalize import CanonicalizeMode, canonicalize_program
from .decompose import Component, decompose_components
from .ir import KernelResult, WeylProgram
from .solvers import SolverName, find_min_odd_cycle
from .validate import validate_program


def compress_min_odd_q(
    program: WeylProgram,
    *,
    solver: SolverName = "auto",
    max_cycle_dim: int = 24,
    max_weight: int = 8,
    max_checks: int = 2_000_000,
    max_nodes: int = 1_000_000,
    decompose: bool = True,
    canonicalize: CanonicalizeMode = "none",
) -> KernelResult:
    """Find the minimum-size odd-Q contextual kernel."""
    validate_program(program)

    if canonicalize != "none":
        program = canonicalize_program(program, mode=canonicalize)
        validate_program(program)

    if program.d % 2 != 0:
        return _empty(program)

    if decompose:
        components = decompose_components(program)
        if len(components) > 1:
            return _compress_decomposed(
                program,
                components,
                solver=solver,
                max_cycle_dim=max_cycle_dim,
                max_weight=max_weight,
                max_checks=max_checks,
                max_nodes=max_nodes,
            )

    return _compress_single(
        program,
        original_program=program,
        context_index_map=list(range(len(program.contexts))),
        solver=solver,
        max_cycle_dim=max_cycle_dim,
        max_weight=max_weight,
        max_checks=max_checks,
        max_nodes=max_nodes,
    )


def _compress_decomposed(
    original: WeylProgram,
    components: list[Component],
    *,
    solver: SolverName,
    max_cycle_dim: int,
    max_weight: int,
    max_checks: int,
    max_nodes: int,
) -> KernelResult:
    best: KernelResult | None = None

    for component in components:
        candidate = _compress_single(
            component.program,
            original_program=original,
            context_index_map=component.context_indices,
            solver=solver,
            max_cycle_dim=max_cycle_dim,
            max_weight=max_weight,
            max_checks=max_checks,
            max_nodes=max_nodes,
        )

        if not candidate.contextual:
            continue

        if best is None:
            best = candidate
            continue

        candidate_score = (candidate.compressed_contexts, candidate.compressed_observables)
        best_score = (best.compressed_contexts, best.compressed_observables)

        if candidate_score < best_score:
            best = candidate

    if best is None:
        return _empty(original)

    return best


def _compress_single(
    program: WeylProgram,
    *,
    original_program: WeylProgram,
    context_index_map: list[int],
    solver: SolverName,
    max_cycle_dim: int,
    max_weight: int,
    max_checks: int,
    max_nodes: int,
) -> KernelResult:
    lam = find_min_odd_cycle(
        program,
        solver=solver,
        max_cycle_dim=max_cycle_dim,
        max_weight=max_weight,
        max_checks=max_checks,
        max_nodes=max_nodes,
    )

    if lam is None:
        return _empty(original_program)

    q = q_of_cycle(program, lam)
    if q != 1:
        raise AssertionError("solver returned a cycle whose Q value is not odd.")

    local_contexts = [i for i, bit in enumerate(lam) if bit]
    selected_contexts = [context_index_map[i] for i in local_contexts]
    selected_observables = sorted(
        {name for idx in selected_contexts for name in original_program.contexts[idx]}
    )

    return KernelResult(
        contextual=True,
        original_contexts=len(original_program.contexts),
        original_observables=len(original_program.observables),
        compressed_contexts=len(selected_contexts),
        compressed_observables=len(selected_observables),
        selected_contexts=selected_contexts,
        selected_observables=selected_observables,
        q_value=q,
        compression_ratio_contexts=len(original_program.contexts) / len(selected_contexts),
        compression_ratio_observables=len(original_program.observables) / len(selected_observables),
    )


def _empty(program: WeylProgram) -> KernelResult:
    return KernelResult(
        contextual=False,
        original_contexts=len(program.contexts),
        original_observables=len(program.observables),
        compressed_contexts=0,
        compressed_observables=0,
        selected_contexts=[],
        selected_observables=[],
        q_value=None,
        compression_ratio_contexts=0.0,
        compression_ratio_observables=0.0,
    )
