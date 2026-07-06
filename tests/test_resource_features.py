import json
import subprocess
import sys
from pathlib import Path

from qkernel.examples import peres_mermin_program
from qkernel.resource_features import resource_feature_report_dict
from qkernel.zoo import single_context_program


ROOT = Path(__file__).resolve().parents[1]


def test_resource_features_export_verified_pm_metrics():
    data = resource_feature_report_dict(peres_mermin_program(), enumerate_all_kernels=True)

    assert data["schema"] == "qkernel.resource_features.v1"
    assert data["contextual"] is True
    assert data["verified"] is True
    assert data["kernel_contexts"] == 6
    assert data["kernel_context_fraction"] == 1.0
    assert data["n_minimal_kernels"] == 1
    assert data["criterion_ledger"]["criterion_id"] == "odd_Q_even_d_v1"
    assert any("external resource oracle" in item for item in data["safe_use"])
    assert "kernel compression is a resource monotone" in data["unsafe_claims"]
    json.dumps(data)


def test_resource_features_noncontextual_has_no_kernel_claim():
    data = resource_feature_report_dict(single_context_program())

    assert data["contextual"] is False
    assert data["kernel_contexts"] is None
    assert data["kernel_observables"] is None
    assert data["obstruction_value"] == 0
    assert data["candidate_features"]["kernel_context_count"] is None


def test_cli_resource_features():
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "qkernel.cli",
            "resource-features",
            str(ROOT / "examples/peres_mermin_pauli.json"),
            "--input",
            "pauli",
            "--enumerate",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )

    data = json.loads(proc.stdout)
    assert data["contextual"] is True
    assert data["kernel_contexts"] == 6
    assert data["candidate_features"]["n_minimal_kernels"] == 1
