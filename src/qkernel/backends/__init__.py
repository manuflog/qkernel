"""Optional solver backends.

The Q-Kernel core remains dependency-free. Backends here may require optional
extras such as `qkernel[sat]`.
"""

from .pysat_backend import (
    OptionalBackendUnavailable,
    BackendSolveResult,
    pysat_available,
    solve_sat_with_pysat,
    solve_maxsat_with_rc2,
)

__all__ = [
    "OptionalBackendUnavailable",
    "BackendSolveResult",
    "pysat_available",
    "solve_sat_with_pysat",
    "solve_maxsat_with_rc2",
]
