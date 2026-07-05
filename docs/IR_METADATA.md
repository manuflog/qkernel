# IR Metadata and Identity Semantics

Q-Kernel v0.7 adds optional observable metadata.

The core mathematical object is still:

```python
WeylProgram(
    d,
    m,
    observables,
    contexts,
)
```

but it can now carry:

```python
observable_metadata: dict[str, ObservableMetadata]
```

## ObservableMetadata

```python
ObservableMetadata(
    identity_scope="observable" | "event",
    source=None,
    round=None,
    notes=None,
)
```

## Why this exists

A real compiler frontend must distinguish two different notions:

```text
algebraic equality: same Weyl vector
protocol identity: same measurement object/event
```

Two names may have the same vector:

```json
"ZI_round_1": [1,0,0,0],
"ZI_round_2": [1,0,0,0]
```

but if they represent distinct measurement events, merging them may create a false parity cycle.

## Identity scopes

### `observable`

The name is intended to refer to an algebraic observable. It may be merged with other names carrying the same Weyl vector when using:

```bash
--canonicalize by-vector
```

### `event`

The name is a protocol-level measurement event. It remains distinct under safe canonicalization, even if another event has the same Weyl vector.

Only force mode merges event identities:

```bash
--canonicalize by-vector-force
```

This should be used for algebraic experiments, not faithful protocol analysis.

## Design rule

Frontend adapters must choose identity semantics explicitly. Q-Kernel should not guess.
