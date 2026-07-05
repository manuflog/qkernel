# Standalone Certificates

Q-Kernel v0.10 adds a stable JSON certificate format.

A certificate binds a selected odd-Q kernel to a specific input program through a SHA-256 hash of the canonical program representation.

## Create a certificate

```bash
qkernel certify examples/peres_mermin_pauli.json \
  --input pauli \
  --out pm_certificate.json
```

## Verify a certificate

```bash
qkernel verify-certificate examples/peres_mermin_pauli.json \
  --input pauli \
  --certificate pm_certificate.json
```

Expected output:

```json
{
  "valid": true,
  "reason": "valid odd-Q contextual kernel",
  "q_value": 1,
  "program_sha256": "..."
}
```

## Certificate fields

```json
{
  "schema": "qkernel.certificate.v1",
  "program_sha256": "...",
  "program": {
    "d": 2,
    "m": 2,
    "contexts": 6,
    "observables": 9,
    "observable_order": ["IX", "..."]
  },
  "kernel": {
    "contextual": true,
    "q_value": 1,
    "lambda": [1,1,1,1,1,1],
    "selected_contexts": [0,1,2,3,4,5],
    "selected_observables": ["IX", "..."],
    "b_vector": [0,0,0,0,0,1],
    "compression": {}
  },
  "verification": {
    "verified_by": "qkernel.verify.verify_kernel",
    "valid": true,
    "reason": "valid odd-Q contextual kernel"
  }
}
```

## Why this matters

Solvers are allowed to evolve. Some future solvers may be heuristic or external. The certificate layer makes solver output independently checkable.

The trusted object is not:

```text
solver says contextual
```

The trusted object is:

```text
program hash + lambda + independent verification
```


## Version and convention metadata

Since v0.11, certificates also record:

```json
{
  "software": {
    "qkernel_version": "0.11.0"
  },
  "conventions": {
    "coordinate_convention": {
      "id": "interleaved_zx_v1"
    },
    "integer_carry_rule": {
      "id": "integer_lift_before_mod_v1"
    }
  },
  "criterion": {
    "id": "odd_Q_even_d_v1"
  }
}
```

Verification rejects certificates with unsupported criterion, coordinate convention, or carry rule.

This matters because the certificate must remain interpretable as the IR evolves.
