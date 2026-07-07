import json
import subprocess
import sys

from qkernel.application_prd import application_prd_dict, application_prd_markdown, next_application_prd


def test_application_prd_recommends_cli_first_workbench():
    data = application_prd_dict(next_application_prd())
    option_ids = {option["option_id"] for option in data["options"]}

    assert data["schema"] == "qkernel.application_prd.v1"
    assert "CLI-first application workbench" in data["recommended_v1"]
    assert "compiler_resource_workbench" in option_ids
    assert "circuit_builder_ui" in option_ids
    assert "factory_simulator_bridge" in option_ids
    assert "production optimizer or transpiler integration in v1" in data["non_goals"]
    json.dumps(data)


def test_application_prd_keeps_claim_gates_in_p0_requirements():
    data = application_prd_dict(next_application_prd())
    p0_names = {req["name"] for req in data["requirements"] if req["priority"] == "P0"}

    assert "Candidate packet schema" in p0_names
    assert "Evidence packet renderer" in p0_names
    assert "Claim-boundary gate" in p0_names
    assert any("missing semantic-equivalence proof blocks optimizer claims" in criterion
               for req in data["requirements"]
               for criterion in req["acceptance_criteria"])


def test_application_prd_markdown_covers_magic_compiler_and_factory_paths():
    md = application_prd_markdown(next_application_prd())

    assert "# PRD: QKernel Application Workbench" in md
    assert "Compiler/resource evidence workbench" in md
    assert "Circuit-builder readiness UI" in md
    assert "Magic-state factory simulator bridge" in md
    assert "does not claim qkernel optimizes T-count or T-depth by itself" in md


def test_cli_application_prd_writes_markdown(tmp_path):
    out = tmp_path / "application_prd.md"
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "qkernel.cli",
            "application-prd",
            "--out-md",
            str(out),
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    assert f"wrote Markdown application PRD: {out}" in proc.stdout
    data = json.loads(proc.stdout.split("\nwrote Markdown application PRD:", 1)[0])
    assert data["title"] == "PRD: QKernel Application Workbench"
    assert "Candidate packet schema" in out.read_text(encoding="utf-8")
