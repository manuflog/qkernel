import pytest
import subprocess
import sys
from pathlib import Path

from qkernel.backends.pysat_backend import pysat_available


ROOT = Path(__file__).resolve().parents[1]


def test_cli_solve_pysat_missing_backend_message():
    if pysat_available():
        return

    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "qkernel.cli",
            "solve-pysat",
            str(ROOT / "examples/peres_mermin_pauli.json"),
            "--input",
            "pauli",
            "--max-weight",
            "6",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    assert proc.returncode != 0
    assert "pip install" in (proc.stdout + proc.stderr)
