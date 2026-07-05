from itertools import product
from pathlib import Path

from qkernel.examples import peres_mermin_program
from qkernel.maxsat_export import build_wcnf_maxsat, write_wcnf_maxsat
from qkernel.pauli import pauli_program


def _best_wcnf_assignment(model):
    best_cost = None
    best_assignment = None
    n = model.num_vars

    for values in product([False, True], repeat=n):
        hard_ok = True
        for clause in model.hard_clauses:
            sat = False
            for lit in clause:
                value = values[abs(lit) - 1]
                if (lit > 0 and value) or (lit < 0 and not value):
                    sat = True
                    break
            if not sat:
                hard_ok = False
                break

        if not hard_ok:
            continue

        cost = 0
        for weight, clause in model.soft_clauses:
            sat = False
            for lit in clause:
                value = values[abs(lit) - 1]
                if (lit > 0 and value) or (lit < 0 and not value):
                    sat = True
                    break
            if not sat:
                cost += weight

        if best_cost is None or cost < best_cost:
            best_cost = cost
            best_assignment = values

    return best_cost, best_assignment


def test_wcnf_pm_min_cost_is_6():
    program = peres_mermin_program()
    model = build_wcnf_maxsat(program)

    cost, assignment = _best_wcnf_assignment(model)

    assert cost == 6
    assert assignment is not None
    assert [assignment[var - 1] for var in model.lambda_vars] == [True] * 6


def test_wcnf_row_only_has_no_hard_satisfying_assignment():
    program = pauli_program([
        ["ZI", "IZ", "ZZ"],
        ["IX", "XI", "XX"],
        ["ZX", "XZ", "YY"],
    ])
    model = build_wcnf_maxsat(program)

    cost, assignment = _best_wcnf_assignment(model)

    assert cost is None
    assert assignment is None


def test_write_wcnf_contains_metadata(tmp_path):
    program = peres_mermin_program()
    path = tmp_path / "pm.wcnf"
    write_wcnf_maxsat(program, path)

    text = path.read_text()

    assert "p wcnf" in text
    assert "c qkernel_wcnf_v1" in text
    assert "c criterion odd_Q_even_d_v1" in text
    assert "soft clauses -lambda_i minimize selected contexts" in text
