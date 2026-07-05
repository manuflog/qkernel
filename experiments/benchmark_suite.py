"""Benchmark suite: how the exact odd-Q kernel solvers scale.

Sweeps synthetic Weyl families of growing size (a fixed Peres-Mermin kernel embedded
in a growing sea of *connected* zero-carry contexts, so component decomposition alone
cannot strip the noise) and records, per size:

  - n_contexts                     problem size
  - solve time (decompose on/off)  wall-clock median over repeats
  - kernel size                    must stay 6 (the PM core) -- correctness at scale
  - agreement                      the three exact solvers must return the same cycle

Run:  python experiments/benchmark_suite.py            (prints a table, writes CSV)
The point is to locate where exact solving grows and whether decomposition tames it,
which is the empirical input to deciding if sparse-cycle heuristics are warranted.
"""
from __future__ import annotations

import csv
import statistics
import time
from pathlib import Path

try:
    from experiments.generate_noisy_pm import noisy_pm_with_connected_zero_carry_ladder
except ImportError:  # when run as a script from the experiments/ directory
    from generate_noisy_pm import noisy_pm_with_connected_zero_carry_ladder
from qkernel.optimizer import compress_min_odd_q
from qkernel.analyzer import analyze
from qkernel.verify import verify_kernel

OUT = Path(__file__).resolve().parent / "output"
OUT.mkdir(parents=True, exist_ok=True)

SIZES = [0, 5, 10, 25, 50, 100, 200, 400]
PM_KERNEL = 6  # the Peres-Mermin core every family compresses to


def _median_ms(fn, repeats: int = 5):
    result, times = None, []
    for _ in range(repeats):
        t = time.perf_counter()
        result = fn()
        times.append((time.perf_counter() - t) * 1e3)
    return result, statistics.median(times)


def run(sizes=SIZES, repeats: int = 5):
    rows = []
    print(f"{'contexts':>9} {'t_decomp(ms)':>13} {'t_flat(ms)':>12} "
          f"{'kernel':>7} {'contextual':>11} {'verified':>9}")
    for extra in sizes:
        prog = noisy_pm_with_connected_zero_carry_ladder(extra)
        n = len(prog.contexts)

        kernel_d, t_d = _median_ms(lambda: compress_min_odd_q(prog, decompose=True), repeats)
        kernel_f, t_f = _median_ms(lambda: compress_min_odd_q(prog, decompose=False), repeats)

        ksize = len(kernel_d.selected_contexts)
        contextual = analyze(prog).contextual
        verified = bool(verify_kernel(prog, kernel_d).valid)
        agree = kernel_d.selected_contexts == kernel_f.selected_contexts

        rows.append({
            "contexts": n, "t_decomp_ms": round(t_d, 3), "t_flat_ms": round(t_f, 3),
            "kernel": ksize, "contextual": contextual, "verified": verified,
            "solvers_agree": agree,
        })
        print(f"{n:>9} {t_d:>13.3f} {t_f:>12.3f} {ksize:>7} "
              f"{str(contextual):>11} {str(verified):>9}")

        # correctness invariants at every size
        assert ksize == PM_KERNEL, f"kernel size {ksize} != {PM_KERNEL} at n={n}"
        assert contextual and verified, f"lost contextuality/verification at n={n}"
        assert agree, f"solvers disagree at n={n}"

    csv_path = OUT / "benchmark_suite.csv"
    with open(csv_path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"\nwrote {csv_path}")
    return rows


if __name__ == "__main__":
    run()


def crossover(max_m: int = 3):
    """Exact vs heuristic on dense Pauli families: shows where exact enumeration
    becomes infeasible (cycle_dim explodes) but the heuristic still finds the
    minimal odd-Q kernel. Returns rows; m>=3 has cycle_dim in the hundreds."""
    import time
    try:
        from experiments.dense_pauli import dense_pauli_triples
    except ImportError:
        from dense_pauli import dense_pauli_triples
    from qkernel.incidence import left_kernel_basis
    from qkernel.analyzer import analyze
    from qkernel.solvers import find_min_odd_cycle_heuristic, hamming_weight

    rows = []
    print(f"{'m':>2} {'contexts':>9} {'cycle_dim':>10} {'exact_feasible':>15} "
          f"{'heur_ms':>9} {'heur_wt':>8}")
    for m in range(2, max_m + 1):
        prog = dense_pauli_triples(m)
        dim = len(left_kernel_basis(prog))
        exact_feasible = dim <= 20  # 2^dim enumeration cap
        t = time.perf_counter()
        lam = find_min_odd_cycle_heuristic(prog)
        ms = (time.perf_counter() - t) * 1e3
        wt = hamming_weight(lam) if lam else None
        contextual = analyze(prog).contextual
        rows.append({"m": m, "contexts": len(prog.contexts), "cycle_dim": dim,
                     "exact_feasible": exact_feasible, "heur_ms": round(ms, 2),
                     "heur_wt": wt, "contextual": contextual})
        print(f"{m:>2} {len(prog.contexts):>9} {dim:>10} {str(exact_feasible):>15} "
              f"{ms:>9.2f} {str(wt):>8}")
        assert contextual and wt == 6, f"expected contextual weight-6 kernel at m={m}"
    return rows
