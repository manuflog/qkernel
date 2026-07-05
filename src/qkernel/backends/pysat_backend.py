from __future__ import annotations

from dataclasses import dataclass
import importlib.util
from typing import Literal

from qkernel.ir import KernelResult, WeylProgram
from qkernel.sat_export import build_dimacs_cnf
from qkernel.maxsat_export import build_wcnf_maxsat
from qkernel.solver_output import kernel_from_lambda
from qkernel.verify import VerificationResult, verify_kernel


class OptionalBackendUnavailable(RuntimeError):
    """Raised when an optional solver backend is requested but not installed."""


@dataclass(frozen=True)
class BackendSolveResult:
    backend: str
    status: Literal["sat", "unsat", "unavailable"]
    lambda_vector: list[int] | None
    kernel: KernelResult | None
    verification: VerificationResult | None
    raw_model: list[int] | None
    message: str


def pysat_available() -> bool:
    """Return True if python-sat appears importable."""
    try:
        return (
            importlib.util.find_spec("pysat") is not None
            and importlib.util.find_spec("pysat.solvers") is not None
        )
    except ModuleNotFoundError:
        return False


def _require_pysat():
    if not pysat_available():
        raise OptionalBackendUnavailable(
            "PySAT is not installed. Install optional dependency with: pip install 'qkernel[sat]'"
        )


def _lambda_from_model(model: list[int], lambda_vars: list[int], context_count: int) -> list[int]:
    assignment = {abs(lit): lit > 0 for lit in model if lit != 0}
    lam = [0] * context_count

    for idx, var in enumerate(lambda_vars):
        lam[idx] = 1 if assignment.get(var, False) else 0

    return lam


def _result_from_lambda(
    *,
    backend: str,
    program: WeylProgram,
    lam: list[int],
    raw_model: list[int] | None,
    message: str,
) -> BackendSolveResult:
    kernel = kernel_from_lambda(program, lam)
    verification = verify_kernel(program, kernel)

    return BackendSolveResult(
        backend=backend,
        status="sat" if verification.valid else "unsat",
        lambda_vector=lam,
        kernel=kernel,
        verification=verification,
        raw_model=raw_model,
        message=message,
    )


def solve_sat_with_pysat(
    program: WeylProgram,
    *,
    max_weight: int | None = None,
    solver_name: str = "cadical153",
) -> BackendSolveResult:
    """Solve the exported CNF using PySAT, if installed.

    With `max_weight=None`, this solves feasibility only. With a fixed
    `max_weight`, it solves the bounded-k odd-Q feasibility problem using the
    current Q-Kernel CNF encoding.

    This is optional. The dependency-free DIMACS export remains the stable core
    interface for external SAT solvers.
    """
    _require_pysat()

    from pysat.solvers import Solver  # type: ignore

    model = build_dimacs_cnf(program, max_weight=max_weight)

    with Solver(name=solver_name, bootstrap_with=model.clauses) as solver:
        sat = solver.solve()
        if not sat:
            return BackendSolveResult(
                backend=f"pysat:{solver_name}",
                status="unsat",
                lambda_vector=None,
                kernel=None,
                verification=None,
                raw_model=None,
                message="PySAT reported UNSAT.",
            )

        raw_model = solver.get_model() or []
        lam = _lambda_from_model(raw_model, model.lambda_vars, len(program.contexts))

    return _result_from_lambda(
        backend=f"pysat:{solver_name}",
        program=program,
        lam=lam,
        raw_model=raw_model,
        message="PySAT returned a candidate lambda; Q-Kernel independently verified it.",
    )


def solve_maxsat_with_rc2(program: WeylProgram) -> BackendSolveResult:
    """Solve the direct WCNF minimum-kernel problem with PySAT RC2, if installed."""
    _require_pysat()

    try:
        from pysat.formula import WCNF  # type: ignore
        from pysat.examples.rc2 import RC2  # type: ignore
    except Exception as exc:  # pragma: no cover - only when partial PySAT installs exist
        raise OptionalBackendUnavailable(
            "PySAT is installed but RC2/WCNF support is unavailable. "
            "Install with: pip install 'python-sat[pblib,aiger]'"
        ) from exc

    exported = build_wcnf_maxsat(program)
    wcnf = WCNF()

    for clause in exported.hard_clauses:
        wcnf.append(clause)

    for weight, clause in exported.soft_clauses:
        wcnf.append(clause, weight=weight)

    with RC2(wcnf) as rc2:
        raw_model = rc2.compute()

    if raw_model is None:
        return BackendSolveResult(
            backend="pysat:rc2",
            status="unsat",
            lambda_vector=None,
            kernel=None,
            verification=None,
            raw_model=None,
            message="RC2 did not return a satisfying assignment.",
        )

    lam = _lambda_from_model(raw_model, exported.lambda_vars, len(program.contexts))
    return _result_from_lambda(
        backend="pysat:rc2",
        program=program,
        lam=lam,
        raw_model=raw_model,
        message="RC2 returned a candidate minimum lambda; Q-Kernel independently verified it.",
    )
