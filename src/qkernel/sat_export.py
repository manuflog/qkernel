from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from pathlib import Path

from .carry import b_vector
from .incidence import build_incidence
from .ir import WeylProgram
from .metadata import COORDINATE_CONVENTION, CRITERION, INTEGER_CARRY_RULE, QKERNEL_VERSION
from .validate import validate_program


@dataclass(frozen=True)
class DimacsModel:
    clauses: list[list[int]]
    num_vars: int
    comments: list[str]
    lambda_vars: list[int]

    def to_dimacs(self) -> str:
        lines: list[str] = []
        for comment in self.comments:
            lines.append(f"c {comment}")
        lines.append(f"p cnf {self.num_vars} {len(self.clauses)}")
        for clause in self.clauses:
            lines.append(" ".join(str(lit) for lit in clause) + " 0")
        return "\n".join(lines) + "\n"


def _xor2_clauses(x: int, y: int, z: int) -> list[list[int]]:
    """CNF clauses for z <-> x XOR y."""
    return [
        [-x, -y, -z],
        [-x, y, z],
        [x, -y, z],
        [x, y, -z],
    ]


def _xor_constraint(
    vars_: list[int],
    rhs: int,
    *,
    next_var: int,
) -> tuple[list[list[int]], int]:
    """Return clauses enforcing XOR(vars_) == rhs plus next available var."""
    if rhs not in {0, 1}:
        raise ValueError("rhs must be 0 or 1.")

    if not vars_:
        if rhs == 0:
            return [], next_var
        # Unsatisfiable empty clause.
        return [[]], next_var

    if len(vars_) == 1:
        return ([[vars_[0]]] if rhs == 1 else [[-vars_[0]]]), next_var

    clauses: list[list[int]] = []
    current = vars_[0]

    for var in vars_[1:]:
        aux = next_var
        next_var += 1
        clauses.extend(_xor2_clauses(current, var, aux))
        current = aux

    clauses.append([current] if rhs == 1 else [-current])
    return clauses, next_var


def _at_most_k_clauses(vars_: list[int], k: int, *, max_clauses: int = 250_000) -> list[list[int]]:
    """Naive at-most-k encoding: every k+1 subset contains a false literal.

    This is only intended for small external SAT exports. For large instances,
    a real cardinality-network, sequential-counter, MaxSAT, or MILP backend is
    preferable.
    """
    if k < 0:
        return [[]]
    if k >= len(vars_):
        return []

    count = 0
    clauses: list[list[int]] = []
    for combo in combinations(vars_, k + 1):
        count += 1
        if count > max_clauses:
            raise RuntimeError(
                "at-most-k naive encoding would create too many clauses; "
                "raise max_cardinality_clauses or use a real cardinality/MaxSAT backend."
            )
        clauses.append([-v for v in combo])

    return clauses


def build_dimacs_cnf(
    program: WeylProgram,
    *,
    max_weight: int | None = None,
    max_cardinality_clauses: int = 250_000,
) -> DimacsModel:
    """Build a DIMACS CNF encoding of the odd-Q feasibility problem.

    Variables x_i correspond to context-selection bits lambda_i.

    Constraints:
      - for every observable column j: XOR_i A[i,j] x_i = 0;
      - for carry: XOR_i b[i] x_i = 1;
      - optionally: sum_i x_i <= max_weight.

    This is a feasibility export, not a native MaxSAT file. To find a minimum
    kernel with an external SAT solver, call this repeatedly with increasing
    max_weight until satisfiable.
    """
    validate_program(program)

    A, observable_order = build_incidence(program)
    b = b_vector(program)

    n_contexts = len(program.contexts)
    lambda_vars = list(range(1, n_contexts + 1))
    next_var = n_contexts + 1

    clauses: list[list[int]] = []

    # Incidence closure: A^T lambda = 0.
    for col, obs_name in enumerate(observable_order):
        involved = [
            lambda_vars[row]
            for row in range(n_contexts)
            if A[row][col] & 1
        ]
        col_clauses, next_var = _xor_constraint(involved, 0, next_var=next_var)
        clauses.extend(col_clauses)

    # Odd carry: b^T lambda = 1.
    carry_involved = [
        lambda_vars[row]
        for row in range(n_contexts)
        if b[row] & 1
    ]
    carry_clauses, next_var = _xor_constraint(carry_involved, 1, next_var=next_var)
    clauses.extend(carry_clauses)

    if max_weight is not None:
        clauses.extend(
            _at_most_k_clauses(
                lambda_vars,
                max_weight,
                max_clauses=max_cardinality_clauses,
            )
        )

    comments = [
        "qkernel_dimacs_v1",
        f"qkernel_version {QKERNEL_VERSION}",
        f"criterion {CRITERION['id']}",
        f"coordinate_convention {COORDINATE_CONVENTION['id']}",
        f"integer_carry_rule {INTEGER_CARRY_RULE['id']}",
        "variables lambda_i select context i, using 0-based context indices in comments",
    ]
    comments.extend(
        f"lambda_var {var} context_index {idx}"
        for idx, var in enumerate(lambda_vars)
    )
    comments.extend(
        f"observable_col {idx} {name}"
        for idx, name in enumerate(observable_order)
    )

    return DimacsModel(
        clauses=clauses,
        num_vars=next_var - 1,
        comments=comments,
        lambda_vars=lambda_vars,
    )


def write_dimacs_cnf(
    program: WeylProgram,
    path: str | Path,
    *,
    max_weight: int | None = None,
    max_cardinality_clauses: int = 250_000,
) -> DimacsModel:
    model = build_dimacs_cnf(
        program,
        max_weight=max_weight,
        max_cardinality_clauses=max_cardinality_clauses,
    )
    Path(path).write_text(model.to_dimacs(), encoding="utf-8")
    return model
