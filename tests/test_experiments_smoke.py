import importlib.util
from pathlib import Path


def test_experiment_scripts_exist():
    root = Path(__file__).resolve().parents[1]
    assert (root / "experiments/benchmark_decomposition.py").exists()
    assert (root / "experiments/compare_solvers.py").exists()
    assert (root / "experiments/generate_noisy_pm.py").exists()


def test_generate_noisy_pm_importable():
    root = Path(__file__).resolve().parents[1]
    path = root / "experiments/generate_noisy_pm.py"
    spec = importlib.util.spec_from_file_location("generate_noisy_pm", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)

    program = mod.noisy_pm_with_disconnected_checks(3)
    assert len(program.contexts) == 9


def test_connected_ladder_generator_validates():
    root = Path(__file__).resolve().parents[1]
    path = root / "experiments/generate_noisy_pm.py"
    spec = importlib.util.spec_from_file_location("generate_noisy_pm", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)

    from qkernel.validate import validate_program
    from qkernel.optimizer import compress_min_odd_q

    program = mod.noisy_pm_with_connected_zero_carry_ladder(10)
    validate_program(program)
    kernel = compress_min_odd_q(program)
    assert kernel.contextual
    assert kernel.compressed_contexts == 6
