from __future__ import annotations

import hashlib
import json

from .ir import ObservableMetadata, WeylProgram


def _metadata_to_dict(meta: ObservableMetadata) -> dict[str, object]:
    out: dict[str, object] = {
        "identity_scope": meta.identity_scope,
    }
    if meta.source is not None:
        out["source"] = meta.source
    if meta.round is not None:
        out["round"] = meta.round
    if meta.notes is not None:
        out["notes"] = meta.notes
    return out


def canonical_program_dict(program: WeylProgram) -> dict[str, object]:
    """Return a stable JSON-serializable representation of a WeylProgram.

    This intentionally sorts observables and metadata keys so the digest is
    independent of Python dict insertion order.
    """
    return {
        "d": program.d,
        "m": program.m,
        "observables": {
            name: list(program.observables[name])
            for name in sorted(program.observables)
        },
        "observable_metadata": {
            name: _metadata_to_dict(program.observable_metadata[name])
            for name in sorted(program.observable_metadata)
        },
        "contexts": [
            list(context)
            for context in program.contexts
        ],
        "context_phases": list(program.context_phases) if program.context_phases is not None else None,
    }


def canonical_program_json(program: WeylProgram) -> str:
    return json.dumps(
        canonical_program_dict(program),
        sort_keys=True,
        separators=(",", ":"),
    )


def program_sha256(program: WeylProgram) -> str:
    payload = canonical_program_json(program).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()
