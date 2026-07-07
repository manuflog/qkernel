from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

from .ir import WeylProgram


SCHEMA_VERSION = "qkernel.circuit_manifest.v1"


@dataclass(frozen=True)
class CircuitBuilderManifest:
    schema: str
    program_id: str
    d: int
    m: int
    contexts: int
    observables: int
    selected_contexts: list[int]
    exportable: bool
    supported_exporter: str | None
    required_protocol: str | None
    blocker_reasons: list[str]
    backend_requirements: list[str]
    next_actions: list[str]
    claim_scope: str
    not_claimed: list[str]


def _selected_contexts(program: WeylProgram, selected_contexts: list[int] | None) -> list[int]:
    selected = selected_contexts if selected_contexts is not None else list(range(len(program.contexts)))
    out: list[int] = []
    for idx in selected:
        if idx < 0 or idx >= len(program.contexts):
            raise ValueError(f"context index {idx} out of range for {len(program.contexts)} context(s)")
        out.append(idx)
    return out


def circuit_builder_manifest(
    program: WeylProgram,
    *,
    program_id: str = "program",
    selected_contexts: list[int] | None = None,
) -> CircuitBuilderManifest:
    selected = _selected_contexts(program, selected_contexts)
    blockers: list[str] = []

    if program.d != 2:
        blockers.append(
            f"d=2 required for current Qiskit exporter; got d={program.d}. "
            "Higher-d qudit protocols need a validated Z_d phase-readout design."
        )
    if program.m != 2:
        blockers.append(f"m=2 required for current two-qubit Qiskit exporter; got m={program.m}.")
    for idx in selected:
        if len(program.contexts[idx]) != 3:
            blockers.append(
                f"context {idx} has {len(program.contexts[idx])} observable(s); "
                "current sequential Pauli exporter expects triples"
            )

    exportable = not blockers
    if exportable:
        supported_exporter = "export_qiskit_protocol"
        required_protocol = "sequential non-destructive ancilla Hadamard-test per observable"
        next_actions = [
            "run qkernel export-circuit to emit the standalone Qiskit script",
            "run exact sign verification during export",
            "execute on hardware only with QISKIT_IBM_TOKEN and backend calibration review",
        ]
    else:
        supported_exporter = None
        required_protocol = None
        next_actions = [
            "do not emit a hardware-ready circuit from this manifest",
            "build an explicit protocol design for the unsupported d,m or context arity",
            "add simulator/hardware validation before enabling an exporter",
        ]

    return CircuitBuilderManifest(
        schema=SCHEMA_VERSION,
        program_id=program_id,
        d=program.d,
        m=program.m,
        contexts=len(program.contexts),
        observables=len(program.observables),
        selected_contexts=selected,
        exportable=exportable,
        supported_exporter=supported_exporter,
        required_protocol=required_protocol,
        blocker_reasons=blockers,
        backend_requirements=[
            "2 data qubits plus 1 ancilla for the current Qiskit exporter",
            "separate ancilla measurements for each observable to avoid pinned statistics",
            "backend supports controlled Pauli decomposition after transpilation",
            "hardware run must report S, standard error, noncontextual bound, and sigma margin",
        ],
        next_actions=next_actions,
        claim_scope=(
            "circuit-builder readiness manifest; describes whether qkernel can emit a currently "
            "validated protocol, not whether a circuit is resource-optimal"
        ),
        not_claimed=[
            "does not synthesize unsupported qudit protocols",
            "does not prove hardware success before execution",
            "does not optimize circuit depth",
            "does not optimize T-count or magic-state cost",
            "does not certify semantic equivalence of compiler rewrites",
        ],
    )


def circuit_builder_manifest_dict(report: CircuitBuilderManifest) -> dict:
    return asdict(report)


def _fmt(value: object) -> str:
    if value is None:
        return "-"
    if value is True:
        return "yes"
    if value is False:
        return "no"
    return str(value)


def circuit_builder_manifest_markdown(report: CircuitBuilderManifest | dict) -> str:
    data = asdict(report) if isinstance(report, CircuitBuilderManifest) else report
    lines = [
        "# Circuit Builder Manifest",
        "",
        "## Scope",
        "",
        data["claim_scope"],
        "",
        "## Readiness",
        "",
        "| field | value |",
        "| --- | --- |",
    ]
    for key in [
        "program_id",
        "d",
        "m",
        "contexts",
        "observables",
        "selected_contexts",
        "exportable",
        "supported_exporter",
        "required_protocol",
    ]:
        lines.append(f"| {key} | {_fmt(data.get(key))} |")
    lines.extend([
        "",
        "## Blockers",
        "",
        "\n".join(f"- {item}" for item in data["blocker_reasons"]) or "-",
        "",
        "## Backend Requirements",
        "",
        "\n".join(f"- {item}" for item in data["backend_requirements"]),
        "",
        "## Next Actions",
        "",
        "\n".join(f"- {item}" for item in data["next_actions"]),
        "",
        "## Non-Claims",
        "",
        "\n".join(f"- {item}" for item in data["not_claimed"]),
        "",
    ])
    return "\n".join(lines)


def write_circuit_builder_manifest_markdown(report: CircuitBuilderManifest | dict, path: str | Path) -> None:
    Path(path).write_text(circuit_builder_manifest_markdown(report), encoding="utf-8")
