from pathlib import Path

from qkernel.io import load_program
from qkernel.tower import (
    FiberObservable,
    direct_m_ab,
    split_fiber_vector,
    tower_generativity_bit_from_fibers,
    tower_law_report,
)
from qkernel.cli import main


ROOT = Path(__file__).resolve().parents[1]


def test_split_fiber_vector_d4_to_d2():
    u, x = split_fiber_vector((3, 0, 1, 2), base_d=2, lifted_d=4)

    assert u == (1, 0, 1, 0)
    assert x == (1, 0, 0, 1)


def test_direct_m_ab_formula():
    a = FiberObservable("a", (1, 0), (1, 0), (0, 0))
    b = FiberObservable("b", (0, 3), (0, 1), (0, 1))

    assert direct_m_ab(a, b) == -1


def test_tower_generativity_floor_correction_manual():
    # Construct pair terms M values [1, 1, 0], so sum=2, K=2.
    # G = floor(2/2) XOR floor(2/2) = 1 XOR 1 = 0.
    a = FiberObservable("a", (0, 0), (1, 0), (0, 0))
    b = FiberObservable("b", (0, 0), (0, 0), (0, 1))
    c = FiberObservable("c", (0, 0), (0, 0), (0, 1))

    g, sum_m, k, floor_sum, floor_k = tower_generativity_bit_from_fibers([a, b, c])

    assert sum_m == -2
    assert k == 2
    assert g == 0


def test_trivial_d4_lift_is_certified_nongenerative():
    program = load_program(ROOT / "examples/tower_pair_d4_nongenerative.json")
    lam = [1, 1]

    report = tower_law_report(program, lam, base_d=2)

    assert report.certified
    assert report.status == "certified_nongenerative"
    assert report.generativity_bit == 0
    assert report.non_generative is True
    assert report.sum_m == 0
    assert report.odd_m_count == 0
    assert report.repeated_observables["A"] == 2


def test_tower_law_cli(monkeypatch, capsys):
    monkeypatch.setattr(
        "sys.argv",
        [
            "qkernel",
            "tower-scope",
            str(ROOT / "examples/tower_pair_d4_nongenerative.json"),
            "--input",
            "weyl",
            "--contexts",
            "0,1",
            "--base-d",
            "2",
        ],
    )

    main()
    out = capsys.readouterr().out

    assert '"certified": true' in out
    assert '"generativity_bit": 0' in out
    assert '"non_generative": true' in out
