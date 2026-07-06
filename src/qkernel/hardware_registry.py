"""Hardware Result Registry (v0.42).

Closes the loop  theory -> certificate -> protocol -> **measured result**:
a dependency-free, schema-validated JSON record linking, for one hardware run,

- the *test* (the contexts actually measured, with their constraint signs),
- the *prediction* (the v0.40 backend-model estimate made before running),
- the *measurement* (per-context shot counts of the +1/-1 context statistic),
- the derived *verdict* (measured S, its standard error, the significance z
  above the noncontextual bound n-2, certified yes/no), and
- the *provenance* (qkernel version, criterion ledger, protocol id, device).

The registry never stores a bare "certified" flag without the numbers that
produced it, and every record carries a criterion ledger, so a measured odd-Q
parity violation cannot silently be quoted at a stronger claim scope.

Statistics.  For context c, from ``plus``/``minus`` counts of the shot-by-shot
product statistic (see ``export_circuit`` for why the product must come from
physically separate observable measurements): the correlator estimate is
E_c = (plus - minus)/N_c with standard error sqrt((1 - E_c^2)/N_c); the signed
functional is S = sum_c eps_c E_c with eps_c the context constraint sign, and

    z = (S - (n - 2)) / sqrt( sum_c (1 - E_c^2) / N_c ).

``certified`` is True iff z >= k_sigma (default 5).
"""
from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from math import sqrt

from .metadata import CERTIFICATE_SOFTWARE, criterion_ledger

SCHEMA_ID = "qkernel.hardware_result.v1"

#: Required top-level fields of a registry record (the schema, kept explicit
#: and dependency-free rather than via jsonschema).
_REQUIRED = {
    "schema": str,
    "record_id": str,
    "created_unix": (int, float),
    "device": dict,       # {"name": str, ...free-form provenance...}
    "test": dict,         # {"contexts": [[str,...],...], "signs": [int,...]}
    "prediction": (dict, type(None)),
    "measurement": dict,  # {"counts": [{"plus": int, "minus": int}, ...], "k_sigma": float}
    "verdict": dict,      # computed: S, nc_bound, per_context, sigma_S, z, certified
    "criterion_ledger": dict,
    "software": dict,
}


@dataclass
class ContextMeasurement:
    """Counts of the +1/-1 context product statistic for one context."""

    plus: int
    minus: int

    @property
    def shots(self) -> int:
        return self.plus + self.minus

    @property
    def correlator(self) -> float:
        n = self.shots
        if n <= 0:
            raise ValueError("context has zero shots")
        return (self.plus - self.minus) / n

    @property
    def stderr(self) -> float:
        e = self.correlator
        return sqrt(max(0.0, 1.0 - e * e) / self.shots)


@dataclass
class Verdict:
    n_contexts: int
    nc_bound: int
    quantum_value: int
    per_context: list[float]
    per_context_stderr: list[float]
    S: float
    sigma_S: float
    z: float
    k_sigma: float
    certified: bool


def compute_verdict(
    counts: list[ContextMeasurement], signs: list[int], *, k_sigma: float = 5.0
) -> Verdict:
    """Measured functional, uncertainty, and significance above the NC bound."""
    n = len(counts)
    if n != len(signs) or n == 0:
        raise ValueError("counts and signs must be same nonzero length")
    if any(s not in (-1, 1) for s in signs):
        raise ValueError("constraint signs must be +/-1")
    corr = [c.correlator for c in counts]
    errs = [c.stderr for c in counts]
    S = sum(s * e for s, e in zip(signs, corr))
    var = sum(er * er for er in errs)
    sigma = sqrt(var)
    nc = n - 2
    z = (S - nc) / sigma if sigma > 0 else float("inf") if S > nc else float("-inf")
    return Verdict(
        n_contexts=n,
        nc_bound=nc,
        quantum_value=n,
        per_context=corr,
        per_context_stderr=errs,
        S=S,
        sigma_S=sigma,
        z=z,
        k_sigma=k_sigma,
        certified=bool(z >= k_sigma),
    )


def new_record(
    *,
    record_id: str,
    device: dict,
    contexts: list[list[str]],
    signs: list[int],
    counts: list[ContextMeasurement],
    prediction: dict | None = None,
    k_sigma: float = 5.0,
) -> dict:
    """Build a complete, schema-valid registry record from raw counts.

    ``prediction`` should be the (JSON-serialisable) v0.40 estimate made before
    the run, e.g. ``{"expected_S": ..., "shots_total": ..., "backend_model": ...}``;
    pass ``None`` when no prediction was made — the absence is then explicit.
    """
    if len(contexts) != len(signs) or len(contexts) != len(counts):
        raise ValueError("contexts, signs, counts must have equal length")
    verdict = compute_verdict(counts, signs, k_sigma=k_sigma)
    ledger = criterion_ledger(
        criterion_id="odd_Q_even_d_v1",
        verifier_used="hardware product-statistic measurement vs noncontextual bound n-2",
        claim_scope=(
            "measured state-independent parity violation on the recorded device; "
            "certifies odd-Q contextuality of the measured family at the stated z"
        ),
        stronger_verifier_available="zd_avn_valuation_v1",
        stronger_verifier_passed=None,
    )
    rec = {
        "schema": SCHEMA_ID,
        "record_id": record_id,
        "created_unix": time.time(),
        "device": device,
        "test": {"contexts": contexts, "signs": signs},
        "prediction": prediction,
        "measurement": {
            "counts": [{"plus": c.plus, "minus": c.minus} for c in counts],
            "k_sigma": k_sigma,
        },
        "verdict": asdict(verdict),
        "criterion_ledger": ledger,
        "software": dict(CERTIFICATE_SOFTWARE),
    }
    validate_record(rec)
    return rec


def validate_record(rec: dict) -> None:
    """Raise ValueError unless the record satisfies the v1 schema."""
    if not isinstance(rec, dict):
        raise ValueError("record must be a dict")
    for key, typ in _REQUIRED.items():
        if key not in rec:
            raise ValueError(f"missing required field: {key}")
        if not isinstance(rec[key], typ):
            raise ValueError(f"field {key} has wrong type: {type(rec[key]).__name__}")
    if rec["schema"] != SCHEMA_ID:
        raise ValueError(f"unknown schema: {rec['schema']}")
    t = rec["test"]
    if "contexts" not in t or "signs" not in t or len(t["contexts"]) != len(t["signs"]):
        raise ValueError("test.contexts and test.signs must align")
    m = rec["measurement"]
    if len(m.get("counts", [])) != len(t["contexts"]):
        raise ValueError("measurement.counts must align with test.contexts")
    for c in m["counts"]:
        if c.get("plus", -1) < 0 or c.get("minus", -1) < 0 or c["plus"] + c["minus"] == 0:
            raise ValueError("each context needs nonnegative counts and >=1 shot")
    v = rec["verdict"]
    for f in ("S", "sigma_S", "z", "certified", "nc_bound"):
        if f not in v:
            raise ValueError(f"verdict missing {f}")
    if "criterion_id" not in rec["criterion_ledger"]:
        raise ValueError("criterion_ledger missing criterion_id")


def append_record(path: str, rec: dict) -> None:
    """Append a validated record to a JSON-lines registry file."""
    validate_record(rec)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, sort_keys=True) + "\n")


def load_registry(path: str) -> list[dict]:
    """Load and validate every record in a JSON-lines registry file."""
    out: list[dict] = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            validate_record(rec)
            out.append(rec)
    return out


def prediction_gap(rec: dict) -> float | None:
    """Measured minus predicted S, when a prediction was recorded (else None)."""
    pred = rec.get("prediction") or {}
    if "expected_S" not in pred:
        return None
    return float(rec["verdict"]["S"]) - float(pred["expected_S"])
