import pytest
pytest.importorskip("qiskit")
import json
from pathlib import Path

from qkernel.cli import main


ROOT = Path(__file__).resolve().parents[1]


def test_cli_inspect_qiskit_lite(monkeypatch, capsys):
    monkeypatch.setattr(
        "sys.argv",
        [
            "qkernel",
            "inspect-qiskit-lite",
            str(ROOT / "examples/peres_mermin_qiskit_lite.json"),
        ],
    )

    main()
    data = json.loads(capsys.readouterr().out)

    assert data["qubit_order"] == "qiskit"
    assert data["layers"][0] == ["ZI", "IZ", "ZZ"]


def test_cli_analyze_qiskit_lite(monkeypatch, capsys):
    monkeypatch.setattr(
        "sys.argv",
        [
            "qkernel",
            "analyze-qiskit-lite",
            str(ROOT / "examples/peres_mermin_qiskit_lite.json"),
        ],
    )

    main()
    out = capsys.readouterr().out

    assert "contextual: True" in out
    assert "q_value: 1" in out
