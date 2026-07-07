# Application Evidence Packets

`application-packet` renders a single evidence packet from existing qkernel
artifacts. It is the first implementation step from the application workbench
PRD: one reviewable packet that links compiler candidates, factory candidates,
resource/correlation rows, and later circuit manifests.

Run:

```bash
qkernel application-packet examples/application_packet_demo.json
qkernel application-packet examples/application_packet_demo.json --out-md packet.md
```

## Packet Shape

A packet has:

- `tracked_candidates`: stable candidate IDs, roles, and rationale
- `sources`: existing qkernel artifacts to load and summarize
- `recommendation`: human-readable next decision guidance

Supported source types:

- `compiler_candidate_corpus`
- `factory_candidate_corpus`
- `correlation_study`
- `circuit_manifest_json`
- `resource_feature_json`

Compiler, factory, and correlation sources are loaded through the corresponding
qkernel report code. Circuit manifests and resource-feature reports can be
attached as pre-rendered JSON artifacts.

## Claim Gates

Each source receives a `claim_gate_status`. The gate is blocked if a required
source is missing, a referenced candidate ID is absent, or the source reports
missing evidence. A packet is `ready_for_claims` only when all required sources
load and no source has evidence blockers.

The packet does not claim qkernel is a production compiler, does not claim
MagicScout motifs are validated factories, and does not claim unsupported
circuit manifests are hardware-ready circuits.
