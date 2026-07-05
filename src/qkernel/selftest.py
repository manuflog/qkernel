from __future__ import annotations

from dataclasses import asdict, dataclass

from .certificate import kernel_to_dict
from .examples import peres_mermin_program
from .metadata import QKERNEL_VERSION
from .optimizer import compress_min_odd_q
from .verify import verify_kernel


@dataclass(frozen=True)
class SelfTestResult:
    version: str
    ok: bool
    contextual: bool
    selected_contexts: list[int]
    q_value: int | None
    verification_reason: str


def run_selftest() -> SelfTestResult:
    program = peres_mermin_program()
    kernel = compress_min_odd_q(program)
    verification = verify_kernel(program, kernel)

    return SelfTestResult(
        version=QKERNEL_VERSION,
        ok=verification.valid,
        contextual=kernel.contextual,
        selected_contexts=kernel.selected_contexts,
        q_value=verification.q_value,
        verification_reason=verification.reason,
    )


def run_selftest_dict() -> dict:
    return asdict(run_selftest())
