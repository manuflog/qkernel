from __future__ import annotations

from pathlib import Path

from qkernel.release_audit import run_release_audit, write_release_audit_outputs


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments" / "output"


def run_audit() -> tuple[Path, Path]:
    OUT.mkdir(parents=True, exist_ok=True)
    report = run_release_audit(ROOT)
    json_path = OUT / "release_audit.json"
    md_path = OUT / "RELEASE_AUDIT.md"
    write_release_audit_outputs(report, json_path=json_path, markdown_path=md_path)
    return json_path, md_path


def main() -> None:
    json_path, md_path = run_audit()
    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")


if __name__ == "__main__":
    main()
