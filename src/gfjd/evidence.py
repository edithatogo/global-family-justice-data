"""Build and verify the outcomes evidence-map product.

The evidence catalogue is intentionally separate from routine court performance
observations. It describes study design, population, outcome measurement, appraisal,
rights, and review state without converting unlike studies into a pooled outcome.
"""

from __future__ import annotations

import json
import shutil
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from .io import atomic_write_text, read_csv, read_json, sha256_file, write_csv, write_json
from .project import Project, load_project
from .schema_validation import coerce_row


class EvidenceCatalogueError(RuntimeError):
    """Raised when the outcomes evidence catalogue cannot be built or verified."""


@dataclass(frozen=True, slots=True)
class EvidenceCatalogueResult:
    output_dir: Path
    summary_path: Path
    records_path: Path
    coverage_path: Path
    design_summary_path: Path
    markdown_path: Path
    record_count: int
    accepted_count: int
    appraised_count: int

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        for field in (
            "output_dir",
            "summary_path",
            "records_path",
            "coverage_path",
            "design_summary_path",
            "markdown_path",
        ):
            payload[field] = str(payload[field])
        return payload


COVERAGE_HEADERS = [
    "jurisdiction_id",
    "jurisdiction_name",
    "outcome_domain",
    "record_count",
    "accepted_count",
    "appraised_count",
    "high_or_critical_risk_count",
    "coverage_state",
]

DESIGN_HEADERS = [
    "summary_type",
    "category",
    "record_count",
    "accepted_count",
    "appraised_count",
]


def build_evidence_catalogue(
    project_or_root: Project | Path | str,
    output_dir: Path = Path("build/evidence"),
    *,
    input_path: Path = Path("data/seed/outcomes_evidence_template.csv"),
    as_of: date | None = None,
    clean: bool = True,
) -> EvidenceCatalogueResult:
    """Build a study-level evidence map and explicit jurisdiction/domain gap matrix."""

    project = _project(project_or_root)
    destination = _output_dir(project, output_dir)
    source = _confined(project, input_path)
    if not source.is_file():
        raise EvidenceCatalogueError(f"Evidence input does not exist: {source}")
    if clean:
        shutil.rmtree(destination, ignore_errors=True)
    destination.mkdir(parents=True, exist_ok=True)

    schema = read_json(project.root / "schemas/outcome_evidence.schema.json")
    expected_headers = list(schema["properties"])
    headers, raw_rows = read_csv(source)
    if headers != expected_headers:
        raise EvidenceCatalogueError(
            "Evidence columns do not match the canonical schema order; expected "
            f"{expected_headers!r}, found {headers!r}"
        )

    jurisdictions = _register(project, "jurisdiction_register.csv", "jurisdiction_id")
    matter_types = _register(project, "matter_type_dictionary.csv", "matter_type_id")
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    records: list[dict[str, Any]] = []
    errors: list[str] = []
    seen: set[str] = set()
    for row_number, raw in enumerate(raw_rows, start=2):
        record = coerce_row(raw, schema)
        for error in sorted(validator.iter_errors(record), key=lambda item: list(item.path)):
            location = ".".join(str(part) for part in error.path)
            errors.append(
                f"row {row_number}{' field ' + location if location else ''}: {error.message}"
            )
        identifier = str(record.get("evidence_record_id") or "")
        if identifier in seen:
            errors.append(f"row {row_number}: duplicate evidence_record_id {identifier!r}")
        seen.add(identifier)
        jurisdiction_id = str(record.get("jurisdiction_id") or "")
        if jurisdiction_id not in jurisdictions:
            errors.append(f"row {row_number}: unknown jurisdiction_id {jurisdiction_id!r}")
        matter_type_id = record.get("matter_type_id")
        if matter_type_id is not None and str(matter_type_id) not in matter_types:
            errors.append(f"row {row_number}: unknown matter_type_id {matter_type_id!r}")
        start = record.get("data_collection_start")
        end = record.get("data_collection_end")
        if start and end and str(start) > str(end):
            errors.append(f"row {row_number}: data_collection_start is after data_collection_end")
        if record.get("review_status") == "accepted" and (
            not record.get("reviewer_role") or not record.get("reviewed_on")
        ):
            errors.append(
                f"row {row_number}: accepted evidence requires reviewer_role and reviewed_on"
            )
        if record.get("quality_appraisal_status") == "complete" and record.get("risk_of_bias") in {
            "not_appraised",
            None,
        }:
            errors.append(
                f"row {row_number}: completed appraisal requires a risk_of_bias conclusion"
            )
        records.append(record)
    if errors:
        preview = "; ".join(errors[:30])
        suffix = f"; {len(errors) - 30} additional error(s)" if len(errors) > 30 else ""
        raise EvidenceCatalogueError("Evidence catalogue validation failed: " + preview + suffix)

    records.sort(key=lambda row: str(row["evidence_record_id"]))
    records_path = destination / "evidence-records.csv"
    write_csv(records_path, expected_headers, records)

    domain_values = tuple(schema["properties"]["outcome_domain"]["enum"])
    coverage_rows = _coverage_rows(jurisdictions, records, domain_values)
    coverage_path = destination / "coverage-matrix.csv"
    write_csv(coverage_path, COVERAGE_HEADERS, coverage_rows)

    design_rows = _summary_rows(records)
    design_path = destination / "design-and-domain-summary.csv"
    write_csv(design_path, DESIGN_HEADERS, design_rows)

    effective_date = as_of or date.fromisoformat(str(project.project_config["status_as_of"]))
    accepted_count = sum(row.get("review_status") == "accepted" for row in records)
    appraised_count = sum(row.get("quality_appraisal_status") == "complete" for row in records)
    counts_by_design = dict(sorted(Counter(str(row["evidence_design"]) for row in records).items()))
    counts_by_domain = dict(sorted(Counter(str(row["outcome_domain"]) for row in records).items()))
    markdown_path = destination / "evidence-map.md"
    atomic_write_text(
        markdown_path,
        _markdown(
            effective_date,
            len(records),
            accepted_count,
            appraised_count,
            counts_by_design,
            counts_by_domain,
            coverage_rows,
        ),
    )

    artifacts = [records_path, coverage_path, design_path, markdown_path]
    summary = {
        "schema_version": "1.0",
        "built_on": effective_date.isoformat(),
        "input_path": source.relative_to(project.root).as_posix(),
        "input_sha256": sha256_file(source),
        "record_count": len(records),
        "accepted_count": accepted_count,
        "appraised_count": appraised_count,
        "jurisdiction_count": len({str(row["jurisdiction_id"]) for row in records}),
        "counts_by_design": counts_by_design,
        "counts_by_domain": counts_by_domain,
        "coverage_cells": len(coverage_rows),
        "artifacts": [
            {
                "path": path.relative_to(destination).as_posix(),
                "sha256": sha256_file(path),
            }
            for path in artifacts
        ],
    }
    _validate_summary(project, summary)
    summary_path = destination / "evidence-summary.json"
    write_json(summary_path, summary)
    verification = verify_evidence_catalogue(destination, project_or_root=project)
    if verification:
        raise EvidenceCatalogueError(
            "Built evidence catalogue failed verification: " + "; ".join(verification)
        )
    return EvidenceCatalogueResult(
        output_dir=destination,
        summary_path=summary_path,
        records_path=records_path,
        coverage_path=coverage_path,
        design_summary_path=design_path,
        markdown_path=markdown_path,
        record_count=len(records),
        accepted_count=accepted_count,
        appraised_count=appraised_count,
    )


def verify_evidence_catalogue(
    output_dir: Path,
    *,
    project_or_root: Project | Path | str | None = None,
) -> list[str]:
    """Verify summary schema, source digest, artifact hashes, and coverage row count."""

    directory = output_dir.expanduser().resolve()
    summary_path = directory / "evidence-summary.json"
    if not summary_path.is_file():
        return [f"Evidence summary does not exist: {summary_path}"]
    errors: list[str] = []
    try:
        raw = json.loads(summary_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"Could not read evidence summary: {exc}"]
    if not isinstance(raw, dict):
        return ["Evidence summary root must be an object"]
    project = _project(project_or_root) if project_or_root is not None else None
    if project is not None:
        try:
            _validate_summary(project, raw)
        except EvidenceCatalogueError as exc:
            errors.append(str(exc))
        input_relative = str(raw.get("input_path") or "")
        try:
            source = _confined(project, Path(input_relative))
        except EvidenceCatalogueError as exc:
            errors.append(str(exc))
        else:
            if not source.is_file():
                errors.append(f"Evidence input is missing: {input_relative}")
            elif sha256_file(source) != raw.get("input_sha256"):
                errors.append(f"Evidence input checksum mismatch: {input_relative}")
    required = {
        "evidence-records.csv",
        "coverage-matrix.csv",
        "design-and-domain-summary.csv",
        "evidence-map.md",
    }
    listed: set[str] = set()
    artifacts = raw.get("artifacts", [])
    if not isinstance(artifacts, list):
        errors.append("Evidence summary artifacts must be an array")
        artifacts = []
    for item in artifacts:
        if not isinstance(item, dict):
            errors.append("Malformed artifact entry in evidence summary")
            continue
        relative = str(item.get("path") or "")
        if Path(relative).is_absolute() or ".." in Path(relative).parts:
            errors.append(f"Unsafe evidence artifact path: {relative}")
            continue
        if relative in listed:
            errors.append(f"Duplicate evidence artifact path: {relative}")
            continue
        listed.add(relative)
        path = directory / relative
        if not path.is_file():
            errors.append(f"Evidence artifact is missing: {relative}")
        elif sha256_file(path) != item.get("sha256"):
            errors.append(f"Evidence artifact checksum mismatch: {relative}")
    for relative in sorted(required - listed):
        errors.append(f"Required evidence artifact not listed: {relative}")
    coverage_path = directory / "coverage-matrix.csv"
    if coverage_path.is_file():
        headers, rows = read_csv(coverage_path)
        if headers != COVERAGE_HEADERS:
            errors.append("Evidence coverage matrix columns do not match the contract")
        if len(rows) != raw.get("coverage_cells"):
            errors.append("Evidence coverage row count does not match summary")
    return errors


def _project(value: Project | Path | str) -> Project:
    return value if isinstance(value, Project) else load_project(Path(value))


def _confined(project: Project, value: Path) -> Path:
    candidate = value.expanduser()
    resolved = (
        candidate.resolve() if candidate.is_absolute() else (project.root / candidate).resolve()
    )
    try:
        resolved.relative_to(project.root)
    except ValueError as exc:
        raise EvidenceCatalogueError(f"Path escapes repository root: {value}") from exc
    return resolved


def _output_dir(project: Project, value: Path) -> Path:
    resolved = _confined(project, value)
    try:
        resolved.relative_to(project.root / "build")
    except ValueError as exc:
        raise EvidenceCatalogueError("Evidence products must be written under build/") from exc
    return resolved


def _register(project: Project, filename: str, key: str) -> dict[str, dict[str, str]]:
    _, rows = read_csv(project.root / "data/seed" / filename)
    return {row[key]: row for row in rows if row.get(key)}


def _coverage_rows(
    jurisdictions: dict[str, dict[str, str]],
    records: list[dict[str, Any]],
    domains: tuple[str, ...],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for jurisdiction_id, jurisdiction in sorted(jurisdictions.items()):
        for domain in domains:
            selected = [
                row
                for row in records
                if row.get("jurisdiction_id") == jurisdiction_id
                and row.get("outcome_domain") == domain
            ]
            accepted = sum(row.get("review_status") == "accepted" for row in selected)
            appraised = sum(row.get("quality_appraisal_status") == "complete" for row in selected)
            high_risk = sum(row.get("risk_of_bias") in {"high", "critical"} for row in selected)
            if appraised:
                state = "appraised"
            elif accepted:
                state = "reviewed"
            elif selected:
                state = "identified_unreviewed"
            else:
                state = "none"
            rows.append(
                {
                    "jurisdiction_id": jurisdiction_id,
                    "jurisdiction_name": jurisdiction.get("name", ""),
                    "outcome_domain": domain,
                    "record_count": len(selected),
                    "accepted_count": accepted,
                    "appraised_count": appraised,
                    "high_or_critical_risk_count": high_risk,
                    "coverage_state": state,
                }
            )
    return rows


def _summary_rows(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for summary_type, field in (
        ("design", "evidence_design"),
        ("outcome_domain", "outcome_domain"),
        ("review_status", "review_status"),
        ("risk_of_bias", "risk_of_bias"),
    ):
        categories = sorted({str(row[field]) for row in records})
        for category in categories:
            selected = [row for row in records if str(row[field]) == category]
            rows.append(
                {
                    "summary_type": summary_type,
                    "category": category,
                    "record_count": len(selected),
                    "accepted_count": sum(
                        row.get("review_status") == "accepted" for row in selected
                    ),
                    "appraised_count": sum(
                        row.get("quality_appraisal_status") == "complete" for row in selected
                    ),
                }
            )
    return rows


def _markdown(
    built_on: date,
    record_count: int,
    accepted_count: int,
    appraised_count: int,
    counts_by_design: dict[str, int],
    counts_by_domain: dict[str, int],
    coverage_rows: list[dict[str, Any]],
) -> str:
    cells_with_records = sum(int(row["record_count"]) > 0 for row in coverage_rows)
    lines = [
        "# Outcomes evidence map",
        "",
        f"Built on: {built_on.isoformat()}",
        "",
        "This product maps study-level evidence. It does not infer child or family outcomes ",
        "from court speed, order type, or clearance rate, and it does not pool unlike designs.",
        "",
        "## Catalogue status",
        "",
        f"- Records: {record_count}",
        f"- Accepted records: {accepted_count}",
        f"- Completed quality appraisals: {appraised_count}",
        f"- Jurisdiction/domain cells with at least one record: {cells_with_records}",
        "",
        "## Evidence designs",
        "",
    ]
    if counts_by_design:
        lines.extend(f"- {key}: {value}" for key, value in counts_by_design.items())
    else:
        lines.append("- No evidence records have been added.")
    lines.extend(["", "## Outcome domains", ""])
    if counts_by_domain:
        lines.extend(f"- {key}: {value}" for key, value in counts_by_domain.items())
    else:
        lines.append("- No evidence records have been added.")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "A zero cell is an explicit evidence-map gap for the current input, not proof that ",
            "no study exists. Search completion, inclusion decisions, local-language review, ",
            "rights review, and independent appraisal remain separate evidence requirements.",
            "",
        ]
    )
    return "\n".join(lines)


def _validate_summary(project: Project, summary: dict[str, Any]) -> None:
    schema = read_json(project.root / "schemas/outcomes_catalogue_summary.schema.json")
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(summary),
        key=lambda item: list(item.path),
    )
    if errors:
        rendered = []
        for error in errors:
            location = ".".join(str(part) for part in error.path)
            rendered.append(f"{location}: {error.message}" if location else error.message)
        raise EvidenceCatalogueError(
            "Evidence catalogue summary failed schema: " + "; ".join(rendered)
        )
