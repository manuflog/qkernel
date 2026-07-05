from pathlib import Path

from qkernel.canonicalize import canonicalization_report, canonicalize_program
from qkernel.io import dump_program, load_program
from qkernel.optimizer import compress_min_odd_q


def test_metadata_round_trip(tmp_path):
    source = Path(__file__).resolve().parents[1] / "examples/duplicate_vectors_events_weyl.json"
    program = load_program(source)

    out = tmp_path / "round_trip.json"
    dump_program(program, out)
    loaded = load_program(out)

    assert loaded.observable_metadata["ZI_round_1"].identity_scope == "event"
    assert loaded.observable_metadata["ZI_round_1"].round == 1
    assert loaded.observable_metadata["ZI_round_2"].identity_scope == "event"


def test_by_vector_respects_event_identity():
    source = Path(__file__).resolve().parents[1] / "examples/duplicate_vectors_events_weyl.json"
    program = load_program(source)

    report = canonicalization_report(program)
    safe = canonicalize_program(program, mode="by-vector")
    forced = canonicalize_program(program, mode="by-vector-force")

    assert "ZI_round_1" in report["event_scoped_observables"]
    assert "ZI_round_2" in report["event_scoped_observables"]

    # Safe canonicalization keeps event-scoped duplicates distinct.
    assert len(safe.observables) == 10

    # Forced canonicalization merges them.
    assert len(forced.observables) == 9


def test_force_canonicalization_recovers_contextual_kernel_but_safe_mode_does_not():
    source = Path(__file__).resolve().parents[1] / "examples/duplicate_vectors_events_weyl.json"
    program = load_program(source)

    safe_kernel = compress_min_odd_q(program, canonicalize="by-vector")
    forced_kernel = compress_min_odd_q(program, canonicalize="by-vector-force")

    assert not safe_kernel.contextual
    assert forced_kernel.contextual
    assert forced_kernel.selected_contexts == [0, 1, 2, 3, 4, 5]
