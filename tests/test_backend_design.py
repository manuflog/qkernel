"""v0.40 backend-aware experiment design tests."""
from math import isclose, sqrt

from qkernel.backend_design import (
    BackendModel,
    backend_aware_tests,
    context_visibility,
    estimate_significance,
    observable_visibility,
    pauli_support,
)
from qkernel.experiment_design import minimal_contextuality_tests

PAULIS = ["XI", "IX", "XX", "IY", "YI", "YY", "XY", "YX", "ZZ"]


def _pm_test():
    return minimal_contextuality_tests(PAULIS, top=1)[0]


def test_support_and_visibility():
    assert pauli_support("XI") == [0]
    assert pauli_support("IY") == [1]
    assert pauli_support("ZZ") == [0, 1]
    b = BackendModel(default_readout_error=0.05)
    assert isclose(observable_visibility("XI", b), 0.9)
    assert isclose(observable_visibility("ZZ", b), 0.81)
    # independent reads: context visibility is product over its observables
    assert isclose(context_visibility(["XI", "IX", "XX"], b), 0.9 * 0.9 * 0.81)


def test_perfect_readout_gives_full_margin():
    est = estimate_significance(_pm_test(), BackendModel(default_readout_error=0.0))
    assert est.n_contexts == 6 and est.nc_bound == 4 and est.quantum_value == 6
    assert isclose(est.expected_S, 6.0)
    assert isclose(est.margin, 2.0)
    assert est.certifiable and est.shots_total == 6  # zero variance: 1 shot/context


def test_uniform_eta_matches_ap1_closed_form():
    # Force uniform per-context visibility eta by the joint-basis model on
    # symmetric errors: eta = (1-2e)^2 per context (both qubits read once).
    e = 0.05
    b = BackendModel(default_readout_error=e, joint_basis=True)
    t = _pm_test()
    eta = (1 - 2 * e) ** 2
    est = estimate_significance(t, b, k_sigma=5.0)
    assert all(isclose(x, eta) for x in est.eta_per_context)
    # AP-1 closed form: total = n * k^2 * n(1-eta^2) / (n*eta - (n-2))^2
    n, k = 6, 5.0
    expected_total = n * (k * k * n * (1 - eta * eta) / (n * eta - (n - 2)) ** 2)
    assert abs(est.shots_total - expected_total) <= n  # ceil per total, off by < n


def test_threshold_behavior():
    t = _pm_test()
    # eta just above/below the 2/3 threshold via joint-basis symmetric error:
    # eta = (1-2e)^2 = 2/3  =>  e = (1 - sqrt(2/3)) / 2 ~ 0.0918
    e_star = (1 - sqrt(2 / 3)) / 2
    above = estimate_significance(t, BackendModel(default_readout_error=e_star - 0.01, joint_basis=True))
    below = estimate_significance(t, BackendModel(default_readout_error=e_star + 0.01, joint_basis=True))
    assert above.certifiable and above.shots_total is not None
    assert not below.certifiable and below.shots_total is None


def test_monotone_in_noise():
    t = _pm_test()
    prev = None
    for e in (0.0, 0.005, 0.01, 0.02):
        est = estimate_significance(t, BackendModel(default_readout_error=e))
        assert est.certifiable
        if prev is not None:
            assert est.shots_total >= prev  # worse readout never needs fewer shots
        prev = est.shots_total
    # with independent triple reads, 5% per-qubit error drops the context
    # visibility below the (n-2)/n threshold: correctly not certifiable
    est = estimate_significance(t, BackendModel(default_readout_error=0.05))
    assert not est.certifiable and est.shots_total is None


def test_backend_aware_ranking_prefers_good_qubits():
    # Two candidate tests exist over the PM Pauli set; make qubit 1 terrible and
    # confirm ranking is by shots (certifiable first, fewest shots first).
    b = BackendModel(readout_error={0: 0.005, 1: 0.09}, default_readout_error=0.02)
    ranked = backend_aware_tests(PAULIS, b, top=3, candidates=5)
    assert ranked, "no tests returned"
    shots = [r.estimate.shots_total for r in ranked if r.estimate.certifiable]
    assert shots == sorted(shots)
    for r in ranked:
        led = r.estimate.criterion_ledger
        assert led is not None and led["criterion_id"] == "odd_Q_even_d_v1"
        assert "planning estimate" in led["claim_scope"]


def test_bad_error_rejected():
    b = BackendModel(default_readout_error=0.6)
    try:
        observable_visibility("XI", b)
    except ValueError:
        pass
    else:
        raise AssertionError("readout error >= 0.5 must raise")
