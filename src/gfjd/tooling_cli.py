"""Additional operational CLI commands used by CI and the handoff bootstrap."""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import date
from pathlib import Path
from typing import Any

from . import __version__
from .bootstrap import (
    apply_bootstrap,
    build_plan,
    create_context,
    preflight,
    validate_bootstrap_plan,
    verify_audit_log,
    verify_bootstrap_receipt,
    write_plan,
)
from .ci_policy import audit_workflows
from .contract_lock import verify_contract_lock, write_contract_lock
from .harness import (
    audit_lockfile,
    check_coverage_budget,
    check_test_runtime,
    compare_artifacts,
    verify_sdist,
    verify_wheel,
)
from .manifest import verify_manifest, write_manifest
from .project import Project
from .repository_policy import audit_repository_controls


def register_tooling_commands(
    commands: argparse._SubParsersAction[argparse.ArgumentParser],
) -> None:
    version = commands.add_parser("version", help="Show software and repository contract versions")
    version.add_argument("--json", action="store_true", dest="json_output")

    policy = commands.add_parser("policy", help="Audit CI workflows or desired repository controls")
    policy_sub = policy.add_subparsers(dest="policy_command", required=True)
    for name in ("ci", "repository"):
        parser = policy_sub.add_parser(name)
        parser.add_argument("--json", action="store_true", dest="json_output")

    harness = commands.add_parser("harness", help="Run focused quality and distribution controls")
    harness_sub = harness.add_subparsers(dest="harness_command", required=True)
    lock = harness_sub.add_parser("lock", help="Audit the frozen dependency lock")
    lock.add_argument("path", nargs="?", type=Path, default=Path("uv.lock"))
    lock.add_argument("--json", action="store_true", dest="json_output")
    contracts = harness_sub.add_parser(
        "contracts", help="Verify or regenerate the public-contract lock"
    )
    contracts.add_argument("--write", action="store_true")
    contracts.add_argument("--json", action="store_true", dest="json_output")
    coverage = harness_sub.add_parser("coverage", help="Enforce coverage budgets and ratchets")
    coverage.add_argument("coverage_json", type=Path)
    coverage.add_argument("--json", action="store_true", dest="json_output")
    runtime = harness_sub.add_parser("runtime", help="Enforce test runtime budgets")
    runtime.add_argument("timing_paths", nargs="+", type=Path)
    runtime.add_argument("--suite", choices=("unit", "integration"), required=True)
    runtime.add_argument("--json", action="store_true", dest="json_output")
    wheel = harness_sub.add_parser("wheel", help="Inspect a wheel adversarially")
    wheel.add_argument("path", type=Path)
    wheel.add_argument("--json", action="store_true", dest="json_output")
    sdist = harness_sub.add_parser("sdist", help="Inspect a source distribution adversarially")
    sdist.add_argument("path", type=Path)
    sdist.add_argument("--json", action="store_true", dest="json_output")
    repro = harness_sub.add_parser("repro", help="Require byte-identical artifacts")
    repro.add_argument("first", type=Path)
    repro.add_argument("second", type=Path)
    repro.add_argument("--json", action="store_true", dest="json_output")

    manifest = commands.add_parser("manifest", help="Write or verify MANIFEST.sha256")
    action = manifest.add_mutually_exclusive_group(required=False)
    action.add_argument("--write", action="store_true")
    action.add_argument("--verify", action="store_true")

    doctor = commands.add_parser("doctor", help="Run non-mutating repository diagnostics")
    doctor.add_argument("--json", action="store_true", dest="json_output")

    bootstrap = commands.add_parser(
        "bootstrap", help="Plan, apply and verify local/remote bootstrap"
    )
    bootstrap_sub = bootstrap.add_subparsers(dest="bootstrap_command", required=True)
    bootstrap_sub.add_parser("preflight")
    plan = bootstrap_sub.add_parser("plan")
    _add_bootstrap_discovery(plan)
    plan.add_argument("--output", type=Path, default=Path("build/bootstrap"))
    apply = bootstrap_sub.add_parser("apply")
    apply.add_argument("--output", type=Path, default=Path("build/bootstrap"))
    apply.add_argument("--github-owner", default="")
    apply.add_argument("--github-repository", default="")
    apply.add_argument(
        "--github-visibility", choices=("private", "public", "internal"), default="private"
    )
    apply.add_argument("--author-name", default="")
    apply.add_argument("--author-email", default="")
    apply.add_argument("--no-push", action="store_true")
    apply.add_argument("--apply-github-controls", action="store_true")
    apply.add_argument("--create-huggingface", action="store_true")
    apply.add_argument("--huggingface-namespace", default="")
    apply.add_argument("--yes", action="store_true")
    verify = bootstrap_sub.add_parser("verify")
    verify.add_argument(
        "--receipt", type=Path, default=Path("build/bootstrap/bootstrap-receipt.json")
    )
    verify.add_argument(
        "--audit-log", type=Path, default=Path("build/bootstrap/bootstrap-audit.jsonl")
    )

    demo = commands.add_parser("demo", help="Run or verify the fictional heterogeneous pilot")
    demo_sub = demo.add_subparsers(dest="demo_command", required=True)
    for name in ("run", "verify"):
        parser = demo_sub.add_parser(name)
        parser.add_argument("--output", type=Path, default=Path("build/demo"))

    evidence = commands.add_parser("evidence", help="Build or verify the outcomes evidence map")
    evidence_sub = evidence.add_subparsers(dest="evidence_command", required=True)
    evidence_build = evidence_sub.add_parser("build")
    evidence_build.add_argument(
        "--input", type=Path, default=Path("data/seed/outcomes_evidence_template.csv")
    )
    evidence_build.add_argument("--output", type=Path, default=Path("build/evidence"))
    evidence_build.add_argument("--as-of", type=date.fromisoformat)
    evidence_verify = evidence_sub.add_parser("verify")
    evidence_verify.add_argument("--output", type=Path, default=Path("build/evidence"))

    comparability = commands.add_parser(
        "comparability", help="Build or verify conservative comparability candidates"
    )
    comp_sub = comparability.add_subparsers(dest="comparability_command", required=True)
    comp_build = comp_sub.add_parser("build")
    comp_build.add_argument("--input", action="append", default=[])
    comp_build.add_argument("--output", type=Path, default=Path("build/comparability"))
    comp_verify = comp_sub.add_parser("verify")
    comp_verify.add_argument("--output", type=Path, default=Path("build/comparability"))

    resilience = commands.add_parser(
        "resilience", help="Build, verify and rehearse critical-state backups"
    )
    res_sub = resilience.add_subparsers(dest="resilience_command", required=True)
    backup = res_sub.add_parser("backup")
    backup.add_argument("--output", type=Path, default=Path("build/backup"))
    backup.add_argument("--source-date-epoch", type=int)
    verify_backup_parser = res_sub.add_parser("verify")
    verify_backup_parser.add_argument("archive", type=Path)
    restore = res_sub.add_parser("restore-rehearsal")
    restore.add_argument("archive", type=Path)
    restore.add_argument("--output", type=Path, default=Path("build/restore-rehearsal"))
    verify_restore = res_sub.add_parser("verify-restore")
    verify_restore.add_argument("receipt", type=Path)

    warehouse = commands.add_parser(
        "warehouse", help="Build, verify or query the portable SQLite warehouse"
    )
    warehouse_sub = warehouse.add_subparsers(dest="warehouse_command", required=True)
    warehouse_build = warehouse_sub.add_parser("build")
    warehouse_build.add_argument("--output", type=Path, default=Path("build/warehouse/gfjd.sqlite"))
    warehouse_build.add_argument("--source-date-epoch", type=int)
    warehouse_verify = warehouse_sub.add_parser("verify")
    warehouse_verify.add_argument("database", type=Path)
    warehouse_query = warehouse_sub.add_parser("query")
    warehouse_query.add_argument("database", type=Path)
    warehouse_query.add_argument("sql")
    warehouse_query.add_argument("--limit", type=int, default=1000)

    governance = commands.add_parser(
        "governance", help="Build or verify the fail-closed governance assurance pack"
    )
    governance_sub = governance.add_subparsers(dest="governance_command", required=True)
    governance_build = governance_sub.add_parser("build")
    governance_build.add_argument("--output", type=Path, default=Path("build/governance"))
    governance_build.add_argument("--as-of", type=date.fromisoformat)
    governance_verify = governance_sub.add_parser("verify")
    governance_verify.add_argument("--output", type=Path, default=Path("build/governance"))


def _add_bootstrap_discovery(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--scan-root", action="append", type=Path, default=[])
    parser.add_argument("--github-owner", default="")
    parser.add_argument("--github-repository", default="")
    parser.add_argument("--huggingface-namespace", default="")


def _resolve(project: Project, value: Path) -> Path:
    candidate = value.expanduser()
    return candidate.resolve() if candidate.is_absolute() else (project.root / candidate).resolve()


def _print_report(report: Any, *, json_output: bool = False) -> int:
    if json_output and hasattr(report, "to_dict"):
        print(json.dumps(report.to_dict(), indent=2, ensure_ascii=False, sort_keys=True))
    elif hasattr(report, "render_text"):
        print(report.render_text())
    else:
        print(str(report))
    return 0 if int(getattr(report, "error_count", 0)) == 0 else 1


def run_tooling_command(project: Project, args: argparse.Namespace) -> int | None:
    command = args.command
    if command == "version":
        payload = {
            "software_version": __version__,
            "project_version": str(project.project_config.get("version", "")),
            "contract_version": str(project.project_config.get("contract_version", "")),
            "ontology_version": str(project.project_config.get("ontology_version", "")),
            "git_revision": _git_revision(project.root),
        }
        print(
            json.dumps(payload, indent=2, sort_keys=True)
            if args.json_output
            else "\n".join(f"{key}: {value}" for key, value in payload.items())
        )
        return 0

    if command == "policy":
        report = (
            audit_workflows(project.root)
            if args.policy_command == "ci"
            else audit_repository_controls(project.root)
        )
        return _print_report(report, json_output=args.json_output)

    if command == "harness":
        quality = project.root / "config" / "quality.toml"
        sub = args.harness_command
        if sub == "lock":
            report = audit_lockfile(_resolve(project, args.path))
        elif sub == "contracts":
            if args.write:
                path = write_contract_lock(project)
                print(f"Wrote {path.relative_to(project.root)}")
            report = verify_contract_lock(project)
        elif sub == "coverage":
            report = check_coverage_budget(_resolve(project, args.coverage_json), quality)
        elif sub == "runtime":
            report = check_test_runtime(
                [_resolve(project, value) for value in args.timing_paths], quality, suite=args.suite
            )
        elif sub == "wheel":
            report = verify_wheel(_resolve(project, args.path), quality)
        elif sub == "sdist":
            report = verify_sdist(_resolve(project, args.path), quality)
        elif sub == "repro":
            report = compare_artifacts(
                _resolve(project, args.first), _resolve(project, args.second)
            )
        else:  # pragma: no cover - argparse prevents this
            raise ValueError(f"Unknown harness command {sub}")
        return _print_report(report, json_output=args.json_output)

    if command == "manifest":
        if args.write:
            write_manifest()
            print("Wrote MANIFEST.sha256")
            return 0
        errors = verify_manifest()
        if errors:
            print("Manifest verification failed:\n" + "\n".join(f"- {item}" for item in errors))
            return 1
        print("Repository manifest verified.")
        return 0

    if command == "doctor":
        payload = _doctor(project)
        print(
            json.dumps(payload, indent=2, sort_keys=True)
            if args.json_output
            else _doctor_text(payload)
        )
        return 0 if not payload["errors"] else 1

    if command == "bootstrap":
        return _run_bootstrap(project, args)

    if command == "demo":
        from .demo import run_demo, verify_demo

        output = _resolve(project, args.output)
        if args.demo_command == "run":
            print(json.dumps(run_demo(project, output).to_dict(), indent=2, sort_keys=True))
            return 0
        errors = verify_demo(project, output)
        return _print_errors("Synthetic pilot", errors)

    if command == "evidence":
        from .evidence import build_evidence_catalogue, verify_evidence_catalogue

        output = _resolve(project, args.output)
        if args.evidence_command == "build":
            result = build_evidence_catalogue(
                project, output, input_path=args.input, as_of=args.as_of
            )
            print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
            return 0
        return _print_errors(
            "Evidence catalogue", verify_evidence_catalogue(output, project_or_root=project)
        )

    if command == "comparability":
        from .comparability import build_comparability_audit, verify_comparability_audit

        output = _resolve(project, args.output)
        if args.comparability_command == "build":
            result = build_comparability_audit(
                project,
                output,
                input_patterns=args.input or ["data/gold/**/*.csv"],
            )
            print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
            return 0
        return _print_errors(
            "Comparability audit", verify_comparability_audit(output, project_or_root=project)
        )

    if command == "resilience":
        from .resilience import (
            build_backup,
            rehearse_restore,
            verify_backup,
            verify_restore_receipt,
        )

        sub = args.resilience_command
        if sub == "backup":
            result = build_backup(project, args.output, source_date_epoch=args.source_date_epoch)
            print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
            return 0
        if sub == "verify":
            return _print_errors("Backup", verify_backup(_resolve(project, args.archive)))
        if sub == "restore-rehearsal":
            result = rehearse_restore(project, args.archive, args.output)
            print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
            return 0
        return _print_errors("Restore receipt", verify_restore_receipt(project, args.receipt))

    if command == "warehouse":
        from .warehouse import build_warehouse, query_warehouse, verify_warehouse

        sub = args.warehouse_command
        if sub == "build":
            result = build_warehouse(project, args.output, source_date_epoch=args.source_date_epoch)
            print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
            return 0
        if sub == "verify":
            return _print_errors("Warehouse", verify_warehouse(_resolve(project, args.database)))
        result = query_warehouse(_resolve(project, args.database), args.sql, limit=args.limit)
        print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
        return 0
    if command == "governance":
        from .governance import build_governance_pack, verify_governance_pack

        output = _resolve(project, args.output)
        if args.governance_command == "build":
            governance_result = build_governance_pack(project, output, as_of=args.as_of)
            print(json.dumps(governance_result.to_dict(), indent=2, sort_keys=True))
            return 0
        return _print_errors("Governance pack", verify_governance_pack(output))
    return None


def _run_bootstrap(project: Project, args: argparse.Namespace) -> int:
    output = _resolve(project, getattr(args, "output", Path("build/bootstrap")))
    context = create_context(project, output)
    if args.bootstrap_command == "preflight":
        print(json.dumps(preflight(context), indent=2, ensure_ascii=False, sort_keys=True))
        return 0
    if args.bootstrap_command == "plan":
        roots = [_resolve(project, value) for value in args.scan_root] or None
        plan = build_plan(
            context,
            scan_roots=roots,
            github_owner=args.github_owner,
            github_repository=args.github_repository,
            huggingface_namespace=args.huggingface_namespace,
        )
        validate_bootstrap_plan(context, plan)
        paths = write_plan(context, plan)
        print(json.dumps({"plan": plan, "outputs": paths}, indent=2, ensure_ascii=False))
        return 0
    if args.bootstrap_command == "apply":
        receipt = apply_bootstrap(
            context,
            github_owner=args.github_owner,
            github_repository=args.github_repository,
            github_visibility=args.github_visibility,
            author_name=args.author_name,
            author_email=args.author_email,
            push=not args.no_push,
            apply_github_controls=args.apply_github_controls,
            create_huggingface=args.create_huggingface,
            huggingface_namespace=args.huggingface_namespace,
            confirmation=args.yes,
        )
        print(json.dumps(receipt, indent=2, ensure_ascii=False, sort_keys=True))
        return 0
    errors = verify_bootstrap_receipt(_resolve(project, args.receipt)) + verify_audit_log(
        _resolve(project, args.audit_log)
    )
    return _print_errors("Bootstrap", errors)


def _doctor(project: Project) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    versions = {
        "package": __version__,
        "project": str(project.project_config.get("version", "")),
        "version_file": (project.root / "VERSION").read_text(encoding="utf-8").strip()
        if (project.root / "VERSION").is_file()
        else "",
    }
    normalised_package = versions["package"].replace("a", "-alpha.", 1)
    if normalised_package != versions["project"]:
        errors.append("Package and project versions differ")
    if versions["version_file"] != versions["project"]:
        errors.append("VERSION and project versions differ")
    manifest_errors = verify_manifest()
    errors.extend(f"manifest: {item}" for item in manifest_errors)
    contract_report = verify_contract_lock(project)
    errors.extend(
        f"contract: {item.message}" for item in contract_report.issues if item.severity == "error"
    )
    warnings.extend(
        f"contract: {item.message}" for item in contract_report.issues if item.severity == "warning"
    )
    for relative in (
        "AGENTS.md",
        "START_HERE.md",
        "BOOTSTRAP_AND_HANDOFF_PROMPT.md",
        "CODEX_IMPLEMENTATION_PROMPT.md",
        "HISTORY_PROVENANCE.md",
    ):
        if not (project.root / relative).is_file():
            errors.append(f"missing required handoff file: {relative}")
    return {
        "versions": versions,
        "git_revision": _git_revision(project.root),
        "errors": errors,
        "warnings": warnings,
    }


def _doctor_text(payload: dict[str, Any]) -> str:
    lines = ["GFJD doctor", f"git_revision: {payload['git_revision']}"]
    lines.extend(f"{key}: {value}" for key, value in payload["versions"].items())
    lines.append(f"errors: {len(payload['errors'])}")
    lines.extend(f"- {item}" for item in payload["errors"])
    lines.append(f"warnings: {len(payload['warnings'])}")
    lines.extend(f"- {item}" for item in payload["warnings"])
    return "\n".join(lines)


def _git_revision(root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return "unavailable"
    return result.stdout.strip() if result.returncode == 0 else "unavailable"


def _print_errors(label: str, errors: list[str]) -> int:
    if errors:
        print(f"{label} verification failed:\n" + "\n".join(f"- {item}" for item in errors))
        return 1
    print(f"{label} verified.")
    return 0
