from __future__ import annotations

from qkernel.examples import peres_mermin_program
from qkernel.ir import WeylProgram


def noisy_pm_with_disconnected_checks(noise_blocks: int) -> WeylProgram:
    """Build PM core plus disconnected noncontextual closed triples.

    Each noise block uses fresh observable names, so it becomes a separate
    connected component of the context-observable bipartite graph.

    This benchmark is synthetic. It measures whether decomposition prevents
    irrelevant independent blocks from increasing kernel-search cost.
    """
    base = peres_mermin_program()

    observables = dict(base.observables)
    contexts = [list(ctx) for ctx in base.contexts]

    for k in range(noise_blocks):
        a = f"N{k}_ZI"
        b = f"N{k}_IZ"
        c = f"N{k}_ZZ"

        observables[a] = (1, 0, 0, 0)
        observables[b] = (0, 0, 1, 0)
        observables[c] = (1, 0, 1, 0)

        contexts.append([a, b, c])

    return WeylProgram(
        d=base.d,
        m=base.m,
        observables=observables,
        contexts=contexts,
    )



def noisy_pm_with_connected_zero_carry_ladder(extra_pairs: int) -> WeylProgram:
    """Build a connected synthetic family sharing PM observables.

    This is not meant to model a real compiler circuit. It creates additional
    zero-carry contexts connected to the PM observable names so that component
    decomposition alone cannot remove all noise.

    The construction ensures each added triple is:
      - closed under Z_2 label addition;
      - pairwise commuting;
      - zero-carry.
    """
    base = peres_mermin_program()

    observables = dict(base.observables)
    contexts = [list(ctx) for ctx in base.contexts]

    partner = {
        "ZI": "IZ",
        "IZ": "ZI",
        "ZZ": "ZI",
        "IX": "XI",
        "XI": "IX",
        "XX": "IX",
    }
    anchors = list(partner.keys())

    for k in range(extra_pairs):
        anchor = anchors[k % len(anchors)]
        anchor_vec = observables[anchor]
        va_source = partner[anchor]
        va = observables[va_source]
        vb = tuple((x + y) % 2 for x, y in zip(anchor_vec, va))

        a = f"L{k}_{va_source}_copy"
        b = f"L{k}_sum"

        observables[a] = va
        observables[b] = vb
        contexts.append([anchor, a, b])

    return WeylProgram(
        d=base.d,
        m=base.m,
        observables=observables,
        contexts=contexts,
    )
