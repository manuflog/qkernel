"""Cross-validate qkernel against real Stim (v1.16+) as an independent oracle.

Skipped if Stim is absent. Uses Stim's own PauliString algebra to confirm that
(1) Stim parses the .stim examples qkernel accepts, and (2) every qkernel context
is pairwise-commuting and multiplies to +/-I -- an authoritative external check on
qkernel's Pauli handling.
"""
from pathlib import Path
import pytest

stim = pytest.importorskip("stim")

from qkernel.adapters.stim_lite import load_stim_lite_program
from qkernel.analyzer import analyze

EX = Path(__file__).resolve().parents[1] / "examples"


def _to_stim(vec, m):
    s = ""
    for i in range(m):
        s += {"00": "_", "10": "Z", "01": "X", "11": "Y"}[f"{vec[2*i]}{vec[2*i+1]}"]
    return stim.PauliString(s)


def test_stim_parses_qkernel_mpp_example():
    circ = stim.Circuit.from_file(str(EX / "peres_mermin_mpp.stim"))
    products = [g for inst in circ if inst.name == "MPP" for g in inst.target_groups()]
    assert len(products) == 18  # 6 contexts x 3 Pauli products


def test_stim_confirms_context_validity():
    prog = load_stim_lite_program(str(EX / "peres_mermin_mpp.stim"))
    assert analyze(prog).contextual is True
    for ctx in prog.contexts:
        ps = [_to_stim(prog.observables[n], prog.m) for n in ctx]
        for i in range(len(ps)):
            for j in range(i + 1, len(ps)):
                assert ps[i].commutes(ps[j])  # Stim confirms commuting
        acc = stim.PauliString(prog.m)
        for p in ps:
            acc = acc * p
        assert acc.weight == 0  # product is +/-I per Stim
