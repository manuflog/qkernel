from __future__ import annotations

from typing import Literal

from .ir import ObservableMetadata, WeylProgram


CanonicalizeMode = Literal["none", "by-vector", "by-vector-force"]


def _metadata(program: WeylProgram, name: str) -> ObservableMetadata:
    return program.observable_metadata.get(name, ObservableMetadata())


def canonicalize_program(
    program: WeylProgram,
    *,
    mode: CanonicalizeMode = "none",
) -> WeylProgram:
    """Return a canonicalized copy of a WeylProgram.

    Modes:
      - none: return the program unchanged.
      - by-vector: merge observables with identical Weyl labels only when
        their metadata identity_scope is "observable". Observables marked
        identity_scope="event" remain distinct.
      - by-vector-force: merge by Weyl vector even across event identities.

    This is intentionally explicit. In compiler/protocol analysis, two equal
    Weyl labels may still refer to operationally distinct measurement events.
    Merging them can create cycles that are algebraically valid but not present
    in the original protocol semantics.
    """
    if mode == "none":
        return program

    if mode in {"by-vector", "by-vector-force"}:
        return canonicalize_by_vector(program, force=(mode == "by-vector-force"))

    raise ValueError(f"unknown canonicalization mode {mode!r}")


def canonicalize_by_vector(program: WeylProgram, *, force: bool = False) -> WeylProgram:
    """Merge observable names with identical Weyl vectors.

    If force=False, names with identity_scope="event" are kept distinct.

    Naming rule:
      - the lexicographically first original name for each merge class becomes
        the canonical name.

    Safety rule:
      - if two observables inside the same context collapse to the same
        canonical name, raise ValueError. This avoids silently changing the
        multiplicity semantics of a context.
    """
    merge_key_to_names: dict[tuple[object, ...], list[str]] = {}

    for name, vec in program.observables.items():
        meta = _metadata(program, name)

        if force or meta.identity_scope == "observable":
            key: tuple[object, ...] = ("vector", vec)
        else:
            key = ("event", name)

        merge_key_to_names.setdefault(key, []).append(name)

    name_to_canonical: dict[str, str] = {}
    canonical_observables: dict[str, tuple[int, ...]] = {}
    canonical_metadata: dict[str, ObservableMetadata] = {}

    for key, names in merge_key_to_names.items():
        canonical_name = sorted(names)[0]
        canonical_vec = program.observables[canonical_name]
        canonical_observables[canonical_name] = canonical_vec

        # Preserve metadata of the canonical representative. If a merge occurs,
        # the result is an observable-level identity unless forced event merges
        # are explicitly requested.
        representative_meta = _metadata(program, canonical_name)
        if len(names) > 1:
            representative_meta = ObservableMetadata(
                identity_scope="observable",
                source=representative_meta.source,
                round=representative_meta.round,
                notes=representative_meta.notes,
            )
        canonical_metadata[canonical_name] = representative_meta

        for name in names:
            name_to_canonical[name] = canonical_name

    canonical_contexts: list[list[str]] = []

    for idx, context in enumerate(program.contexts):
        new_context = [name_to_canonical[name] for name in context]
        if len(set(new_context)) != len(new_context):
            raise ValueError(
                "canonicalization would merge two observables inside context "
                f"{idx}; refusing to change context multiplicity semantics."
            )
        canonical_contexts.append(new_context)

    return WeylProgram(
        d=program.d,
        m=program.m,
        observables=canonical_observables,
        contexts=canonical_contexts,
        observable_metadata=canonical_metadata,
        context_phases=program.context_phases,
    )


def canonicalization_report(program: WeylProgram) -> dict[str, object]:
    """Report duplicate Weyl labels and identity scopes without modifying the program."""
    vector_to_names: dict[tuple[int, ...], list[str]] = {}
    identity_scopes: dict[str, str] = {}

    for name, vec in program.observables.items():
        vector_to_names.setdefault(vec, []).append(name)
        identity_scopes[name] = _metadata(program, name).identity_scope

    duplicates = {
        str(vec): sorted(names)
        for vec, names in vector_to_names.items()
        if len(names) > 1
    }

    event_names = sorted(
        name
        for name in program.observables
        if _metadata(program, name).identity_scope == "event"
    )

    return {
        "observables": len(program.observables),
        "unique_vectors": len(vector_to_names),
        "duplicate_vector_classes": duplicates,
        "event_scoped_observables": event_names,
        "identity_scopes": identity_scopes,
    }
