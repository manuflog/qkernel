# Compiler Pass Playground

This is a conservative before/after diagnostic example.

It does **not** prove a circuit rewrite is semantically valid.

## Before

- contexts: 8
- observables: 15
- components: 3
- kernel contexts: 6
- verified: True

## After

- contexts: 6
- observables: 9
- components: 1
- kernel contexts: 6
- verified: True

## Delta

- context delta: -2
- observable delta: -6
- kernel context delta: 0
- requires semantic-equivalence proof: True

## Verdict

after removes nonkernel contexts/observables while preserving the detected odd-Q kernel size; this is a promising pruning diagnostic, not a semantic optimization proof.
