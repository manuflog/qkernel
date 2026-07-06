# MagicScout Research Reports

`qkernel.magic_report` renders MagicScout JSON diagnostics into shareable Markdown
research notes.

The reporter is intentionally conservative. It preserves:

- contextuality verdicts;
- criterion-ledger scope;
- backend planning estimates;
- template compatibility;
- missing factory evidence;
- safe claim language;
- forbidden claim language;
- suggested next experiments.

It does not upgrade MagicScout diagnostics into factory claims.

## Intended CLI

```bash
qkernel magic-report examples/magic_protocol_pm_probe.json --out magic_report.md
qkernel magic-search XI IX XX IY YI YY XY YX ZZ --top 5 > magic_search.json
qkernel magic-search-report magic_search.json --out magic_search_report.md
```

## Python API

```python
from qkernel.magic import analyze_magic_protocol_record, load_magic_protocol
from qkernel.magic_report import magic_report_markdown, write_markdown_report

protocol = load_magic_protocol("examples/magic_protocol_pm_probe.json")
report = analyze_magic_protocol_record(protocol)
markdown = magic_report_markdown(report)
write_markdown_report(markdown, "magic_report.md")
```

## Report sections

1. Executive summary
2. Positive signals
3. Missing evidence
4. Criterion ledger
5. Backend planning estimate
6. Template compatibility
7. Safe claim language
8. Forbidden claim language
9. Next experiments

## Claim discipline

MagicScout reports may say:

```text
This candidate contains a small verified contextuality motif worth studying.
```

They must not say:

```text
This candidate lowers magic-state overhead.
This candidate is a valid magic-state factory.
This candidate improves a threshold.
```
