# Rewrite Candidate Policy

Q-Kernel v0.27 adds a rewrite-candidate policy registry so compiler experiments
cannot accidentally present diagnostics as certified resource optimization.

## CLI

List policies:

```bash
qkernel rewrite-policies
```

Assess one policy:

```bash
qkernel assess-rewrite safe_diagnostic_prune
qkernel assess-rewrite forbidden_resource_claim
```

## Policies

### `safe_diagnostic_prune`

A candidate pass removes contexts/observables outside a verified odd-Q kernel.

Allowed:

```text
diagnostic pruning opportunity
kernel-preserving comparison
audit artifact
```

Still required:

```text
external semantic-equivalence proof before a compiler applies the rewrite
```

### `requires_external_semantics`

Generic before/after rewrite comparison. Q-Kernel can compare diagnostics but
cannot prove circuit semantics.

### `experimental_resource_probe`

Exploratory correlation between Q-Kernel metrics and resource metrics.

Allowed:

```text
experiment
correlation study
negative controls
```

Forbidden:

```text
resource theorem
magic optimizer claim
T-count claim
```

### `forbidden_resource_claim`

Claims Q-Kernel must not make.

Examples:

```text
Q-Kernel reduces T-count
Q-Kernel optimizes magic states
passive embedding is free
tower compression is certified
contextuality fraction is an additive resource gauge
```

## Development rule

Any future optimizer-facing feature must declare one policy class. Certified
features should go through propositions and certificates; experimental features
should remain under explicit policy guardrails.
