from __future__ import annotations

from dataclasses import dataclass
from collections import deque

from .ir import WeylProgram


@dataclass(frozen=True)
class Component:
    """Connected component of the context-observable bipartite graph."""

    context_indices: list[int]
    observable_names: list[str]
    program: WeylProgram


def decompose_components(program: WeylProgram) -> list[Component]:
    """Split a WeylProgram by its context-observable bipartite graph.

    Nodes are:
      - context nodes C_i;
      - observable nodes O_name.

    Edges connect C_i to every observable appearing in that context.

    If two blocks share no observables, no odd-Q certificate needs to be
    searched across them jointly. Any minimum odd certificate lies entirely
    inside one connected component.
    """
    n_contexts = len(program.contexts)

    context_to_observables: dict[int, set[str]] = {
        i: set(context) for i, context in enumerate(program.contexts)
    }

    observable_to_contexts: dict[str, set[int]] = {}
    for idx, obs_names in context_to_observables.items():
        for name in obs_names:
            observable_to_contexts.setdefault(name, set()).add(idx)

    unvisited_contexts = set(range(n_contexts))
    components: list[Component] = []

    while unvisited_contexts:
        start = min(unvisited_contexts)

        queue: deque[tuple[str, int | str]] = deque([("context", start)])
        seen_contexts: set[int] = set()
        seen_observables: set[str] = set()

        while queue:
            kind, node = queue.popleft()

            if kind == "context":
                idx = int(node)
                if idx in seen_contexts:
                    continue
                seen_contexts.add(idx)

                for obs_name in context_to_observables[idx]:
                    if obs_name not in seen_observables:
                        queue.append(("observable", obs_name))

            else:
                obs_name = str(node)
                if obs_name in seen_observables:
                    continue
                seen_observables.add(obs_name)

                for idx in observable_to_contexts.get(obs_name, set()):
                    if idx not in seen_contexts:
                        queue.append(("context", idx))

        context_indices = sorted(seen_contexts)
        observable_names = sorted(seen_observables)

        unvisited_contexts.difference_update(context_indices)

        sub_observables = {
            name: program.observables[name]
            for name in observable_names
        }
        sub_metadata = {
            name: program.observable_metadata[name]
            for name in observable_names
            if name in program.observable_metadata
        }
        sub_contexts = [
            list(program.contexts[idx])
            for idx in context_indices
        ]
        sub_phases = (
            [program.context_phases[idx] for idx in context_indices]
            if program.context_phases is not None
            else None
        )
        subprogram = WeylProgram(
            d=program.d,
            m=program.m,
            observables=sub_observables,
            contexts=sub_contexts,
            observable_metadata=sub_metadata,
            context_phases=sub_phases,
        )

        components.append(
            Component(
                context_indices=context_indices,
                observable_names=observable_names,
                program=subprogram,
            )
        )

    return components


def component_summary(program: WeylProgram) -> list[dict[str, int | list[int]]]:
    """Small serializable summary for diagnostics and CLI output."""
    out: list[dict[str, int | list[int]]] = []
    for comp in decompose_components(program):
        out.append(
            {
                "contexts": len(comp.context_indices),
                "observables": len(comp.observable_names),
                "context_indices": comp.context_indices,
            }
        )
    return out
