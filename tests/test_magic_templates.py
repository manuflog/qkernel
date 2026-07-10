import json
from pathlib import Path

from qkernel.magic import analyze_magic_protocol_record, load_magic_protocol, magic_report_dict
from qkernel.magic_templates import (
    assess_magic_templates,
    magic_template_assessments_dict,
    magic_templates_catalog_dict,
)

ROOT = Path(__file__).resolve().parents[1]


def test_magic_templates_catalog_is_serializable_and_conservative():
    catalog = magic_templates_catalog_dict()
    assert catalog["count"] >= 5
    assert "template compatibility" in catalog["claim_scope"]
    assert any(t["template_id"] == "distillation_check_motif" for t in catalog["templates"])
    json.dumps(catalog)


def test_pm_probe_matches_witness_and_verification_templates():
    proto = load_magic_protocol(ROOT / "examples/magic_protocol_pm_probe.json")
    report = analyze_magic_protocol_record(proto)
    assessments = assess_magic_templates(report)
    by_id = {a.template_id: a for a in assessments}

    assert by_id["contextuality_witness"].compatible
    assert by_id["magic_verification_subroutine"].compatible
    assert not by_id["distillation_check_motif"].compatible
    assert any("missing factory metadata" in item for item in by_id["distillation_check_motif"].missing_evidence)
    assert "valid magic-state factory" in by_id["contextuality_witness"].not_claimed
    json.dumps(magic_template_assessments_dict(assessments))


def test_distillation_stub_still_blocks_missing_acceptance_probability():
    proto = load_magic_protocol(ROOT / "examples/magic_protocol_distillation_stub.json")
    report = analyze_magic_protocol_record(proto)
    data = magic_report_dict(report)
    assert data["contextual"] is True

    assessments = assess_magic_templates(report, template_ids=["distillation_check_motif"])
    assessment = assessments[0]
    assert not assessment.compatible
    assert any("acceptance_probability" in item for item in assessment.missing_evidence)
    assert "lower magic-state overhead" in assessment.not_claimed
