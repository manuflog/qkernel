import json
from pathlib import Path

from qkernel.cli import main
from qkernel.release_audit import (
    release_audit_markdown,
    run_release_audit,
    write_release_audit_outputs,
)
from experiments.release_audit import run_audit


ROOT = Path(__file__).resolve().parents[1]


def test_release_audit_passes():
    report = run_release_audit(ROOT)

    assert report.passed
    # version is read from package metadata; assert it matches rather than a
    # hard-coded literal so the test survives version bumps.
    from qkernel.metadata import QKERNEL_VERSION
    assert report.version == QKERNEL_VERSION
    assert "contextuality kernels" in report.safe_positioning
    assert any("not a T-count" in item for item in report.unsafe_positioning)


def test_release_audit_markdown_contains_key_sections():
    report = run_release_audit(ROOT)
    md = release_audit_markdown(report)

    assert "Safe positioning" in md
    assert "Unsafe positioning" in md
    assert "core:pm_kernel_verified" in md
    assert "novelty:linear_system_not_claimed" in md


def test_release_audit_writes_outputs(tmp_path):
    report = run_release_audit(ROOT)
    json_path = tmp_path / "audit.json"
    md_path = tmp_path / "audit.md"

    write_release_audit_outputs(report, json_path=json_path, markdown_path=md_path)

    data = json.loads(json_path.read_text(encoding="utf-8"))
    assert data["passed"] is True
    assert md_path.exists()


def test_release_audit_cli(monkeypatch, capsys, tmp_path):
    json_path = tmp_path / "audit.json"
    md_path = tmp_path / "audit.md"

    monkeypatch.setattr(
        "sys.argv",
        [
            "qkernel",
            "release-audit",
            "--root",
            str(ROOT),
            "--out-json",
            str(json_path),
            "--out-md",
            str(md_path),
        ],
    )

    main()
    stdout = capsys.readouterr().out
    json_text = stdout.split("\nwrote JSON audit:", 1)[0]
    data = json.loads(json_text)

    assert data["passed"] is True
    assert json_path.exists()
    assert md_path.exists()


def test_release_audit_script_outputs():
    json_path, md_path = run_audit()

    assert json_path.exists()
    assert md_path.exists()
    data = json.loads(json_path.read_text(encoding="utf-8"))
    assert data["passed"] is True
