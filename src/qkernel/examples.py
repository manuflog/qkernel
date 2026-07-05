from __future__ import annotations

from .ir import WeylProgram
from .symplectic import add_mod, basis


def peres_mermin_program() -> WeylProgram:
    """Two-qubit Peres-Mermin square over d=2."""
    d = 2
    m = 2

    obs = {
        "ZI": (1, 0, 0, 0),
        "IZ": (0, 0, 1, 0),
        "ZZ": (1, 0, 1, 0),
        "IX": (0, 0, 0, 1),
        "XI": (0, 1, 0, 0),
        "XX": (0, 1, 0, 1),
        "ZX": (1, 0, 0, 1),
        "XZ": (0, 1, 1, 0),
        "YY": (1, 1, 1, 1),
    }

    contexts = [
        ["ZI", "IZ", "ZZ"],
        ["IX", "XI", "XX"],
        ["ZX", "XZ", "YY"],
        ["ZI", "IX", "ZX"],
        ["IZ", "XI", "XZ"],
        ["ZZ", "XX", "YY"],
    ]

    return WeylProgram(d=d, m=m, observables=obs, contexts=contexts)


def noisy_peres_mermin_program(noise_contexts: int = 40) -> WeylProgram:
    """Peres-Mermin core plus many irrelevant commuting contexts."""
    d = 2
    m = max(4, noise_contexts + 4)

    obs: dict[str, tuple[int, ...]] = {}

    def put(name: str, vec: tuple[int, ...]) -> str:
        obs[name] = vec
        return name

    put("ZI", basis(m, 0, "Z"))
    put("IZ", basis(m, 1, "Z"))
    put("ZZ", add_mod(obs["ZI"], obs["IZ"], d))

    put("IX", basis(m, 1, "X"))
    put("XI", basis(m, 0, "X"))
    put("XX", add_mod(obs["IX"], obs["XI"], d))

    put("ZX", add_mod(obs["ZI"], obs["IX"], d))
    put("XZ", add_mod(obs["XI"], obs["IZ"], d))
    put("YY", add_mod(obs["ZX"], obs["XZ"], d))

    contexts = [
        ["ZI", "IZ", "ZZ"],
        ["IX", "XI", "XX"],
        ["ZX", "XZ", "YY"],
        ["ZI", "IX", "ZX"],
        ["IZ", "XI", "XZ"],
        ["ZZ", "XX", "YY"],
    ]

    for t in range(noise_contexts):
        j = 2 + t
        k = 3 + t
        a = put(f"N{t}_Za", basis(m, j, "Z"))
        b = put(f"N{t}_Zb", basis(m, k, "Z"))
        c = put(f"N{t}_Zab", add_mod(obs[a], obs[b], d))
        contexts.append([a, b, c])

    return WeylProgram(d=d, m=m, observables=obs, contexts=contexts)
