from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Literal

from qkernel.ir import WeylProgram
from qkernel.pauli import pauli_program
from qkernel.pauli_schedule import schedule_program


QubitOrder = Literal["qiskit", "qkernel"]


@dataclass(frozen=True)
class QiskitLiteParseResult:
    """Parsed dependency-free Qiskit-lite Pauli-family data."""

    layers: list[list[str]]
    qubit_order: QubitOrder
    ignored_coefficients: list[str]


def normalize_qiskit_pauli_label(label: str, *, qubit_order: QubitOrder = "qiskit") -> str:
    """Normalize a Pauli label into Q-Kernel's left-to-right qubit order.

    Qiskit string labels are conventionally displayed with the highest qubit on
    the left. Q-Kernel's Pauli frontend interprets the leftmost character as the
    first coordinate block. Therefore, `qubit_order="qiskit"` reverses labels.

    Use `qubit_order="qkernel"` when labels are already in Q-Kernel convention.
    """
    normalized = label.strip().upper()
    if not normalized:
        raise ValueError("Pauli label cannot be empty.")

    unsupported = sorted({ch for ch in normalized if ch not in {"I", "X", "Y", "Z"}})
    if unsupported:
        raise ValueError(f"unsupported Pauli character(s) {unsupported}; expected I, X, Y, Z.")

    if qubit_order == "qiskit":
        return normalized[::-1]
    if qubit_order == "qkernel":
        return normalized
    raise ValueError("qubit_order must be 'qiskit' or 'qkernel'.")


def _extract_pauli_label(item: Any) -> tuple[str, str | None]:
    """Extract `(pauli, coeff)` from common lightweight Qiskit-like items."""
    if isinstance(item, str):
        return item, None

    if isinstance(item, dict):
        for key in ["pauli", "label", "string"]:
            if key in item:
                coeff = item.get("coeff", item.get("coefficient"))
                return str(item[key]), None if coeff is None else str(coeff)

    if isinstance(item, (list, tuple)) and item:
        coeff = item[1] if len(item) > 1 else None
        return str(item[0]), None if coeff is None else str(coeff)

    raise ValueError(f"could not extract Pauli label from item: {item!r}")


def _normalize_layer(raw_layer: Any, *, qubit_order: QubitOrder) -> tuple[list[str], list[str]]:
    ignored_coefficients: list[str] = []

    if isinstance(raw_layer, dict):
        raw_items = raw_layer.get("paulis", raw_layer.get("observables", raw_layer.get("terms")))
        if raw_items is None:
            raise ValueError(f"layer dict must contain paulis/observables/terms: {raw_layer!r}")
    else:
        raw_items = raw_layer

    if not isinstance(raw_items, list):
        raise ValueError(f"layer must contain a list of Pauli labels/items: {raw_layer!r}")

    labels: list[str] = []
    for item in raw_items:
        label, coeff = _extract_pauli_label(item)
        labels.append(normalize_qiskit_pauli_label(label, qubit_order=qubit_order))
        if coeff is not None and coeff not in {"1", "1.0", "+1", "+1.0"}:
            ignored_coefficients.append(coeff)

    return labels, ignored_coefficients


def parse_qiskit_lite_data(data: dict[str, Any]) -> QiskitLiteParseResult:
    """Parse a dependency-free Qiskit-lite Pauli JSON object.

    Supported forms:

    1. Layered Pauli family:

        {
          "type": "qiskit_pauli_layers",
          "qubit_order": "qiskit",
          "layers": [
            {"name": "r0", "paulis": ["ZI", "IZ", "ZZ"]},
            ["IX", "XI", "XX"]
          ]
        }

    2. Context family:

        {
          "type": "qiskit_pauli_contexts",
          "qubit_order": "qiskit",
          "contexts": [["ZI", "IZ", "ZZ"]]
        }

    3. Flat terms with layer/context ids:

        {
          "type": "qiskit_sparse_pauli_terms",
          "terms": [
            {"pauli": "ZI", "layer": "r0", "coeff": 1},
            {"pauli": "IZ", "layer": "r0"}
          ]
        }

    Coefficients are recorded as ignored metadata because Q-Kernel analyzes
    Weyl/Pauli labels and contexts, not Hamiltonian weights.
    """
    kind = data.get("type", "qiskit_pauli_layers")
    qubit_order = data.get("qubit_order", "qiskit")
    if qubit_order not in {"qiskit", "qkernel"}:
        raise ValueError("qubit_order must be 'qiskit' or 'qkernel'.")

    ignored_coefficients: list[str] = []

    if "layers" in data:
        layers = []
        for raw_layer in data["layers"]:
            labels, ignored = _normalize_layer(raw_layer, qubit_order=qubit_order)
            layers.append(labels)
            ignored_coefficients.extend(ignored)
        return QiskitLiteParseResult(
            layers=layers,
            qubit_order=qubit_order,
            ignored_coefficients=ignored_coefficients,
        )

    if "contexts" in data:
        layers = []
        for raw_context in data["contexts"]:
            labels, ignored = _normalize_layer(raw_context, qubit_order=qubit_order)
            layers.append(labels)
            ignored_coefficients.extend(ignored)
        return QiskitLiteParseResult(
            layers=layers,
            qubit_order=qubit_order,
            ignored_coefficients=ignored_coefficients,
        )

    if "terms" in data:
        groups: dict[str, list[Any]] = {}
        order: list[str] = []
        for i, item in enumerate(data["terms"]):
            if not isinstance(item, dict):
                raise ValueError("flat terms must be dictionaries with pauli and layer/context id.")
            group = str(item.get("layer", item.get("context", item.get("context_id", f"default_{i}"))))
            if group not in groups:
                groups[group] = []
                order.append(group)
            groups[group].append(item)

        layers = []
        for group in order:
            labels, ignored = _normalize_layer(groups[group], qubit_order=qubit_order)
            layers.append(labels)
            ignored_coefficients.extend(ignored)

        return QiskitLiteParseResult(
            layers=layers,
            qubit_order=qubit_order,
            ignored_coefficients=ignored_coefficients,
        )

    raise ValueError("Qiskit-lite JSON must contain layers, contexts, or terms.")


def load_qiskit_lite_layers(path: str | Path) -> QiskitLiteParseResult:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return parse_qiskit_lite_data(data)


def load_qiskit_lite_program(
    path: str | Path,
    *,
    include_full_layers: bool = True,
    include_closed_triples: bool = True,
) -> WeylProgram:
    parsed = load_qiskit_lite_layers(path)
    return schedule_program(
        parsed.layers,
        include_full_layers=include_full_layers,
        include_closed_triples=include_closed_triples,
    )


def load_qiskit_lite_context_program(path: str | Path) -> WeylProgram:
    """Load Qiskit-lite contexts without extra schedule extraction.

    This is useful when the input contexts are already explicit and should not
    be expanded by the schedule frontend.
    """
    parsed = load_qiskit_lite_layers(path)
    return pauli_program(parsed.layers)
