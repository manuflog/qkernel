"""Round-trip correctness tests for the compiler-facing adapters (Phase 2).

Each adapter parses an explicit Pauli measurement family into a WeylProgram; the
gold-standard check is that a Peres-Mermin family round-trips to a *contextual*
verdict, a single row does not, and the observable-identity semantics
(shared `observable` scope vs independent `event` scope) are honoured. These lock
in the previously untested stim_lite / pauli_table / pauli_schedule parsers.
"""
from pathlib import Path

from qkernel.analyzer import analyze
from qkernel.adapters.stim_lite import load_stim_lite_program
from qkernel.adapters.pauli_table import load_pauli_table
from qkernel.pauli_schedule import load_pauli_schedule

EX = Path(__file__).resolve().parents[1] / "examples"


def _verdict(program):
    return len(program.contexts), analyze(program).contextual


# --- Peres-Mermin round-trips: every adapter must detect contextuality ---

def test_stim_lite_peres_mermin_is_contextual():
    n, contextual = _verdict(load_stim_lite_program(str(EX / "peres_mermin_mpp.stim")))
    assert n == 6 and contextual is True


def test_pauli_table_json_peres_mermin_is_contextual():
    n, contextual = _verdict(load_pauli_table(str(EX / "peres_mermin_table.json")))
    assert n == 6 and contextual is True


def test_pauli_table_csv_peres_mermin_is_contextual():
    n, contextual = _verdict(load_pauli_table(str(EX / "peres_mermin_table.csv")))
    assert n == 6 and contextual is True


def test_pauli_schedule_peres_mermin_is_contextual():
    n, contextual = _verdict(load_pauli_schedule(str(EX / "peres_mermin_schedule.json")))
    assert n == 6 and contextual is True


# --- negative controls: a single row of PM is not contextual ---

def test_row_only_schedule_is_not_contextual():
    n, contextual = _verdict(load_pauli_schedule(str(EX / "row_only_schedule.json")))
    assert n == 3 and contextual is False


# --- observable-identity semantics: event scope breaks cross-context identity ---

def test_event_scope_makes_identical_paulis_noncontextual():
    """Same PM Pauli strings, but identity_scope='event' => each measurement is an
    independent event with no shared identity across contexts, so the consistency
    constraint that makes PM contextual is absent."""
    shared = load_pauli_table(str(EX / "peres_mermin_table.json"))
    events = load_pauli_table(str(EX / "peres_mermin_table_events.json"))
    assert analyze(shared).contextual is True
    assert analyze(events).contextual is False


# --- noise robustness: extra contexts do not destroy the detected kernel ---

def test_noise_schedule_still_contextual():
    prog = load_pauli_schedule(str(EX / "peres_mermin_with_noise_schedule.json"))
    assert analyze(prog).contextual is True


# --- cross-adapter agreement: same physics, same verdict across formats ---

def test_adapters_agree_on_peres_mermin():
    verdicts = {
        "stim": analyze(load_stim_lite_program(str(EX / "peres_mermin_mpp.stim"))).contextual,
        "table": analyze(load_pauli_table(str(EX / "peres_mermin_table.json"))).contextual,
        "schedule": analyze(load_pauli_schedule(str(EX / "peres_mermin_schedule.json"))).contextual,
    }
    assert set(verdicts.values()) == {True}
