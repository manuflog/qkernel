from qkernel.examples import peres_mermin_program
from qkernel.optimizer import compress_min_odd_q
from qkernel.verify import verify_kernel


def test_verify_valid_pm_kernel():
    program = peres_mermin_program()
    kernel = compress_min_odd_q(program)

    verification = verify_kernel(program, kernel)

    assert verification.valid
    assert verification.q_value == 1
    assert verification.lambda_vector == [1, 1, 1, 1, 1, 1]
