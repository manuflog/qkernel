"""Tests for the experiment-design layer (device Paulis -> cheapest contextuality test)."""
from qkernel.experiment_design import minimal_contextuality_tests

PM9 = ["XI", "IX", "XX", "IY", "YI", "YY", "XY", "YX", "ZZ"]
ALL15 = ["XI", "YI", "ZI", "IX", "IY", "IZ", "XX", "XY", "XZ",
         "YX", "YY", "YZ", "ZX", "ZY", "ZZ"]


def test_pm_paulis_give_single_six_setting_test():
    tests = minimal_contextuality_tests(PM9)
    assert len(tests) == 1
    t = tests[0]
    assert t.n_contexts == 6 and t.verified is True
    assert t.obstruction_value == 1
    # every context is a commuting triple of measurable Paulis
    for ctx in t.contexts:
        assert len(ctx) == 3 and all(p in PM9 for p in ctx)


def test_full_two_qubit_paulis_give_ten_tests():
    tests = minimal_contextuality_tests(ALL15, top=100)
    assert len(tests) == 10  # the ten Mermin squares of the doily
    assert all(t.n_contexts == 6 for t in tests)


def test_noncontextual_measurable_set_gives_no_test():
    assert minimal_contextuality_tests(["XI", "IX", "XX"]) == []


def test_ranking_prefers_fewer_settings_then_fewer_observables():
    tests = minimal_contextuality_tests(ALL15, top=100)
    keys = [(t.n_contexts, t.n_observables) for t in tests]
    assert keys == sorted(keys)
