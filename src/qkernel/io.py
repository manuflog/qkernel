from __future__ import annotations

import json
from pathlib import Path

from .ir import ObservableMetadata, WeylProgram


def _metadata_from_json(data: dict) -> dict[str, ObservableMetadata]:
    raw = data.get("observable_metadata", {})
    metadata: dict[str, ObservableMetadata] = {}

    for name, item in raw.items():
        metadata[name] = ObservableMetadata(
            identity_scope=item.get("identity_scope", "observable"),
            source=item.get("source"),
            round=item.get("round"),
            notes=item.get("notes"),
        )

    return metadata


def load_program(path: str | Path) -> WeylProgram:
    data = json.loads(Path(path).read_text(encoding="utf-8"))

    d = int(data["d"])
    m = int(data["m"])
    observables = {name: tuple(int(x) for x in vec) for name, vec in data["observables"].items()}
    contexts = [list(context) for context in data["contexts"]]
    metadata = _metadata_from_json(data)
    context_phases = data.get("context_phases")
    context_phases = [int(x) for x in context_phases] if context_phases is not None else None

    return WeylProgram(
        d=d,
        m=m,
        observables=observables,
        contexts=contexts,
        observable_metadata=metadata,
        context_phases=context_phases,
    )


def dump_program(program: WeylProgram, path: str | Path) -> None:
    data = {
        "d": program.d,
        "m": program.m,
        "observables": {name: list(vec) for name, vec in program.observables.items()},
        "contexts": program.contexts,
    }

    if program.context_phases is not None:
        data["context_phases"] = list(program.context_phases)

    if program.observable_metadata:
        data["observable_metadata"] = {
            name: {
                "identity_scope": meta.identity_scope,
                **({"source": meta.source} if meta.source is not None else {}),
                **({"round": meta.round} if meta.round is not None else {}),
                **({"notes": meta.notes} if meta.notes is not None else {}),
            }
            for name, meta in program.observable_metadata.items()
        }

    Path(path).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
