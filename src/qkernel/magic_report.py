"""MagicScout Markdown research-report generator.

The report layer turns JSON diagnostics into a research-note style artifact that
can be shared with collaborators without accidentally upgrading the claim. It
summarizes contextuality evidence, criterion-ledger scope, backend planning
estimates, template compatibility, missing factory evidence, and safe/forbidden
claim language.
"""
from __future__ import annotations

from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any


SAFE_CLAIM_LANGUAGE = [
    "This is a contextuality-resource diagnostic.",
    "The report identifies candidate motifs worth studying in magic-state-adjacent workflows.",
    "Backend numbers are planning estimates under an explicit readout-noise model.",
    "Template compatibility means checklist compatibility, not factory validity.",
]

FORBIDDEN_CLAIM_LANGUAGE = [
    "This protocol lowers magic-state overhead.",
    "This is a valid magic-state distillation protocol.",
    "This improves a threshold.",
    "This bounds output fidelity.",
    "This proves a factory space-time advantage.",
    "This proves compiler semantic equivalence.",
]


def _plain(obj: Any) -> Any:
    if is_dataclass(obj):
        return asdict(obj)
    return obj


def _fmt_bool(value: Any) -> str:
    if value is True:
        return "yes"
    if value is False:
        return "no"
    if value is None:
        return "not run / not applicable"
    return str(value)


def _fmt_float(value: Any, digits: int = 3) -> str:
    if value is None:
        return "—"
    try:
        return f"{float(value):.{digits}f}"
    except (TypeError, ValueError):
        return str(value)


def _list_block(items: list[Any] | None, *, empty: str = "—") -> str:
    if not items:
        return empty
    return "\n".join(f"- {item}" for item in items)


def _table(headers: list[str], rows: list[list[Any]]) -> str:
    if not rows:
        return ""
    head = "| " + " | ".join(headers) + " |"
    sep = "| " + " | ".join("---" for _ in headers) + " |"
    body = ["| " + " | ".join(str(cell) for cell in row) + " |" for row in rows]
    return "\n".join([head, sep, *body])


def _ledger_table(ledger: dict[str, Any] | None) -> str:
    if not ledger:
        return "No criterion ledger attached."
    rows = [
        ["criterion_id", ledger.get("criterion_id", "—")],
        ["verifier_used", ledger.get("verifier_used", "—")],
        ["claim_scope", ledger.get("claim_scope", "—")],
        ["stronger_verifier_available", ledger.get("stronger_verifier_available", "—")],
        ["stronger_verifier_passed", _fmt_bool(ledger.get("stronger_verifier_passed"))],
    ]
    return _table(["field", "value"], rows)


def _backend_table(backend: dict[str, Any] | None) -> str:
    if not backend:
        return "No backend estimate attached."
    rows = [
        ["available", _fmt_bool(backend.get("backend_available"))],
        ["reason", backend.get("reason", "—")],
        ["expected_S", _fmt_float(backend.get("expected_S"))],
        ["noncontextual_bound", backend.get("nc_bound", "—")],
        ["margin", _fmt_float(backend.get("margin"))],
        ["certifiable", _fmt_bool(backend.get("certifiable"))],
        ["shots_total", backend.get("shots_total", "—")],
        ["k_sigma", backend.get("k_sigma", "—")],
    ]
    return _table(["field", "value"], rows)


def _template_table(assessments: list[dict[str, Any]] | None) -> str:
    if not assessments:
        return "No template assessments attached."
    rows = []
    for a in assessments:
        rows.append([
            a.get("template_id", "—"),
            a.get("template_name", "—"),
            _fmt_bool(a.get("compatible")),
            _fmt_float(a.get("template_score")),
            len(a.get("missing_evidence", []) or []),
        ])
    return _table(["template", "name", "compatible", "score", "missing items"], rows)


def magic_report_markdown(report: Any, *, title: str | None = None) -> str:
    """Render a single MagicScout report as Markdown."""
    r = _plain(report)
    title = title or f"MagicScout Report — {r.get('protocol_id', 'candidate')}"
    backend = r.get("backend_estimate")
    if backend is not None and not isinstance(backend, dict):
        backend = _plain(backend)

    lines = [
        f"# {title}",
        "",
        "## Executive summary",
        "",
        _table(["field", "value"], [
            ["protocol_id", r.get("protocol_id", "—")],
            ["target", r.get("target", "—")],
            ["role", r.get("role", "—")],
            ["contextual", _fmt_bool(r.get("contextual"))],
            ["verified", _fmt_bool(r.get("verified"))],
            ["Z_d / AvN contextual", _fmt_bool(r.get("zd_avn_contextual"))],
            ["kernel weight", r.get("kernel_weight", "—")],
            ["minimal kernels", r.get("n_minimal_kernels", "—")],
            ["obstruction value", r.get("obstruction_value", "—")],
            ["interest score", _fmt_float(r.get("interest_score"))],
        ]),
        "",
        "## Positive signals",
        "",
        _list_block(r.get("positive_signals")),
        "",
        "## Missing evidence",
        "",
        _list_block(r.get("missing_evidence")),
        "",
        "## Criterion ledger",
        "",
        _ledger_table(r.get("criterion_ledger")),
        "",
        "## Backend planning estimate",
        "",
        _backend_table(backend),
        "",
        "## Template compatibility",
        "",
        _template_table(r.get("template_assessments")),
        "",
        "## Safe claim language",
        "",
        _list_block(SAFE_CLAIM_LANGUAGE),
        "",
        "## Forbidden claim language",
        "",
        _list_block(sorted(set(FORBIDDEN_CLAIM_LANGUAGE + list(r.get("not_claimed", []) or [])))),
        "",
        "## Next experiments",
        "",
        _list_block(_next_experiments(r)),
        "",
    ]
    return "\n".join(lines)


def _next_experiments(r: dict[str, Any]) -> list[str]:
    steps = []
    if not r.get("contextual"):
        steps.append("Search a richer Pauli/context set; this candidate is non-contextual under the current criterion.")
    if r.get("zd_avn_contextual") is not True:
        steps.append("Either obtain a Z_d/AvN-passing kernel or keep the claim explicitly odd-Q-only.")
    backend = r.get("backend_estimate") or {}
    if not backend or backend.get("certifiable") is not True:
        steps.append("Run backend-aware design with realistic readout errors and find a certifiable witness.")
    missing = "\n".join(r.get("missing_evidence", []) or [])
    if "acceptance probability" in missing:
        steps.append("Attach an explicit factory/check schedule with acceptance probability before any distillation comparison.")
    if "output infidelity" in missing:
        steps.append("Attach or derive an output-error model before any magic-state quality claim.")
    if not steps:
        steps.append("Promote to a controlled hardware or factory-template study; do not upgrade to overhead claims without external factory metrics.")
    return steps


def magic_portfolio_markdown(portfolio: Any, *, title: str | None = None) -> str:
    """Render a MagicPortfolioReport as Markdown."""
    p = _plain(portfolio)
    title = title or f"MagicScout Portfolio — {p.get('portfolio_id', 'portfolio')}"
    entries = p.get("entries", []) or []
    rows = []
    for entry in entries:
        report = entry.get("report", {})
        rows.append([
            entry.get("rank", "—"),
            entry.get("protocol_id", report.get("protocol_id", "—")),
            report.get("target", "—"),
            _fmt_bool(report.get("contextual")),
            _fmt_bool(report.get("zd_avn_contextual")),
            report.get("kernel_weight", "—"),
            _fmt_float(report.get("interest_score")),
        ])
    lines = [
        f"# {title}",
        "",
        "## Ranking",
        "",
        p.get("ranking_rule", "—"),
        "",
        _table(["rank", "protocol", "target", "contextual", "Z_d/AvN", "kernel", "score"], rows),
        "",
        "## Non-claims",
        "",
        _list_block(p.get("not_claimed")),
        "",
    ]
    for entry in entries:
        lines.append(magic_report_markdown(entry.get("report", {}), title=f"Candidate {entry.get('rank')}: {entry.get('protocol_id')}"))
    return "\n".join(lines)


def magic_search_markdown(search_report: Any, *, title: str | None = None) -> str:
    """Render a MagicSearchReport as Markdown."""
    s = _plain(search_report)
    title = title or f"MagicScout Search — {s.get('search_id', 'search')}"
    rows = []
    for c in s.get("results", []) or []:
        report = c.get("report", {})
        be = report.get("backend_estimate") or {}
        rows.append([
            c.get("rank", "—"),
            c.get("protocol", {}).get("protocol_id", report.get("protocol_id", "—")),
            _fmt_float(c.get("ranking_score")),
            _fmt_float(report.get("interest_score")),
            report.get("kernel_weight", "—"),
            _fmt_bool(report.get("zd_avn_contextual")),
            _fmt_bool(be.get("certifiable")),
            be.get("shots_total", "—"),
            ", ".join(c.get("template_compatible_ids", []) or []),
        ])
    lines = [
        f"# {title}",
        "",
        "## Search summary",
        "",
        _table(["field", "value"], [
            ["target", s.get("target", "—")],
            ["available Paulis", ", ".join(s.get("available_paulis", []) or [])],
            ["candidates considered", s.get("candidates_considered", "—")],
            ["candidates returned", s.get("candidates_returned", "—")],
            ["required templates", ", ".join(s.get("required_templates", []) or []) or "—"],
            ["ranking rule", s.get("ranking_rule", "—")],
        ]),
        "",
        "## Candidate ranking",
        "",
        _table([
            "rank", "protocol", "ranking", "interest", "kernel", "Z_d/AvN", "backend certifiable", "shots", "templates"
        ], rows),
        "",
        "## Criterion ledger",
        "",
        _ledger_table(s.get("criterion_ledger")),
        "",
        "## Non-claims",
        "",
        _list_block(s.get("not_claimed")),
        "",
        "## Candidate details",
        "",
    ]
    for c in s.get("results", []) or []:
        proto_id = c.get("protocol", {}).get("protocol_id", "candidate")
        lines.append(f"### {c.get('rank', '?')}. {proto_id}")
        lines.append("")
        lines.append("**Ranking explanation**")
        lines.append("")
        lines.append(_list_block(c.get("ranking_explanation")))
        lines.append("")
        lines.append(magic_report_markdown(c.get("report", {}), title=f"Report: {proto_id}"))
        lines.append("")
    return "\n".join(lines)


def write_markdown_report(markdown: str, path: str | Path) -> None:
    Path(path).write_text(markdown, encoding="utf-8")
