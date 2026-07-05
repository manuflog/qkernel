# Security Policy

Q-Kernel is research software and should not be used as a security boundary.

## Supported versions

Only the current alpha branch is maintained.

## Reporting issues

For security-sensitive issues, do not open a public issue with exploit details.
Contact the maintainer privately first.

## Scope

Q-Kernel handles local JSON/CSV/text inputs and can write local reports and certificates.
It does not execute untrusted solver binaries internally. External SAT/MaxSAT solvers
should be treated as untrusted candidate generators; Q-Kernel independently verifies
returned lambda vectors.

## Important non-security boundary

Q-Kernel certificates are mathematical/research artifacts. They are not guarantees of
hardware safety, compiler correctness, or cryptographic validity.
