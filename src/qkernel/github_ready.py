from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path


@dataclass(frozen=True)
class GitHubReadyCheck:
    path: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class GitHubReadyReport:
    passed: bool
    checks: list[GitHubReadyCheck]
    recommendation: str


REQUIRED_FILES = [
    "README.md",
    "ALPHA_README.md",
    "LICENSE",
    "CITATION.cff",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "CODE_OF_CONDUCT.md",
    "SUPPORT.md",
    "RELEASE_AUDIT.md",
    "docs/ALPHA_QUICKSTART.md",
    "docs/PUBLIC_REPO_STATUS.md",
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/ISSUE_TEMPLATE/bug_report.md",
    ".github/ISSUE_TEMPLATE/math_correction.md",
    ".github/ISSUE_TEMPLATE/feature_request.md",
    ".github/workflows/tests.yml",
    ".github/workflows/release-audit.yml",
    ".github/dependabot.yml",
]


def run_github_ready_check(root: str | Path) -> GitHubReadyReport:
    repo = Path(root)
    checks: list[GitHubReadyCheck] = []

    for rel in REQUIRED_FILES:
        path = repo / rel
        checks.append(
            GitHubReadyCheck(
                path=rel,
                passed=path.exists(),
                detail="present" if path.exists() else "missing",
            )
        )

    readme = repo / "README.md"
    if readme.exists():
        text = readme.read_text(encoding="utf-8")
        checks.append(
            GitHubReadyCheck(
                path="README.md:claim_boundaries",
                passed=("not a magic" in text or "not a T-count" in text or "Release audit" in text),
                detail="README contains public alpha/release-audit positioning",
            )
        )

    passed = all(check.passed for check in checks)

    return GitHubReadyReport(
        passed=passed,
        checks=checks,
        recommendation=(
            "GitHub alpha scaffolding is present; publish as alpha/public-review only."
            if passed
            else "Missing GitHub-ready files; do not publish yet."
        ),
    )


def github_ready_report_dict(report: GitHubReadyReport) -> dict:
    return {
        "passed": report.passed,
        "checks": [asdict(check) for check in report.checks],
        "recommendation": report.recommendation,
    }


def github_ready_report_markdown(report: GitHubReadyReport) -> str:
    lines = [
        "# GitHub Readiness Report",
        "",
        f"- passed: `{report.passed}`",
        f"- recommendation: {report.recommendation}",
        "",
        "## Checks",
        "",
    ]

    for check in report.checks:
        mark = "PASS" if check.passed else "FAIL"
        lines.append(f"- `{mark}` `{check.path}` — {check.detail}")

    return "\n".join(lines) + "\n"


def write_github_ready_report(
    report: GitHubReadyReport,
    *,
    json_path: str | Path | None = None,
    markdown_path: str | Path | None = None,
) -> None:
    if json_path is not None:
        Path(json_path).write_text(json.dumps(github_ready_report_dict(report), indent=2) + "\n", encoding="utf-8")

    if markdown_path is not None:
        Path(markdown_path).write_text(github_ready_report_markdown(report), encoding="utf-8")
