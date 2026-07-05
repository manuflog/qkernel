# Observable Canonicalization

Q-Kernel v0.6 adds explicit observable canonicalization.

## Why it exists

Two different observable names may carry the same Weyl vector:

```json
"ZI_a": [1,0,0,0],
"ZI_b": [1,0,0,0]
```

For algebraic compression, these can be treated as the same observable. For protocol analysis, they may represent distinct measurement events. Therefore canonicalization is opt-in.

## Modes

```text
none       # default, safest
by-vector  # merge observables with identical Weyl labels
```

## CLI

```bash
qkernel canonicalize-report examples/duplicate_vectors_weyl.json
qkernel compress examples/duplicate_vectors_weyl.json --canonicalize by-vector --json
qkernel components examples/duplicate_vectors_weyl.json --canonicalize by-vector
```

## Safety rule

If canonicalization would merge two observables inside the same context, Q-Kernel raises an error instead of silently changing multiplicity semantics.

Example unsafe context:

```text
["X_a", "X_b", "I"]
```

where `X_a` and `X_b` have the same Weyl vector.

## Why the default remains `none`

Automatic canonicalization can create cycles that are algebraically valid but operationally false for a specific circuit or measurement protocol. A compiler adapter must decide whether identical labels are the same observable or distinct measurement events.


## Event-aware mode

Since v0.7, `by-vector` respects `identity_scope="event"` metadata. Event-scoped observables are not merged.

Force mode exists for algebraic experiments:

```bash
qkernel compress examples/duplicate_vectors_events_weyl.json --canonicalize by-vector-force
```

Use this carefully. It can create algebraic cycles that are not protocol-faithful.
