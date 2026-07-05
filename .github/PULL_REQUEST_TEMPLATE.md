# Pull Request

## Summary

## Type

```text
bug fix
math correction
new adapter
solver/reporting feature
docs
tests
```

## Checklist

- [ ] `pytest -q`
- [ ] `qkernel self-test`
- [ ] `qkernel release-audit --root .`
- [ ] Docs updated
- [ ] Tests added/updated
- [ ] Claim boundaries preserved

## Safety-critical area touched?

- [ ] carry arithmetic
- [ ] closed Q form
- [ ] Z_d valuation verification
- [ ] tower/lift logic
- [ ] certificates
- [ ] solver encodings
- [ ] compiler diagnostics
- [ ] no safety-critical area

## Claims

State exactly what this PR claims and what it does **not** claim.
