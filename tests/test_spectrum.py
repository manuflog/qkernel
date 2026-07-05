"""Tests for the spectrum summary command (H(d) = {0, d/2} + 2-primary)."""
import pytest

from qkernel.valuation import spectrum_summary


def test_even_spectrum():
    for d in [2, 4, 6, 8, 16, 100]:
        s = spectrum_summary(d)
        assert s.is_even
        assert s.achievable_values == [0, d // 2]
        assert s.nonzero_value == d // 2
        assert s.value_order == 2          # d/2 always has order 2 in Z_d
        assert s.two_primary.is_two_primary


def test_odd_spectrum():
    for d in [3, 5, 9, 15]:
        s = spectrum_summary(d)
        assert not s.is_even
        assert s.achievable_values == [0]
        assert s.nonzero_value is None
        assert "odd d" in s.reason


def test_rejects_small_modulus():
    with pytest.raises(ValueError):
        spectrum_summary(1)


def test_matches_certificates():
    assert spectrum_summary(4).nonzero_value == 2   # cert4
    assert spectrum_summary(8).nonzero_value == 4   # cert8
