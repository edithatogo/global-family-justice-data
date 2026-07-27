"""Build a conservative jurisdiction-census readiness report.

The report is an operational control, not a source of empirical findings.  It
never infers a coverage status from the seed register: a jurisdiction becomes
ready only when a separately supplied universe entry, assessment and search
log meet the declared review threshold.
"""

from __future__ import annotations

import json
import shutil
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from .io import atomic_write_text, read_csv, sha256_file, write_csv, write_json
from .project import Project, load_project
from .schema_validation import coerce_row


class CensusError(RuntimeError):
    """Raised for unsafe census output paths or invalid report inputs."""


MATRIX_HEADERS = [
    "jurisdiction_id",
    "name",
    "pilot_phase",
    "register_coverage_status",
    "universe_state",
    "universe_review_status",
    "assessment_count",
    "current_assessment_state",
    "assessment_review_status",
    "search_log_count",
    "reviewed_search_log_count",
    "direct_enquiry_state",
    "readiness_state",
    "gap_reason",
]
GAP_HEADERS = ["jurisdiction_id", "gap_code", "message"]


@dataclass(frozen=True, slots=True)
class CensusResult:
    output_dir: Path
    summary_path: Path
    matrix_path: Path
    gaps_path: Path
    markdown_path: Path
    jurisdiction_count: int
    ready_count: int
    gap_count: int

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        for key in ("output_dir", "summary_path", "matrix_path", "gaps_path", "markdown_path"):
            result[key] = str(result[key])
        return result


def build_census_readiness(
    project_or_root: Project | Path | str,
    output_dir: Path = Path("build/census"),
    *,
    clean: bool = True,
) -> CensusResult:
    project = _project(project_or_root)
    destination = _output_dir(project, output_dir)
    if clean:
        shutil.rmtree(destination, ignore_errors=True)
    destination.mkdir(parents=True, exist_ok=True)
    inputs = {
        "jurisdictions": project.root / "data/seed/jurisdiction_register.csv",
        "universe": _operational_input(
            project,
            "data/census/jurisdiction_universe.csv",
            "data/seed/jurisdiction_universe_template.csv",
        ),
        "assessments": _operational_input(
            project,
            "data/census/coverage_assessment.csv",
            "data/seed/coverage_assessment_template.csv",
        ),
        "search_logs": _operational_input(
            project, "data/census/search_log.csv", "data/seed/search_log_template.csv"
        ),
        "enquiries": _confined_input(project, "data/census/direct_enquiry_register.csv"),
    }
    for name, path in inputs.items():
        if not path.is_file():
            raise CensusError(f"Census input is missing: {name}: {path.relative_to(project.root)}")
    _, jurisdictions = read_csv(inputs["jurisdictions"])
    _, universe = read_csv(inputs["universe"])
    _, assessments = read_csv(inputs["assessments"])
    _, search_logs = read_csv(inputs["search_logs"])
    _, enquiries = read_csv(inputs["enquiries"])
    _validate_input_rows(project, universe, "schemas/jurisdiction_universe.schema.json")
    _validate_input_rows(project, assessments, "schemas/coverage_assessment.schema.json")
    _validate_input_rows(project, search_logs, "schemas/search_log.schema.json")
    _validate_input_rows(project, enquiries, "schemas/direct_enquiry.schema.json")
    _unique(universe, "jurisdiction_id", "universe")
    _unique(universe, "universe_entry_id", "universe")
    _unique(assessments, "assessment_id", "coverage assessments")
    _unique(search_logs, "search_log_id", "search logs")
    _unique(enquiries, "enquiry_id", "direct enquiries")
    gaps: list[dict[str, str]] = []
    register_ids = {row["jurisdiction_id"] for row in jurisdictions}
    for label, rows in (
        ("universe", universe),
        ("coverage assessments", assessments),
        ("search logs", search_logs),
        ("direct enquiries", enquiries),
    ):
        for row in rows:
            if row.get("jurisdiction_id") not in register_ids:
                gaps.append(
                    {
                        "jurisdiction_id": row.get("jurisdiction_id", ""),
                        "gap_code": "ORPHAN_CENSUS_RECORD",
                        "message": (
                            f"{label.title()} record references a jurisdiction absent from "
                            "the jurisdiction register."
                        ),
                    }
                )
    assessments_by_id = _group(assessments)
    logs_by_id = _group(search_logs)
    enquiries_by_id = _group(enquiries)
    universe_by_id = {row["jurisdiction_id"]: row for row in universe}
    matrix: list[dict[str, str | int]] = []
    for jurisdiction in sorted(jurisdictions, key=lambda row: row["jurisdiction_id"]):
        jid = jurisdiction["jurisdiction_id"]
        entry = universe_by_id.get(jid)
        current = _current_assessment(assessments_by_id[jid])
        reviewed_logs = [
            row for row in logs_by_id[jid] if row.get("review_status") in {"reviewed", "accepted"}
        ]
        reasons: list[tuple[str, str]] = []
        if entry is None:
            reasons.append(
                ("UNIVERSE_ENTRY_MISSING", "No controlled jurisdiction-universe entry exists.")
            )
        elif entry.get("inclusion_status") != "included":
            reasons.append(
                (
                    "UNIVERSE_NOT_INCLUDED",
                    "Jurisdiction is not currently included in the controlled universe.",
                )
            )
        elif entry.get("review_status") not in {"reviewed", "accepted"}:
            reasons.append(
                ("UNIVERSE_UNREVIEWED", "Included universe entry has not been reviewed.")
            )
        if current is None:
            reasons.append(
                ("COVERAGE_ASSESSMENT_MISSING", "No current coverage assessment exists.")
            )
        elif current.get("review_status") not in {"reviewed", "accepted"}:
            reasons.append(
                ("COVERAGE_UNREVIEWED", "Current coverage assessment has not been reviewed.")
            )
        elif current.get("coverage_state") not in {
            "candidate_complete",
            "verified_complete",
            "partial",
            "stale",
            "not_started",
        }:
            reasons.append(
                ("COVERAGE_STATE_INVALID", "Coverage assessment has an unrecognised state.")
            )
        if not reviewed_logs:
            reasons.append(("SEARCH_LOG_UNREVIEWED", "No reviewed source-search log exists."))
        # Direct enquiry is deliberately not inferred from an empty log. It is only
        # considered closed when a reviewed log records it in notes using the exact
        # controlled marker, preserving a transparent audit trail without contacts.
        reviewed_enquiries = [
            row
            for row in enquiries_by_id[jid]
            if row.get("review_status") in {"reviewed", "accepted"}
        ]
        enquiry = "not_required_or_unrecorded"
        if reviewed_enquiries:
            enquiry = ";".join(sorted({row.get("state", "") for row in reviewed_enquiries}))
        if jurisdiction.get("pilot_phase") in {"1", "2"} and not any(
            row.get("state") in {"answered", "closed_no_response", "not_required"}
            for row in reviewed_enquiries
        ):
            reasons.append(
                (
                    "DIRECT_ENQUIRY_UNRESOLVED",
                    "Priority jurisdiction has no reviewed enquiry outcome or transparent closure.",
                )
            )
        if any("direct_enquiry:closed" in row.get("notes", "") for row in reviewed_logs):
            enquiry = "closed"
        elif any("direct_enquiry:sent" in row.get("notes", "") for row in reviewed_logs):
            enquiry = "sent"
        readiness = "ready_for_methods_review" if not reasons else "unresolved"
        for code, message in reasons:
            gaps.append({"jurisdiction_id": jid, "gap_code": code, "message": message})
        matrix.append(
            {
                "jurisdiction_id": jid,
                "name": jurisdiction.get("name", ""),
                "pilot_phase": jurisdiction.get("pilot_phase", ""),
                "register_coverage_status": jurisdiction.get("coverage_status", ""),
                "universe_state": entry.get("inclusion_status", "missing") if entry else "missing",
                "universe_review_status": entry.get("review_status", "missing")
                if entry
                else "missing",
                "assessment_count": len(assessments_by_id[jid]),
                "current_assessment_state": current.get("coverage_state", "missing")
                if current
                else "missing",
                "assessment_review_status": current.get("review_status", "missing")
                if current
                else "missing",
                "search_log_count": len(logs_by_id[jid]),
                "reviewed_search_log_count": len(reviewed_logs),
                "direct_enquiry_state": enquiry,
                "readiness_state": readiness,
                "gap_reason": ";".join(code for code, _ in reasons),
            }
        )
    matrix_path, gaps_path = (
        destination / "coverage-readiness-matrix.csv",
        destination / "census-gaps.csv",
    )
    write_csv(matrix_path, MATRIX_HEADERS, matrix)
    write_csv(gaps_path, GAP_HEADERS, gaps)
    ready = sum(row["readiness_state"] == "ready_for_methods_review" for row in matrix)
    markdown_path = destination / "census-readiness.md"
    atomic_write_text(markdown_path, _markdown(len(matrix), ready, gaps))
    artifacts = [matrix_path, gaps_path, markdown_path]
    summary = {
        "schema_version": "1.0",
        "built_on": str(project.project_config["status_as_of"]),
        "jurisdiction_count": len(matrix),
        "ready_for_methods_review_count": ready,
        "gap_count": len(gaps),
        "gap_counts": dict(sorted(Counter(row["gap_code"] for row in gaps).items())),
        "inputs": [
            {"path": path.relative_to(project.root).as_posix(), "sha256": sha256_file(path)}
            for path in inputs.values()
        ],
        "artifacts": [{"path": path.name, "sha256": sha256_file(path)} for path in artifacts],
    }
    summary_path = destination / "census-summary.json"
    write_json(summary_path, summary)
    errors = verify_census_readiness(destination, project_or_root=project)
    if errors:
        raise CensusError("Built census readiness report failed verification: " + "; ".join(errors))
    return CensusResult(
        destination,
        summary_path,
        matrix_path,
        gaps_path,
        markdown_path,
        len(matrix),
        ready,
        len(gaps),
    )


def verify_census_readiness(
    output_dir: Path, *, project_or_root: Project | Path | str | None = None
) -> list[str]:
    directory = output_dir.expanduser().resolve()
    summary_path = directory / "census-summary.json"
    if not summary_path.is_file():
        return [f"Census summary does not exist: {summary_path}"]
    try:
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"Could not read census summary: {exc}"]
    errors: list[str] = []
    required_artifacts = {
        "coverage-readiness-matrix.csv",
        "census-gaps.csv",
        "census-readiness.md",
    }
    listed_artifacts: set[str] = set()
    for item in summary.get("artifacts", []):
        if not isinstance(item, dict):
            errors.append("Malformed census artifact entry")
            continue
        relative = str(item.get("path", ""))
        if Path(relative).is_absolute() or ".." in Path(relative).parts:
            errors.append(f"Unsafe census artifact path: {relative}")
            continue
        if relative in listed_artifacts:
            errors.append(f"Duplicate census artifact path: {relative}")
            continue
        listed_artifacts.add(relative)
        path = directory / relative
        if not path.is_file():
            errors.append(f"Census artifact is missing: {relative}")
        elif sha256_file(path) != item.get("sha256"):
            errors.append(f"Census artifact checksum mismatch: {relative}")
    for relative in sorted(required_artifacts - listed_artifacts):
        errors.append(f"Required census artifact not listed: {relative}")
    if project_or_root is not None:
        project = _project(project_or_root)
        for item in summary.get("inputs", []):
            if not isinstance(item, dict):
                errors.append("Malformed census input entry")
                continue
            relative = str(item.get("path", ""))
            try:
                path = _confined_input(project, relative)
            except CensusError as exc:
                errors.append(str(exc))
                continue
            if not path.is_file():
                errors.append(f"Census input is missing: {relative}")
            elif sha256_file(path) != item.get("sha256"):
                errors.append(f"Census input checksum mismatch: {relative}")
    matrix = directory / "coverage-readiness-matrix.csv"
    if matrix.is_file():
        headers, rows = read_csv(matrix)
        if headers != MATRIX_HEADERS:
            errors.append("Census matrix columns do not match the contract")
        if len(rows) != summary.get("jurisdiction_count"):
            errors.append("Census matrix row count does not match summary")
    return errors


def _project(value: Project | Path | str) -> Project:
    return value if isinstance(value, Project) else load_project(Path(value))


def _output_dir(project: Project, value: Path) -> Path:
    path = value.expanduser().resolve() if value.is_absolute() else (project.root / value).resolve()
    if path != project.root / "build" and project.root / "build" not in path.parents:
        raise CensusError("Census products must be written under build/")
    return path


def _confined_input(project: Project, relative: str) -> Path:
    candidate = Path(relative)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise CensusError(f"Unsafe census input path: {relative}")
    path = (project.root / candidate).resolve()
    try:
        path.relative_to(project.root)
    except ValueError as exc:
        raise CensusError(f"Census input path escapes repository root: {relative}") from exc
    return path


def _operational_input(project: Project, operational: str, template: str) -> Path:
    """Use the declared census data path when populated, otherwise its template."""

    operational_path = _confined_input(project, operational)
    return operational_path if operational_path.is_file() else _confined_input(project, template)


def _group(rows: list[dict[str, str]]) -> defaultdict[str, list[dict[str, str]]]:
    grouped: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row.get("jurisdiction_id", "")].append(row)
    return grouped


def _validate_input_rows(
    project: Project, rows: list[dict[str, str]], schema_relative: str
) -> None:
    schema = json.loads((project.root / schema_relative).read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors: list[str] = []
    for number, raw in enumerate(rows, start=2):
        typed = coerce_row(raw, schema)
        for error in sorted(validator.iter_errors(typed), key=lambda item: list(item.path)):
            location = ".".join(str(part) for part in error.path)
            errors.append(
                f"{schema_relative} row {number}"
                f"{' ' + location if location else ''}: {error.message}"
            )
    if errors:
        raise CensusError("Census input validation failed: " + "; ".join(errors[:20]))


def _unique(rows: list[dict[str, str]], field: str, label: str) -> None:
    values = [row.get(field, "") for row in rows]
    duplicates = sorted({value for value in values if values.count(value) > 1})
    if duplicates:
        raise CensusError(f"Duplicate {field} in {label}: {', '.join(duplicates)}")


def _current_assessment(rows: list[dict[str, str]]) -> dict[str, str] | None:
    active = [row for row in rows if row.get("review_status") != "superseded"]
    if len(active) > 1:
        raise CensusError(
            "More than one non-superseded coverage assessment exists for a jurisdiction"
        )
    return active[0] if active else None


def _markdown(total: int, ready: int, gaps: list[dict[str, str]]) -> str:
    counts = Counter(row["gap_code"] for row in gaps)
    lines = [
        "# Jurisdiction census readiness",
        "",
        "This is a deterministic readiness report, not a claim that a jurisdiction is covered "
        "or that enquiries occurred.",
        "",
        "## Status",
        "",
        f"- Registered jurisdictions: {total}",
        f"- Ready for methods review: {ready}",
        f"- Unresolved control gaps: {len(gaps)}",
        "",
        "## Gap counts",
        "",
    ]
    lines.extend(f"- {code}: {count}" for code, count in sorted(counts.items()))
    lines.extend(
        [
            "",
            "A ready row still requires accountable methods and governance review; no report "
            "output is gate evidence by itself.",
            "",
        ]
    )
    return "\n".join(lines)
