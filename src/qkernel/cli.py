from __future__ import annotations

import argparse
import json

from .analyzer import analyze
from .canonicalize import canonicalization_report, canonicalize_program
from .certificate import kernel_to_json, kernel_to_markdown, write_certificate, verify_certificate_file, inspect_certificate
from .decompose import component_summary
from .io import load_program, dump_program
from .optimizer import compress_min_odd_q
from .pauli import load_pauli_program
from .pauli_schedule import load_pauli_schedule
from .verify import verify_kernel
from .adapters.pauli_table import load_pauli_table
from .adapters.stim_lite import load_stim_lite_program, load_stim_lite_schedule
from .adapters.qiskit_lite import load_qiskit_lite_program, load_qiskit_lite_layers
from .sat_export import write_dimacs_cnf
from .maxsat_export import write_wcnf_maxsat
from .solver_output import import_solver_solution, import_solver_solution_and_write_certificate
from .closed_form import compare_q_forms, is_cycle
from .tower import tower_law_report
from .fiber_lift import find_even_base_fiber_lift, fiber_lift_result_dict
from .lift_pipeline import run_lift_pipeline, lift_pipeline_report_dict, write_lift_pipeline_outputs
from .release_audit import run_release_audit, release_audit_dict, write_release_audit_outputs
from .github_ready import run_github_ready_check, github_ready_report_dict, write_github_ready_report
from .backends.pysat_backend import OptionalBackendUnavailable, solve_sat_with_pysat, solve_maxsat_with_rc2
from .compiler import compiler_report_dict, compare_compiler_pass_dict
from .kernel_census import kernel_census_report_dict
from .selftest import run_selftest_dict
from .rewrite_policy import list_rewrite_policies_dict, assess_rewrite_candidate_dict
from .valuation import check_zd_valuation, check_kernel_zd_valuation, two_primary_report, spectrum_summary
from .export_circuit import export_qiskit_protocol
from .magic import (
    analyze_magic_portfolio_file,
    analyze_magic_protocol,
    analyze_magic_protocol_record,
    generated_magic_report_dict,
    generate_magic_candidates_from_paulis,
    load_magic_protocol,
    magic_audit_report_dict,
    magic_portfolio_report_dict,
    magic_report_dict,
    magic_zoo_report_dict,
    run_magic_audit,
    run_magic_zoo,
)
from .magic_report import magic_report_markdown, magic_search_markdown, write_markdown_report
from .magic_search import magic_search_report_dict, search_magic_candidates_from_paulis
from .magic_templates import (
    assess_magic_templates,
    magic_template_assessments_dict,
    magic_templates_catalog_dict,
)


def _add_solver_args(cmd) -> None:
    cmd.add_argument("--solver", choices=["auto", "span", "bounded-weight", "branch-bound"], default="auto")
    cmd.add_argument("--max-cycle-dim", type=int, default=24)
    cmd.add_argument("--max-weight", type=int, default=8)
    cmd.add_argument("--max-checks", type=int, default=2_000_000)
    cmd.add_argument("--max-nodes", type=int, default=1_000_000)
    cmd.add_argument("--no-decompose", action="store_true", help="disable component decomposition")
    cmd.add_argument(
        "--canonicalize",
        choices=["none", "by-vector", "by-vector-force"],
        default="none",
        help="explicit observable canonicalization mode",
    )


def _load_by_kind(path: str, kind: str):
    if kind == "weyl":
        return load_program(path)
    if kind == "pauli":
        return load_pauli_program(path)
    if kind == "schedule":
        return load_pauli_schedule(path)
    if kind == "table":
        return load_pauli_table(path)
    if kind == "stim-lite":
        return load_stim_lite_program(path)
    if kind == "qiskit-lite":
        return load_qiskit_lite_program(path)
    raise ValueError(f"unknown input kind {kind!r}")


def _print_analysis(result) -> None:
    print(f"contextual: {result.contextual}")
    print(f"reason: {result.reason}")
    print(f"b_vector: {result.b_vector}")
    print(f"cycle_basis_dimension: {len(result.cycle_basis)}")
    print(f"q_value: {result.q_value}")
    print(f"selected_contexts: {result.selected_contexts}")


def _compress(program, args) -> None:
    kernel = compress_min_odd_q(
        program,
        solver=args.solver,
        max_cycle_dim=args.max_cycle_dim,
        max_weight=args.max_weight,
        max_checks=args.max_checks,
        max_nodes=args.max_nodes,
        decompose=not args.no_decompose,
        canonicalize=args.canonicalize,
    )
    effective_program = canonicalize_program(program, mode=args.canonicalize)
    print(kernel_to_json(effective_program, kernel) if args.json else kernel_to_markdown(effective_program, kernel))


def main() -> None:
    parser = argparse.ArgumentParser(prog="qkernel")
    sub = parser.add_subparsers(dest="command", required=True)


    selftest_cmd = sub.add_parser("self-test", help="run built-in Peres-Mermin smoke test")

    analyze_cmd = sub.add_parser("analyze", help="detect odd-Q contextuality in Weyl JSON")
    analyze_cmd.add_argument("path")

    compress_cmd = sub.add_parser("compress", help="extract a minimal odd-Q kernel from Weyl JSON")
    compress_cmd.add_argument("path")
    compress_cmd.add_argument("--json", action="store_true", help="print JSON certificate")
    _add_solver_args(compress_cmd)

    enum_cmd = sub.add_parser(
        "enumerate-kernels",
        help="count all distinct minimal odd-Q kernels (contextuality-structure invariant)",
    )
    enum_cmd.add_argument("path")
    enum_cmd.add_argument("--max-cycle-dim", type=int, default=20)

    census_cmd = sub.add_parser("kernel-census", help="run conservative minimal-kernel census over benchmark zoo")
    census_cmd.add_argument("--contextual-only", action="store_true", help="omit non-contextual control instances")

    activation_cmd = sub.add_parser("activation", help="check contextuality activation by d->2d embedding of a Weyl base")
    activation_cmd.add_argument("path")

    mintest_cmd = sub.add_parser("minimal-test", help="cheapest contextuality test from a device's measurable Paulis")
    mintest_cmd.add_argument("paulis", nargs="+", help="measurable Pauli strings, e.g. XI IX XX IY YI YY XY YX ZZ")
    mintest_cmd.add_argument("--top", type=int, default=1)

    actres_cmd = sub.add_parser("activation-resource", help="cheapest contextuality test activated by d->2d embedding of a non-contextual Weyl base")
    actres_cmd.add_argument("path")

    analyze_pauli_cmd = sub.add_parser("analyze-pauli", help="detect odd-Q contextuality in Pauli-context JSON")
    analyze_pauli_cmd.add_argument("path")

    compress_pauli_cmd = sub.add_parser("compress-pauli", help="extract a minimal odd-Q kernel from Pauli-context JSON")
    compress_pauli_cmd.add_argument("path")
    compress_pauli_cmd.add_argument("--json", action="store_true", help="print JSON certificate")
    _add_solver_args(compress_pauli_cmd)


    analyze_table_cmd = sub.add_parser("analyze-table", help="load Pauli table CSV/JSON, then analyze")
    analyze_table_cmd.add_argument("path")

    compress_table_cmd = sub.add_parser("compress-table", help="load Pauli table CSV/JSON, then compress")
    compress_table_cmd.add_argument("path")
    compress_table_cmd.add_argument("--json", action="store_true", help="print JSON certificate")
    _add_solver_args(compress_table_cmd)

    analyze_schedule_cmd = sub.add_parser("analyze-schedule", help="extract contexts from grouped Pauli schedule, then analyze")
    analyze_schedule_cmd.add_argument("path")

    compress_schedule_cmd = sub.add_parser("compress-schedule", help="extract contexts from grouped Pauli schedule, then compress")
    compress_schedule_cmd.add_argument("path")
    compress_schedule_cmd.add_argument("--json", action="store_true", help="print JSON certificate")
    _add_solver_args(compress_schedule_cmd)



    analyze_qiskit_cmd = sub.add_parser("analyze-qiskit-lite", help="parse Qiskit-lite Pauli JSON, then analyze")
    analyze_qiskit_cmd.add_argument("path")

    compress_qiskit_cmd = sub.add_parser("compress-qiskit-lite", help="parse Qiskit-lite Pauli JSON, then compress")
    compress_qiskit_cmd.add_argument("path")
    compress_qiskit_cmd.add_argument("--json", action="store_true", help="print JSON certificate")
    _add_solver_args(compress_qiskit_cmd)

    inspect_qiskit_cmd = sub.add_parser("inspect-qiskit-lite", help="show layers parsed from Qiskit-lite JSON")
    inspect_qiskit_cmd.add_argument("path")

    analyze_stim_cmd = sub.add_parser("analyze-stim-lite", help="parse Stim-lite MPP subset, then analyze")
    analyze_stim_cmd.add_argument("path")
    analyze_stim_cmd.add_argument("--strict", action="store_true", help="reject unsupported non-MPP instructions")

    compress_stim_cmd = sub.add_parser("compress-stim-lite", help="parse Stim-lite MPP subset, then compress")
    compress_stim_cmd.add_argument("path")
    compress_stim_cmd.add_argument("--strict", action="store_true", help="reject unsupported non-MPP instructions")
    compress_stim_cmd.add_argument("--json", action="store_true", help="print JSON certificate")
    _add_solver_args(compress_stim_cmd)

    inspect_stim_cmd = sub.add_parser("inspect-stim-lite", help="show layers parsed from Stim-lite MPP subset")
    inspect_stim_cmd.add_argument("path")
    inspect_stim_cmd.add_argument("--strict", action="store_true", help="reject unsupported non-MPP instructions")

    verify_cmd = sub.add_parser("verify-demo", help="run optimizer and verify the resulting certificate")
    verify_cmd.add_argument("path")
    verify_cmd.add_argument("--input", choices=["weyl", "pauli", "schedule", "table", "stim-lite", "qiskit-lite"], default="weyl")
    _add_solver_args(verify_cmd)


    cert_cmd = sub.add_parser("certify", help="write a standalone odd-Q kernel certificate")
    cert_cmd.add_argument("path")
    cert_cmd.add_argument("--input", choices=["weyl", "pauli", "schedule", "table", "stim-lite", "qiskit-lite"], default="weyl")
    cert_cmd.add_argument("--out", required=True)
    _add_solver_args(cert_cmd)






    qforms_cmd = sub.add_parser("q-forms", help="compare lambda·b and closed symplectic Q forms for selected contexts")
    qforms_cmd.add_argument("path")
    qforms_cmd.add_argument("--input", choices=["weyl", "pauli", "schedule", "table", "stim-lite", "qiskit-lite"], default="weyl")
    qforms_cmd.add_argument("--contexts", required=True, help="comma-separated context indices, e.g. 0,1,2")





    github_ready_cmd = sub.add_parser("github-ready", help="check GitHub alpha repository scaffolding")
    github_ready_cmd.add_argument("--root", default=".", help="repository root")
    github_ready_cmd.add_argument("--out-json", help="optional JSON report path")
    github_ready_cmd.add_argument("--out-md", help="optional Markdown report path")

    release_audit_cmd = sub.add_parser("release-audit", help="run release/readiness audit")
    release_audit_cmd.add_argument("--root", default=None, help="repository root; defaults to installed package root")
    release_audit_cmd.add_argument("--out-json", help="optional JSON audit path")
    release_audit_cmd.add_argument("--out-md", help="optional Markdown audit path")

    lift_pipeline_cmd = sub.add_parser("lift-pipeline", help="run fiber-lift -> Z_d valuation -> tower-law report")
    lift_pipeline_cmd.add_argument("path")
    lift_pipeline_cmd.add_argument("--input", choices=["weyl", "pauli", "schedule", "table", "stim-lite", "qiskit-lite"], default="weyl")
    lift_pipeline_cmd.add_argument("--contexts", help="comma-separated selected context indices; defaults to all contexts")
    lift_pipeline_cmd.add_argument("--out-program", help="optional output Weyl JSON path for constructed lift")
    lift_pipeline_cmd.add_argument("--out-json", help="optional JSON report path")
    lift_pipeline_cmd.add_argument("--out-md", help="optional Markdown report path")

    fiber_lift_cmd = sub.add_parser("fiber-lift", help="construct a validated d -> 2d fiber lift when possible")
    fiber_lift_cmd.add_argument("path")
    fiber_lift_cmd.add_argument("--input", choices=["weyl", "pauli", "schedule", "table", "stim-lite", "qiskit-lite"], default="weyl")
    fiber_lift_cmd.add_argument("--out", help="optional output Weyl JSON path for constructed lift")
    fiber_lift_cmd.add_argument("--include-program", action="store_true", help="include lifted program in JSON output")

    tower_cmd = sub.add_parser("tower-scope", help="certified closed tower/doubling-law generativity report")
    tower_cmd.add_argument("path")
    tower_cmd.add_argument("--input", choices=["weyl", "pauli", "schedule", "table", "stim-lite", "qiskit-lite"], default="weyl")
    tower_cmd.add_argument("--contexts", required=True, help="comma-separated context indices, e.g. 0,1,2")
    tower_cmd.add_argument("--base-d", type=int, default=None, help="base modulus d for a d -> 2d fiber lift")

    import_solver_cmd = sub.add_parser("import-solver-output", help="import external SAT/MaxSAT assignment and optionally write certificate")
    import_solver_cmd.add_argument("path")
    import_solver_cmd.add_argument("--input", choices=["weyl", "pauli", "schedule", "table", "stim-lite", "qiskit-lite"], default="weyl")
    import_solver_cmd.add_argument("--model", required=True, help="Q-Kernel CNF/WCNF file with lambda_var comments")
    import_solver_cmd.add_argument("--solution", required=True, help="external solver output file")
    import_solver_cmd.add_argument("--out", help="optional output certificate path")





    zd_cmd = sub.add_parser("zd-valuation", help="check genuine Z_d valuation-system contextuality")
    zd_cmd.add_argument("path")
    zd_cmd.add_argument("--input", choices=["weyl", "pauli", "schedule", "table", "stim-lite", "qiskit-lite"], default="weyl")

    two_primary_cmd = sub.add_parser("two-primary", help="report 2-primary structure of the obstruction value and mod-2 shadow value-faithfulness")
    two_primary_cmd.add_argument("path")
    two_primary_cmd.add_argument("--input", choices=["weyl", "pauli", "schedule", "table", "stim-lite", "qiskit-lite"], default="weyl")

    spectrum_cmd = sub.add_parser("spectrum", help="obstruction spectrum H(d)={0,d/2} + 2-primary structure for a local dimension d (no program file needed)")
    spectrum_cmd.add_argument("--d", type=int, required=True, help="local dimension d")

    export_circuit_cmd = sub.add_parser("export-circuit", help="export a runnable Qiskit measurement protocol for a 2-qubit kernel (theory -> runnable hardware test)")
    export_circuit_cmd.add_argument("path")
    export_circuit_cmd.add_argument("--input", choices=["weyl", "pauli", "schedule", "table", "stim-lite", "qiskit-lite"], default="weyl")
    export_circuit_cmd.add_argument("--out", help="write the runnable script to this path", default=None)
    export_circuit_cmd.add_argument("--contexts", help="comma-separated context indices (default: all)", default=None)
    export_circuit_cmd.add_argument("--no-verify", action="store_true", help="skip exact-sim verification (not recommended)")

    rewrite_policies_cmd = sub.add_parser("rewrite-policies", help="list Q-Kernel rewrite/optimizer policy guardrails")

    assess_rewrite_cmd = sub.add_parser("assess-rewrite", help="assess a rewrite claim policy")
    assess_rewrite_cmd.add_argument(
        "policy_id",
        choices=[
            "safe_diagnostic_prune",
            "requires_external_semantics",
            "experimental_resource_probe",
            "forbidden_resource_claim",
        ],
    )

    compiler_report_cmd = sub.add_parser("compiler-report", help="compiler-facing odd-Q diagnostic report")
    compiler_report_cmd.add_argument("path")
    compiler_report_cmd.add_argument("--input", choices=["weyl", "pauli", "schedule", "table", "stim-lite", "qiskit-lite"], default="weyl")

    compare_pass_cmd = sub.add_parser("compare-pass", help="compare before/after programs as candidate compiler-pass diagnostics")
    compare_pass_cmd.add_argument("before")
    compare_pass_cmd.add_argument("after")
    compare_pass_cmd.add_argument("--input", choices=["weyl", "pauli", "schedule", "table", "stim-lite", "qiskit-lite"], default="weyl")

    pysat_cmd = sub.add_parser("solve-pysat", help="optional PySAT fixed-k feasibility backend")
    pysat_cmd.add_argument("path")
    pysat_cmd.add_argument("--input", choices=["weyl", "pauli", "schedule", "table", "stim-lite", "qiskit-lite"], default="weyl")
    pysat_cmd.add_argument("--max-weight", type=int, default=None)
    pysat_cmd.add_argument("--solver-name", default="cadical153")
    pysat_cmd.add_argument("--out", help="optional output certificate path")

    rc2_cmd = sub.add_parser("solve-rc2", help="optional PySAT RC2 MaxSAT backend")
    rc2_cmd.add_argument("path")
    rc2_cmd.add_argument("--input", choices=["weyl", "pauli", "schedule", "table", "stim-lite", "qiskit-lite"], default="weyl")
    rc2_cmd.add_argument("--out", help="optional output certificate path")

    maxsat_cmd = sub.add_parser("export-maxsat", help="export minimum odd-Q kernel problem as WCNF MaxSAT")
    maxsat_cmd.add_argument("path")
    maxsat_cmd.add_argument("--input", choices=["weyl", "pauli", "schedule", "table", "stim-lite", "qiskit-lite"], default="weyl")
    maxsat_cmd.add_argument("--out", required=True)

    sat_cmd = sub.add_parser("export-sat", help="export odd-Q feasibility problem as DIMACS CNF")
    sat_cmd.add_argument("path")
    sat_cmd.add_argument("--input", choices=["weyl", "pauli", "schedule", "table", "stim-lite", "qiskit-lite"], default="weyl")
    sat_cmd.add_argument("--out", required=True)
    sat_cmd.add_argument("--max-weight", type=int, default=None)
    sat_cmd.add_argument("--max-cardinality-clauses", type=int, default=250_000)

    inspect_cert_cmd = sub.add_parser("inspect-certificate", help="inspect certificate metadata without verifying against a program")
    inspect_cert_cmd.add_argument("certificate")

    verify_cert_cmd = sub.add_parser("verify-certificate", help="verify a saved certificate against an input program")
    verify_cert_cmd.add_argument("path")
    verify_cert_cmd.add_argument("--input", choices=["weyl", "pauli", "schedule", "table", "stim-lite", "qiskit-lite"], default="weyl")
    verify_cert_cmd.add_argument("--certificate", required=True)

    components_cmd = sub.add_parser("components", help="show context-observable connected components")
    components_cmd.add_argument("path")
    components_cmd.add_argument("--input", choices=["weyl", "pauli", "schedule", "table", "stim-lite", "qiskit-lite"], default="weyl")
    components_cmd.add_argument("--canonicalize", choices=["none", "by-vector", "by-vector-force"], default="none")

    canon_cmd = sub.add_parser("canonicalize-report", help="report duplicate Weyl labels")
    canon_cmd.add_argument("path")
    canon_cmd.add_argument("--input", choices=["weyl", "pauli", "schedule", "table", "stim-lite", "qiskit-lite"], default="weyl")

    magic_analyze_cmd = sub.add_parser("magic-analyze", help="MagicScout diagnostic for an input program")
    magic_analyze_cmd.add_argument("path")
    magic_analyze_cmd.add_argument("--input", choices=["weyl", "pauli", "schedule", "table", "stim-lite", "qiskit-lite"], default="weyl")
    magic_analyze_cmd.add_argument("--target", default="generic_non_clifford")
    magic_analyze_cmd.add_argument("--protocol-id", default="candidate_protocol")
    magic_analyze_cmd.add_argument("--certify-minimal", action="store_true")
    magic_analyze_cmd.add_argument("--no-enumerate", action="store_true")

    magic_protocol_cmd = sub.add_parser("magic-protocol", help="MagicScout protocol-schema diagnostic")
    magic_protocol_cmd.add_argument("path")
    magic_protocol_cmd.add_argument("--certify-minimal", action="store_true")
    magic_protocol_cmd.add_argument("--no-enumerate", action="store_true")

    magic_portfolio_cmd = sub.add_parser("magic-portfolio", help="rank a portfolio of MagicScout protocol records")
    magic_portfolio_cmd.add_argument("path")

    magic_zoo_cmd = sub.add_parser("magic-zoo", help="rank Contextuality Benchmark Zoo instances with MagicScout")
    magic_zoo_cmd.add_argument("--include-noncontextual", action="store_true")
    magic_zoo_cmd.add_argument("--top", type=int, default=None)

    magic_generate_cmd = sub.add_parser("magic-generate", help="generate MagicScout candidates from available Pauli operators")
    magic_generate_cmd.add_argument("paulis", nargs="+")
    magic_generate_cmd.add_argument("--target", default="generic_non_clifford")
    magic_generate_cmd.add_argument("--top", type=int, default=10)

    magic_audit_cmd = sub.add_parser("magic-audit", help="run MagicScout claim-scope/readiness audit")

    magic_templates_cmd = sub.add_parser("magic-templates", help="list MagicScout factory-template checklists")

    magic_template_assess_cmd = sub.add_parser("magic-template-assess", help="assess MagicScout template compatibility for a protocol")
    magic_template_assess_cmd.add_argument("path")
    magic_template_assess_cmd.add_argument("--template", action="append", dest="templates", help="template id to require; repeatable")

    magic_search_cmd = sub.add_parser("magic-search", help="search available Pauli operators for MagicScout candidates")
    magic_search_cmd.add_argument("paulis", nargs="+")
    magic_search_cmd.add_argument("--target", default="generic_non_clifford")
    magic_search_cmd.add_argument("--top", type=int, default=10)
    magic_search_cmd.add_argument("--candidates", type=int, default=50)
    magic_search_cmd.add_argument("--required-template", action="append", default=[])
    magic_search_cmd.add_argument("--certify-minimal", action="store_true")

    magic_report_cmd = sub.add_parser("magic-report", help="write a Markdown MagicScout protocol report")
    magic_report_cmd.add_argument("path")
    magic_report_cmd.add_argument("--out", required=True)

    magic_search_report_cmd = sub.add_parser("magic-search-report", help="write a Markdown MagicScout search report from JSON")
    magic_search_report_cmd.add_argument("path")
    magic_search_report_cmd.add_argument("--out", required=True)

    args = parser.parse_args()

    if args.command == "self-test":
        print(json.dumps(run_selftest_dict(), indent=2))

    elif args.command == "analyze":
        _print_analysis(analyze(load_program(args.path)))

    elif args.command == "enumerate-kernels":
        from .solvers import find_all_min_odd_cycles, hamming_weight

        program = load_program(args.path)
        try:
            cycles = find_all_min_odd_cycles(program, max_cycle_dim=args.max_cycle_dim)
        except ValueError as exc:
            print(f"cannot enumerate: {exc}")
            return 0
        if not cycles:
            print("non-contextual: no odd-Q kernel.")
        else:
            w = hamming_weight(cycles[0])
            print(f"{len(cycles)} distinct minimal odd-Q kernel(s), each of weight {w}.")
            for i, lam in enumerate(cycles):
                sel = [j for j, bit in enumerate(lam) if bit]
                print(f"  kernel {i + 1}: contexts {sel}")

    elif args.command == "kernel-census":
        print(json.dumps(
            kernel_census_report_dict(include_noncontextual=not args.contextual_only),
            indent=2,
        ))

    elif args.command == "activation":
        from .embedding import activation_report
        r = activation_report(load_program(args.path))
        print(f"base d={r.base_d}: contextual={r.base_contextual} ({r.base_contexts} contexts)")
        print(f"fiber d={r.fiber_d}: contextual={r.fiber_contextual} ({r.fiber_contexts} contexts)")
        print(f"activated={r.activated} -- {r.reason}")

    elif args.command == "minimal-test":
        from .experiment_design import minimal_contextuality_tests
        tests = minimal_contextuality_tests(args.paulis, top=args.top)
        if not tests:
            print("no contextuality test: the measurable set is non-contextual.")
        else:
            print(f"{len(tests)} cheapest test(s); each {tests[0].n_contexts} settings, {tests[0].n_observables} observables.")
            for k, t in enumerate(tests):
                print(f"  test {k+1} (value d/2 = {t.obstruction_value}, verified={t.verified}):")
                for ctx in t.contexts:
                    print(f"    measure together: {ctx}")

    elif args.command == "activation-resource":
        from .embedding import activated_resource
        r = activated_resource(load_program(args.path))
        if not r.activated:
            print(f"not activated: {r.reason}")
        else:
            print(f"activated: base d={r.base_d} (non-contextual) -> fiber d={r.fiber_d} (contextual).")
            print(f"cheapest activated test: {r.test_weight} settings, value d/2={r.obstruction_value}, verified={r.verified}")

    elif args.command == "compress":
        _compress(load_program(args.path), args)

    elif args.command == "analyze-pauli":
        _print_analysis(analyze(load_pauli_program(args.path)))

    elif args.command == "compress-pauli":
        _compress(load_pauli_program(args.path), args)


    elif args.command == "analyze-table":
        _print_analysis(analyze(load_pauli_table(args.path)))

    elif args.command == "compress-table":
        _compress(load_pauli_table(args.path), args)

    elif args.command == "analyze-schedule":
        _print_analysis(analyze(load_pauli_schedule(args.path)))

    elif args.command == "compress-schedule":
        _compress(load_pauli_schedule(args.path), args)



    elif args.command == "analyze-qiskit-lite":
        _print_analysis(analyze(load_qiskit_lite_program(args.path)))

    elif args.command == "compress-qiskit-lite":
        _compress(load_qiskit_lite_program(args.path), args)

    elif args.command == "inspect-qiskit-lite":
        parsed = load_qiskit_lite_layers(args.path)
        print(json.dumps({
            "qubit_order": parsed.qubit_order,
            "layers": parsed.layers,
            "ignored_coefficients": parsed.ignored_coefficients,
        }, indent=2))

    elif args.command == "analyze-stim-lite":
        _print_analysis(analyze(load_stim_lite_program(args.path, strict=args.strict)))

    elif args.command == "compress-stim-lite":
        _compress(load_stim_lite_program(args.path, strict=args.strict), args)

    elif args.command == "inspect-stim-lite":
        parsed = load_stim_lite_schedule(args.path, strict=args.strict)
        print(json.dumps({
            "num_qubits": parsed.num_qubits,
            "layers": parsed.layers,
            "ignored_lines": parsed.ignored_lines,
        }, indent=2))

    elif args.command == "verify-demo":
        program = _load_by_kind(args.path, args.input)
        effective_program = canonicalize_program(program, mode=args.canonicalize)
        kernel = compress_min_odd_q(
            program,
            solver=args.solver,
            max_cycle_dim=args.max_cycle_dim,
            max_weight=args.max_weight,
            max_checks=args.max_checks,
            max_nodes=args.max_nodes,
            decompose=not args.no_decompose,
            canonicalize=args.canonicalize,
        )
        verification = verify_kernel(effective_program, kernel)
        print(f"kernel_contextual: {kernel.contextual}")
        print(f"verification_valid: {verification.valid}")
        print(f"reason: {verification.reason}")
        print(f"lambda: {verification.lambda_vector}")
        print(f"q_value: {verification.q_value}")


    elif args.command == "certify":
        program = _load_by_kind(args.path, args.input)
        effective_program = canonicalize_program(program, mode=args.canonicalize)
        kernel = compress_min_odd_q(
            program,
            solver=args.solver,
            max_cycle_dim=args.max_cycle_dim,
            max_weight=args.max_weight,
            max_checks=args.max_checks,
            max_nodes=args.max_nodes,
            decompose=not args.no_decompose,
            canonicalize=args.canonicalize,
        )
        write_certificate(effective_program, kernel, args.out)
        print(f"wrote certificate: {args.out}")






    elif args.command == "q-forms":
        program = _load_by_kind(args.path, args.input)
        selected = [int(x) for x in args.contexts.split(",") if x.strip() != ""]
        lam = [0] * len(program.contexts)
        for idx in selected:
            lam[idx] ^= 1
        comparison = compare_q_forms(program, lam)
        print(json.dumps({
            "lambda": comparison.lambda_vector,
            "is_cycle": is_cycle(program, lam),
            "q_from_context_carries": comparison.q_from_context_carries,
            "q_from_observable_multiset": comparison.q_from_observable_multiset,
            "numerator": comparison.numerator,
            "valid": comparison.valid,
        }, indent=2))





    elif args.command == "github-ready":
        report = run_github_ready_check(args.root)
        write_github_ready_report(report, json_path=args.out_json, markdown_path=args.out_md)
        print(json.dumps(github_ready_report_dict(report), indent=2))
        if args.out_json:
            print(f"wrote JSON GitHub-ready report: {args.out_json}")
        if args.out_md:
            print(f"wrote Markdown GitHub-ready report: {args.out_md}")

    elif args.command == "release-audit":
        report = run_release_audit(args.root)
        write_release_audit_outputs(report, json_path=args.out_json, markdown_path=args.out_md)
        print(json.dumps(release_audit_dict(report), indent=2))
        if args.out_json:
            print(f"wrote JSON audit: {args.out_json}")
        if args.out_md:
            print(f"wrote Markdown audit: {args.out_md}")

    elif args.command == "lift-pipeline":
        program = _load_by_kind(args.path, args.input)
        selected = None
        if args.contexts:
            selected = [int(x) for x in args.contexts.split(",") if x.strip() != ""]
        report = run_lift_pipeline(program, selected_contexts=selected)
        if args.out_program and report.constructed:
            lifted = find_even_base_fiber_lift(program).program
            if lifted is not None:
                dump_program(lifted, args.out_program)
        write_lift_pipeline_outputs(report, json_path=args.out_json, markdown_path=args.out_md)
        print(json.dumps(lift_pipeline_report_dict(report), indent=2))
        if args.out_program and report.constructed:
            print(f"wrote lifted program: {args.out_program}")
        if args.out_json:
            print(f"wrote JSON report: {args.out_json}")
        if args.out_md:
            print(f"wrote Markdown report: {args.out_md}")

    elif args.command == "fiber-lift":
        program = _load_by_kind(args.path, args.input)
        result = find_even_base_fiber_lift(program)
        if args.out and result.program is not None:
            dump_program(result.program, args.out)
        print(json.dumps(fiber_lift_result_dict(result, include_program=args.include_program), indent=2))
        if result.constructed and args.out:
            print(f"wrote lifted program: {args.out}")

    elif args.command == "tower-scope":
        program = _load_by_kind(args.path, args.input)
        selected = [int(x) for x in args.contexts.split(",") if x.strip() != ""]
        lam = [0] * len(program.contexts)
        for idx in selected:
            lam[idx] ^= 1
        report = tower_law_report(program, lam, base_d=args.base_d)
        print(json.dumps({
            "status": report.status,
            "certified": report.certified,
            "reason": report.reason,
            "selected_contexts": report.selected_contexts,
            "base_d": report.base_d,
            "lifted_d": report.lifted_d,
            "flattened_observables": report.flattened_observables,
            "repeated_observables": report.repeated_observables,
            "sum_m": report.sum_m,
            "odd_m_count": report.odd_m_count,
            "floor_sum_m_over_2": report.floor_sum_m_over_2,
            "floor_odd_m_count_over_2": report.floor_odd_m_count_over_2,
            "generativity_bit": report.generativity_bit,
            "non_generative": report.non_generative,
            "zd_contextual": report.zd_contextual,
            "zd_reason": report.zd_reason,
        }, indent=2))

    elif args.command == "import-solver-output":
        program = _load_by_kind(args.path, args.input)
        if args.out:
            imported = import_solver_solution_and_write_certificate(
                program,
                model_path=args.model,
                solver_output_path=args.solution,
                certificate_path=args.out,
            )
            print(f"wrote certificate: {args.out}")
        else:
            imported = import_solver_solution(
                program,
                model_path=args.model,
                solver_output_path=args.solution,
            )
        print(f"verification_valid: {imported.verification.valid}")
        print(f"reason: {imported.verification.reason}")
        print(f"q_value: {imported.verification.q_value}")
        print(f"lambda: {imported.lambda_vector}")
        print(f"selected_contexts: {imported.kernel.selected_contexts}")





    elif args.command == "zd-valuation":
        program = _load_by_kind(args.path, args.input)
        result = check_zd_valuation(program)
        print(json.dumps({
            "contextual": result.contextual,
            "status": result.status,
            "solvable": result.solvable,
            "modulus": result.modulus,
            "phases": result.phases,
            "observable_order": result.observable_order,
            "reason": result.reason,
        }, indent=2))

    elif args.command == "two-primary":
        program = _load_by_kind(args.path, args.input)
        result = check_zd_valuation(program)
        tp = two_primary_report(result.modulus)
        print(json.dumps({
            "contextual": result.contextual,
            "modulus": tp.modulus,
            "two_adic_valuation": tp.two_adic_valuation,
            "odd_part": tp.odd_part,
            "value_dover2": tp.value_dover2,
            "value_odd_component": tp.value_odd_component,
            "is_two_primary": tp.is_two_primary,
            "shadow_value_faithful": tp.shadow_value_faithful,
            "reason": tp.reason,
        }, indent=2))

    elif args.command == "export-circuit":
        program = _load_by_kind(args.path, args.input)
        selected = None
        if args.contexts:
            selected = [int(x) for x in args.contexts.split(",")]
        try:
            proto = export_qiskit_protocol(program, selected, verify=not args.no_verify)
        except ValueError as exc:
            print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
            return
        if args.out:
            with open(args.out, "w") as fh:
                fh.write(proto.script)
        print(json.dumps({
            "ok": True,
            "n_contexts": proto.n_contexts,
            "context_labels": proto.context_labels,
            "context_signs": proto.context_signs,
            "verified": not args.no_verify,
            "script_written_to": args.out,
            "script_chars": len(proto.script),
        }, indent=2))

    elif args.command == "spectrum":
        s = spectrum_summary(args.d)
        print(json.dumps({
            "modulus": s.modulus,
            "is_even": s.is_even,
            "achievable_values": s.achievable_values,
            "nonzero_value": s.nonzero_value,
            "value_order": s.value_order,
            "two_primary": s.two_primary.is_two_primary,
            "shadow_value_faithful": s.two_primary.shadow_value_faithful,
            "reason": s.reason,
        }, indent=2))

    elif args.command == "rewrite-policies":
        print(json.dumps(list_rewrite_policies_dict(), indent=2))

    elif args.command == "assess-rewrite":
        print(json.dumps(assess_rewrite_candidate_dict(args.policy_id), indent=2))

    elif args.command == "compiler-report":
        program = _load_by_kind(args.path, args.input)
        print(json.dumps(compiler_report_dict(program), indent=2))

    elif args.command == "compare-pass":
        before = _load_by_kind(args.before, args.input)
        after = _load_by_kind(args.after, args.input)
        print(json.dumps(compare_compiler_pass_dict(before, after), indent=2))

    elif args.command == "solve-pysat":
        program = _load_by_kind(args.path, args.input)
        try:
            result = solve_sat_with_pysat(program, max_weight=args.max_weight, solver_name=args.solver_name)
        except OptionalBackendUnavailable as exc:
            raise SystemExit(str(exc))
        print(json.dumps({
            "backend": result.backend,
            "status": result.status,
            "message": result.message,
            "lambda": result.lambda_vector,
            "selected_contexts": result.kernel.selected_contexts if result.kernel else None,
            "verification_valid": result.verification.valid if result.verification else None,
            "q_value": result.verification.q_value if result.verification else None,
        }, indent=2))
        if args.out and result.kernel and result.verification and result.verification.valid:
            write_certificate(program, result.kernel, args.out)
            print(f"wrote certificate: {args.out}")

    elif args.command == "solve-rc2":
        program = _load_by_kind(args.path, args.input)
        try:
            result = solve_maxsat_with_rc2(program)
        except OptionalBackendUnavailable as exc:
            raise SystemExit(str(exc))
        print(json.dumps({
            "backend": result.backend,
            "status": result.status,
            "message": result.message,
            "lambda": result.lambda_vector,
            "selected_contexts": result.kernel.selected_contexts if result.kernel else None,
            "verification_valid": result.verification.valid if result.verification else None,
            "q_value": result.verification.q_value if result.verification else None,
        }, indent=2))
        if args.out and result.kernel and result.verification and result.verification.valid:
            write_certificate(program, result.kernel, args.out)
            print(f"wrote certificate: {args.out}")

    elif args.command == "export-maxsat":
        program = _load_by_kind(args.path, args.input)
        model = write_wcnf_maxsat(program, args.out)
        print(f"wrote WCNF MaxSAT: {args.out}")
        print(f"vars: {model.num_vars}")
        print(f"hard_clauses: {len(model.hard_clauses)}")
        print(f"soft_clauses: {len(model.soft_clauses)}")
        print(f"top_weight: {model.top_weight}")
        print(f"lambda_vars: {model.lambda_vars}")

    elif args.command == "export-sat":
        program = _load_by_kind(args.path, args.input)
        model = write_dimacs_cnf(
            program,
            args.out,
            max_weight=args.max_weight,
            max_cardinality_clauses=args.max_cardinality_clauses,
        )
        print(f"wrote DIMACS CNF: {args.out}")
        print(f"vars: {model.num_vars}")
        print(f"clauses: {len(model.clauses)}")
        print(f"lambda_vars: {model.lambda_vars}")

    elif args.command == "inspect-certificate":
        print(json.dumps(inspect_certificate(args.certificate), indent=2))

    elif args.command == "verify-certificate":
        program = _load_by_kind(args.path, args.input)
        result = verify_certificate_file(program, args.certificate)
        print(json.dumps(result, indent=2))

    elif args.command == "components":
        program = canonicalize_program(_load_by_kind(args.path, args.input), mode=args.canonicalize)
        print(json.dumps(component_summary(program), indent=2))

    elif args.command == "canonicalize-report":
        program = _load_by_kind(args.path, args.input)
        print(json.dumps(canonicalization_report(program), indent=2))

    elif args.command == "magic-analyze":
        program = _load_by_kind(args.path, args.input)
        report = analyze_magic_protocol(
            program,
            protocol_id=args.protocol_id,
            target=args.target,
            enumerate_all_kernels=not args.no_enumerate,
            certify_minimal=args.certify_minimal,
        )
        print(json.dumps(magic_report_dict(report), indent=2))

    elif args.command == "magic-protocol":
        proto = load_magic_protocol(args.path)
        report = analyze_magic_protocol_record(
            proto,
            enumerate_all_kernels=not args.no_enumerate,
            certify_minimal=args.certify_minimal,
        )
        print(json.dumps(magic_report_dict(report), indent=2))

    elif args.command == "magic-portfolio":
        report = analyze_magic_portfolio_file(args.path)
        print(json.dumps(magic_portfolio_report_dict(report), indent=2))

    elif args.command == "magic-zoo":
        entries = run_magic_zoo(include_noncontextual=args.include_noncontextual, top=args.top)
        print(json.dumps(magic_zoo_report_dict(entries), indent=2))

    elif args.command == "magic-generate":
        candidates = generate_magic_candidates_from_paulis(args.paulis, target=args.target, top=args.top)
        print(json.dumps(generated_magic_report_dict(candidates), indent=2))

    elif args.command == "magic-audit":
        report = run_magic_audit()
        print(json.dumps(magic_audit_report_dict(report), indent=2))

    elif args.command == "magic-templates":
        print(json.dumps(magic_templates_catalog_dict(), indent=2))

    elif args.command == "magic-template-assess":
        proto = load_magic_protocol(args.path)
        report = analyze_magic_protocol_record(proto)
        assessments = assess_magic_templates(report, template_ids=args.templates)
        print(json.dumps(magic_template_assessments_dict(assessments), indent=2))

    elif args.command == "magic-search":
        report = search_magic_candidates_from_paulis(
            args.paulis,
            target=args.target,
            top=args.top,
            candidates=args.candidates,
            required_templates=args.required_template,
            certify_minimal=args.certify_minimal,
        )
        print(json.dumps(magic_search_report_dict(report), indent=2))

    elif args.command == "magic-report":
        proto = load_magic_protocol(args.path)
        report = analyze_magic_protocol_record(proto)
        write_markdown_report(magic_report_markdown(report), args.out)
        print(f"wrote Markdown MagicScout report: {args.out}")

    elif args.command == "magic-search-report":
        with open(args.path) as fh:
            data = json.load(fh)
        write_markdown_report(magic_search_markdown(data), args.out)
        print(f"wrote Markdown MagicScout search report: {args.out}")


if __name__ == "__main__":
    main()
