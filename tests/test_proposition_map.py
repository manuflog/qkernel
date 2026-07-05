from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper/qkernel_note.tex"
MAP = ROOT / "docs/PROPOSITION_MAP.md"


LABELS = [
    "prop:integer-carry",
    "prop:odd-q-criterion",
    "prop:closed-q-form",
    "prop:component-decomposition",
    "prop:certificate-soundness",
]


def test_paper_has_proposition_labels():
    text = PAPER.read_text(encoding="utf-8")

    for label in LABELS:
        assert rf"\label{{{label}}}" in text


def test_paper_references_proposition_labels_in_code_map():
    text = PAPER.read_text(encoding="utf-8")

    for label in LABELS:
        assert rf"\ref{{{label}}}" in text


def test_docs_proposition_map_mentions_labels_and_code_modules():
    text = MAP.read_text(encoding="utf-8")

    for label in LABELS:
        assert label in text

    for module in [
        "symplectic.py",
        "carry.py",
        "analyzer.py",
        "closed_form.py",
        "decompose.py",
        "certificate.py",
        "verify.py",
    ]:
        assert module in text


def test_paper_contains_proof_environments_for_internal_propositions():
    text = PAPER.read_text(encoding="utf-8")

    assert r"\begin{proof}" in text
    assert "Component decomposition" in text
    assert "Closed symplectic form" in text
