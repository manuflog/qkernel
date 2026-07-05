from __future__ import annotations

import csv
import json
from collections import OrderedDict
from pathlib import Path
from typing import Any, Iterable

from qkernel.ir import ObservableMetadata, WeylProgram
from qkernel.pauli import pauli_string_to_vector


def _read_rows(path: str | Path) -> list[dict[str, Any]]:
    path = Path(path)

    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("type") not in {None, "pauli_table"}:
            raise ValueError("expected JSON type 'pauli_table'.")
        rows = data.get("rows")
        if not isinstance(rows, list):
            raise ValueError("pauli_table JSON requires a list field 'rows'.")
        return [dict(row) for row in rows]

    if path.suffix.lower() == ".csv":
        with path.open(newline="", encoding="utf-8") as f:
            return [dict(row) for row in csv.DictReader(f)]

    raise ValueError(f"unsupported Pauli table file type: {path.suffix!r}")


def _context_key(row: dict[str, Any]) -> str:
    for key in ("context_id", "layer_id", "context", "layer"):
        value = row.get(key)
        if value not in {None, ""}:
            return str(value)
    raise ValueError("each Pauli table row must include context_id or layer_id.")


def _identity_scope(row: dict[str, Any], default_identity_scope: str) -> str:
    value = row.get("identity_scope", default_identity_scope)
    if value in {None, ""}:
        value = default_identity_scope
    value = str(value)
    if value not in {"observable", "event"}:
        raise ValueError(f"invalid identity_scope {value!r}; expected observable or event.")
    return value


def _observable_name(
    row: dict[str, Any],
    *,
    pauli: str,
    context_id: str,
    row_index: int,
    identity_scope: str,
) -> str:
    name = row.get("name") or row.get("observable") or row.get("observable_id")
    if name not in {None, ""}:
        return str(name)

    if identity_scope == "observable":
        return pauli

    return f"{pauli}@{context_id}:{row_index}"


def pauli_table_program(
    rows: list[dict[str, Any]],
    *,
    default_identity_scope: str = "observable",
) -> WeylProgram:
    """Build a WeylProgram from a row-oriented Pauli table.

    Required row fields:
      - context_id or layer_id
      - pauli

    Optional row fields:
      - name / observable / observable_id
      - identity_scope: observable | event
      - source
      - round
      - notes
      - order

    Identity semantics:
      - observable rows without names reuse the Pauli string as the observable name;
      - event rows without names get unique event names such as `ZI@round1:0`.

    This adapter is "Qiskit-lite": real Qiskit/Stim adapters should first emit
    this table shape, so Q-Kernel's core does not depend on heavy SDKs.
    """
    if not rows:
        raise ValueError("Pauli table cannot be empty.")

    if default_identity_scope not in {"observable", "event"}:
        raise ValueError("default_identity_scope must be observable or event.")

    normalized_rows: list[dict[str, Any]] = []

    for i, row in enumerate(rows):
        pauli = str(row.get("pauli", "")).upper().strip()
        if not pauli:
            raise ValueError(f"row {i} is missing required field 'pauli'.")

        context_id = _context_key(row)
        identity_scope = _identity_scope(row, default_identity_scope)

        normalized = {
            **row,
            "_row_index": i,
            "_pauli": pauli,
            "_context_id": context_id,
            "_identity_scope": identity_scope,
            "_order": int(row.get("order", i) or i),
        }
        normalized["_name"] = _observable_name(
            row,
            pauli=pauli,
            context_id=context_id,
            row_index=i,
            identity_scope=identity_scope,
        )

        normalized_rows.append(normalized)

    lengths = {len(row["_pauli"]) for row in normalized_rows}
    if len(lengths) != 1:
        raise ValueError(f"all Pauli strings must have the same length; got {sorted(lengths)}.")

    m = next(iter(lengths))

    contexts_by_id: OrderedDict[str, list[dict[str, Any]]] = OrderedDict()
    for row in normalized_rows:
        contexts_by_id.setdefault(row["_context_id"], []).append(row)

    observables: dict[str, tuple[int, ...]] = {}
    metadata: dict[str, ObservableMetadata] = {}
    contexts: list[list[str]] = []

    for context_id, context_rows in contexts_by_id.items():
        ordered_rows = sorted(context_rows, key=lambda row: row["_order"])
        context_names: list[str] = []

        for row in ordered_rows:
            name = row["_name"]
            vec = pauli_string_to_vector(row["_pauli"])

            if name in observables and observables[name] != vec:
                raise ValueError(
                    f"observable name {name!r} is used for two different Pauli strings."
                )

            observables[name] = vec
            metadata[name] = ObservableMetadata(
                identity_scope=row["_identity_scope"],
                source=str(row["source"]) if row.get("source") not in {None, ""} else None,
                round=int(row["round"]) if row.get("round") not in {None, ""} else None,
                notes=str(row["notes"]) if row.get("notes") not in {None, ""} else None,
            )
            context_names.append(name)

        contexts.append(context_names)

    return WeylProgram(
        d=2,
        m=m,
        observables=observables,
        contexts=contexts,
        observable_metadata=metadata,
    )


def load_pauli_table(
    path: str | Path,
    *,
    default_identity_scope: str = "observable",
) -> WeylProgram:
    rows = _read_rows(path)
    return pauli_table_program(rows, default_identity_scope=default_identity_scope)
