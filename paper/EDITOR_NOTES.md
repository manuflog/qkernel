# Editor Notes for `qkernel_note.tex`

The paper was restructured in v0.17 because the codebase became more mature than the draft.

## Current intended paper shape

1. Purpose and scope
2. Weyl/Pauli measurement programs
3. Incidence cycles and odd-Q criterion
4. Closed symplectic form for Q
5. Kernelization problem
6. Observable identity semantics
7. Input frontends
8. Algorithms and solvers
9. External SAT/MaxSAT workflows
10. Certificates
11. Peres--Mermin test case
12. Synthetic benchmarks
13. Tower/doubling scope
14. Limitations
15. Roadmap

## Non-negotiable wording boundaries

Do not describe Q-Kernel as:

- a magic-state optimizer;
- a T-count lower-bound tool;
- an additive contextuality resource meter;
- proof that passive dimension embedding is free;
- a certified tower-compression tool.

Safe phrase:

> exact odd-Q contextuality kernel extractor

## What to add before submission

- More precise theorem/proposition labels.
- A small table of CLI commands.
- A benchmark table copied from `experiments/output`.
- References to ORBR, ROZF, Howard et al., Gottesman/Knill, etc. from `references.bib`.
- A release archive / DOI if publishing as software.


## Generated benchmark tables

Run:

```bash
PYTHONPATH=src python experiments/render_paper_tables.py
```

This writes:

```text
paper/generated_benchmark_tables.tex
paper/generated_benchmark_tables.md
```

The paper includes the LaTeX table file with:

```tex
\input{generated_benchmark_tables}
```


## Proposition labels

The paper now has explicit proposition labels:

```text
prop:integer-carry
prop:odd-q-criterion
prop:closed-q-form
prop:component-decomposition
prop:certificate-soundness
```

Keep implementation and tests aligned with `docs/PROPOSITION_MAP.md`.


## Saniga-Holweck / finite geometry citation boundary

Before submission, keep the Related Work section. Do not claim novelty for:

```text
GF(2) linear-system contextuality framing
binary symplectic polar-space Pauli geometry
finite-geometric contextuality degree searches
```

The paper now cites de Boutray--Holweck--Giorgetti--Masson--Saniga and Muller--Saniga--Giorgetti--de Boutray--Holweck.
