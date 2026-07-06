"""v0.42 hardware result registry tests."""
import json
from math import isclose, sqrt

import pytest
from qkernel.hardware_registry import (
    ContextMeasurement,
    append_record,
    compute_verdict,
    load_registry,
    new_record,
    prediction_gap,
    validate_record,
)

PM_CONTEXTS = [["XI","IX","XX"],["IY","YI","YY"],["XY","YX","ZZ"],
               ["XI","IY","XY"],["IX","YI","YX"],["XX","YY","ZZ"]]
PM_SIGNS = [1, 1, 1, 1, 1, -1]


def _counts_for_visibility(eta: float, shots: int = 1000):
    """Synthetic counts: signed correlator eta per context (product statistic
    aligned with the constraint sign, so eps_c * E_c = eta)."""
    out = []
    for s in PM_SIGNS:
        e = s * eta  # measured correlator has the constraint's sign
        plus = round(shots * (1 + e) / 2)
        out.append(ContextMeasurement(plus=plus, minus=shots - plus))
    return out


def test_correlator_and_stderr():
    c = ContextMeasurement(plus=900, minus=100)
    assert isclose(c.correlator, 0.8)
    assert isclose(c.stderr, sqrt((1 - 0.64) / 1000))


def test_verdict_matches_hand_computation():
    eta, shots = 0.9, 1000
    v = compute_verdict(_counts_for_visibility(eta, shots), PM_SIGNS)
    assert v.n_contexts == 6 and v.nc_bound == 4
    assert isclose(v.S, 6 * eta, abs_tol=0.01)
    sigma = sqrt(6 * (1 - eta * eta) / shots)
    assert isclose(v.sigma_S, sigma, rel_tol=0.05)
    assert v.z > 5 and v.certified


def test_below_bound_not_certified():
    v = compute_verdict(_counts_for_visibility(0.6, 2000), PM_SIGNS)  # S=3.6 < 4
    assert v.S < v.nc_bound and v.z < 0 and not v.certified


def test_record_roundtrip(tmp_path):
    rec = new_record(
        record_id="pm-demo-001",
        device={"name": "synthetic", "note": "unit test"},
        contexts=PM_CONTEXTS,
        signs=PM_SIGNS,
        counts=_counts_for_visibility(0.85, 500),
        prediction={"expected_S": 6 * 0.85, "shots_total": 3000, "k_sigma": 5.0},
    )
    validate_record(rec)  # already validated in new_record; idempotent
    path = tmp_path / "registry.jsonl"
    append_record(str(path), rec)
    append_record(str(path), rec)
    loaded = load_registry(str(path))
    assert len(loaded) == 2
    assert loaded[0]["verdict"]["certified"] is True
    gap = prediction_gap(loaded[0])
    assert gap is not None and abs(gap) < 0.05
    # ledger present with correct claim scope discipline
    led = loaded[0]["criterion_ledger"]
    assert led["criterion_id"] == "odd_Q_even_d_v1"
    assert "measured" in led["claim_scope"]


def test_schema_rejects_malformed():
    rec = new_record(
        record_id="x", device={"name": "d"}, contexts=PM_CONTEXTS, signs=PM_SIGNS,
        counts=_counts_for_visibility(0.9, 100),
    )
    bad = json.loads(json.dumps(rec))
    del bad["verdict"]["z"]
    with pytest.raises(ValueError):
        validate_record(bad)
    bad2 = json.loads(json.dumps(rec))
    bad2["measurement"]["counts"] = bad2["measurement"]["counts"][:-1]
    with pytest.raises(ValueError):
        validate_record(bad2)
    with pytest.raises(ValueError):
        compute_verdict(_counts_for_visibility(0.9, 100), [1, 1, 1, 1, 1, 2])
