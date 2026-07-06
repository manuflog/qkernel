from __future__ import annotations

QKERNEL_VERSION = "0.43.0"

COORDINATE_CONVENTION = {
    "id": "interleaved_zx_v1",
    "description": "Weyl vectors are interleaved [z1,x1,z2,x2,...,zm,xm].",
}

CRITERION = {
    "id": "odd_Q_even_d_v1",
    "description": (
        "For even local dimension d, a Weyl family is contextual iff "
        "there exists lambda with A^T lambda = 0 mod 2 and b^T lambda = Q(lambda) = 1 mod 2."
    ),
}

CRITERION_ZD_AVN = {
    "id": "zd_avn_valuation_v1",
    "description": (
        "Z_d / AvN valuation-contextuality: the integer valuation system "
        "M phi = gamma mod d has no solution. Strictly stronger claim scope than "
        "the odd-Q parity obstruction; the two criteria are distinct and must not be conflated."
    ),
}

#: Registry of all claim criteria used anywhere in qkernel. Every user-facing
#: result (analysis, certificate, activation, experiment design, subroutine)
#: must carry a ``criterion`` ledger built by :func:`criterion_ledger` so that
#: the claim scope of each verdict is machine-readable and cannot drift.
CRITERIA = {
    CRITERION["id"]: CRITERION,
    CRITERION_ZD_AVN["id"]: CRITERION_ZD_AVN,
}


def criterion_ledger(
    *,
    criterion_id: str = "odd_Q_even_d_v1",
    verifier_used: str,
    claim_scope: str,
    stronger_verifier_available: str | None = None,
    stronger_verifier_passed: bool | None = None,
) -> dict:
    """Build the semantic-firewall ledger attached to every qkernel result.

    ``stronger_verifier_passed`` is ``True``/``False`` only when the stronger
    verifier was actually run; ``None`` means not run / not applicable. The
    ledger exists so that odd-Q parity verdicts are never silently read as
    Z_d/AvN valuation verdicts (or vice versa).
    """
    if criterion_id not in CRITERIA:
        raise ValueError(f"unknown criterion_id: {criterion_id!r}")
    return {
        "criterion_id": criterion_id,
        "criterion": CRITERIA[criterion_id],
        "verifier_used": verifier_used,
        "claim_scope": claim_scope,
        "stronger_verifier_available": stronger_verifier_available,
        "stronger_verifier_passed": stronger_verifier_passed,
    }


INTEGER_CARRY_RULE = {
    "id": "integer_lift_before_mod_v1",
    "description": (
        "Compute symplectic pairings as integer lifts, divide by d on commuting pairs, "
        "then reduce mod 2. Do not reduce the symplectic pairing modulo d before division."
    ),
}

CERTIFICATE_SOFTWARE = {
    "qkernel_version": QKERNEL_VERSION,
    "coordinate_convention": COORDINATE_CONVENTION,
    "criterion": CRITERION,
    "integer_carry_rule": INTEGER_CARRY_RULE,
}
