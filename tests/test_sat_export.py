from itertools import product
from pathlib import Path

from qkernel.examples import peres_mermin_program
from qkernel.pauli import pauli_program
from qkernel.sat_export import build_dimacs_cnf, write_dimacs_cnf


def _satisfiable_by_bruteforce(model):
    n = model.num_vars
    for values in product([False, True], repeat=n):
        ok = True
        for clause in model.clauses:
            if not clause:
                ok = False
                break
            sat = False
            for lit in clause:
                value = values[abs(lit) - 1]
                if (lit > 0 and value) or (lit < 0 and not value):
                    sat = True
                    break
            if not sat:
                ok = False
                break
        if ok:
            return True, values
    return False, None


def test_dimacs_pm_is_satisfiable_at_weight_6():
    program = peres_mermin_program()
    model = build_dimacs_cnf(program, max_weight=6)

    sat, assignment = _satisfiable_by_bruteforce(model)

    assert sat
    assert assignment is not None
    assert [assignment[v - 1] for v in model.lambda_vars] == [True] * 6


def test_dimacs_pm_unsat_below_weight_6():
    program = peres_mermin_program()
    model = build_dimacs_cnf(program, max_weight=5)

    sat, _ = _satisfiable_by_bruteforce(model)

    assert not sat


def test_dimacs_row_only_is_unsatisfiable():
    program = pauli_program([
        ["ZI", "IZ", "ZZ"],
        ["IX", "XI", "XX"],
        ["ZX", "XZ", "YY"],
    ])
    model = build_dimacs_cnf(program)

    sat, _ = _satisfiable_by_bruteforce(model)

    assert not sat


def test_write_dimacs_contains_metadata(tmp_path):
    program = peres_mermin_program()
    path = tmp_path / "pm.cnf"
    write_dimacs_cnf(program, path, max_weight=6)

    text = path.read_text()

    assert "p cnf" in text
    assert "c qkernel_dimacs_v1" in text
    assert "c criterion odd_Q_even_d_v1" in text
    assert "c lambda_var 1 context_index 0" in text
