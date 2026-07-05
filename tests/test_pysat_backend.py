import pytest
pytest.importorskip("pysat")
from pathlib import Path
import importlib.util

import pytest

from qkernel.backends.pysat_backend import (
    OptionalBackendUnavailable,
    pysat_available,
    solve_sat_with_pysat,
    solve_maxsat_with_rc2,
)
from qkernel.examples import peres_mermin_program


ROOT = Path(__file__).resolve().parents[1]


def test_sat_extra_declared_in_pyproject():
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")

    assert "sat = " in text
    assert "python-sat" in text


def test_pysat_available_returns_bool():
    assert isinstance(pysat_available(), bool)


def test_pysat_backend_missing_or_solves_pm():
    program = peres_mermin_program()

    if not pysat_available():
        with pytest.raises(OptionalBackendUnavailable):
            solve_sat_with_pysat(program, max_weight=6)
        return

    result = solve_sat_with_pysat(program, max_weight=6)
    assert result.status == "sat"
    assert result.verification is not None
    assert result.verification.valid


def test_rc2_backend_missing_or_solves_pm():
    program = peres_mermin_program()

    if not pysat_available():
        with pytest.raises(OptionalBackendUnavailable):
            solve_maxsat_with_rc2(program)
        return

    result = solve_maxsat_with_rc2(program)
    assert result.status == "sat"
    assert result.kernel is not None
    assert result.kernel.contextual
