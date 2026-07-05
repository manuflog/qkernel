from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

from qkernel.ir import WeylProgram
from qkernel.pauli_schedule import schedule_program


_FACTOR_RE = re.compile(r"([XYZ])(\d+)$")


@dataclass(frozen=True)
class StimLiteParseResult:
    """Result of parsing the supported MPP subset of a Stim-like text file."""

    layers: list[list[str]]
    ignored_lines: list[str]
    num_qubits: int


def _pauli_mul_ignoring_phase(a: str, b: str) -> str:
    if a == "I":
        return b
    if b == "I":
        return a
    if a == b:
        return "I"
    return ({"X", "Y", "Z"} - {a, b}).pop()


def _normalize_mpp_token(token: str) -> str:
    token = token.strip()
    # Stim MPP allows sign inversion with ! in front of a target. Signs/phases
    # are intentionally not part of Q-Kernel's Weyl-label geometry.
    while token.startswith(("!", "+", "-")):
        token = token[1:]
    return token


def parse_mpp_product(token: str) -> dict[int, str]:
    """Parse one MPP product token into a sparse Pauli map.

    Supported token examples:

        X0
        Z0*Z1
        X0*Y3*Z5

    Signs are ignored at this adapter boundary because Q-Kernel tracks Weyl
    labels, not measurement outcome signs.
    """
    token = _normalize_mpp_token(token)
    if not token:
        raise ValueError("empty MPP product token.")

    sparse: dict[int, str] = {}

    for raw_factor in token.split("*"):
        factor = _normalize_mpp_token(raw_factor)
        match = _FACTOR_RE.fullmatch(factor)
        if not match:
            raise ValueError(f"unsupported MPP factor {raw_factor!r} in token {token!r}.")

        pauli = match.group(1)
        qubit = int(match.group(2))
        sparse[qubit] = _pauli_mul_ignoring_phase(sparse.get(qubit, "I"), pauli)

    return {q: p for q, p in sparse.items() if p != "I"}


def _sparse_to_pauli_string(sparse: dict[int, str], num_qubits: int) -> str:
    chars = ["I"] * num_qubits
    for qubit, pauli in sparse.items():
        if qubit < 0 or qubit >= num_qubits:
            raise ValueError(f"qubit index out of range: {qubit}")
        chars[qubit] = pauli
    return "".join(chars)


def parse_stim_lite_text(text: str, *, strict: bool = False) -> StimLiteParseResult:
    """Parse the supported Stim-lite MPP subset.

    Supported lines:

        TICK
        MPP X0 Z1 X0*Z1

    Each TICK-delimited block becomes one schedule layer. Each MPP product token
    becomes one Pauli observable in that layer. Non-MPP circuit operations are
    ignored by default and rejected with strict=True.

    This is not a full Stim parser. It is a stable bridge format for explicit
    Pauli-product measurement families before adding an optional real Stim
    dependency.
    """
    raw_layers: list[list[dict[int, str]]] = []
    current: list[dict[int, str]] = []
    ignored: list[str] = []
    max_qubit = -1

    def flush_current() -> None:
        nonlocal current
        if current:
            raw_layers.append(current)
            current = []

    for lineno, original in enumerate(text.splitlines(), start=1):
        line = original.split("#", 1)[0].strip()
        if not line:
            continue

        upper = line.upper()

        if upper == "TICK":
            flush_current()
            continue

        if upper.startswith("MPP "):
            tokens = line.split()[1:]
            if not tokens:
                raise ValueError(f"line {lineno}: MPP instruction has no products.")

            for token in tokens:
                sparse = parse_mpp_product(token)
                if sparse:
                    max_qubit = max(max_qubit, max(sparse))
                current.append(sparse)
            continue

        if strict:
            raise ValueError(f"line {lineno}: unsupported Stim-lite instruction {line!r}.")

        ignored.append(line)

    flush_current()

    if max_qubit < 0:
        raise ValueError("no MPP Pauli products found.")

    num_qubits = max_qubit + 1
    layers = [
        [_sparse_to_pauli_string(sparse, num_qubits) for sparse in layer]
        for layer in raw_layers
    ]

    return StimLiteParseResult(
        layers=layers,
        ignored_lines=ignored,
        num_qubits=num_qubits,
    )


def load_stim_lite_schedule(path: str | Path, *, strict: bool = False) -> StimLiteParseResult:
    return parse_stim_lite_text(Path(path).read_text(encoding="utf-8"), strict=strict)


def load_stim_lite_program(
    path: str | Path,
    *,
    strict: bool = False,
    include_full_layers: bool = True,
    include_closed_triples: bool = True,
) -> WeylProgram:
    parsed = load_stim_lite_schedule(path, strict=strict)
    return schedule_program(
        parsed.layers,
        include_full_layers=include_full_layers,
        include_closed_triples=include_closed_triples,
    )
