import pytest

from qkernel.examples import peres_mermin_program
from qkernel.tower import tower_law_report


def test_tower_scope_rejects_non_lifted_base_d():
    program = peres_mermin_program()
    lam = [1, 1, 1, 1, 1, 1]

    with pytest.raises(ValueError):
        tower_law_report(program, lam, base_d=1)
