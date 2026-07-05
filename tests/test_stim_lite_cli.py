import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_cli_inspect_stim_lite():
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "qkernel.cli",
            "inspect-stim-lite",
            str(ROOT / "examples/peres_mermin_mpp.stim"),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )

    data = json.loads(proc.stdout)

    assert data["num_qubits"] == 2
    assert data["layers"][0] == ["ZI", "IZ", "ZZ"]


def test_cli_analyze_stim_lite():
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "qkernel.cli",
            "analyze-stim-lite",
            str(ROOT / "examples/peres_mermin_mpp.stim"),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )

    assert "contextual: True" in proc.stdout
    assert "q_value: 1" in proc.stdout
