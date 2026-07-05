# Proposition Map

Q-Kernel v0.19 adds explicit theorem/proposition labels to the paper and maps them to code.

## Paper propositions

| Label | Paper statement | Primary code |
|---|---|---|
| `prop:integer-carry` | Carry must be computed from integer symplectic lifts before reducing mod `d`. | `symplectic.py`, `carry.py`, `test_integer_carry_bug.py` |
| `prop:odd-q-criterion` | Even-`d` odd-Q criterion: `A^T lambda = 0`, `b^T lambda = 1`. | `incidence.py`, `analyzer.py`, `optimizer.py` |
| `prop:closed-q-form` | Closed observable-multiset symplectic form equals `lambda·b`. | `closed_form.py`, `test_closed_q_form.py` |
| `prop:component-decomposition` | Disconnected components can be searched independently; global minimum is component minimum. | `decompose.py`, `test_decompose.py` |
| `prop:certificate-soundness` | Accepted certificates bind to program hash and verify `A^T lambda = 0`, `Q(lambda)=1`. | `certificate.py`, `verify.py`, `solver_output.py` |

## Development rule

Every new certified feature should be attached to one of:

1. an existing proposition;
2. a new proposition;
3. an explicitly experimental namespace.

No uncertified resource claim should enter the certified path.


## Prior-art boundary

The proposition map is not a novelty map. In particular, the GF(2) linear-system and binary symplectic polar-space ingredients overlap with prior finite-geometric work by Saniga/Holweck/de Boutray/Muller and collaborators. Q-Kernel's novelty target is the odd-Q carry/kernel/certificate implementation and qudit-aware software architecture.
