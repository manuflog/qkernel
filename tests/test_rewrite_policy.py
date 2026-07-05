import pytest
pytest.importorskip("qiskit")
import json

from qkernel.cli import main
from qkernel.rewrite_policy import (
    assess_rewrite_candidate,
    list_rewrite_policies,
)
from qkernel.adapters.qiskit_lite import load_qiskit_lite_program
from qkernel.compiler import compare_compiler_pass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_rewrite_policy_registry_contains_forbidden_claims():
    policies = {policy.id: policy for policy in list_rewrite_policies()}

    assert "safe_diagnostic_prune" in policies
    assert "forbidden_resource_claim" in policies
    assert policies["forbidden_resource_claim"].status == "forbidden"
    assert any("T-count" in claim for claim in policies["forbidden_resource_claim"].forbidden_claims)


def test_safe_diagnostic_prune_is_reportable_not_applicable():
    assessment = assess_rewrite_candidate("safe_diagnostic_prune")

    assert assessment.allowed_to_report
    assert not assessment.allowed_to_apply
    assert assessment.requires_semantic_equivalence_proof


def test_forbidden_resource_claim_not_reportable():
    assessment = assess_rewrite_candidate("forbidden_resource_claim")

    assert not assessment.allowed_to_report
    assert not assessment.allowed_to_apply
    assert assessment.status == "forbidden"


def test_cli_rewrite_policies(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["qkernel", "rewrite-policies"])

    main()
    data = json.loads(capsys.readouterr().out)

    assert any(policy["id"] == "safe_diagnostic_prune" for policy in data)
    assert any(policy["id"] == "forbidden_resource_claim" for policy in data)


def test_cli_assess_rewrite(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["qkernel", "assess-rewrite", "forbidden_resource_claim"])

    main()
    data = json.loads(capsys.readouterr().out)

    assert data["status"] == "forbidden"
    assert data["allowed_to_apply"] is False


def test_compare_pass_contains_policy_fields():
    before = load_qiskit_lite_program(ROOT / "examples/compiler_before_qiskit_lite.json")
    after = load_qiskit_lite_program(ROOT / "examples/compiler_after_qiskit_lite.json")

    comparison = compare_compiler_pass(before, after)

    assert comparison.rewrite_policy_id == "safe_diagnostic_prune"
    assert comparison.allowed_to_report is True
    assert comparison.allowed_to_apply is False
