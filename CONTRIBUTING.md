# Contributing to Q-Kernel

Q-Kernel is alpha-stage research software. Contributions are welcome, but the
claim boundaries are strict.

## Development setup

```bash
python -m pip install -e .[dev]
pytest -q
qkernel self-test
qkernel release-audit --root .
```

Optional SAT backend:

```bash
python -m pip install -e .[sat,dev]
```

## Claim discipline

Allowed:

```text
odd-Q contextuality kernel extraction
Z_d valuation verification
certificate/report generation
compiler diagnostics
experimental resource-correlation probes
```

Not allowed without a new theorem and audit update:

```text
Q-Kernel optimizes magic states
Q-Kernel reduces T-count
tower compression is certified as a resource optimization
passive embedding is free
diagnostic pruning is a valid compiler rewrite by itself
```

## Pull request checklist

Before opening a PR:

```text
pytest -q
qkernel self-test
qkernel release-audit --root .
```

Also update relevant docs/tests when adding features.

## Mathematical changes

Any change to the following requires tests and documentation:

```text
carry arithmetic
closed Q form
Z_d valuation verifier
tower/doubling law
fiber-lift constructor
certificate schema
solver encodings
```

## Public API caution

The project is still alpha. Prefer adding explicit, conservative APIs rather than
changing core semantics silently.
