from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from .ir import Context, Vector, WeylProgram


PAULI_TO_ZX = {
    "I": (0, 0),
    "X": (0, 1),
    "Y": (1, 1),
    "Z": (1, 0),
}


PERES_MERMIN_CONTEXTS: list[list[str]] = [
    ["ZI", "IZ", "ZZ"],
    ["IX", "XI", "XX"],
    ["ZX", "XZ", "YY"],
    ["ZI", "IX", "ZX"],
    ["IZ", "XI", "XZ"],
    ["ZZ", "XX", "YY"],
]


def pauli_string_to_vector(pauli: str) -> Vector:
    """Convert a qubit Pauli string to a Weyl vector over d=2.

    Coordinates are interleaved as:

        [z1, x1, z2, x2, ..., zm, xm]

    Mapping per qubit:

        I -> (0,0)
        X -> (0,1)
        Z -> (1,0)
        Y -> (1,1)

    Examples:
        "ZI" -> (1,0,0,0)
        "IX" -> (0,0,0,1)
        "YY" -> (1,1,1,1)
    """
    if not pauli:
        raise ValueError("Pauli string cannot be empty.")

    coords: list[int] = []
    for ch in pauli.upper():
        if ch not in PAULI_TO_ZX:
            raise ValueError(f"unsupported Pauli character {ch!r}; expected I, X, Y, Z.")
        coords.extend(PAULI_TO_ZX[ch])

    return tuple(coords)


def pauli_program(contexts: list[Context], *, name: str | None = None) -> WeylProgram:
    """Build a d=2 WeylProgram from human-readable Pauli contexts.

    The observable names are the Pauli strings themselves. This is the first
    practical frontend for compiler-style input, because users should not need
    to hand-write Weyl vectors.

    The returned program is still validated by qkernel.validate/analyzer.
    """
    if not contexts:
        raise ValueError("contexts cannot be empty.")

    lengths = {len(p) for context in contexts for p in context}
    if len(lengths) != 1:
        raise ValueError(f"all Pauli strings must have equal length; got {sorted(lengths)}.")

    m = next(iter(lengths))
    observables = {
        pauli.upper(): pauli_string_to_vector(pauli)
        for context in contexts
        for pauli in context
    }

    normalized_contexts = [[p.upper() for p in context] for context in contexts]

    return WeylProgram(d=2, m=m, observables=observables, contexts=normalized_contexts)


def load_pauli_program(path: str | Path) -> WeylProgram:
    """Load a Pauli-context JSON file.

    Format:

        {
          "type": "pauli_contexts",
          "contexts": [
            ["ZI", "IZ", "ZZ"],
            ...
          ]
        }
    """
    data = json.loads(Path(path).read_text(encoding="utf-8"))

    if data.get("type") not in {None, "pauli_contexts"}:
        raise ValueError("expected JSON type 'pauli_contexts'.")

    return pauli_program(data["contexts"])
