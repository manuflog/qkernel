"""Backend-aware experiment design: rank contextuality tests by expected significance.

``minimal_contextuality_tests`` (v0.38) ranks state-independent contextuality
tests by *cost* (fewest measurement settings / observables). This module ranks
them by *expected experimental significance* under an explicit device noise
model: given per-qubit readout errors, which test yields the largest violation
of the noncontextual bound per shot, and how many shots certify it at k sigma?

Statistical model (state-independent parity test with n contexts)
-----------------------------------------------------------------
Each context operator is +/- identity (a scalar), so every context correlator
is +/-1 for *every* input state; state preparation noise does not degrade the
signal. The binding imperfection is measurement. With per-context correlator
visibility eta_c, the measured functional is

    S = sum_c eta_c            (ideal S = n, the number of contexts)

while any noncontextual value assignment satisfies at most n - 1 of the n
parity constraints (the product of the constraint signs is -1), so

    S_NC = n - 2               (noncontextual bound)

Contextuality is certified when the measured S exceeds n - 2 with statistical
significance. Estimating each correlator from N shots gives variance
(1 - eta_c^2)/N, hence

    z = (sum_c eta_c - (n - 2)) / sqrt( sum_c (1 - eta_c^2) / N )

and the total shots to certify at k sigma with a uniform per-context budget is

    total = n * N = n * k^2 * sum_c (1 - eta_c^2) / (sum_c eta_c - (n-2))^2 .

Readout model
-------------
An observable (Pauli string) read out on its support qubits has visibility
v = prod_{q in support} (1 - 2 e_q) with e_q the per-qubit assignment error.
In the default independent-reads model the context correlator visibility is
the product of its observables' visibilities; ``joint_basis=True`` instead
reads each context in one joint eigenbasis measurement with visibility
prod_{q in union support} (1 - 2 e_q).

Claim scope
-----------
This is an *expected-significance model* for planning, not a hardware claim:
it assumes uncorrelated readout errors and perfect context implementation
between readouts. Results carry a criterion ledger; the underlying tests are
odd-Q kernels independently re-checked by ``verify_kernel`` (odd-Q + Z_d/AvN).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from math import sqrt

from .experiment_design import ContextualityTest, minimal_contextuality_tests
from .metadata import criterion_ledger


@dataclass(frozen=True)
class BackendModel:
    """Minimal readout-noise model of a device.

    ``readout_error``: per-qubit assignment error probability, by qubit index;
    qubits not listed use ``default_readout_error``. ``joint_basis=True``
    models one joint eigenbasis measurement per context instead of three
    independent observable readouts.
    """

    readout_error: dict[int, float] = field(default_factory=dict)
    default_readout_error: float = 0.02
    joint_basis: bool = False

    def qubit_error(self, q: int) -> float:
        e = self.readout_error.get(q, self.default_readout_error)
        if not 0.0 <= e < 0.5:
            raise ValueError(f"readout error for qubit {q} must be in [0, 0.5): {e}")
        return e


def pauli_support(p: str) -> list[int]:
    """Qubit indices on which the Pauli string acts nontrivially."""
    return [i for i, ch in enumerate(p) if ch.upper() != "I"]


def observable_visibility(p: str, backend: BackendModel) -> float:
    """Readout visibility of one Pauli observable: prod (1 - 2 e_q) over support."""
    v = 1.0
    for q in pauli_support(p):
        v *= 1.0 - 2.0 * backend.qubit_error(q)
    return v


def context_visibility(context: list[str], backend: BackendModel) -> float:
    """Correlator visibility of one context (measurement setting)."""
    if backend.joint_basis:
        qubits = sorted({q for p in context for q in pauli_support(p)})
        v = 1.0
        for q in qubits:
            v *= 1.0 - 2.0 * backend.qubit_error(q)
        return v
    v = 1.0
    for p in context:
        v *= observable_visibility(p, backend)
    return v


@dataclass
class SignificanceEstimate:
    """Expected-significance figures for one contextuality test on one backend."""

    n_contexts: int
    nc_bound: int                     # n - 2
    quantum_value: int                # n
    eta_per_context: list[float]
    expected_S: float                 # sum of visibilities
    margin: float                     # expected_S - nc_bound
    certifiable: bool                 # margin > 0
    shots_total: int | None           # total shots to certify at k_sigma (None if not certifiable)
    k_sigma: float
    criterion_ledger: dict | None = None


def estimate_significance(
    test: ContextualityTest, backend: BackendModel, *, k_sigma: float = 5.0
) -> SignificanceEstimate:
    """Expected significance of a contextuality test under a backend noise model."""
    n = test.n_contexts
    etas = [context_visibility(ctx, backend) for ctx in test.contexts]
    expected_S = sum(etas)
    nc = n - 2
    margin = expected_S - nc
    certifiable = margin > 0.0
    shots: int | None = None
    if certifiable:
        var_sum = sum(1.0 - e * e for e in etas)
        per_ctx = (k_sigma * k_sigma) * var_sum / (margin * margin)
        shots = max(n, int(-(-n * per_ctx // 1)))  # n * ceil-ish total, at least 1/context
    ledger = criterion_ledger(
        criterion_id="odd_Q_even_d_v1",
        verifier_used="verify_kernel on the underlying test; analytic significance model on top",
        claim_scope=(
            "expected-significance planning estimate under an uncorrelated readout-noise "
            "model; not a hardware measurement"
        ),
        stronger_verifier_available="zd_avn_valuation_v1",
        stronger_verifier_passed=(
            test.criterion_ledger.get("stronger_verifier_passed")
            if test.criterion_ledger
            else None
        ),
    )
    return SignificanceEstimate(
        n_contexts=n,
        nc_bound=nc,
        quantum_value=n,
        eta_per_context=etas,
        expected_S=expected_S,
        margin=margin,
        certifiable=certifiable,
        shots_total=shots,
        k_sigma=k_sigma,
        criterion_ledger=ledger,
    )


@dataclass
class RankedTest:
    test: ContextualityTest
    estimate: SignificanceEstimate


def backend_aware_tests(
    paulis: list[str],
    backend: BackendModel,
    *,
    top: int = 3,
    k_sigma: float = 5.0,
    candidates: int = 10,
) -> list[RankedTest]:
    """Rank the cheapest contextuality tests by expected experimental significance.

    Draws up to ``candidates`` minimal tests from ``minimal_contextuality_tests``
    and re-ranks them by total shots to certify at ``k_sigma`` on ``backend``
    (fewest shots first; non-certifiable tests last). Cost-minimal and
    significance-optimal tests need not coincide once qubit errors are uneven.
    """
    tests = minimal_contextuality_tests(paulis, top=candidates)
    ranked = [RankedTest(t, estimate_significance(t, backend, k_sigma=k_sigma)) for t in tests]
    ranked.sort(
        key=lambda r: (
            not r.estimate.certifiable,
            r.estimate.shots_total if r.estimate.shots_total is not None else float("inf"),
            r.test.n_contexts,
            r.test.n_observables,
        )
    )
    return ranked[:top]
