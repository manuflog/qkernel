from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .analyzer import q_of_cycle
from .certificate import write_certificate
from .ir import KernelResult, WeylProgram
from .verify import VerificationResult, verify_kernel


_LAMBDA_COMMENT_RE = re.compile(r"^c\s+lambda_var\s+(\d+)\s+context_index\s+(\d+)\s*$")


@dataclass(frozen=True)
class ImportedSolverSolution:
    """Imported external SAT/MaxSAT assignment interpreted as a Q-Kernel kernel."""

    lambda_vector: list[int]
    kernel: KernelResult
    verification: VerificationResult
    assignment: dict[int, bool]
    lambda_var_map: dict[int, int]


def parse_lambda_var_map(model_path: str | Path) -> dict[int, int]:
    """Read lambda-var comments from a Q-Kernel CNF/WCNF model.

    Expected comment format:

        c lambda_var 1 context_index 0
    """
    path = Path(model_path)
    mapping: dict[int, int] = {}

    for line in path.read_text(encoding="utf-8").splitlines():
        match = _LAMBDA_COMMENT_RE.match(line.strip())
        if match:
            var = int(match.group(1))
            idx = int(match.group(2))
            mapping[var] = idx

    if not mapping:
        raise ValueError("model file contains no qkernel lambda_var comments.")

    return mapping


def parse_solver_assignment_text(text: str) -> dict[int, bool]:
    """Parse common SAT/MaxSAT assignment output.

    Supported styles:

    DIMACS-like signed literal lines:

        s SATISFIABLE
        v 1 -2 3 0

    MaxSAT-style bitstring lines:

        s OPTIMUM FOUND
        v 101001

    Returns a map from variable number to assigned Boolean value.
    """
    status_lines = [
        line.strip().lower()
        for line in text.splitlines()
        if line.strip().lower().startswith("s ")
    ]

    for status in status_lines:
        if "unsat" in status:
            raise ValueError(f"solver reported UNSAT/UNSATISFIABLE: {status}")

    assignment: dict[int, bool] = {}

    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("c"):
            continue

        if line.startswith("v "):
            payload = line[2:].strip()
        elif line.startswith("V "):
            payload = line[2:].strip()
        else:
            continue

        tokens = payload.split()

        if len(tokens) == 1 and re.fullmatch(r"[01]+", tokens[0]):
            bitstring = tokens[0]
            for i, char in enumerate(bitstring, start=1):
                assignment[i] = (char == "1")
            continue

        for token in tokens:
            if token == "0":
                continue
            try:
                lit = int(token)
            except ValueError:
                continue
            if lit == 0:
                continue
            assignment[abs(lit)] = lit > 0

    if not assignment:
        raise ValueError("solver output contains no parseable assignment lines.")

    return assignment


def parse_solver_assignment_file(path: str | Path) -> dict[int, bool]:
    return parse_solver_assignment_text(Path(path).read_text(encoding="utf-8"))


def lambda_from_assignment(
    assignment: dict[int, bool],
    lambda_var_map: dict[int, int],
    *,
    context_count: int,
) -> list[int]:
    lam = [0] * context_count

    for var, context_idx in lambda_var_map.items():
        if context_idx < 0 or context_idx >= context_count:
            raise ValueError(
                f"lambda var {var} maps to out-of-range context index {context_idx}."
            )
        lam[context_idx] = 1 if assignment.get(var, False) else 0

    return lam


def kernel_from_lambda(program: WeylProgram, lam: list[int]) -> KernelResult:
    if len(lam) != len(program.contexts):
        raise ValueError("lambda length does not match program context count.")

    selected_contexts = [i for i, bit in enumerate(lam) if bit]
    selected_observables = sorted(
        {name for idx in selected_contexts for name in program.contexts[idx]}
    )
    q = q_of_cycle(program, lam) if selected_contexts else None

    return KernelResult(
        contextual=(q == 1),
        original_contexts=len(program.contexts),
        original_observables=len(program.observables),
        compressed_contexts=len(selected_contexts),
        compressed_observables=len(selected_observables),
        selected_contexts=selected_contexts,
        selected_observables=selected_observables,
        q_value=q,
        compression_ratio_contexts=(
            len(program.contexts) / len(selected_contexts) if selected_contexts else 0.0
        ),
        compression_ratio_observables=(
            len(program.observables) / len(selected_observables) if selected_observables else 0.0
        ),
    )


def import_solver_solution(
    program: WeylProgram,
    *,
    model_path: str | Path,
    solver_output_path: str | Path,
) -> ImportedSolverSolution:
    """Import an external SAT/MaxSAT assignment and verify it as a Q-Kernel certificate."""
    lambda_var_map = parse_lambda_var_map(model_path)
    assignment = parse_solver_assignment_file(solver_output_path)
    lam = lambda_from_assignment(
        assignment,
        lambda_var_map,
        context_count=len(program.contexts),
    )
    kernel = kernel_from_lambda(program, lam)
    verification = verify_kernel(program, kernel)

    return ImportedSolverSolution(
        lambda_vector=lam,
        kernel=kernel,
        verification=verification,
        assignment=assignment,
        lambda_var_map=lambda_var_map,
    )


def import_solver_solution_and_write_certificate(
    program: WeylProgram,
    *,
    model_path: str | Path,
    solver_output_path: str | Path,
    certificate_path: str | Path,
) -> ImportedSolverSolution:
    imported = import_solver_solution(
        program,
        model_path=model_path,
        solver_output_path=solver_output_path,
    )
    if not imported.verification.valid:
        raise ValueError(f"external solver assignment failed verification: {imported.verification.reason}")

    write_certificate(program, imported.kernel, certificate_path)
    return imported
