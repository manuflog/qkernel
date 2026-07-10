"""Tests for the 2-primary obstruction-value corollary.

Corollary (from the Obstruction Spectrum Theorem H(d)={0,d/2} for even d):
the achievable value d/2 is always 2-primary (zero in the odd CRT factor), so
the mod-2 carry shadow is value-faithful at every even d, not just 2-powers.
"""
from qkernel.valuation import two_primary_report


def test_two_primary_for_all_even_d_up_to_200():
    for d in range(2, 201, 2):
        r = two_primary_report(d)
        assert r.is_two_primary, f"d={d} value {r.value_dover2} not 2-primary"
        assert r.value_odd_component == 0
        assert r.shadow_value_faithful


def test_two_primary_reports_two_adic_valuation():
    r = two_primary_report(8)   # 8 = 2^3
    assert r.two_adic_valuation == 3
    assert r.odd_part == 1
    assert r.value_dover2 == 4

    r = two_primary_report(12)  # 12 = 2^2 * 3
    assert r.two_adic_valuation == 2
    assert r.odd_part == 3
    assert r.value_dover2 == 6
    assert r.value_odd_component == 0  # 6 mod 3 == 0


def test_odd_d_is_trivially_value_faithful():
    r = two_primary_report(3)
    assert r.is_two_primary
    assert r.shadow_value_faithful
    assert "odd d" in r.reason


def test_two_primary_matches_certificates():
    # cert4 (d=4) -> value 2; cert8 (d=8) -> value 4; both 2-primary
    assert two_primary_report(4).value_dover2 == 2
    assert two_primary_report(8).value_dover2 == 4
    assert two_primary_report(4).is_two_primary
    assert two_primary_report(8).is_two_primary
