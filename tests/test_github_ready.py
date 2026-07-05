import json
from pathlib import Path

from qkernel.cli import main
from qkernel.github_ready import (
    github_ready_report_markdown,
    run_github_ready_check,
    write_github_ready_report,
)


ROOT = Path(__file__).resolve().parents[1]


def test_github_ready_passes():
    report = run_github_ready_check(ROOT)

    assert report.passed
    assert "alpha" in report.recommendation


def test_github_ready_markdown():
    report = run_github_ready_check(ROOT)
    md = github_ready_report_markdown(report)

    assert "GitHub Readiness Report" in md
    assert "CONTRIBUTING.md" in md
    assert "release-audit.yml" in md


def test_github_ready_writes_outputs(tmp_path):
    report = run_github_ready_check(ROOT)
    json_path = tmp_path / "github_ready.json"
    md_path = tmp_path / "GITHUB_READY.md"

    write_github_ready_report(report, json_path=json_path, markdown_path=md_path)

    data = json.loads(json_path.read_text(encoding="utf-8"))
    assert data["passed"] is True
    assert md_path.exists()


def test_github_ready_cli(monkeypatch, capsys, tmp_path):
    json_path = tmp_path / "github_ready.json"
    md_path = tmp_path / "GITHUB_READY.md"

    monkeypatch.setattr(
        "sys.argv",
        [
            "qkernel",
            "github-ready",
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
    json_text = stdout.split("\nwrote JSON GitHub-ready report:", 1)[0]
    data = json.loads(json_text)

    assert data["passed"] is True
    assert json_path.exists()
    assert md_path.exists()


def test_github_files_exist():
    required = [
        "CONTRIBUTING.md",
        "SECURITY.md",
        ".github/ISSUE_TEMPLATE/bug_report.md",
        ".github/ISSUE_TEMPLATE/math_correction.md",
        ".github/PULL_REQUEST_TEMPLATE.md",
        ".github/workflows/release-audit.yml",
    ]

    for rel in required:
        assert (ROOT / rel).exists()
