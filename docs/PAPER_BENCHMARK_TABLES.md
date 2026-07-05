# Paper Benchmark Tables

Q-Kernel v0.18 adds generated benchmark tables for the arXiv-style note.

Run:

```bash
PYTHONPATH=src python experiments/render_paper_tables.py
```

This regenerates:

```text
paper/generated_benchmark_tables.tex
paper/generated_benchmark_tables.md
```

The LaTeX paper includes:

```tex
\input{generated_benchmark_tables}
```

## Policy

The benchmark tables are regression and scaling diagnostics only.

They must not be described as:

- hardware performance measurements;
- magic-resource evidence;
- T-count lower bounds;
- tower/doubling advantage claims.

They show whether the software architecture behaves sensibly on synthetic structured cases.
