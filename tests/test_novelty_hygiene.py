from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_paper_cites_saniga_holweck_prior_art():
    paper = (ROOT / "paper/qkernel_note.tex").read_text(encoding="utf-8")

    assert r"\section{Related work and novelty hygiene}" in paper
    assert "deBoutrayHolweckGiorgettiMassonSaniga2022" in paper
    assert "MullerSanigaGiorgettiDeBoutrayHolweck2023" in paper
    assert "does not claim novelty for the linear-system framing" in paper


def test_bibliography_has_finite_geometry_entries():
    bib = (ROOT / "paper/references.bib").read_text(encoding="utf-8")

    assert "deBoutrayHolweckGiorgettiMassonSaniga2022" in bib
    assert "Contextuality degree of quadrics" in bib
    assert "MullerSanigaGiorgettiDeBoutrayHolweck2023" in bib
    assert "New and improved bounds" in bib


def test_novelty_hygiene_doc_sets_boundaries():
    doc = (ROOT / "docs/NOVELTY_HYGIENE.md").read_text(encoding="utf-8")

    assert "Do not claim novelty" in doc
    assert "GF(2) incidence constraints" in doc
    assert "closed symplectic Q form" in doc
    assert "standalone verifiable certificates" in doc
