from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .carry import b_vector
from .hashing import program_sha256
from .incidence import build_incidence
from .ir import KernelResult, WeylProgram
from .metadata import CERTIFICATE_SOFTWARE, COORDINATE_CONVENTION, CRITERION, INTEGER_CARRY_RULE, QKERNEL_VERSION
from .verify import verify_kernel
from .valuation import context_phase_vector


SCHEMA_VERSION = "qkernel.certificate.v1"


def lambda_from_kernel(program: WeylProgram, kernel: KernelResult) -> list[int]:
    lam = [0] * len(program.contexts)
    for idx in kernel.selected_contexts:
        lam[idx] ^= 1
    return lam


def kernel_to_dict(program: WeylProgram, kernel: KernelResult) -> dict[str, Any]:
    """Return a stable, standalone certificate dictionary.

    The certificate is not a substitute for the input program. It binds to the
    input program through `program_sha256` and records the exact convention and
    criterion under which the certificate was produced.
    """
    verification = verify_kernel(program, kernel) if kernel.contextual else None
    _, observable_order = build_incidence(program)
    lam = lambda_from_kernel(program, kernel)

    return {
        "schema": SCHEMA_VERSION,
        "software": {
            "qkernel_version": QKERNEL_VERSION,
        },
        "conventions": {
            "coordinate_convention": COORDINATE_CONVENTION,
            "integer_carry_rule": INTEGER_CARRY_RULE,
        },
        "criterion": CRITERION,
        "program_sha256": program_sha256(program),
        "program": {
            "d": program.d,
            "m": program.m,
            "contexts": len(program.contexts),
            "observables": len(program.observables),
            "observable_order": observable_order,
        },
        "kernel": {
            "contextual": kernel.contextual,
            "q_value": kernel.q_value,
            "lambda": lam,
            "selected_contexts": kernel.selected_contexts,
            "selected_observables": kernel.selected_observables,
            "b_vector": b_vector(program),
            "context_phases": context_phase_vector(program),
            "compression": {
                "contexts_original": kernel.original_contexts,
                "contexts_kernel": kernel.compressed_contexts,
                "observables_original": kernel.original_observables,
                "observables_kernel": kernel.compressed_observables,
                "context_ratio": kernel.compression_ratio_contexts,
                "observable_ratio": kernel.compression_ratio_observables,
            },
        },
        "verification": {
            "verified_by": "qkernel.verify.verify_kernel",
            "valid": verification.valid if verification else False,
            "reason": verification.reason if verification else "noncontextual result; no odd-Q certificate",
            "q_value": verification.q_value if verification else None,
            "zd_contextual": verification.zd_contextual if verification else False,
            "zd_reason": verification.zd_reason if verification else None,
        },
    }


def kernel_to_json(program: WeylProgram, kernel: KernelResult) -> str:
    return json.dumps(kernel_to_dict(program, kernel), indent=2) + "\n"


def kernel_to_markdown(program: WeylProgram, kernel: KernelResult) -> str:
    cert = kernel_to_dict(program, kernel)
    lines = [
        "# Q-Kernel certificate",
        "",
        f"Schema: `{cert['schema']}`",
        f"Q-Kernel version: `{cert['software']['qkernel_version']}`",
        f"Criterion: `{cert['criterion']['id']}`",
        f"Coordinate convention: `{cert['conventions']['coordinate_convention']['id']}`",
        f"Program SHA-256: `{cert['program_sha256']}`",
        "",
        "## Program",
        "",
        f"- d: {program.d}",
        f"- m: {program.m}",
        f"- contexts: {len(program.contexts)}",
        f"- observables: {len(program.observables)}",
        "",
        "## Kernel",
        "",
        f"- contextual: {kernel.contextual}",
        f"- q_value: {kernel.q_value}",
        f"- selected_contexts: {kernel.selected_contexts}",
        f"- selected_observables: {kernel.selected_observables}",
        f"- compression_contexts: {kernel.compressed_contexts}/{kernel.original_contexts}",
        f"- compression_observables: {kernel.compressed_observables}/{kernel.original_observables}",
        "",
        "## Verification",
        "",
        f"- valid: {cert['verification']['valid']}",
        f"- reason: {cert['verification']['reason']}",
    ]
    return "\n".join(lines) + "\n"


def write_certificate(program: WeylProgram, kernel: KernelResult, path: str | Path) -> None:
    Path(path).write_text(kernel_to_json(program, kernel), encoding="utf-8")


def load_certificate(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def inspect_certificate(path: str | Path) -> dict[str, Any]:
    """Return non-validating metadata from a certificate file."""
    cert = load_certificate(path)
    return {
        "schema": cert.get("schema"),
        "qkernel_version": cert.get("software", {}).get("qkernel_version"),
        "criterion": cert.get("criterion", {}).get("id"),
        "coordinate_convention": cert.get("conventions", {}).get("coordinate_convention", {}).get("id"),
        "integer_carry_rule": cert.get("conventions", {}).get("integer_carry_rule", {}).get("id"),
        "program_sha256": cert.get("program_sha256"),
        "contextual": cert.get("kernel", {}).get("contextual"),
        "q_value": cert.get("kernel", {}).get("q_value"),
        "selected_contexts": cert.get("kernel", {}).get("selected_contexts"),
    }


def _check_metadata(cert: dict[str, Any]) -> dict[str, Any] | None:
    if cert.get("schema") != SCHEMA_VERSION:
        return {
            "valid": False,
            "reason": f"unsupported schema {cert.get('schema')!r}",
        }

    criterion_id = cert.get("criterion", {}).get("id")
    if criterion_id != CRITERION["id"]:
        return {
            "valid": False,
            "reason": f"unsupported criterion {criterion_id!r}",
            "expected_criterion": CRITERION["id"],
        }

    convention_id = cert.get("conventions", {}).get("coordinate_convention", {}).get("id")
    if convention_id != COORDINATE_CONVENTION["id"]:
        return {
            "valid": False,
            "reason": f"unsupported coordinate convention {convention_id!r}",
            "expected_coordinate_convention": COORDINATE_CONVENTION["id"],
        }

    carry_rule_id = cert.get("conventions", {}).get("integer_carry_rule", {}).get("id")
    if carry_rule_id != INTEGER_CARRY_RULE["id"]:
        return {
            "valid": False,
            "reason": f"unsupported integer carry rule {carry_rule_id!r}",
            "expected_integer_carry_rule": INTEGER_CARRY_RULE["id"],
        }

    return None


def verify_certificate_file(program: WeylProgram, path: str | Path) -> dict[str, Any]:
    """Verify a saved certificate against a supplied program.

    The certificate is accepted only if:
      1. schema and criterion metadata match;
      2. program hash matches;
      3. lambda matches selected_contexts;
      4. qkernel.verify.verify_kernel accepts it.
    """
    cert = load_certificate(path)

    metadata_error = _check_metadata(cert)
    if metadata_error is not None:
        return metadata_error

    expected_hash = program_sha256(program)
    if cert.get("program_sha256") != expected_hash:
        return {
            "valid": False,
            "reason": "program_sha256 mismatch",
            "expected_program_sha256": expected_hash,
            "certificate_program_sha256": cert.get("program_sha256"),
        }

    kernel_data = cert.get("kernel", {})
    selected_contexts = list(kernel_data.get("selected_contexts", []))
    cert_lambda = list(kernel_data.get("lambda", []))

    if len(cert_lambda) != len(program.contexts):
        return {
            "valid": False,
            "reason": "lambda length does not match program context count",
        }

    expected_lambda = [0] * len(program.contexts)
    for idx in selected_contexts:
        if not isinstance(idx, int):
            return {"valid": False, "reason": f"non-integer context index {idx!r}"}
        if idx < 0 or idx >= len(program.contexts):
            return {"valid": False, "reason": f"context index out of range {idx}"}
        expected_lambda[idx] ^= 1

    if cert_lambda != expected_lambda:
        return {
            "valid": False,
            "reason": "lambda does not match selected_contexts",
            "expected_lambda": expected_lambda,
            "certificate_lambda": cert_lambda,
        }

    kernel = KernelResult(
        contextual=bool(kernel_data.get("contextual", False)),
        original_contexts=int(kernel_data.get("compression", {}).get("contexts_original", len(program.contexts))),
        original_observables=int(kernel_data.get("compression", {}).get("observables_original", len(program.observables))),
        compressed_contexts=int(kernel_data.get("compression", {}).get("contexts_kernel", len(selected_contexts))),
        compressed_observables=int(kernel_data.get("compression", {}).get("observables_kernel", 0)),
        selected_contexts=selected_contexts,
        selected_observables=list(kernel_data.get("selected_observables", [])),
        q_value=kernel_data.get("q_value"),
        compression_ratio_contexts=float(kernel_data.get("compression", {}).get("context_ratio", 0.0)),
        compression_ratio_observables=float(kernel_data.get("compression", {}).get("observable_ratio", 0.0)),
    )

    verification = verify_kernel(program, kernel)

    return {
        "valid": verification.valid,
        "reason": verification.reason,
        "q_value": verification.q_value,
        "program_sha256": expected_hash,
        "qkernel_version": cert.get("software", {}).get("qkernel_version"),
        "criterion": cert.get("criterion", {}).get("id"),
        "coordinate_convention": cert.get("conventions", {}).get("coordinate_convention", {}).get("id"),
    }
