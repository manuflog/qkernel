from pathlib import Path

from qkernel.certificate import kernel_to_dict, verify_certificate_file, write_certificate
from qkernel.examples import peres_mermin_program
from qkernel.hashing import program_sha256
from qkernel.optimizer import compress_min_odd_q


def test_certificate_contains_stable_program_hash():
    program = peres_mermin_program()
    kernel = compress_min_odd_q(program)

    cert = kernel_to_dict(program, kernel)

    assert cert["schema"] == "qkernel.certificate.v1"
    assert cert["program_sha256"] == program_sha256(program)
    assert cert["kernel"]["lambda"] == [1, 1, 1, 1, 1, 1]
    assert cert["verification"]["valid"] is True


def test_certificate_round_trip_verifies(tmp_path):
    program = peres_mermin_program()
    kernel = compress_min_odd_q(program)

    path = tmp_path / "pm_certificate.json"
    write_certificate(program, kernel, path)

    result = verify_certificate_file(program, path)

    assert result["valid"] is True
    assert result["q_value"] == 1


def test_certificate_rejects_wrong_program_hash(tmp_path):
    program = peres_mermin_program()
    kernel = compress_min_odd_q(program)

    path = tmp_path / "pm_certificate.json"
    write_certificate(program, kernel, path)

    # Remove one context to change the hash.
    mutated = type(program)(
        d=program.d,
        m=program.m,
        observables=program.observables,
        contexts=program.contexts[:-1],
    )

    result = verify_certificate_file(mutated, path)

    assert result["valid"] is False
    assert "program_sha256 mismatch" in result["reason"]
