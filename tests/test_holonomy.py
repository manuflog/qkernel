import numpy as np
from qkernel.holonomy import (mub_loop_bases, bargmann_invariant, strand_phases,
                              det_section_holonomy, hadamard_test_plan)

def test_strand_phases_are_pm_quarter_pi():
    p0, p1, loop = strand_phases()
    assert abs(p0 - np.pi / 4) < 1e-12 and abs(p1 + np.pi / 4) < 1e-12
    assert abs(loop - 1) < 1e-12

def test_gauge_invariance():
    rng = np.random.default_rng(3)
    B = mub_loop_bases()
    for _ in range(50):
        Bg = [V @ np.diag(np.exp(1j * rng.uniform(0, 2 * np.pi, 2))) for V in B]
        p0, p1, loop = strand_phases(Bg)
        assert abs(loop - 1) < 1e-9 and abs(abs(p0) - np.pi / 4) < 1e-9

def test_det_section_is_minus_i():
    H = np.array([[1, 1], [1, -1]]) / np.sqrt(2); S = np.diag([1, 1j])
    Vy = S @ H
    W = Vy.conj().T / np.linalg.det(Vy.conj().T) ** 0.5
    assert abs(det_section_holonomy([H, S], W) + 1j) < 1e-12

def test_plan_reconstructs_strands():
    plan = hadamard_test_plan()
    acc = {0: 1 + 0j, 1: 1 + 0j}
    for k in (0, 1):
        for step in range(3):
            e = np.eye(2)[:, k]
            U = next(p for p in plan if p["strand"] == k and p["step"] == step
                     and p["part"] == "re")["unitary"]
            acc[k] *= np.vdot(e, U @ e)
    assert abs(np.angle(acc[0]) - np.pi / 4) < 1e-12
    assert abs(np.angle(acc[1]) + np.pi / 4) < 1e-12
