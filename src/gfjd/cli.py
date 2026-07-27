"""Command-line interface for the GFJD repository toolchain."""
from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path
import re
import sys
from typing import Any, Sequence

from .acquisition import (
    AcquisitionError,
    acquire_local_file,
    acquire_url,
    verify_acquisition_manifest,
)
from .conductor import Conductor, work_item_to_dict
from .pipeline import PipelineError, map_structured_csv, promote_observations
from .project import Project, ProjectError, load_project
from .release import ReleaseError, build_release, diff_releases, verify_release
from .security import scan_repository
from .validation import validate_project
from .tooling_cli import register_tooling_commands, run_tooling_command


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gfjd",
        description="Global Family Justice Data validation, conductor, pipeline and release tooling.",
    )
    parser.add_argument("--root", type=Path, help="Repository root (defaults to auto-discovery)")
    commands = parser.add_subparsers(dest="command", required=True)

    validate_parser = commands.add_parser(
        "validate", help="Validate contracts, semantics, programme controls and security"
    )
    validate_parser.add_argument("--strict", action="store_true")
    validate_parser.add_argument("--as-of", type=_iso_date)
    validate_parser.add_argument("--json", action="store_true", dest="json_output")
    validate_parser.add_argument("--no-security", action="store_true")

    conductor = commands.add_parser(
        "conductor", aliases=["programme"], help="Operate the evidence-driven v1 programme conductor"
    )
    conductor_sub = conductor.add_subparsers(dest="conductor_command", required=True)

    status = conductor_sub.add_parser("status", help="Show integrated track, gate and maturity status")
    status.add_argument("--json", action="store_true", dest="json_output")
    status.add_argument("--write", type=Path)

    gate = conductor_sub.add_parser("gate", help="Inspect one stage gate")
    gate.add_argument("gate_id")
    gate.add_argument("--json", action="store_true", dest="json_output")

    next_parser = conductor_sub.add_parser("next", help="List dependency-ready work items")
    next_parser.add_argument("--limit", type=int, default=20)
    next_parser.add_argument("--gate")
    next_parser.add_argument("--json", action="store_true", dest="json_output")

    graph = conductor_sub.add_parser("graph", help="Render the programme dependency graph")
    graph.add_argument("--format", choices=["mermaid", "dot"], default="mermaid")
    graph.add_argument("--write", type=Path)

    render = conductor_sub.add_parser("render", help="Render status JSON, Markdown and DOT graph")
    render.add_argument("--output", type=Path, default=Path("build/programme"))

    generated = conductor_sub.add_parser(
        "check-generated", help="Verify checked-in generated status and graph are current"
    )
    generated.add_argument(
        "--status-path", type=Path, default=Path("docs/programme/generated/status.md")
    )
    generated.add_argument(
        "--graph-path", type=Path, default=Path("docs/programme/generated/programme-graph.mmd")
    )

    work = conductor_sub.add_parser("work", help="Change a work item through the controlled state machine")
    work.add_argument("work_item_id")
    work.add_argument("--status", required=True)
    work.add_argument("--actor", required=True)
    work.add_argument("--note", default="")

    evidence = conductor_sub.add_parser("evidence", help="Review or accept evidence")
    evidence.add_argument("evidence_id")
    evidence.add_argument("--status", required=True)
    evidence.add_argument("--reviewer", required=True)
    evidence.add_argument("--reviewed-on", type=_iso_date)
    evidence.add_argument("--notes")

    decision = conductor_sub.add_parser("decision", help="Record a formal stage-gate decision")
    decision.add_argument("gate_id")
    decision.add_argument("--status", required=True)
    decision.add_argument("--authority", required=True)
    decision.add_argument("--reference", required=True)
    decision.add_argument("--conditions", default="")
    decision.add_argument("--expires-on", type=_iso_date)
    decision.add_argument("--notes", default="")

    risk = conductor_sub.add_parser("risk", help="Review a programme risk")
    risk.add_argument("risk_id")
    risk.add_argument("--actor", required=True)
    risk.add_argument("--status")
    risk.add_argument("--residual-severity")
    risk.add_argument("--next-review-on", type=_iso_date)
    risk.add_argument("--notes")

    pipeline = commands.add_parser("pipeline", help="Map and promote observation data")
    pipeline_sub = pipeline.add_subparsers(dest="pipeline_command", required=True)
    map_parser = pipeline_sub.add_parser("map", help="Map a source CSV to the observation contract")
    map_parser.add_argument("--mapping", type=Path, required=True)
    map_parser.add_argument("--input", type=Path, required=True)
    map_parser.add_argument("--output", type=Path, required=True)
    promote = pipeline_sub.add_parser("promote", help="Promote eligible silver rows and quarantine the rest")
    promote.add_argument("--input", type=Path, required=True)
    promote.add_argument("--gold", type=Path, required=True)
    promote.add_argument("--quarantine", type=Path, required=True)
    promote.add_argument("--report", type=Path, required=True)

    acquire = commands.add_parser("acquire", help="Create checksum and rights-aware source manifests")
    acquire_sub = acquire.add_subparsers(dest="acquire_command", required=True)
    acquire_file = acquire_sub.add_parser("file", help="Register and optionally preserve a local file")
    _add_acquisition_common(acquire_file)
    acquire_file.add_argument("--input", type=Path, required=True)
    acquire_http = acquire_sub.add_parser("url", help="Safely retrieve a public URL")
    _add_acquisition_common(acquire_http)
    acquire_http.add_argument("--url", required=True)
    acquire_http.add_argument("--timeout", type=int, default=30)
    acquire_http.add_argument("--max-bytes", type=int, default=100 * 1024 * 1024)
    acquire_http.add_argument("--allow-http", action="store_true")
    acquire_http.add_argument("--allow-private-network", action="store_true")
    verify_acq = acquire_sub.add_parser("verify", help="Verify a manifest and stored source")
    verify_acq.add_argument("manifest", type=Path)

    release = commands.add_parser("release", help="Build, verify or compare immutable releases")
    release_sub = release.add_subparsers(dest="release_command", required=True)
    release_build = release_sub.add_parser("build")
    release_build.add_argument("--version", required=True)
    release_build.add_argument("--output", type=Path, default=Path("dist"))
    release_build.add_argument("--source-date-epoch", type=int)
    release_build.add_argument("--allow-version-override", action="store_true")
    release_verify = release_sub.add_parser("verify")
    release_verify.add_argument("release_dir", type=Path)
    release_diff = release_sub.add_parser("diff")
    release_diff.add_argument("old_dir", type=Path)
    release_diff.add_argument("new_dir", type=Path)
    release_diff.add_argument("--output", type=Path)

    security = commands.add_parser("security", help="Run secret and public-data safety scans")
    security.add_argument("--json", action="store_true", dest="json_output")
    register_tooling_commands(commands)
    return parser


def _add_acquisition_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--source-edition-id")
    parser.add_argument("--destination", type=Path, default=Path("data/raw/acquisitions"))
    parser.add_argument(
        "--rights-status",
        choices=["cleared", "review_required", "restricted", "unknown"],
        default="review_required",
    )
    parser.add_argument(
        "--redistribution-status",
        choices=["allowed", "metadata_only", "prohibited", "unknown"],
        default="metadata_only",
    )
    parser.add_argument("--expected-sha256")
    parser.add_argument("--notes", default="")


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        project = load_project(args.root)
        tooling_result = run_tooling_command(project, args)
        if tooling_result is not None:
            return tooling_result
        if args.command == "validate":
            return _run_validate(project, args)
        if args.command in {"conductor", "programme"}:
            return _run_conductor(project, args)
        if args.command == "pipeline":
            return _run_pipeline(project, args)
        if args.command == "acquire":
            return _run_acquisition(project, args)
        if args.command == "release":
            return _run_release(project, args)
        if args.command == "security":
            report = scan_repository(project.root)
            print(json.dumps(report.to_dict(), indent=2) if args.json_output else report.render_text())
            return 0 if report.error_count == 0 else 1
    except (ProjectError, PipelineError, AcquisitionError, ReleaseError, KeyError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 2


def _run_validate(project: Project, args: argparse.Namespace) -> int:
    report = validate_project(
        project.root,
        strict=args.strict,
        as_of=args.as_of,
        include_security=not args.no_security,
    )
    if args.json_output:
        print(json.dumps(report.to_dict(), indent=2, ensure_ascii=False))
    else:
        maximum = int(project.config.get("validation", {}).get("max_errors_displayed", 200))
        print(report.render_text(max_issues=maximum))
    return 0 if report.ok(strict=args.strict) else 1


def _run_conductor(project: Project, args: argparse.Namespace) -> int:
    conductor = Conductor.load(project)
    command = args.conductor_command
    if command == "status":
        payload = conductor.status_payload()
        output = (
            json.dumps(payload, indent=2, ensure_ascii=False)
            if args.json_output
            else conductor.render_status_markdown()
        )
        if args.write:
            path = _project_path(project, args.write)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(output + ("" if output.endswith("\n") else "\n"), encoding="utf-8")
            print(path)
        else:
            print(output)
        return 0 if payload["validation"]["counts"]["errors"] == 0 else 1
    if command == "gate":
        result = conductor.gate_result(args.gate_id)
        payload = result.as_dict()
        if args.json_output:
            print(json.dumps(payload, indent=2, ensure_ascii=False))
        else:
            print(f"{result.gate.id} — {result.gate.name}: {result.state}")
            print(f"Ready: {result.ready}; passed: {result.passed}; decision: {result.decision_status}")
            print(f"Controls complete: {result.completed_requirements}/{result.total_requirements}")
            for blocker in result.blockers:
                print(f"- {blocker}")
        return 0 if result.passed else 2
    if command == "next":
        items = conductor.next_actions(args.limit, gate_id=args.gate)
        if args.json_output:
            print(json.dumps([work_item_to_dict(item) for item in items], indent=2, ensure_ascii=False))
        else:
            for item in items:
                print(f"{item.priority} {item.id} {item.track_id}/{item.gate_id} [{item.status}] {item.title}")
        return 0
    if command == "graph":
        content = conductor.render_mermaid() if args.format == "mermaid" else conductor.render_dependency_graph()
        if args.write:
            path = _project_path(project, args.write)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            print(path)
        else:
            print(content, end="")
        return 0
    if command == "render":
        output = _project_path(project, args.output)
        paths = conductor.render(output)
        print("\n".join(str(path) for path in paths))
        return 0
    if command == "check-generated":
        status_path = _project_path(project, args.status_path)
        graph_path = _project_path(project, args.graph_path)
        errors: list[str] = []
        expected_status = conductor.render_status_markdown()
        expected_graph = conductor.render_mermaid()
        if not status_path.exists():
            errors.append(f"Missing generated status: {status_path}")
        elif _normalise_generated_status(status_path.read_text(encoding="utf-8")) != _normalise_generated_status(expected_status):
            errors.append(f"Generated status is stale: {status_path}")
        if not graph_path.exists():
            errors.append(f"Missing generated graph: {graph_path}")
        elif graph_path.read_text(encoding="utf-8") != expected_graph:
            errors.append(f"Generated graph is stale: {graph_path}")
        if errors:
            print("\n".join(errors))
            return 1
        print("Generated conductor artefacts are current.")
        return 0
    if command == "work":
        item = conductor.set_work_status(args.work_item_id, args.status, actor=args.actor, note=args.note)
        print(json.dumps(work_item_to_dict(item), indent=2, ensure_ascii=False))
        return 0
    if command == "evidence":
        item = conductor.review_evidence(
            args.evidence_id,
            args.status,
            reviewer_role=args.reviewer,
            reviewed_on=args.reviewed_on,
            notes=args.notes,
        )
        print(json.dumps(_object_dict(item), indent=2, ensure_ascii=False))
        return 0
    if command == "decision":
        item = conductor.record_gate_decision(
            args.gate_id,
            args.status,
            authority=args.authority,
            reference=args.reference,
            conditions=args.conditions,
            expires_on=args.expires_on,
            notes=args.notes,
        )
        print(json.dumps(_object_dict(item), indent=2, ensure_ascii=False))
        return 0
    if command == "risk":
        item = conductor.update_risk(
            args.risk_id,
            actor=args.actor,
            status=args.status,
            residual_severity=args.residual_severity,
            next_review_on=args.next_review_on,
            notes=args.notes,
        )
        print(json.dumps(_object_dict(item), indent=2, ensure_ascii=False))
        return 0
    raise ValueError(f"Unhandled conductor command {command}")


def _run_pipeline(project: Project, args: argparse.Namespace) -> int:
    if args.pipeline_command == "map":
        result = map_structured_csv(
            project,
            _project_path(project, args.mapping),
            _project_path(project, args.input),
            _project_path(project, args.output),
        )
    else:
        result = promote_observations(
            project,
            _project_path(project, args.input),
            _project_path(project, args.gold),
            _project_path(project, args.quarantine),
            _project_path(project, args.report),
        )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


def _run_acquisition(project: Project, args: argparse.Namespace) -> int:
    if args.acquire_command == "verify":
        errors = verify_acquisition_manifest(project, _project_path(project, args.manifest))
        if errors:
            print("\n".join(f"- {error}" for error in errors))
            return 1
        print("Acquisition manifest verified.")
        return 0
    common: dict[str, Any] = {
        "project": project,
        "source_id": args.source_id,
        "destination_root": _project_path(project, args.destination),
        "source_edition_id": args.source_edition_id,
        "rights_status": args.rights_status,
        "redistribution_status": args.redistribution_status,
        "expected_sha256": args.expected_sha256,
        "notes": args.notes,
    }
    if args.acquire_command == "file":
        manifest, path = acquire_local_file(**common, input_path=_project_path(project, args.input))
    else:
        manifest, path = acquire_url(
            **common,
            url=args.url,
            timeout_seconds=args.timeout,
            max_bytes=args.max_bytes,
            allow_http=args.allow_http,
            allow_private_network=args.allow_private_network,
        )
    print(json.dumps({"manifest_path": str(path), "manifest": manifest}, indent=2, ensure_ascii=False))
    return 0


def _run_release(project: Project, args: argparse.Namespace) -> int:
    if args.release_command == "build":
        result = build_release(
            project,
            version=args.version,
            output_root=_project_path(project, args.output),
            source_date_epoch=args.source_date_epoch,
            allow_version_override=args.allow_version_override,
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    if args.release_command == "verify":
        errors = verify_release(_project_path(project, args.release_dir))
        if errors:
            print("\n".join(f"- {error}" for error in errors))
            return 1
        print("Release verified.")
        return 0
    result = diff_releases(
        _project_path(project, args.old_dir),
        _project_path(project, args.new_dir),
    )
    if args.output:
        output = _project_path(project, args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(output)
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


def _normalise_generated_status(value: str) -> str:
    return re.sub(r"^Generated: `[^`]+`$", "Generated: `<dynamic>`", value, flags=re.MULTILINE).rstrip() + "\n"


def _object_dict(value: Any) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for name in value.__dataclass_fields__:  # type: ignore[attr-defined]
        item = getattr(value, name)
        if isinstance(item, date):
            result[name] = item.isoformat()
        elif isinstance(item, tuple):
            result[name] = list(item)
        else:
            result[name] = item
    return result


def _project_path(project: Project, path: Path) -> Path:
    return path.expanduser().resolve() if path.is_absolute() else (project.root / path).resolve()


def _iso_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Date must be YYYY-MM-DD") from exc


if __name__ == "__main__":
    sys.exit(main())
