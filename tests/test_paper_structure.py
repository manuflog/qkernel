from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper/qkernel_note.tex"


REQUIRED_SECTIONS = [
    r"\section{Purpose and scope}",
    r"\section{Related work and novelty hygiene}",
    r"\section{Weyl/Pauli measurement programs}",
    r"\section{Incidence cycles and the odd-\(Q\) criterion}",
    r"\section{Closed symplectic form for \(Q\)}",
    r"\section{Kernelization problem}",
    r"\section{Observable identity semantics}",
    r"\section{Input frontends}",
    r"\section{Algorithms and solvers}",
    r"\section{External SAT and MaxSAT workflows}",
    r"\section{Certificates}",
    r"\section{Peres--Mermin test case}",
    r"\section{Synthetic benchmarks}",
    r"\section{Tower and doubling scope}",
    r"\section{Limitations}",
    r"\section{Roadmap}",
]


FORBIDDEN_UNQUALIFIED_PHRASES = [
    "Q-Kernel is a magic-state optimizer",
    "Q-Kernel is a T-count",
    "passive dimension embedding is free",
    "tower compression is certified",
    "additive contextuality fuel",
]


def test_paper_has_required_sections():
    text = PAPER.read_text(encoding="utf-8")

    for section in REQUIRED_SECTIONS:
        assert section in text


def test_paper_does_not_use_forbidden_unqualified_claims():
    text = PAPER.read_text(encoding="utf-8")

    for phrase in FORBIDDEN_UNQUALIFIED_PHRASES:
        assert phrase not in text


def test_paper_states_safe_scope():
    text = PAPER.read_text(encoding="utf-8")

    assert "contextuality-kernel extractor" in text
    assert "not a magic-state optimizer" in text
    assert "not certify tower compression" in text
