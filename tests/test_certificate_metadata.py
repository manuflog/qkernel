import json

from qkernel.certificate import inspect_certificate, kernel_to_dict, verify_certificate_file, write_certificate
from qkernel.examples import peres_mermin_program
from qkernel.metadata import COORDINATE_CONVENTION, CRITERION, INTEGER_CARRY_RULE, QKERNEL_VERSION
from qkernel.optimizer import compress_min_odd_q


def test_certificate_records_version_convention_and_criterion():
    program = peres_mermin_program()
    kernel = compress_min_odd_q(program)
    cert = kernel_to_dict(program, kernel)

    assert cert["software"]["qkernel_version"] == QKERNEL_VERSION
    assert cert["criterion"]["id"] == CRITERION["id"]
    assert cert["conventions"]["coordinate_convention"]["id"] == COORDINATE_CONVENTION["id"]
    assert cert["conventions"]["integer_carry_rule"]["id"] == INTEGER_CARRY_RULE["id"]


def test_inspect_certificate_metadata(tmp_path):
    program = peres_mermin_program()
    kernel = compress_min_odd_q(program)
    path = tmp_path / "cert.json"

    write_certificate(program, kernel, path)
    info = inspect_certificate(path)

    assert info["qkernel_version"] == QKERNEL_VERSION
    assert info["criterion"] == CRITERION["id"]
    assert info["coordinate_convention"] == COORDINATE_CONVENTION["id"]
    assert info["q_value"] == 1


def test_verify_rejects_wrong_criterion(tmp_path):
    program = peres_mermin_program()
    kernel = compress_min_odd_q(program)
    path = tmp_path / "cert.json"

    write_certificate(program, kernel, path)
    cert = json.loads(path.read_text())
    cert["criterion"]["id"] = "wrong_criterion"
    path.write_text(json.dumps(cert))

    result = verify_certificate_file(program, path)

    assert result["valid"] is False
    assert "unsupported criterion" in result["reason"]
