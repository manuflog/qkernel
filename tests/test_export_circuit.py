"""Tests for the export-circuit bridge (kernel -> runnable Qiskit protocol).

The emitted protocol uses SEQUENTIAL non-destructive measurement so that the
statistic is genuinely data-dependent.  A regression test guards against ever
re-introducing the algebraically-pinned single-joint-measurement (which returns
the ideal value on any data and certifies nothing).
"""
import pytest

from qkernel.examples import peres_mermin_program
from qkernel.export_circuit import export_qiskit_protocol, vector_to_pauli_label


def test_vector_to_pauli_label_interleaved():
    assert vector_to_pauli_label((1, 0, 0, 0), 2) == "ZI"
    assert vector_to_pauli_label((0, 1, 0, 0), 2) == "XI"
    assert vector_to_pauli_label((1, 1, 1, 1), 2) == "YY"
    assert vector_to_pauli_label((0, 0, 1, 0), 2) == "IZ"


def test_export_pm_all_contexts_verified():
    p = peres_mermin_program()
    proto = export_qiskit_protocol(p, verify=True)
    assert proto.n_contexts == 6
    # exactly one context carries the -1 sign (the obstruction)
    assert proto.context_signs.count(-1) == 1
    for labels in proto.context_labels:
        assert len(labels) == 3
    # script is self-contained runnable text using the sequential protocol
    assert "QiskitRuntimeService" in proto.script
    assert "product_expectation" in proto.script
    assert "_measure_obs" in proto.script  # ancilla Hadamard-test measurement


def test_emitted_statistic_is_data_dependent_not_pinned():
    """REGRESSION GUARD: the emitted product_expectation must depend on its input.
    The old (buggy) joint-measurement statistic returned the context sign on ANY
    counts.  Here, feeding two different count distributions must give two
    different values for at least one context."""
    p = peres_mermin_program()
    proto = export_qiskit_protocol(p, verify=True)
    ns: dict = {}
    body = proto.script.replace(
        "from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler\n", ""
    ).split("if __name__")[0]
    exec(body, ns)
    pe = ns["product_expectation"]
    # all-even-parity counts vs all-odd-parity counts must differ (statistic reads the data)
    even = {"000": 100, "011": 100, "101": 100, "110": 100}
    odd = {"001": 100, "010": 100, "100": 100, "111": 100}
    name = next(iter(ns["CONTEXTS"]))
    assert pe(name, even) == pytest.approx(1.0)
    assert pe(name, odd) == pytest.approx(-1.0)
    assert pe(name, even) != pe(name, odd)  # NOT pinned


def test_emitted_ideal_value_is_full_violation():
    """On noiseless outcomes the sequential statistic gives the ideal S = n_contexts
    (each context product = its sign)."""
    p = peres_mermin_program()
    proto = export_qiskit_protocol(p, verify=True)
    ns: dict = {}
    body = proto.script.replace(
        "from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler\n", ""
    ).split("if __name__")[0]
    exec(body, ns)
    pe = ns["product_expectation"]
    S = 0.0
    for name, (obs, sgn) in ns["CONTEXTS"].items():
        # ideal outcome: three parities whose product is sgn (put all weight on one such string)
        bits = "000" if sgn == 1 else "001"  # parity product +1 or -1
        S += sgn * pe(name, {bits: 1000})
    assert abs(S - 6.0) < 1e-9


def test_scope_guard_refuses_high_d():
    from qkernel.ir import WeylProgram
    prog = WeylProgram(d=4, m=2, observables={"a": (1, 0, 0, 0)}, contexts=[["a"]])
    with pytest.raises(ValueError, match="d=2"):
        export_qiskit_protocol(prog)
