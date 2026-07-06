from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python <3.11 local tooling
    import tomli as tomllib


ROOT = Path(__file__).resolve().parents[1]


def test_package_metadata_files_exist():
    for rel in [
        "LICENSE",
        "CITATION.cff",
        "MANIFEST.in",
        "CHANGELOG.md",
        "src/qkernel/py.typed",
    ]:
        assert (ROOT / rel).exists()


def test_pyproject_has_license_and_sat_extra():
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")

    assert "Apache-2.0" in text
    assert "python-sat" in text
    assert "qkernel = [\"py.typed\"]" in text


def test_dev_extra_covers_workflow_test_dependencies():
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    dev = data["project"]["optional-dependencies"]["dev"]

    assert any(dep.startswith("pytest") for dep in dev)
    assert any(dep.startswith("numpy") for dep in dev)


def test_compiler_optimizer_path_doc_exists():
    text = (ROOT / "docs/COMPILER_OPTIMIZER_PATH.md").read_text(encoding="utf-8")

    assert "not by relabeling kernel" in text
    assert "requires_semantic_equivalence_proof" in text
    assert "Q-Kernel reduces T-count" in text
