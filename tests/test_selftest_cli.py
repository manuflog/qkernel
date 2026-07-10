import json

from qkernel.cli import main
from qkernel.selftest import run_selftest


def test_run_selftest_ok():
    result = run_selftest()

    assert result.ok
    assert result.contextual
    assert result.q_value == 1


def test_cli_selftest_ok(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["qkernel", "self-test"])

    main()
    data = json.loads(capsys.readouterr().out)

    assert data["ok"] is True
    assert data["q_value"] == 1
