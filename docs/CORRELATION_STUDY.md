# Correlation Study Harness

`qkernel.correlation_study` joins qkernel feature rows with externally supplied
resource metrics for exploratory studies.

It does not fit a model, predict resources, or prove a resource theorem. The
point is to create a reproducible table with negative controls and explicit
coverage checks before anyone talks about T-count, T-depth, magic injections,
or stabilizer rank.

## CLI

```bash
qkernel correlation-study examples/resource_correlation_study.json
qkernel correlation-study examples/resource_correlation_study.json --out-md correlation_study.md
qkernel correlation-study examples/resource_correlation_study.json --out-csv joined.csv
```

## Corpus Schema

```json
{
  "study_id": "resource_correlation_demo",
  "rows": [
    {
      "program_id": "peres_mermin_probe",
      "path": "peres_mermin.json",
      "input_kind": "weyl",
      "role": "candidate",
      "external_resource_metrics": {
        "program_id": "peres_mermin_probe",
        "source": "external oracle",
        "t_count": 7,
        "t_depth": 3,
        "magic_injections": 1,
        "stabilizer_rank": null
      }
    }
  ]
}
```

Paths are resolved relative to the study file.

## Summary Checks

The report marks `correlation_ready=false` until the corpus has:

```text
at least 3 rows with external resource metrics
at least 1 negative control
at least 1 metric populated on at least 3 rows
```

These are minimal hygiene checks, not a guarantee that a correlation is
scientifically valid.

`--out-csv` writes the joined qkernel/resource table for notebooks,
spreadsheets, or external statistical tools. The CSV is still a correlation-only
artifact; it does not contain model fits or resource predictions.

## Non-Claims

The harness does not claim:

```text
resource theorem
resource prediction
T-count optimization
magic-state factory optimization
resource advantage
```
