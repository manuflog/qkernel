"""Q-Kernel: contextuality kernel extraction for Weyl/Pauli measurement programs."""

from .analyzer import analyze
from .canonicalize import canonicalize_program, canonicalization_report
from .decompose import decompose_components
from .ir import AnalysisResult, KernelResult, WeylProgram
from .optimizer import compress_min_odd_q
from .pauli import pauli_program, pauli_string_to_vector
from .pauli_schedule import extract_contexts_from_layers, schedule_program
from .verify import verify_kernel

__all__ = [
    "WeylProgram",
    "AnalysisResult",
    "KernelResult",
    "analyze",
    "canonicalize_program",
    "canonicalization_report",
    "decompose_components",
    "compress_min_odd_q",
    "pauli_program",
    "pauli_string_to_vector",
    "extract_contexts_from_layers",
    "schedule_program",
    "verify_kernel",
]
