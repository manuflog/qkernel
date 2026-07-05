from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Literal, Optional, Tuple

Vector = Tuple[int, ...]
Context = List[str]
IdentityScope = Literal["observable", "event"]


@dataclass(frozen=True)
class ObservableMetadata:
    """Protocol/compiler metadata for an observable label.

    identity_scope:
      - observable: repeated references with the same Weyl vector may be
        intentionally treated as the same observable when canonicalizing.
      - event: this name refers to a distinct measurement event, even if its
        Weyl vector equals another event's vector.

    The core math uses only vectors and contexts. Metadata exists to prevent
    compiler frontends from silently confusing algebraic equality with
    protocol identity.
    """

    identity_scope: IdentityScope = "observable"
    source: Optional[str] = None
    round: Optional[int] = None
    notes: Optional[str] = None


@dataclass(frozen=True)
class WeylProgram:
    """Internal representation of a Weyl/Pauli measurement program.

    Observables are vectors in Z_d^(2m), using interleaved coordinates:

        [z1, x1, z2, x2, ..., zm, xm]

    Contexts are lists of observable names.

    observable_metadata is optional and backward compatible. If omitted, every
    observable is treated as identity_scope="observable".
    """

    d: int
    m: int
    observables: Dict[str, Vector]
    contexts: List[Context]
    observable_metadata: Dict[str, ObservableMetadata] = field(default_factory=dict)
    context_phases: Optional[List[int]] = None


@dataclass(frozen=True)
class AnalysisResult:
    contextual: bool
    reason: str
    b_vector: List[int]
    cycle_basis: List[List[int]]
    odd_cycle: Optional[List[int]]
    q_value: Optional[int]
    selected_contexts: List[int]


@dataclass(frozen=True)
class KernelResult:
    contextual: bool
    original_contexts: int
    original_observables: int
    compressed_contexts: int
    compressed_observables: int
    selected_contexts: List[int]
    selected_observables: List[str]
    q_value: Optional[int]
    compression_ratio_contexts: float
    compression_ratio_observables: float
