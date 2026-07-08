from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]


def test_package_metadata_files_exist():
    for rel in [
        "LICENSE",
        "CITATION.cff",
        "MANIFEST.in",
        "CHANGELOG.md",
        "docs/KERNEL_CENSUS.md",
        "docs/ADJACENT_REPO_DECISION.md",
        "docs/RESOURCE_ORACLE.md",
        "docs/COMPILER_CANDIDATES.md",
        "docs/CIRCUIT_MANIFEST.md",
        "docs/FACTORY_CANDIDATES.md",
        "docs/CORRELATION_STUDY.md",
        "docs/IMPACT_REGISTER.md",
        "docs/APPLICATION_PACKET.md",
        "docs/PRD_APPLICATION_WORKBENCH.md",
        "docs/PRD_COMPILER_MAGIC_FACTORY_BRIDGE.md",
        "docs/RESEARCH_PLAN.md",
        "docs/RELEASE_READINESS.md",
        "docs/RELEASE_BUNDLE.md",
        "examples/application_packet_demo.json",
        "examples/circuit_manifest_d4_probe.json",
        "examples/compiler_candidate_corpus.json",
        "examples/factory_candidate_corpus.json",
        "examples/resource_correlation_study.json",
        "examples/kernel_theorem_pins.json",
        "examples/kernel_census_targets.json",
        "examples/resource_feature_pm_probe.json",
        "examples/resource_metrics_stub.json",
        "paper/PAPER_SCAFFOLD.md",
        "paper/repro_manifest_template.json",
        "src/qkernel/application_prd.py",
        "src/qkernel/application_packet.py",
        "src/qkernel/compiler_candidates.py",
        "src/qkernel/circuit_manifest.py",
        "src/qkernel/correlation_study.py",
        "src/qkernel/factory_candidates.py",
        "src/qkernel/impact_register.py",
        "src/qkernel/kernel_census.py",
        "src/qkernel/resource_oracle.py",
        "src/qkernel/py.typed",
    ]:
        assert (ROOT / rel).exists()


def test_pyproject_has_license_and_sat_extra():
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")

    assert "Apache-2.0" in text
    assert "numpy>=1.26" in text
    assert "tomli>=2" in text
    assert "python-sat" in text
    assert "qkernel = [\"py.typed\"]" in text


def test_manifest_includes_current_release_artifacts():
    text = (ROOT / "MANIFEST.in").read_text(encoding="utf-8")

    assert "recursive-include paper *.tex *.bib *.md *.json *.pdf" in text
    assert "MANIFEST_QKERNEL.md" not in text
    assert "QKERNEL_NOTE_LOCATION.md" not in text


def test_compiler_optimizer_path_doc_exists():
    text = (ROOT / "docs/COMPILER_OPTIMIZER_PATH.md").read_text(encoding="utf-8")

    assert "not by relabeling kernel" in text
    assert "requires_semantic_equivalence_proof" in text
    assert "Q-Kernel reduces T-count" in text


def test_release_readiness_doc_tracks_workbench_commands():
    text = (ROOT / "docs/RELEASE_READINESS.md").read_text(encoding="utf-8")

    assert "application-packet" in text
    assert "--fail-on-blocked" in text
    assert "does not claim" in text
    assert "validated magic-state factory construction" in text
    assert "RELEASE_BUNDLE.md" in text
    assert "application-packet --fail-on-blocked` command is expected to exit nonzero" in text
    assert "release-audit` command is expected to pass" in text


def test_release_bundle_links_checks_and_claim_boundaries():
    text = (ROOT / "docs/RELEASE_BUNDLE.md").read_text(encoding="utf-8")

    assert "pytest -q" in text
    assert "qkernel release-audit --root ." in text
    assert "paper/repro_manifest_template.json" in text
    assert "MANIFEST.in" in text
    assert "does not claim" in text


def test_adjacent_repo_decision_recommends_not_splitting_yet():
    text = (ROOT / "docs/ADJACENT_REPO_DECISION.md").read_text(encoding="utf-8")

    assert "Do not split the repository yet" in text
    assert "qkernel-research-atlas" in text
    assert "Current Decision" in text


def test_research_plan_preserves_evidence_gates():
    text = (ROOT / "docs/RESEARCH_PLAN.md").read_text(encoding="utf-8")

    assert "Paper Tracks" in text
    assert "Minimum Evidence Gates" in text
    assert "application-packet --out-json" in text
    assert "does not claim" in text


def test_paper_scaffold_maps_tracks_to_missing_evidence():
    text = (ROOT / "paper/PAPER_SCAFFOLD.md").read_text(encoding="utf-8")

    assert "Track A" in text
    assert "Track D" in text
    assert "Missing before a paper claim" in text
    assert "Reproducibility Manifest Shape" in text
    assert "paper/repro_manifest_template.json" in text


def test_paper_repro_manifest_template_preserves_non_claims():
    import json

    data = json.loads((ROOT / "paper/repro_manifest_template.json").read_text(encoding="utf-8"))

    assert data["schema"] == "qkernel.paper_repro_manifest.v1"
    assert data["qkernel"]["git_commit"] == "REPLACE_WITH_QKERNEL_COMMIT"
    assert data["external_evidence_sources"]
    assert "compiler semantic proof missing" in data["blocked_claim_gates"]
    assert any("does not claim" in item for item in data["non_claims_for_appendix"])


def test_readme_local_markdown_links_exist():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    missing: list[str] = []

    for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
        if "://" in target or target.startswith("#"):
            continue
        path_text = target.split("#", 1)[0]
        if not path_text:
            continue
        if not (ROOT / path_text).exists():
            missing.append(target)

    assert missing == []
