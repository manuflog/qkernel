from pathlib import Path

import pytest

from qkernel.certificate import verify_certificate_file
from qkernel.examples import peres_mermin_program
from qkernel.maxsat_export import write_wcnf_maxsat
from qkernel.solver_output import (
    import_solver_solution,
    import_solver_solution_and_write_certificate,
    parse_solver_assignment_text,
)
from qkernel.sat_export import write_dimacs_cnf


def test_parse_signed_dimacs_assignment():
    assignment = parse_solver_assignment_text("s SATISFIABLE\nv 1 -2 3 0\nv -4 5 0\n")

    assert assignment[1] is True
    assert assignment[2] is False
    assert assignment[3] is True
    assert assignment[4] is False
    assert assignment[5] is True


def test_parse_bitstring_assignment():
    assignment = parse_solver_assignment_text("s OPTIMUM FOUND\nv 1010\n")

    assert assignment == {1: True, 2: False, 3: True, 4: False}


def test_parse_rejects_unsat():
    with pytest.raises(ValueError):
        parse_solver_assignment_text("s UNSATISFIABLE\n")


def test_import_solver_solution_from_fake_dimacs_output(tmp_path):
    program = peres_mermin_program()
    model_path = tmp_path / "pm.cnf"
    solution_path = tmp_path / "pm.sat.out"

    write_dimacs_cnf(program, model_path, max_weight=6)
    # lambda vars are 1..6. Aux vars can be arbitrary if clauses are not rechecked here;
    # Q-Kernel verifies only the imported lambda against the original program.
    solution_path.write_text("s SATISFIABLE\nv 1 2 3 4 5 6 0\n")

    imported = import_solver_solution(
        program,
        model_path=model_path,
        solver_output_path=solution_path,
    )

    assert imported.verification.valid
    assert imported.lambda_vector == [1, 1, 1, 1, 1, 1]
    assert imported.kernel.selected_contexts == [0, 1, 2, 3, 4, 5]


def test_import_solver_solution_writes_certificate(tmp_path):
    program = peres_mermin_program()
    model_path = tmp_path / "pm.wcnf"
    solution_path = tmp_path / "pm.maxsat.out"
    cert_path = tmp_path / "pm.cert.json"

    write_wcnf_maxsat(program, model_path)
    solution_path.write_text("s OPTIMUM FOUND\nv 111111000000000\n")

    imported = import_solver_solution_and_write_certificate(
        program,
        model_path=model_path,
        solver_output_path=solution_path,
        certificate_path=cert_path,
    )
    verification = verify_certificate_file(program, cert_path)

    assert imported.verification.valid
    assert verification["valid"] is True
    assert verification["q_value"] == 1


def test_import_solver_solution_rejects_bad_lambda(tmp_path):
    program = peres_mermin_program()
    model_path = tmp_path / "pm.wcnf"
    solution_path = tmp_path / "bad.out"

    write_wcnf_maxsat(program, model_path)
    solution_path.write_text("s OPTIMUM FOUND\nv 100000000000000\n")

    imported = import_solver_solution(
        program,
        model_path=model_path,
        solver_output_path=solution_path,
    )

    assert not imported.verification.valid
