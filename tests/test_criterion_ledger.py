"""v0.39 semantic firewall: every user-facing result carries a criterion ledger."""
from qkernel.metadata import CRITERIA, criterion_ledger, QKERNEL_VERSION
from qkernel.examples import peres_mermin_program
from qkernel.subroutine import analyze_contextuality
from qkernel.experiment_design import minimal_contextuality_tests
from qkernel.embedding import activation_report


REQUIRED = {"criterion_id", "criterion", "verifier_used", "claim_scope",
            "stronger_verifier_available", "stronger_verifier_passed"}


def _check(ledger):
    assert ledger is not None
    assert REQUIRED <= set(ledger)
    assert ledger["criterion_id"] in CRITERIA


def test_registry_and_helper():
    assert {"odd_Q_even_d_v1", "zd_avn_valuation_v1"} <= set(CRITERIA)
    led = criterion_ledger(verifier_used="x", claim_scope="y")
    _check(led)
    try:
        criterion_ledger(criterion_id="nope", verifier_used="x", claim_scope="y")
    except ValueError:
        pass
    else:
        raise AssertionError("unknown criterion_id must raise")


def test_version_consistency():
    import pathlib
    try:
        import tomllib
    except ModuleNotFoundError:
        import tomli as tomllib

    py = tomllib.loads(pathlib.Path(__file__).resolve().parents[1].joinpath("pyproject.toml").read_text())
    assert py["project"]["version"] == QKERNEL_VERSION


def test_subroutine_carries_ledger():
    res = analyze_contextuality(peres_mermin_program())
    _check(res.criterion_ledger)
    # PM passes the stronger verifier: verify_kernel ran Z_d/AvN
    assert res.criterion_ledger["stronger_verifier_passed"] is True


def test_experiment_design_carries_ledger():
    paulis = ["XI", "IX", "XX", "IY", "YI", "YY", "XY", "YX", "ZZ"]
    tests = minimal_contextuality_tests(paulis, top=1)
    assert tests
    _check(tests[0].criterion_ledger)


def test_activation_report_carries_ledger():
    rep = activation_report(peres_mermin_program())
    _check(rep.criterion_ledger)
    assert rep.criterion_ledger["stronger_verifier_available"] == "zd_avn_valuation_v1"
