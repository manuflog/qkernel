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
        "examples/application_packet_demo.json",
        "examples/circuit_manifest_d4_probe.json",
        "examples/compiler_candidate_corpus.json",
        "examples/factory_candidate_corpus.json",
        "examples/resource_correlation_study.json",
        "examples/kernel_theorem_pins.json",
        "examples/kernel_census_targets.json",
        "examples/resource_feature_pm_probe.json",
        "examples/resource_metrics_stub.json",
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
