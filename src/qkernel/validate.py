from __future__ import annotations

from itertools import combinations

from .ir import WeylProgram
from .symplectic import commute


def validate_program(program: WeylProgram) -> None:
    """Validate WeylProgram structure and context constraints."""
    if program.d < 2:
        raise ValueError("d must be >= 2.")
    if program.m < 1:
        raise ValueError("m must be >= 1.")
    if not program.observables:
        raise ValueError("program has no observables.")

    for name in program.observable_metadata:
        if name not in program.observables:
            raise ValueError(f"metadata references unknown observable {name!r}.")

    if program.context_phases is not None:
        if len(program.context_phases) != len(program.contexts):
            raise ValueError("context_phases length must match contexts length.")
        if any(phase < 0 or phase >= program.d for phase in program.context_phases):
            raise ValueError("context_phases entries must lie in Z_d.")

    for name, meta in program.observable_metadata.items():
        if meta.identity_scope not in {"observable", "event"}:
            raise ValueError(f"{name} has invalid identity_scope {meta.identity_scope!r}.")

    expected_len = 2 * program.m

    for name, vec in program.observables.items():
        if len(vec) != expected_len:
            raise ValueError(f"{name} has length {len(vec)}; expected {expected_len}.")
        if any(x < 0 or x >= program.d for x in vec):
            raise ValueError(f"{name} has coordinates outside Z_d.")

    for idx, context in enumerate(program.contexts):
        if len(context) < 2:
            raise ValueError(f"context {idx} has fewer than two observables.")

        for name in context:
            if name not in program.observables:
                raise ValueError(f"context {idx} references unknown observable {name!r}.")

        for a, b in combinations(context, 2):
            if not commute(program.observables[a], program.observables[b], program.d):
                raise ValueError(f"context {idx} is not commuting: {a}, {b}.")

        summed = [
            sum(program.observables[name][j] for name in context) % program.d
            for j in range(expected_len)
        ]
        if any(summed):
            raise ValueError(f"context {idx} does not sum to zero mod d: {summed}.")
