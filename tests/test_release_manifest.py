from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_release_manifest_points_to_note_files():
    manifest = (ROOT / "MANIFEST_QKERNEL.md").read_text(encoding="utf-8")
    locator = (ROOT / "QKERNEL_NOTE_LOCATION.md").read_text(encoding="utf-8")

    assert "paper/qkernel_note.tex" in manifest
    assert "paper/qkernel_note.pdf" in manifest
    assert "paper/qkernel_note.tex" in locator
    assert "paper/qkernel_note.pdf" in locator


def test_note_pdf_exists():
    assert (ROOT / "paper/qkernel_note.pdf").exists()


def test_paper_note_location_file_exists():
    text = (ROOT / "paper/NOTE_LOCATION.md").read_text(encoding="utf-8")
    assert "qkernel_note.tex" in text
    assert "qkernel_note.pdf" in text
