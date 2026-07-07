from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_package_metadata_files_exist():
    for rel in [
        "LICENSE",
        "CITATION.cff",
        "MANIFEST.in",
        "CHANGELOG.md",
        "docs/KERNEL_CENSUS.md",
        "docs/RESOURCE_ORACLE.md",
        "docs/COMPILER_CANDIDATES.md",
        "docs/CIRCUIT_MANIFEST.md",
        "docs/FACTORY_CANDIDATES.md",
        "docs/CORRELATION_STUDY.md",
        "docs/IMPACT_REGISTER.md",
        "docs/PRD_APPLICATION_WORKBENCH.md",
        "docs/PRD_COMPILER_MAGIC_FACTORY_BRIDGE.md",
        "examples/compiler_candidate_corpus.json",
        "examples/factory_candidate_corpus.json",
        "examples/resource_correlation_study.json",
        "examples/kernel_theorem_pins.json",
        "examples/kernel_census_targets.json",
        "examples/resource_metrics_stub.json",
        "src/qkernel/application_prd.py",
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
