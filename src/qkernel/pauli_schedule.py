from __future__ import annotations

import json
from itertools import combinations
from pathlib import Path

from .ir import Context, WeylProgram
from .pauli import pauli_program, pauli_string_to_vector
from .symplectic import add_mod, commute


def _normalize_layer(layer: list[str]) -> list[str]:
    if not layer:
        raise ValueError("schedule layer cannot be empty.")
    return [p.upper() for p in layer]


def _is_commuting_context(context: list[str]) -> bool:
    vectors = {p: pauli_string_to_vector(p) for p in context}
    for a, b in combinations(context, 2):
        if not commute(vectors[a], vectors[b], d=2):
            return False
    return True


def _sums_to_identity(context: list[str]) -> bool:
    vectors = [pauli_string_to_vector(p) for p in context]
    total = tuple(0 for _ in vectors[0])
    for vec in vectors:
        total = add_mod(total, vec, d=2)
    return all(x == 0 for x in total)


def extract_contexts_from_layers(
    layers: list[list[str]],
    *,
    include_full_layers: bool = True,
    include_closed_triples: bool = True,
) -> list[Context]:
    """Extract valid Pauli contexts from a grouped measurement schedule.

    A layer means "these observables are intended to be co-measured or
    considered together." This function deliberately does NOT infer contexts
    across layers. That avoids a common compiler-analysis bug: a mere list of
    available Pauli strings does not determine which compatible sets are actual
    measurement contexts.

    Extraction rules:
      1. If a whole layer is pairwise commuting and its labels sum to identity,
         keep it as a context.
      2. Optionally, also keep every closed commuting triple inside the layer.

    For qubit Paulis, label product closure is vector addition over Z_2. A
    triple [A, B, C] is scalar-product closed when labels sum to zero, i.e.
    C = A + B in Weyl-label notation.
    """
    contexts: list[Context] = []
    seen: set[tuple[str, ...]] = set()

    def add_context(ctx: list[str]) -> None:
        key = tuple(sorted(ctx))
        if key not in seen:
            seen.add(key)
            contexts.append(ctx)

    for raw_layer in layers:
        layer = _normalize_layer(raw_layer)

        lengths = {len(p) for p in layer}
        if len(lengths) != 1:
            raise ValueError(f"all Pauli strings in a layer must have equal length: {layer}")

        if include_full_layers and len(layer) >= 2:
            if _is_commuting_context(layer) and _sums_to_identity(layer):
                add_context(layer)

        if include_closed_triples and len(layer) >= 3:
            for triple in combinations(layer, 3):
                ctx = list(triple)
                if _is_commuting_context(ctx) and _sums_to_identity(ctx):
                    add_context(ctx)

    return contexts


def schedule_program(
    layers: list[list[str]],
    *,
    include_full_layers: bool = True,
    include_closed_triples: bool = True,
) -> WeylProgram:
    """Build a WeylProgram from a grouped Pauli measurement schedule."""
    contexts = extract_contexts_from_layers(
        layers,
        include_full_layers=include_full_layers,
        include_closed_triples=include_closed_triples,
    )

    if not contexts:
        raise ValueError("no valid scalar-product Pauli contexts were extracted from the schedule.")

    return pauli_program(contexts)


def load_pauli_schedule(path: str | Path) -> WeylProgram:
    """Load a grouped Pauli schedule JSON file.

    Format:

        {
          "type": "pauli_schedule",
          "layers": [
            ["ZI", "IZ", "ZZ"],
            ["IX", "XI", "XX"]
          ],
          "include_full_layers": true,
          "include_closed_triples": true
        }

    The distinction between `layers` and a raw observable set is intentional.
    Contextuality depends on actual co-measurement/compatibility contexts, not
    merely on which observables appear somewhere in a circuit.
    """
    data = json.loads(Path(path).read_text(encoding="utf-8"))

    if data.get("type") not in {None, "pauli_schedule"}:
        raise ValueError("expected JSON type 'pauli_schedule'.")

    return schedule_program(
        data["layers"],
        include_full_layers=bool(data.get("include_full_layers", True)),
        include_closed_triples=bool(data.get("include_closed_triples", True)),
    )
