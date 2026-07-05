import pytest
pytest.importorskip("qiskit")
from pathlib import Path

from qkernel.adapters.qiskit_lite import load_qiskit_lite_program
from qkernel.certificate import kernel_to_dict
from qkernel.examples import peres_mermin_program
from qkernel.ir import KernelResult, WeylProgram
from qkernel.optimizer import compress_min_odd_q
from qkernel.valuation import (
    check_zd_valuation,
    check_kernel_zd_valuation,
    context_phase_vector,
    linear_system_solvable_mod_n,
    selected_subprogram,
)
from qkernel.verify import verify_kernel
from qkernel.io import dump_program, load_program


ROOT = Path(__file__).resolve().parents[1]


def test_linear_system_solvable_mod_composite():
    # 2x = 1 mod 4 is unsolvable.
    assert not linear_system_solvable_mod_n([[2]], [1], 4)
    # 2x = 2 mod 4 is solvable.
    assert linear_system_solvable_mod_n([[2]], [2], 4)


def test_peres_mermin_z2_valuation_contextual():
    program = peres_mermin_program()
    result = check_zd_valuation(program)

    assert result.contextual
    assert result.modulus == 2
    assert result.phases == [0, 0, 0, 0, 0, 1]


def test_zero_phase_pm_has_valuation_and_is_not_avn_contextual():
    base = peres_mermin_program()
    program = WeylProgram(
        d=base.d,
        m=base.m,
        observables=base.observables,
        contexts=base.contexts,
        context_phases=[0] * len(base.contexts),
    )

    result = check_zd_valuation(program)

    assert not result.contextual
    assert result.solvable is True


def test_kernel_verification_requires_zd_contextuality():
    base = peres_mermin_program()
    program = WeylProgram(
        d=base.d,
        m=base.m,
        observables=base.observables,
        contexts=base.contexts,
        context_phases=[0] * len(base.contexts),
    )
    kernel = KernelResult(
        contextual=True,
        original_contexts=6,
        original_observables=9,
        compressed_contexts=6,
        compressed_observables=9,
        selected_contexts=[0, 1, 2, 3, 4, 5],
        selected_observables=sorted(base.observables),
        q_value=1,
        compression_ratio_contexts=1.0,
        compression_ratio_observables=1.0,
    )

    verification = verify_kernel(program, kernel)

    assert not verification.valid
    assert verification.q_value == 1
    assert verification.zd_contextual is False
    assert "not Z_d-contextual" in verification.reason


def test_compressed_pm_kernel_is_zd_contextual_and_cert_records_it():
    program = peres_mermin_program()
    kernel = compress_min_odd_q(program)
    verification = verify_kernel(program, kernel)
    cert = kernel_to_dict(program, kernel)

    assert verification.valid
    assert verification.zd_contextual is True
    assert cert["verification"]["zd_contextual"] is True
    assert cert["kernel"]["context_phases"] == [0, 0, 0, 0, 0, 1]


def test_qiskit_lite_compiler_before_kernel_zd_verifies():
    program = load_qiskit_lite_program(ROOT / "examples/compiler_before_qiskit_lite.json")
    kernel = compress_min_odd_q(program)
    result = check_kernel_zd_valuation(program, kernel)

    assert result.contextual


def test_context_phases_roundtrip_affects_hash_input(tmp_path):
    base = peres_mermin_program()
    program = WeylProgram(
        d=base.d,
        m=base.m,
        observables=base.observables,
        contexts=base.contexts,
        context_phases=[0, 0, 0, 0, 0, 1],
    )

    path = tmp_path / "pm_phased.json"
    dump_program(program, path)
    loaded = load_program(path)

    assert loaded.context_phases == [0, 0, 0, 0, 0, 1]
    assert context_phase_vector(loaded) == [0, 0, 0, 0, 0, 1]
