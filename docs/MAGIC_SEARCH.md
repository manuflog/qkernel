# MagicScout Search

`qkernel.magic_search` turns MagicScout into a candidate-discovery workflow.
Given a set of available Pauli measurements, it asks Q-Kernel's experiment-design
layer for candidate contextuality motifs, runs each motif through MagicScout,
checks conservative factory-template compatibility, and ranks the results.

It is not a magic-state factory synthesizer. A search result is a research
hypothesis: a contextuality motif worth inspecting inside a magic-state-adjacent
workflow.

## API

```python
from qkernel.magic_search import search_magic_candidates_from_paulis, magic_search_report_dict

report = search_magic_candidates_from_paulis(
    ["XI", "IX", "XX", "IY", "YI", "YY", "XY", "YX", "ZZ"],
    target="T",
    top=5,
    required_templates=["contextuality_witness"],
)
print(magic_search_report_dict(report))
```

## CLI

```bash
qkernel magic-search XI IX XX IY YI YY XY YX ZZ --target T --top 5
qkernel magic-search XI IX XX IY YI YY XY YX ZZ --required-template contextuality_witness
```

## Standard demo

```python
from qkernel.magic_search import search_two_qubit_magic_candidates

report = search_two_qubit_magic_candidates(top=10)
```

## Ranking rule

Candidates are ranked by:

```text
MagicScout interest score
+ template compatibility bonuses
+ backend-certifiability bonus, if a backend model is provided
- required-template penalties
- non-contextual penalty
```

Then ties break by backend shots, kernel weight, and protocol id.

## Non-claims

Search does not claim:

```text
magic-state factory synthesis
lower magic-state overhead
distillation threshold
output fidelity bound
acceptance probability
logical-code-distance claim
decoder performance claim
space-time-volume advantage
```
