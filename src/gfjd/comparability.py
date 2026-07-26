"""Build and verify conservative comparability candidate groups.

The audit never declares observations comparable merely because labels match. It
constructs exact semantic signatures from the observation contract, reports where
series fragment across signatures, and preserves the separately reviewed
``comparability_tier`` on every observation.
"""

from __future__ import annotations

import json
import shutil
from collections import Counter, defaultdict
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from .io import (
    atomic_write_text,
    canonical_json_bytes,
    read_csv,
    read_json,
    sha256_bytes,
    sha256_file,
    write_csv,
    write_json,
)
from .project import Project, load_project
from .schema_validation import coerce_row


class ComparabilityError(RuntimeError):
    """Raised when a comparability audit cannot be built or verified."""


@dataclass(frozen=True, slots=True)
class ComparabilityResult:
    output_dir: Path
    summary_path: Path
    cells_path: Path
    index_path: Path
    issues_path: Path
    markdown_path: Path
    observation_count: int
    signature_count: int
    cross_jurisdiction_candidate_count: int
    error_count: int
    warning_count: int

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        for field in (
            "output_dir",
            "summary_path",
            "cells_path",
            "index_path",
            "issues_path",
            "markdown_path",
        ):
            payload[field] = str(payload[field])
        return payload


SIGNATURE_FIELDS = (
    "indicator_id",
    "matter_type_harmonised",
    "proceeding_type",
    "court_level",
    "stage_start",
    "stage_end",
    "statistic_type",
    "unit",
    "count_unit",
    "denominator_definition",
    "time_basis",
    "cohort_basis",
    "population_scope",
)

CELL_HEADERS = [
    "signature_id",
    *SIGNATURE_FIELDS,
    "observation_count",
    "jurisdiction_count",
    "jurisdictions",
    "period_start_min",
    "period_end_max",
    "minimum_declared_tier",
    "maximum_declared_tier",
    "release_eligible_count",
    "comparison_state",
]

INDEX_HEADERS = [
    "observation_id",
    "signature_id",
    "jurisdiction_id",
    "period_start",
    "period_end",
    "declared_comparability_tier",
    "release_eligible",
    "review_status",
]

ISSUE_HEADERS = [
    "severity",
    "code",
    "indicator_id",
    "matter_type_harmonised",
    "signature_id",
    "observation_ids",
    "message",
]


def build_comparability_audit(
    project_or_root: Project | Path | str,
    output_dir: Path = Path("build/comparability"),
    *,
    input_patterns: Sequence[str] = ("data/gold/**/*.csv",),
    as_of: date | None = None,
    clean: bool = True,
) -> ComparabilityResult:
    """Build candidate groups and surface definitional fragmentation or unsafe tiers."""

    project = _project(project_or_root)
    destination = _output_dir(project, output_dir)
    if clean:
        shutil.rmtree(destination, ignore_errors=True)
    destination.mkdir(parents=True, exist_ok=True)

    paths = _expand_inputs(project, input_patterns)
    schema = read_json(project.root / "schemas/observation.schema.json")
    expected_headers = list(schema["properties"])
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    indicator_domains = _indicator_domains(project)
    observations: list[dict[str, Any]] = []
    errors: list[str] = []
    seen: set[str] = set()
    input_entries: list[dict[str, str]] = []
    for path in paths:
        headers, rows = read_csv(path)
        relative = path.relative_to(project.root).as_posix()
        if headers != expected_headers:
            errors.append(f"{relative}: columns do not match the observation contract")
            continue
        input_entries.append({"path": relative, "sha256": sha256_file(path)})
        for row_number, raw in enumerate(rows, start=2):
            row = coerce_row(raw, schema)
            for error in sorted(validator.iter_errors(row), key=lambda item: list(item.path)):
                location = ".".join(str(part) for part in error.path)
                errors.append(
                    f"{relative} row {row_number}"
                    f"{' field ' + location if location else ''}: {error.message}"
                )
            observation_id = str(row.get("observation_id") or "")
            if observation_id in seen:
                errors.append(
                    f"{relative} row {row_number}: duplicate observation_id {observation_id}"
                )
            seen.add(observation_id)
            observations.append(row)
    if errors:
        preview = "; ".join(errors[:30])
        suffix = f"; {len(errors) - 30} additional error(s)" if len(errors) > 30 else ""
        raise ComparabilityError("Comparability input validation failed: " + preview + suffix)

    observations.sort(key=lambda row: str(row["observation_id"]))
    by_signature: dict[str, list[dict[str, Any]]] = defaultdict(list)
    signatures: dict[str, dict[str, Any]] = {}
    index_rows: list[dict[str, Any]] = []
    issues: list[dict[str, Any]] = []
    for row in observations:
        signature = {field: row.get(field) for field in SIGNATURE_FIELDS}
        signature_id = "CMP_" + sha256_bytes(canonical_json_bytes(signature))[:20].upper()
        if signature_id in signatures and signatures[signature_id] != signature:
            raise ComparabilityError(f"Signature collision detected: {signature_id}")
        signatures[signature_id] = signature
        by_signature[signature_id].append(row)
        index_rows.append(
            {
                "observation_id": row["observation_id"],
                "signature_id": signature_id,
                "jurisdiction_id": row["jurisdiction_id"],
                "period_start": row["period_start"],
                "period_end": row["period_end"],
                "declared_comparability_tier": row["comparability_tier"],
                "release_eligible": row["release_eligible"],
                "review_status": row["review_status"],
            }
        )
        if bool(row.get("release_eligible")) and int(row["comparability_tier"]) > 2:
            issues.append(
                _issue(
                    "error",
                    "RELEASE_ELIGIBLE_TIER_GT2",
                    row,
                    signature_id,
                    [str(row["observation_id"])],
                    "Release-eligible observation is declared Tier 3 or 4.",
                )
            )
        if indicator_domains.get(str(row["indicator_id"])) == "timeliness" and (
            not row.get("stage_start") or not row.get("stage_end")
        ):
            issues.append(
                _issue(
                    "warning",
                    "TIMELINESS_CLOCK_UNSPECIFIED",
                    row,
                    signature_id,
                    [str(row["observation_id"])],
                    "Timeliness observation lacks an explicit start or end event.",
                )
            )

    cell_rows: list[dict[str, Any]] = []
    cross_jurisdiction = 0
    for signature_id, rows in sorted(by_signature.items()):
        signature = signatures[signature_id]
        jurisdictions = sorted({str(row["jurisdiction_id"]) for row in rows})
        tiers = sorted({int(row["comparability_tier"]) for row in rows})
        if len(jurisdictions) >= 2 and max(tiers, default=4) <= 2:
            state = "cross_jurisdiction_candidate"
            cross_jurisdiction += 1
            issues.append(
                _issue(
                    "info",
                    "CANDIDATE_REQUIRES_METHODS_REVIEW",
                    rows[0],
                    signature_id,
                    [str(row["observation_id"]) for row in rows],
                    "Exact signatures align across jurisdictions, but comparability still "
                    "requires accountable methods review.",
                )
            )
        elif len(jurisdictions) >= 2:
            state = "descriptive_only"
        else:
            state = "single_jurisdiction"
        if len(tiers) > 1:
            issues.append(
                _issue(
                    "warning",
                    "DECLARED_TIER_CONFLICT",
                    rows[0],
                    signature_id,
                    [str(row["observation_id"]) for row in rows],
                    "Observations with the same exact signature have inconsistent declared tiers.",
                )
            )
        cell_rows.append(
            {
                "signature_id": signature_id,
                **signature,
                "observation_count": len(rows),
                "jurisdiction_count": len(jurisdictions),
                "jurisdictions": ";".join(jurisdictions),
                "period_start_min": min(str(row["period_start"]) for row in rows),
                "period_end_max": max(str(row["period_end"]) for row in rows),
                "minimum_declared_tier": min(tiers),
                "maximum_declared_tier": max(tiers),
                "release_eligible_count": sum(bool(row["release_eligible"]) for row in rows),
                "comparison_state": state,
            }
        )

    series_signatures: dict[tuple[str, str], set[str]] = defaultdict(set)
    series_rows: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for signature_id, rows in by_signature.items():
        key = (str(rows[0]["indicator_id"]), str(rows[0]["matter_type_harmonised"]))
        series_signatures[key].add(signature_id)
        series_rows[key].extend(rows)
    for key, signature_ids in sorted(series_signatures.items()):
        rows = series_rows[key]
        if len(signature_ids) > 1 and len(rows) > 1:
            issues.append(
                {
                    "severity": "info",
                    "code": "SERIES_FRAGMENTED_BY_DEFINITION",
                    "indicator_id": key[0],
                    "matter_type_harmonised": key[1],
                    "signature_id": ";".join(sorted(signature_ids)),
                    "observation_ids": ";".join(sorted(str(row["observation_id"]) for row in rows)),
                    "message": (
                        "The indicator/matter series contains multiple semantic signatures; "
                        "these rows must not be pooled without a documented transformation."
                    ),
                }
            )

    issues.sort(
        key=lambda row: (
            {"error": 0, "warning": 1, "info": 2}[str(row["severity"])],
            str(row["code"]),
            str(row["indicator_id"]),
            str(row["signature_id"]),
        )
    )
    cells_path = destination / "comparability-cells.csv"
    index_path = destination / "observation-signature-index.csv"
    issues_path = destination / "comparability-issues.csv"
    write_csv(cells_path, CELL_HEADERS, cell_rows)
    write_csv(index_path, INDEX_HEADERS, index_rows)
    write_csv(issues_path, ISSUE_HEADERS, issues)

    issue_counts = dict(sorted(Counter(str(row["severity"]) for row in issues).items()))
    state_counts = dict(sorted(Counter(str(row["comparison_state"]) for row in cell_rows).items()))
    effective_date = as_of or date.fromisoformat(str(project.project_config["status_as_of"]))
    markdown_path = destination / "comparability-audit.md"
    atomic_write_text(
        markdown_path,
        _markdown(
            effective_date,
            len(observations),
            len(cell_rows),
            cross_jurisdiction,
            issue_counts,
            state_counts,
        ),
    )
    artifacts = [cells_path, index_path, issues_path, markdown_path]
    summary = {
        "schema_version": "1.0",
        "built_on": effective_date.isoformat(),
        "signature_fields": list(SIGNATURE_FIELDS),
        "inputs": input_entries,
        "observation_count": len(observations),
        "signature_count": len(cell_rows),
        "cross_jurisdiction_candidate_count": cross_jurisdiction,
        "issue_counts": issue_counts,
        "state_counts": state_counts,
        "artifacts": [
            {"path": path.relative_to(destination).as_posix(), "sha256": sha256_file(path)}
            for path in artifacts
        ],
    }
    _validate_summary(project, summary)
    summary_path = destination / "comparability-summary.json"
    write_json(summary_path, summary)
    verification = verify_comparability_audit(destination, project_or_root=project)
    if verification:
        raise ComparabilityError(
            "Built comparability audit failed verification: " + "; ".join(verification)
        )
    return ComparabilityResult(
        output_dir=destination,
        summary_path=summary_path,
        cells_path=cells_path,
        index_path=index_path,
        issues_path=issues_path,
        markdown_path=markdown_path,
        observation_count=len(observations),
        signature_count=len(cell_rows),
        cross_jurisdiction_candidate_count=cross_jurisdiction,
        error_count=issue_counts.get("error", 0),
        warning_count=issue_counts.get("warning", 0),
    )


def verify_comparability_audit(
    output_dir: Path,
    *,
    project_or_root: Project | Path | str | None = None,
) -> list[str]:
    """Verify contracts, input drift, artifact hashes, and summary row counts."""

    directory = output_dir.expanduser().resolve()
    summary_path = directory / "comparability-summary.json"
    if not summary_path.is_file():
        return [f"Comparability summary does not exist: {summary_path}"]
    try:
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"Could not read comparability summary: {exc}"]
    if not isinstance(summary, dict):
        return ["Comparability summary root must be an object"]
    errors: list[str] = []
    project = _project(project_or_root) if project_or_root is not None else None
    if project is not None:
        try:
            _validate_summary(project, summary)
        except ComparabilityError as exc:
            errors.append(str(exc))
        for item in summary.get("inputs", []):
            if not isinstance(item, dict):
                errors.append("Malformed comparability input entry")
                continue
            relative = str(item.get("path") or "")
            try:
                path = _confined(project, Path(relative))
            except ComparabilityError as exc:
                errors.append(str(exc))
                continue
            if not path.is_file():
                errors.append(f"Comparability input is missing: {relative}")
            elif sha256_file(path) != item.get("sha256"):
                errors.append(f"Comparability input checksum mismatch: {relative}")
    required = {
        "comparability-cells.csv",
        "observation-signature-index.csv",
        "comparability-issues.csv",
        "comparability-audit.md",
    }
    listed: set[str] = set()
    artifacts = summary.get("artifacts", [])
    if not isinstance(artifacts, list):
        errors.append("Comparability summary artifacts must be an array")
        artifacts = []
    for item in artifacts:
        if not isinstance(item, dict):
            errors.append("Malformed comparability artifact entry")
            continue
        relative = str(item.get("path") or "")
        if Path(relative).is_absolute() or ".." in Path(relative).parts:
            errors.append(f"Unsafe comparability artifact path: {relative}")
            continue
        if relative in listed:
            errors.append(f"Duplicate comparability artifact path: {relative}")
            continue
        listed.add(relative)
        path = directory / relative
        if not path.is_file():
            errors.append(f"Comparability artifact is missing: {relative}")
        elif sha256_file(path) != item.get("sha256"):
            errors.append(f"Comparability artifact checksum mismatch: {relative}")
    for relative in sorted(required - listed):
        errors.append(f"Required comparability artifact not listed: {relative}")
    cells_path = directory / "comparability-cells.csv"
    if cells_path.is_file():
        headers, rows = read_csv(cells_path)
        if headers != CELL_HEADERS:
            errors.append("Comparability cell columns do not match the contract")
        if len(rows) != summary.get("signature_count"):
            errors.append("Comparability signature row count does not match summary")
    index_path = directory / "observation-signature-index.csv"
    if index_path.is_file():
        headers, rows = read_csv(index_path)
        if headers != INDEX_HEADERS:
            errors.append("Comparability index columns do not match the contract")
        if len(rows) != summary.get("observation_count"):
            errors.append("Comparability observation row count does not match summary")
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
        raise ComparabilityError(f"Path escapes repository root: {value}") from exc
    return resolved


def _output_dir(project: Project, value: Path) -> Path:
    resolved = _confined(project, value)
    try:
        resolved.relative_to(project.root / "build")
    except ValueError as exc:
        raise ComparabilityError("Comparability products must be written under build/") from exc
    return resolved


def _expand_inputs(project: Project, patterns: Sequence[str]) -> list[Path]:
    paths: set[Path] = set()
    for raw in patterns:
        pattern = str(raw)
        if not pattern or Path(pattern).is_absolute() or ".." in Path(pattern).parts:
            raise ComparabilityError(f"Unsafe comparability input pattern: {pattern!r}")
        if any(token in pattern for token in "*?["):
            matches = tuple(project.root.glob(pattern))
        else:
            candidate = _confined(project, Path(pattern))
            matches = (candidate,)
        for path in matches:
            resolved = path.resolve()
            try:
                resolved.relative_to(project.root)
            except ValueError as exc:
                raise ComparabilityError(f"Input escapes repository root: {path}") from exc
            if resolved.is_file() and resolved.suffix.lower() == ".csv":
                paths.add(resolved)
    return sorted(paths)


def _indicator_domains(project: Project) -> dict[str, str]:
    _, rows = read_csv(project.root / "data/seed/indicator_dictionary.csv")
    return {row["indicator_id"]: row["domain"] for row in rows if row.get("indicator_id")}


def _issue(
    severity: str,
    code: str,
    row: dict[str, Any],
    signature_id: str,
    observation_ids: list[str],
    message: str,
) -> dict[str, Any]:
    return {
        "severity": severity,
        "code": code,
        "indicator_id": row["indicator_id"],
        "matter_type_harmonised": row["matter_type_harmonised"],
        "signature_id": signature_id,
        "observation_ids": ";".join(sorted(observation_ids)),
        "message": message,
    }


def _markdown(
    built_on: date,
    observations: int,
    signatures: int,
    cross_jurisdiction: int,
    issue_counts: dict[str, int],
    state_counts: dict[str, int],
) -> str:
    lines = [
        "# Comparability audit",
        "",
        f"Built on: {built_on.isoformat()}",
        "",
        "This audit forms conservative exact-signature candidate groups. A candidate is not an ",
        (
            "approval to pool, rank, or infer equivalence; accountable methods review "
            "remains required."
        ),
        "",
        "## Status",
        "",
        f"- Observations audited: {observations}",
        f"- Exact semantic signatures: {signatures}",
        f"- Cross-jurisdiction candidates: {cross_jurisdiction}",
        f"- Errors: {issue_counts.get('error', 0)}",
        f"- Warnings: {issue_counts.get('warning', 0)}",
        f"- Informational findings: {issue_counts.get('info', 0)}",
        "",
        "## Candidate states",
        "",
    ]
    if state_counts:
        lines.extend(f"- {key}: {value}" for key, value in state_counts.items())
    else:
        lines.append("- No gold observations were present in the selected inputs.")
    lines.extend(
        [
            "",
            "## Interpretation rules",
            "",
            "- Different signatures must not be silently pooled.",
            "- Identical signatures still require substantive and jurisdictional review.",
            "- Declared Tier 3 or 4 observations are descriptive only.",
            "- The audit never upgrades a record's reviewed comparability tier.",
            "",
        ]
    )
    return "\n".join(lines)


def _validate_summary(project: Project, summary: dict[str, Any]) -> None:
    schema = read_json(project.root / "schemas/comparability_summary.schema.json")
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(summary),
        key=lambda item: list(item.path),
    )
    if errors:
        rendered: list[str] = []
        for error in errors:
            location = ".".join(str(part) for part in error.path)
            rendered.append(f"{location}: {error.message}" if location else error.message)
        raise ComparabilityError("Comparability summary failed schema: " + "; ".join(rendered))
