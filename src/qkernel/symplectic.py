from __future__ import annotations

from .ir import Vector


def symplectic_int(v: Vector, w: Vector) -> int:
    """Integer symplectic form for interleaved coordinates [z1,x1,z2,x2,...].

    Important: this returns the integer lift, not the value reduced modulo d.
    The commutator carry b(C) is lost if this is reduced too early.
    """
    if len(v) != len(w) or len(v) % 2 != 0:
        raise ValueError("Vectors must have the same even length.")

    return sum(
        v[2 * k + 1] * w[2 * k] - v[2 * k] * w[2 * k + 1]
        for k in range(len(v) // 2)
    )


def commute(v: Vector, w: Vector, d: int) -> bool:
    """Return True when two Weyl labels commute modulo d."""
    return symplectic_int(v, w) % d == 0


def add_mod(v: Vector, w: Vector, d: int) -> Vector:
    """Vector addition in Z_d^(2m)."""
    if len(v) != len(w):
        raise ValueError("Vectors must have equal length.")
    return tuple((a + b) % d for a, b in zip(v, w))


def zero_vector(m: int) -> Vector:
    return tuple(0 for _ in range(2 * m))


def basis(m: int, qudit: int, axis: str) -> Vector:
    """Basis Weyl label on one qudit.

    axis='Z' sets z_j=1; axis='X' sets x_j=1.
    """
    if axis not in {"Z", "X"}:
        raise ValueError("axis must be 'Z' or 'X'.")
    if not 0 <= qudit < m:
        raise ValueError("qudit index out of range.")
    vec = [0] * (2 * m)
    vec[2 * qudit + (0 if axis == "Z" else 1)] = 1
    return tuple(vec)
