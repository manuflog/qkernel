import json
import subprocess
import sys
from pathlib import Path

from qkernel.kernel_census import (
    KernelTheoremPin,
    kernel_census_markdown,
    kernel_census_report_dict,
    load_kernel_census_targets,
    load_kernel_theorem_pins,
)


ROOT = Path(__file__).resolve().parents[1]


def test_kernel_census_pins_known_zoo_weights():
    data = kernel_census_report_dict()
    by_name = {entry["name"]: entry for entry in data["entries"]}

    assert data["schema"] == "qkernel.kernel_census.v1"
    assert by_name["peres_mermin"]["kernel_weight"] == 6
    assert by_name["doily_two_qubit"]["n_minimal_kernels"] == 10
    assert by_name["cert4_d4"]["d"] == 4
    assert by_name["cert4_d4"]["kernel_weight"] == 6
    assert by_name["single_context"]["contextual"] is False
    assert "does not prove global K(d,m) lower bounds" in data["non_claims"]
    assert data["research_targets"] == []
    json.dumps(data)


def test_kernel_census_summaries_are_witness_scoped():
    data = kernel_census_report_dict()
    summaries = {(s["d"], s["m"]): s for s in data["summaries"]}

    assert summaries[(2, 2)]["witnessed_min_kernel_weight"] == 6
    assert "peres_mermin" in summaries[(2, 2)]["witness_names"]
    assert summaries[(2, 2)]["global_K_proven"] is False
    assert summaries[(2, 2)]["global_K_value"] is None
    assert any("lower-bound proof" in item for item in summaries[(2, 2)]["proof_obligations"])
    assert summaries[(4, 2)]["witnessed_min_kernel_weight"] == 6
    assert "not a proof of global K(d,m)" in summaries[(4, 2)]["claim_scope"]


def test_cli_kernel_census_contextual_only():
    proc = subprocess.run(
        [sys.executable, "-m", "qkernel.cli", "kernel-census", "--contextual-only"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )

    data = json.loads(proc.stdout)
    assert data["entries"]
    assert all(entry["contextual"] for entry in data["entries"])


def test_kernel_census_accepts_external_theorem_pins():
    pins = load_kernel_theorem_pins(ROOT / "examples/kernel_theorem_pins.json")
    data = kernel_census_report_dict(theorem_pins=pins)
    summary = {(s["d"], s["m"]): s for s in data["summaries"]}[(4, 2)]

    assert data["theorem_pins"][0]["theorem_id"] == "K42_MINIMAL_CERTIFICATE"
    assert data["theorem_pin_audits"][0]["status"] == "matches_registered_witness"
    assert "cert4_d4" in data["theorem_pin_audits"][0]["witness_names"]
    assert summary["global_K_proven"] is True
    assert summary["global_K_value"] == 6
    assert summary["proof_obligations"] == []
    assert "K(4,2)=6" in summary["claim_scope"]


def test_kernel_census_rejects_pin_contradicting_zoo_witness():
    bad_pin = KernelTheoremPin(
        d=4,
        m=2,
        K=7,
        theorem_id="bad",
        source="test",
        proof_method="contradicts cert4_d4",
    )
    try:
        kernel_census_report_dict(theorem_pins=[bad_pin])
    except ValueError as exc:
        assert "cert4_d4" in str(exc)
        assert "kernel weight 6" in str(exc)
    else:
        raise AssertionError("contradictory theorem pin must be rejected")


def test_kernel_census_audits_pin_without_registered_witness():
    pin = KernelTheoremPin(
        d=8,
        m=2,
        K=6,
        theorem_id="K82_EXTERNAL",
        source="test",
        proof_method="external proof",
    )
    data = kernel_census_report_dict(theorem_pins=[pin])

    assert data["theorem_pin_audits"] == [{
        "d": 8,
        "m": 2,
        "K": 6,
        "theorem_id": "K82_EXTERNAL",
        "status": "no_registered_witness",
        "witnessed_min_kernel_weight": None,
        "witness_names": [],
        "detail": (
            "no contextual zoo witness is registered for d=8, m=2; "
            "the theorem pin is recorded as external metadata"
        ),
    }]


def test_kernel_census_audits_pin_stronger_than_registered_witnesses():
    pin = KernelTheoremPin(
        d=4,
        m=2,
        K=5,
        theorem_id="K42_STRONGER_EXTERNAL",
        source="test",
        proof_method="external proof",
    )
    data = kernel_census_report_dict(theorem_pins=[pin])
    summary = {(s["d"], s["m"]): s for s in data["summaries"]}[(4, 2)]
    audit = data["theorem_pin_audits"][0]

    assert summary["global_K_proven"] is True
    assert summary["global_K_value"] == 5
    assert audit["status"] == "stronger_than_registered_witnesses"
    assert audit["witnessed_min_kernel_weight"] == 6
    assert "cert4_d4" in audit["witness_names"]


def test_kernel_census_tracks_open_research_targets():
    data = kernel_census_report_dict(research_targets=[(8, 2), (16, 2), (8, 2)])
    targets = {(t["d"], t["m"]): t for t in data["research_targets"]}

    assert sorted(targets) == [(8, 2), (16, 2)]
    assert targets[(8, 2)]["status"] == "open_no_registered_witness"
    assert targets[(8, 2)]["witnessed_min_kernel_weight"] is None
    assert targets[(8, 2)]["global_K_proven"] is False
    assert any("construct or import" in item for item in targets[(8, 2)]["next_actions"])


def test_kernel_census_loads_target_plan_metadata():
    target_specs = load_kernel_census_targets(ROOT / "examples/kernel_census_targets.json")
    data = kernel_census_report_dict(research_targets=target_specs)
    targets = {(t["d"], t["m"]): t for t in data["research_targets"]}

    assert sorted(targets) == [(4, 2), (8, 2), (16, 2)]
    assert targets[(8, 2)]["target_id"] == "K82"
    assert targets[(8, 2)]["priority"] == "next"
    assert targets[(8, 2)]["source"] == "research-atlas-v7/KC"
    assert "Next even-dimension" in targets[(8, 2)]["rationale"]
    assert targets[(4, 2)]["status"] == "witnessed_unpinned"
    assert "cert4_d4" in targets[(4, 2)]["witness_names"]


def test_kernel_census_tracks_witnessed_and_pinned_targets():
    pins = load_kernel_theorem_pins(ROOT / "examples/kernel_theorem_pins.json")
    data = kernel_census_report_dict(
        theorem_pins=pins,
        research_targets=[(4, 2), (2, 2)],
    )
    targets = {(t["d"], t["m"]): t for t in data["research_targets"]}

    assert targets[(4, 2)]["status"] == "pinned_with_registered_witness"
    assert targets[(4, 2)]["global_K_value"] == 6
    assert targets[(4, 2)]["theorem_id"] == "K42_MINIMAL_CERTIFICATE"
    assert "cert4_d4" in targets[(4, 2)]["witness_names"]
    assert targets[(2, 2)]["status"] == "witnessed_unpinned"
    assert targets[(2, 2)]["witnessed_min_kernel_weight"] == 6


def test_kernel_census_markdown_contains_scope_and_tables():
    pins = load_kernel_theorem_pins(ROOT / "examples/kernel_theorem_pins.json")
    md = kernel_census_markdown(kernel_census_report_dict(theorem_pins=pins, research_targets=[(8, 2)]))

    assert "# Kernel Census" in md
    assert "## By `(d,m)`" in md
    assert "## Proof Obligations" in md
    assert "## Theorem Pins" in md
    assert "## Theorem Pin Audit" in md
    assert "## Research Targets" in md
    assert "matches_registered_witness" in md
    assert "open_no_registered_witness" in md
    assert "K82" not in md
    assert "K42_MINIMAL_CERTIFICATE" in md
    assert "peres_mermin" in md
    assert "does not prove global K(d,m) lower bounds" in md


def test_cli_kernel_census_writes_markdown(tmp_path):
    out = tmp_path / "kernel_census.md"
    proc = subprocess.run(
        [sys.executable, "-m", "qkernel.cli", "kernel-census", "--out-md", str(out)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )

    # The command still emits JSON first; the trailing status line is for humans.
    assert f"wrote Markdown kernel census: {out}" in proc.stdout
    text = out.read_text(encoding="utf-8")
    assert "# Kernel Census" in text
    assert "cert4_d4" in text


def test_cli_kernel_census_with_theorem_pins():
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "qkernel.cli",
            "kernel-census",
            "--theorem-pins",
            str(ROOT / "examples/kernel_theorem_pins.json"),
            "--target-dm",
            "8,2",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )

    data = json.loads(proc.stdout)
    summary = {(s["d"], s["m"]): s for s in data["summaries"]}[(4, 2)]
    assert summary["global_K_proven"] is True
    assert data["theorem_pins"][0]["K"] == 6
    assert data["research_targets"][0]["status"] == "open_no_registered_witness"


def test_cli_kernel_census_with_target_file():
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "qkernel.cli",
            "kernel-census",
            "--target-file",
            str(ROOT / "examples/kernel_census_targets.json"),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )

    data = json.loads(proc.stdout)
    targets = {(t["d"], t["m"]): t for t in data["research_targets"]}
    assert targets[(8, 2)]["target_id"] == "K82"
    assert targets[(16, 2)]["status"] == "open_no_registered_witness"
