"""Reproducible optimality certification on dense Pauli families.

Runs the heuristic and the independent CP-SAT backend on dense Pauli families whose
cycle space is far too large for exhaustive span enumeration, and reports whether
CP-SAT *certifies* the heuristic's weight as the true minimum. Documents the claim:

    m=3 (315 contexts, cycle_dim 259, span = 2^259 infeasible)
        -> heuristic weight 6, CP-SAT certifies minimum = 6.

Requires OR-Tools (`pip install qkernel[cpsat]`). Run: `python experiments/certify_dense.py`.
"""
from __future__ import annotations

import sys
import time

sys.path.insert(0, "src")
sys.path.insert(0, "experiments")

from qkernel.incidence import left_kernel_basis
from qkernel.solvers import find_min_odd_cycle_heuristic, hamming_weight
from qkernel.solvers_milp import find_min_odd_cycle_cpsat
from dense_pauli import dense_pauli_triples


def certify(max_m: int = 3, budget_seconds: float = 120.0):
    print(f"{'m':>2} {'contexts':>9} {'cycle_dim':>10} {'heur_wt':>8} "
          f"{'cpsat_wt':>9} {'certified':>10} {'secs':>6}")
    rows = []
    for m in range(2, max_m + 1):
        prog = dense_pauli_triples(m)
        dim = len(left_kernel_basis(prog))
        h = find_min_odd_cycle_heuristic(prog)
        hw = hamming_weight(h) if h else None
        t = time.perf_counter()
        cyc, certified = find_min_odd_cycle_cpsat(prog, max_time_seconds=budget_seconds)
        secs = time.perf_counter() - t
        cw = hamming_weight(cyc) if cyc else None
        rows.append({"m": m, "contexts": len(prog.contexts), "cycle_dim": dim,
                     "heur_wt": hw, "cpsat_wt": cw, "certified": certified, "secs": round(secs, 1)})
        print(f"{m:>2} {len(prog.contexts):>9} {dim:>10} {str(hw):>8} "
              f"{str(cw):>9} {str(certified):>10} {secs:>6.1f}")
        if certified and cw == hw:
            print(f"     => heuristic weight {hw} CERTIFIED minimal (span=2^{dim} infeasible)")
    return rows


if __name__ == "__main__":
    certify(max_m=3)
