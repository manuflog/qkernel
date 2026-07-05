from __future__ import annotations

QKERNEL_VERSION = "0.33.0"

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
