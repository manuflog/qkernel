from qkernel.magic_report import magic_report_markdown, magic_search_markdown


def test_single_magic_report_markdown_contains_scope_sections():
    report = {
        "protocol_id": "toy",
        "target": "T",
        "role": "candidate",
        "contextual": True,
        "verified": True,
        "zd_avn_contextual": True,
        "kernel_weight": 6,
        "n_minimal_kernels": 1,
        "obstruction_value": 1,
        "interest_score": 0.8,
        "positive_signals": ["small contextual core"],
        "missing_evidence": ["no output infidelity model checked"],
        "not_claimed": ["lower magic-state overhead"],
        "criterion_ledger": {
            "criterion_id": "odd_Q_even_d_v1",
            "verifier_used": "test",
            "claim_scope": "diagnostic only",
            "stronger_verifier_available": "zd_avn_valuation_v1",
            "stronger_verifier_passed": True,
        },
        "backend_estimate": {
            "backend_available": True,
            "reason": "computed",
            "expected_S": 5.5,
            "nc_bound": 4,
            "margin": 1.5,
            "certifiable": True,
            "shots_total": 1200,
            "k_sigma": 5.0,
        },
        "template_assessments": [
            {"template_id": "contextuality_witness", "template_name": "Witness", "compatible": True, "template_score": 0.8, "missing_evidence": []}
        ],
    }
    md = magic_report_markdown(report)
    assert "# MagicScout Report" in md
    assert "## Criterion ledger" in md
    assert "## Forbidden claim language" in md
    assert "lower magic-state overhead" in md
    assert "output-error model" in md or "output infidelity" in md


def test_magic_search_markdown_contains_ranking_table():
    search = {
        "search_id": "s",
        "target": "T",
        "available_paulis": ["XI", "IX", "XX"],
        "candidates_considered": 1,
        "candidates_returned": 1,
        "required_templates": [],
        "ranking_rule": "score desc",
        "not_claimed": ["threshold improvement"],
        "criterion_ledger": {"criterion_id": "odd_Q_even_d_v1"},
        "results": [
            {
                "rank": 1,
                "protocol": {"protocol_id": "c1"},
                "ranking_score": 0.9,
                "ranking_explanation": ["good"],
                "template_compatible_ids": ["contextuality_witness"],
                "report": {
                    "protocol_id": "c1",
                    "target": "T",
                    "role": "candidate",
                    "contextual": True,
                    "verified": True,
                    "zd_avn_contextual": True,
                    "kernel_weight": 6,
                    "n_minimal_kernels": 1,
                    "obstruction_value": 1,
                    "interest_score": 0.8,
                    "positive_signals": [],
                    "missing_evidence": [],
                    "not_claimed": [],
                    "backend_estimate": {"certifiable": True, "shots_total": 1000},
                    "template_assessments": [],
                },
            }
        ],
    }
    md = magic_search_markdown(search)
    assert "## Candidate ranking" in md
    assert "contextuality_witness" in md
    assert "score desc" in md
