import json

from qkernel.magic_search import (
    magic_search_report_dict,
    search_magic_candidates_from_paulis,
    search_two_qubit_magic_candidates,
)


SMALL_PM_PAULIS = ["XI", "IX", "XX", "IY", "YI", "YY", "XY", "YX", "ZZ"]


def test_magic_search_finds_contextual_candidates_from_available_paulis():
    report = search_magic_candidates_from_paulis(SMALL_PM_PAULIS, target="T", top=3, candidates=10)

    assert report.candidates_returned >= 1
    assert report.results[0].report.contextual
    assert report.results[0].ranking_score > 0.5
    assert "magic-state factory synthesis" in report.not_claimed
    assert report.criterion_ledger["criterion_id"] == "odd_Q_even_d_v1"


def test_magic_search_required_template_changes_ranking_explanation():
    report = search_magic_candidates_from_paulis(
        SMALL_PM_PAULIS,
        target="T",
        top=3,
        candidates=10,
        required_templates=["contextuality_witness"],
    )

    assert report.results
    assert report.required_templates == ["contextuality_witness"]
    assert any("required templates" in s for s in report.results[0].ranking_explanation)


def test_magic_search_json_serializable():
    report = search_magic_candidates_from_paulis(SMALL_PM_PAULIS, top=1)
    data = magic_search_report_dict(report)

    assert data["candidates_returned"] == 1
    json.dumps(data)


def test_two_qubit_magic_search_standard_demo():
    report = search_two_qubit_magic_candidates(top=5)

    assert report.search_id == "two_qubit_pauli_search"
    assert report.candidates_returned >= 1
    assert all(candidate.report.contextual for candidate in report.results)
