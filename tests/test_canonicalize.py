from pathlib import Path
import pytest

from qkernel.analyzer import analyze
from qkernel.canonicalize import canonicalization_report, canonicalize_program
from qkernel.io import load_program
from qkernel.optimizer import compress_min_odd_q
from qkernel.ir import WeylProgram


def test_canonicalization_report_detects_duplicate_vectors():
    program = load_program(Path(__file__).resolve().parents[1] / "examples/duplicate_vectors_weyl.json")
    report = canonicalization_report(program)

    assert report["observables"] == 10
    assert report["unique_vectors"] == 9
    assert any("ZI_a" in names and "ZI_b" in names for names in report["duplicate_vector_classes"].values())


def test_by_vector_canonicalization_merges_duplicate_names_and_recovers_pm_cycle():
    program = load_program(Path(__file__).resolve().parents[1] / "examples/duplicate_vectors_weyl.json")

    raw = analyze(program)
    canonical = canonicalize_program(program, mode="by-vector")
    canon_result = analyze(canonical)
    kernel = compress_min_odd_q(program, canonicalize="by-vector")

    assert len(canonical.observables) == 9
    assert raw.contextual is False
    assert canon_result.contextual is True
    assert kernel.contextual
    assert kernel.selected_contexts == [0, 1, 2, 3, 4, 5]


def test_canonicalization_refuses_context_internal_merges():
    program = WeylProgram(
        d=2,
        m=1,
        observables={
            "X_a": (0, 1),
            "X_b": (0, 1),
            "I": (0, 0),
        },
        contexts=[
            ["X_a", "X_b", "I"],
        ],
    )

    with pytest.raises(ValueError):
        canonicalize_program(program, mode="by-vector")
