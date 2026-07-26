"""Repository validation for Global Family Justice Data.

The validator deliberately uses the Python standard library so that basic data
contract checks can run in constrained environments. JSON Schema documents are
used as the source of field names, required fields, enums, patterns, primitive
types, dates, and URI expectations. Cross-table and release-layer rules are
implemented below.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import date
from hashlib import sha256
from pathlib import Path
from typing import Any, TypedDict
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]


class TableSpec(TypedDict):
    path: Path
    schema: Path
    id: str


TABLES: dict[str, TableSpec] = {
    "jurisdictions": {
        "path": ROOT / "data/seed/jurisdiction_register.csv",
        "schema": ROOT / "schemas/jurisdiction.schema.json",
        "id": "jurisdiction_id",
    },
    "sources": {
        "path": ROOT / "data/seed/source_register.csv",
        "schema": ROOT / "schemas/source.schema.json",
        "id": "source_id",
    },
    "indicators": {
        "path": ROOT / "data/seed/indicator_dictionary.csv",
        "schema": ROOT / "schemas/indicator.schema.json",
        "id": "indicator_id",
    },
    "evidence": {
        "path": ROOT / "data/seed/evidence_catalogue.csv",
        "schema": ROOT / "schemas/evidence.schema.json",
        "id": "evidence_id",
    },
    "institutions": {
        "path": ROOT / "data/seed/institution_register.csv",
        "schema": ROOT / "schemas/institution.schema.json",
        "id": "institution_id",
    },
    "transformations": {
        "path": ROOT / "data/seed/transformation_register.csv",
        "schema": ROOT / "schemas/transformation.schema.json",
        "id": "transformation_id",
    },
    "releases": {
        "path": ROOT / "data/seed/release_register.csv",
        "schema": ROOT / "schemas/release.schema.json",
        "id": "release_id",
    },
    "observation_template": {
        "path": ROOT / "data/seed/observation_template.csv",
        "schema": ROOT / "schemas/observation.schema.json",
        "id": "observation_id",
    },
}

IGNORED_MANIFEST_PARTS = {
    ".git",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "__pycache__",
    "dist",
    "build",
    "htmlcov",
    ".tox",
    ".nox",
    ".venv",
    "venv",
}

IGNORED_MANIFEST_NAMES = {".coverage"}


def is_ignored_manifest_path(relative: Path) -> bool:
    """Return whether a repository-relative path is a generated local artifact."""
    return (
        relative.name in IGNORED_MANIFEST_NAMES
        or any(part in IGNORED_MANIFEST_PARTS or part.endswith(".egg-info") for part in relative.parts)
    )


@dataclass
class ValidationReport:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    row_counts: dict[str, int] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return not self.errors

    def add_error(self, message: str) -> None:
        self.errors.append(message)

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)


@dataclass
class LoadedTable:
    name: str
    path: Path
    schema: dict[str, Any]
    headers: list[str]
    rows: list[dict[str, str]]


def _relative(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _read_json(path: Path, report: ValidationReport) -> dict[str, Any]:
    try:
        with path.open(encoding="utf-8") as handle:
            value = json.load(handle)
    except FileNotFoundError:
        report.add_error(f"Missing schema: {_relative(path)}")
        return {}
    except json.JSONDecodeError as exc:
        report.add_error(f"{_relative(path)}: invalid JSON: {exc}")
        return {}
    if not isinstance(value, dict):
        report.add_error(f"{_relative(path)}: schema root must be an object")
        return {}
    return value


def _read_csv(path: Path, report: ValidationReport) -> tuple[list[str], list[dict[str, str]]]:
    try:
        with path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            headers = [str(header) for header in (reader.fieldnames or [])]
            raw_rows = list(reader)
            rows: list[dict[str, str]] = []
            for raw_row in raw_rows:
                normalised: dict[str, str] = {}
                for key, value in raw_row.items():
                    if key is None:
                        continue
                    normalised[str(key)] = "" if value is None else str(value)
                rows.append(normalised)
    except FileNotFoundError:
        report.add_error(f"Missing file: {_relative(path)}")
        return [], []
    except csv.Error as exc:
        report.add_error(f"{_relative(path)}: invalid CSV: {exc}")
        return [], []

    if not headers:
        report.add_error(f"{_relative(path)}: missing header row")
    if len(headers) != len(set(headers)):
        duplicates = sorted({h for h in headers if headers.count(h) > 1})
        report.add_error(f"{_relative(path)}: duplicate headers {duplicates}")
    for index, row in enumerate(rows, start=2):
        if None in row:
            report.add_error(f"{_relative(path)}:{index}: row has more values than headers")
    return headers, rows


def _allowed_types(rule: dict[str, Any]) -> list[str]:
    declared = rule.get("type")
    if declared is None:
        return []
    if isinstance(declared, list):
        return [str(item) for item in declared]
    return [str(declared)]


def _validate_value(
    *,
    value: str,
    rule: dict[str, Any],
    field_name: str,
    location: str,
    report: ValidationReport,
) -> None:
    if value == "":
        return

    enum = rule.get("enum")
    if enum is not None and value not in {str(item) for item in enum}:
        report.add_error(f"{location}: {field_name}={value!r} is not one of {enum}")

    pattern = rule.get("pattern")
    if pattern and re.fullmatch(str(pattern), value) is None:
        report.add_error(f"{location}: {field_name}={value!r} does not match {pattern!r}")

    types = _allowed_types(rule)
    if "number" in types:
        try:
            number = float(value)
        except ValueError:
            report.add_error(f"{location}: {field_name}={value!r} is not numeric")
        else:
            if not math.isfinite(number):
                report.add_error(f"{location}: {field_name} must be finite")
            minimum = rule.get("minimum")
            if minimum is not None and number < float(minimum):
                report.add_error(f"{location}: {field_name} is below minimum {minimum}")
    elif "integer" in types:
        try:
            integer = int(value)
        except ValueError:
            report.add_error(f"{location}: {field_name}={value!r} is not an integer")
        else:
            minimum = rule.get("minimum")
            if minimum is not None and integer < int(minimum):
                report.add_error(f"{location}: {field_name} is below minimum {minimum}")
    elif "boolean" in types and value.lower() not in {"true", "false"}:
        report.add_error(f"{location}: {field_name}={value!r} is not a boolean")

    if rule.get("format") == "date":
        try:
            date.fromisoformat(value)
        except ValueError:
            report.add_error(f"{location}: {field_name}={value!r} is not an ISO date")
    elif rule.get("format") == "uri":
        parsed = urlparse(value)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            report.add_error(f"{location}: {field_name}={value!r} is not an HTTP(S) URI")

    min_length = rule.get("minLength")
    if min_length is not None and len(value) < int(min_length):
        report.add_error(f"{location}: {field_name} is shorter than {min_length}")


def _load_and_validate_table(
    name: str,
    path: Path,
    schema_path: Path,
    unique_field: str,
    report: ValidationReport,
) -> LoadedTable:
    schema = _read_json(schema_path, report)
    headers, rows = _read_csv(path, report)
    properties = schema.get("properties", {}) if schema else {}
    required = set(schema.get("required", [])) if schema else set()

    if properties:
        expected = set(properties)
        actual = set(headers)
        missing_headers = sorted(expected - actual)
        unexpected_headers = sorted(actual - expected)
        if missing_headers:
            report.add_error(f"{_relative(path)}: missing schema columns {missing_headers}")
        if unexpected_headers:
            report.add_error(f"{_relative(path)}: unexpected columns {unexpected_headers}")

    seen: set[str] = set()
    for index, row in enumerate(rows, start=2):
        location = f"{_relative(path)}:{index}"
        for field_name in required:
            if not (row.get(field_name) or "").strip():
                report.add_error(f"{location}: required field {field_name!r} is blank")
        for field_name, rule in properties.items():
            value = (row.get(field_name) or "").strip()
            _validate_value(
                value=value,
                rule=rule,
                field_name=field_name,
                location=location,
                report=report,
            )
            if row.get(field_name, "") != value:
                report.add_warning(f"{location}: {field_name!r} has leading or trailing whitespace")

        identifier = (row.get(unique_field) or "").strip()
        if identifier:
            if identifier in seen:
                report.add_error(f"{location}: duplicate {unique_field} {identifier!r}")
            seen.add(identifier)

    report.row_counts[name] = len(rows)
    return LoadedTable(name=name, path=path, schema=schema, headers=headers, rows=rows)


def _parse_iso(value: str) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _validate_cross_table(tables: dict[str, LoadedTable], report: ValidationReport) -> None:
    jurisdictions = tables["jurisdictions"].rows
    sources = tables["sources"].rows
    indicators = tables["indicators"].rows
    evidence = tables["evidence"].rows
    institutions = tables["institutions"].rows
    transformations = tables["transformations"].rows
    releases = tables["releases"].rows

    jurisdiction_ids = {r["jurisdiction_id"].strip() for r in jurisdictions if r.get("jurisdiction_id")}
    source_ids = {r["source_id"].strip() for r in sources if r.get("source_id")}
    indicator_ids = {r["indicator_id"].strip() for r in indicators if r.get("indicator_id")}
    institution_ids = {r["institution_id"].strip() for r in institutions if r.get("institution_id")}

    for index, row in enumerate(jurisdictions, start=2):
        location = f"data/seed/jurisdiction_register.csv:{index}"
        parent = row.get("parent_jurisdiction_id", "").strip()
        current = row.get("jurisdiction_id", "").strip()
        if parent and parent not in jurisdiction_ids:
            report.add_error(f"{location}: unknown parent_jurisdiction_id {parent!r}")
        if parent and parent == current:
            report.add_error(f"{location}: jurisdiction cannot be its own parent")
        status = row.get("coverage_status", "").strip()
        completed = row.get("search_completed_at", "").strip()
        second_reviewed = row.get("second_reviewed", "").strip()
        if status in {"no_public_source_found", "source_inaccessible", "verified_complete"}:
            if not completed:
                report.add_error(f"{location}: coverage_status {status!r} requires search_completed_at")
            if second_reviewed != "yes":
                report.add_error(f"{location}: coverage_status {status!r} requires second_reviewed='yes'")

    for index, row in enumerate(sources, start=2):
        location = f"data/seed/source_register.csv:{index}"
        jurisdiction_id = row.get("jurisdiction_id", "").strip()
        if jurisdiction_id not in jurisdiction_ids:
            report.add_error(f"{location}: unknown jurisdiction_id {jurisdiction_id!r}")
        archived = row.get("archived_url", "").strip()
        if archived:
            parsed = urlparse(archived)
            if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                report.add_error(f"{location}: archived_url is not an HTTP(S) URI")
        last_verified = _parse_iso(row.get("last_verified", "").strip())
        next_due = _parse_iso(row.get("next_review_due", "").strip())
        if last_verified and next_due and next_due < last_verified:
            report.add_error(f"{location}: next_review_due precedes last_verified")
        if row.get("priority", "").strip() == "high" and row.get("licence_status", "").strip() == "":
            report.add_error(f"{location}: high-priority source requires licence_status")
        if row.get("priority", "").strip() == "high" and row.get("rights_reviewed", "").strip() != "yes":
            report.add_warning(f"{location}: high-priority source rights review is incomplete")
        if (
            row.get("rights_reviewed", "").strip() == "yes"
            and row.get("redistribution_decision", "").strip() == "unknown"
        ):
            report.add_error(f"{location}: completed rights review cannot have redistribution_decision='unknown'")

    for index, row in enumerate(indicators, start=2):
        location = f"data/seed/indicator_dictionary.csv:{index}"
        replacement = row.get("replacement_indicator_id", "").strip()
        current = row.get("indicator_id", "").strip()
        if replacement and replacement not in indicator_ids:
            report.add_error(f"{location}: unknown replacement_indicator_id {replacement!r}")
        if replacement and replacement == current:
            report.add_error(f"{location}: indicator cannot replace itself")
        if row.get("status", "").strip() == "deprecated" and not replacement:
            report.add_warning(f"{location}: deprecated indicator has no replacement")

    for index, row in enumerate(evidence, start=2):
        location = f"data/seed/evidence_catalogue.csv:{index}"
        jurisdiction_id = row.get("jurisdiction_id", "").strip()
        source_id = row.get("source_id", "").strip()
        if jurisdiction_id not in jurisdiction_ids:
            report.add_error(f"{location}: unknown jurisdiction_id {jurisdiction_id!r}")
        if source_id and source_id not in source_ids:
            report.add_error(f"{location}: unknown source_id {source_id!r}")
        start = _parse_iso(row.get("period_start", "").strip())
        end = _parse_iso(row.get("period_end", "").strip())
        if start and end and end < start:
            report.add_error(f"{location}: period_end precedes period_start")
        if row.get("review_status", "").strip() == "approved" and row.get("second_reviewed", "").strip() != "yes":
            report.add_error(f"{location}: approved evidence requires second_reviewed='yes'")

    for index, row in enumerate(institutions, start=2):
        location = f"data/seed/institution_register.csv:{index}"
        jurisdiction_id = row.get("jurisdiction_id", "").strip()
        parent = row.get("parent_institution_id", "").strip()
        current = row.get("institution_id", "").strip()
        if jurisdiction_id not in jurisdiction_ids:
            report.add_error(f"{location}: unknown jurisdiction_id {jurisdiction_id!r}")
        if parent and parent not in institution_ids:
            report.add_error(f"{location}: unknown parent_institution_id {parent!r}")
        if parent and parent == current:
            report.add_error(f"{location}: institution cannot be its own parent")
        active_from = _parse_iso(row.get("active_from", "").strip())
        active_to = _parse_iso(row.get("active_to", "").strip())
        if active_from and active_to and active_to < active_from:
            report.add_error(f"{location}: active_to precedes active_from")
        official_url = row.get("official_url", "").strip()
        if official_url:
            parsed = urlparse(official_url)
            if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                report.add_error(f"{location}: official_url is not an HTTP(S) URI")

    for index, row in enumerate(transformations, start=2):
        location = f"data/seed/transformation_register.csv:{index}"
        implementation = row.get("implementation_path", "").strip()
        tests_path = row.get("tests_path", "").strip()
        if row.get("review_status", "").strip() == "approved" and not implementation:
            report.add_error(f"{location}: approved transformation requires implementation_path")
        if implementation and not (ROOT / implementation).exists():
            report.add_warning(f"{location}: implementation_path does not exist: {implementation}")
        if tests_path and not (ROOT / tests_path).exists():
            report.add_warning(f"{location}: tests_path does not exist: {tests_path}")

    for index, row in enumerate(releases, start=2):
        location = f"data/seed/release_register.csv:{index}"
        if row.get("release_status", "").strip() == "stable":
            required_release_fields = (
                "git_commit",
                "archive_identifier",
                "manifest_sha256",
                "release_manager",
                "release_authority",
            )
            for field_name in required_release_fields:
                if not row.get(field_name, "").strip():
                    report.add_error(f"{location}: stable release requires {field_name}")


def _observation_files() -> list[tuple[Path, str]]:
    files: list[tuple[Path, str]] = []
    for layer in ("silver", "gold"):
        base = ROOT / "data" / layer
        if base.exists():
            for path in sorted(base.rglob("*.csv")):
                files.append((path, layer))
    return files


def _validate_observations(
    tables: dict[str, LoadedTable],
    report: ValidationReport,
) -> None:
    schema_path = ROOT / "schemas/observation.schema.json"
    jurisdiction_ids = {r["jurisdiction_id"].strip() for r in tables["jurisdictions"].rows if r.get("jurisdiction_id")}
    source_ids = {r["source_id"].strip() for r in tables["sources"].rows if r.get("source_id")}
    indicator_ids = {r["indicator_id"].strip() for r in tables["indicators"].rows if r.get("indicator_id")}
    institution_ids = {r["institution_id"].strip() for r in tables["institutions"].rows if r.get("institution_id")}
    transformation_ids = {
        r["transformation_id"].strip()
        for r in tables["transformations"].rows
        if r.get("transformation_id")
    }
    release_ids = {r["release_id"].strip() for r in tables["releases"].rows if r.get("release_id")}
    seen_observations: set[str] = set()

    for path, layer in _observation_files():
        table = _load_and_validate_table(
            name=f"{layer}:{_relative(path)}",
            path=path,
            schema_path=schema_path,
            unique_field="observation_id",
            report=report,
        )
        for index, row in enumerate(table.rows, start=2):
            location = f"{_relative(path)}:{index}"
            obs_id = row.get("observation_id", "").strip()
            if obs_id in seen_observations:
                report.add_error(f"{location}: observation_id {obs_id!r} duplicates another file")
            seen_observations.add(obs_id)
            if row.get("jurisdiction_id", "").strip() not in jurisdiction_ids:
                report.add_error(f"{location}: unknown jurisdiction_id")
            if row.get("source_id", "").strip() not in source_ids:
                report.add_error(f"{location}: unknown source_id")
            if row.get("indicator_id", "").strip() not in indicator_ids:
                report.add_error(f"{location}: unknown indicator_id")
            institution_id = row.get("institution_id", "").strip()
            transformation_id = row.get("transformation_id", "").strip()
            release_id = row.get("release_id", "").strip()
            if institution_id and institution_id not in institution_ids:
                report.add_error(f"{location}: unknown institution_id {institution_id!r}")
            if transformation_id and transformation_id not in transformation_ids:
                report.add_error(f"{location}: unknown transformation_id {transformation_id!r}")
            if release_id and release_id not in release_ids:
                report.add_error(f"{location}: unknown release_id {release_id!r}")
            start = _parse_iso(row.get("period_start", "").strip())
            end = _parse_iso(row.get("period_end", "").strip())
            if start and end and end < start:
                report.add_error(f"{location}: period_end precedes period_start")
            if layer == "gold":
                if row.get("second_reviewed", "").strip() != "yes":
                    report.add_error(f"{location}: gold observation requires second_reviewed='yes'")
                if row.get("review_status", "").strip() != "approved":
                    report.add_error(f"{location}: gold observation requires review_status='approved'")
                if row.get("comparability_tier", "").strip() not in {"1", "2"}:
                    report.add_error(f"{location}: gold observation must be comparability tier 1 or 2")
                if not row.get("transformation_id", "").strip():
                    report.add_error(f"{location}: gold observation requires transformation_id")
                if not row.get("source_version", "").strip():
                    report.add_error(f"{location}: gold observation requires source_version")
                if not row.get("release_id", "").strip():
                    report.add_error(f"{location}: gold observation requires release_id")


def _manifest_files() -> Iterable[Path]:
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.name == "MANIFEST.sha256":
            continue
        relative = path.relative_to(ROOT)
        if is_ignored_manifest_path(relative):
            continue
        yield path


def verify_manifest(report: ValidationReport, strict: bool = True) -> None:
    manifest_path = ROOT / "MANIFEST.sha256"
    if not manifest_path.exists():
        report.add_error("Missing MANIFEST.sha256")
        return

    expected: dict[str, str] = {}
    for line_number, raw in enumerate(manifest_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip():
            continue
        try:
            digest, relative = raw.split("  ", 1)
        except ValueError:
            report.add_error(f"MANIFEST.sha256:{line_number}: invalid line")
            continue
        if not re.fullmatch(r"[a-f0-9]{64}", digest):
            report.add_error(f"MANIFEST.sha256:{line_number}: invalid digest")
            continue
        expected[relative] = digest

    actual_paths = {str(path.relative_to(ROOT)): path for path in _manifest_files()}
    for relative, digest in expected.items():
        path = ROOT / relative
        if not path.exists():
            report.add_error(f"MANIFEST.sha256: listed file missing: {relative}")
            continue
        actual = sha256(path.read_bytes()).hexdigest()
        if actual != digest:
            report.add_error(f"MANIFEST.sha256: checksum mismatch: {relative}")

    if strict:
        unlisted = sorted(set(actual_paths) - set(expected))
        extra = sorted(set(expected) - set(actual_paths))
        for relative in unlisted:
            report.add_error(f"MANIFEST.sha256: unlisted file: {relative}")
        for relative in extra:
            report.add_error(f"MANIFEST.sha256: obsolete entry: {relative}")


def run_validation(*, include_manifest: bool = False) -> ValidationReport:
    report = ValidationReport()
    tables: dict[str, LoadedTable] = {}
    for name, spec in TABLES.items():
        tables[name] = _load_and_validate_table(
            name=name,
            path=spec["path"],
            schema_path=spec["schema"],
            unique_field=spec["id"],
            report=report,
        )

    if all(name in tables for name in TABLES):
        _validate_cross_table(tables, report)
        _validate_observations(tables, report)

    if include_manifest:
        verify_manifest(report)
    return report


def validate() -> list[str]:
    """Backwards-compatible helper used by the test suite."""
    return run_validation(include_manifest=False).errors


def _print_text(report: ValidationReport) -> None:
    if report.errors:
        print("Validation failed:")
        for error in report.errors:
            print(f"- ERROR: {error}")
    else:
        print("Validation passed.")
    for warning in report.warnings:
        print(f"- WARNING: {warning}")
    if report.row_counts:
        print("Validated rows:")
        for name, count in sorted(report.row_counts.items()):
            print(f"- {name}: {count}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate GFJD data contracts and repository metadata.")
    parser.add_argument("--manifest", action="store_true", help="also verify MANIFEST.sha256 strictly")
    parser.add_argument("--json", action="store_true", dest="as_json", help="emit a JSON report")
    args = parser.parse_args(argv)

    report = run_validation(include_manifest=args.manifest)
    if args.as_json:
        print(
            json.dumps(
                {
                    "ok": report.ok,
                    "errors": report.errors,
                    "warnings": report.warnings,
                    "row_counts": report.row_counts,
                },
                indent=2,
                sort_keys=True,
            )
        )
    else:
        _print_text(report)
    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(main())
