# Q-Kernel Release Audit

- version: `0.33.0`
- passed: `True`
- recommendation: ready for private/public-review repository; keep alpha label and conservative README positioning

## Safe positioning

Q-Kernel is a research tool for extracting, verifying, and reporting odd-Q / Z_d contextuality kernels in Weyl/Pauli measurement programs.

## Unsafe positioning

- not a magic-state optimizer
- not a T-count optimizer
- not a certified tower-compression optimizer
- not proof that passive embedding is free
- not a compiler semantic-equivalence engine

## Checks

- `PASS` `file:README.md` — present
- `PASS` `file:LICENSE` — present
- `PASS` `file:CITATION.cff` — present
- `PASS` `file:CHANGELOG.md` — present
- `PASS` `file:MANIFEST_QKERNEL.md` — present
- `PASS` `file:paper/qkernel_note.tex` — present
- `PASS` `file:docs/ZD_VALUATION_VERIFICATION.md` — present
- `PASS` `file:docs/TOWER_LAW.md` — present
- `PASS` `file:docs/FIBER_LIFT.md` — present
- `PASS` `file:docs/LIFT_PIPELINE.md` — present
- `PASS` `file:docs/REWRITE_POLICY.md` — present
- `PASS` `file:docs/NOVELTY_HYGIENE.md` — present
- `PASS` `file:docs/COMPILER_OPTIMIZER_PATH.md` — present
- `PASS` `core:pm_kernel_verified` — valid odd-Q and genuine Z_d contextual kernel
- `PASS` `core:pm_zd_unsat` — Z_d valuation system is unsolvable; genuine AvN contextual family
- `PASS` `policy:forbidden_resource_claim_blocked` — forbidden claim; do not report as Q-Kernel result
- `PASS` `policy:safe_prune_reportable_not_applicable` — diagnostic only until external semantic-equivalence proof is supplied
- `PASS` `compiler:playground_requires_semantic_proof` — after removes nonkernel contexts/observables while preserving the detected odd-Q kernel size; this is a promising pruning diagnostic, not a semantic optimization proof.
- `PASS` `tower:fiber_lift_constructed` — valid d -> 2d fiber lift constructed and validated.
- `PASS` `tower:closed_formula_certified` — certified closed tower/doubling formula; cycle is non-generative iff G=0
- `PASS` `tower:pipeline_report_complete` — validated fiber lift plus Z_d valuation result plus closed tower-law generativity report
- `PASS` `novelty:finite_geometry_refs_in_bib` — finite-geometry prior-art BibTeX keys present
- `PASS` `novelty:linear_system_not_claimed` — novelty hygiene document states non-novel parts
