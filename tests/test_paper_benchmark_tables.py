from pathlib import Path

from experiments.render_paper_tables import generate_tables


ROOT = Path(__file__).resolve().parents[1]


def test_paper_tables_can_be_generated_without_rerunning_benchmarks():
    # The repository ships benchmark CSVs after the development workflow. This
    # test checks rendering only, not timing-sensitive benchmark execution.
    tex_path, md_path = generate_tables(run_benchmarks=False)

    assert tex_path.exists()
    assert md_path.exists()

    tex = tex_path.read_text(encoding="utf-8")
    md = md_path.read_text(encoding="utf-8")

    assert "tab:decomposition-benchmark" in tex
    assert "tab:solver-comparison" in tex
    assert "Synthetic decomposition benchmark" in tex
    assert "Generated paper benchmark tables" in md


def test_paper_inputs_generated_benchmark_tables():
    paper = (ROOT / "paper/qkernel_note.tex").read_text(encoding="utf-8")

    assert r"\input{generated_benchmark_tables}" in paper
