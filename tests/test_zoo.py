"""v0.41 benchmark zoo: every registered instance must match its expected verdict."""
import pytest
from qkernel.zoo import ZOO, run_instance, run_zoo


@pytest.mark.parametrize("inst", ZOO, ids=[i.name for i in ZOO])
def test_zoo_instance(inst):
    r = run_instance(inst)
    assert r.passed, f"{inst.name}: {r.failures}"


def test_zoo_all_green():
    results = run_zoo()
    assert all(r.passed for r in results), [(r.name, r.failures) for r in results if not r.passed]
    assert len(results) == len(ZOO) >= 6
