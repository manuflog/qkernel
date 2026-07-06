import json
from pathlib import Path

from qkernel.magic import (
    analyze_magic_portfolio_file,
    analyze_magic_protocol,
    analyze_magic_protocol_record,
    generated_magic_report_dict,
    load_magic_protocol,
    magic_audit_report_dict,
    magic_portfolio_report_dict,
    magic_report_dict,
    magic_zoo_report_dict,
    generate_magic_candidates_from_paulis,
    run_magic_audit,
    run_magic_zoo,
)
from qkernel.pauli import pauli_program


ROOT = Path(__file__).resolve().parents[1]


def test_magic_protocol_schema_reports_contextual_candidate():
    proto = load_magic_protocol(ROOT / "examples/magic_protocol_pm_probe.json")
    report = analyze_magic_protocol_record(proto)

    assert report.contextual
    assert report.kernel_weight == 6
    assert report.verified
    assert report.zd_avn_contextual is True
    assert report.interest_score > 0.6
    assert "lower magic-state overhead" in report.not_claimed
    assert "no distillation map checked" in report.missing_evidence
    assert report.criterion_ledger["criterion_id"] == "odd_Q_even_d_v1"
    assert report.backend_estimate is not None
    json.dumps(magic_report_dict(report))


def test_magic_noncontextual_protocol_is_low_interest():
    program = pauli_program([["ZI", "IZ", "ZZ"]])
    report = analyze_magic_protocol(program, protocol_id="single_row")

    assert not report.contextual
    assert report.kernel_weight is None
    assert report.interest_score < 0.3
    assert any("no odd-Q contextuality" in item for item in report.missing_evidence)


def test_magic_portfolio_ranks_and_serializes():
    portfolio = analyze_magic_portfolio_file(ROOT / "examples/magic_portfolio.json")
    assert portfolio.entries
    assert portfolio.entries[0].rank == 1
    assert portfolio.entries[0].report.interest_score >= portfolio.entries[-1].report.interest_score
    json.dumps(magic_portfolio_report_dict(portfolio))


def test_magic_zoo_bridge_and_negative_controls():
    entries = run_magic_zoo()
    names = [entry.instance_name for entry in entries]
    assert "peres_mermin" in names
    assert "cert4_d4" in names
    assert all(entry.report.contextual for entry in entries)

    all_entries = run_magic_zoo(include_noncontextual=True)
    all_names = [entry.instance_name for entry in all_entries]
    assert "single_context" in all_names
    assert "odd_d_qutrit" in all_names
    json.dumps(magic_zoo_report_dict(all_entries))


def test_magic_generator_from_available_paulis():
    candidates = generate_magic_candidates_from_paulis(
        ["XI", "IX", "XX", "IY", "YI", "YY", "XY", "YX", "ZZ"],
        target="T",
        top=3,
    )
    assert candidates
    assert candidates[0].report.contextual
    assert candidates[0].report.kernel_weight == 6
    json.dumps(generated_magic_report_dict(candidates))


def test_magic_audit_passes():
    audit = run_magic_audit()
    assert audit.passed
    json.dumps(magic_audit_report_dict(audit))
