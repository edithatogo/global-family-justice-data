"""Controlled structured-source mapping and silver-to-gold promotion."""

from __future__ import annotations

import math
import re
from collections import Counter
from collections.abc import Mapping
from datetime import datetime
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from .io import read_csv, read_json, write_csv, write_json
from .project import Project
from .schema_validation import coerce_row


class PipelineError(RuntimeError):
    """Raised when mapping or promotion cannot produce a valid controlled output."""


class _StrictFormatDict(dict[str, Any]):
    def __missing__(self, key: str) -> Any:
        raise KeyError(key)


def map_structured_csv(
    project: Project,
    mapping_path: Path,
    input_path: Path,
    output_path: Path,
) -> dict[str, Any]:
    """Apply a declarative mapping to a source CSV and validate every observation."""

    mapping = read_json(mapping_path)
    mapping_schema = read_json(project.root / "schemas" / "mapping.schema.json")
    mapping_errors = list(
        Draft202012Validator(mapping_schema, format_checker=FormatChecker()).iter_errors(mapping)
    )
    if mapping_errors:
        messages = "; ".join(error.message for error in mapping_errors)
        raise PipelineError(f"Mapping specification is invalid: {messages}")

    delimiter = str(mapping.get("input", {}).get("delimiter", ","))
    encoding = str(mapping.get("input", {}).get("encoding", "utf-8-sig"))
    headers, input_rows = _read_csv_with_options(input_path, delimiter=delimiter, encoding=encoding)
    if not input_rows:
        raise PipelineError(f"Input contains no rows: {input_path}")

    observation_schema = read_json(project.root / "schemas" / "observation.schema.json")
    output_fields = list(observation_schema["properties"])
    field_rules: dict[str, Any] = mapping["fields"]
    unknown_fields = sorted(set(field_rules) - set(output_fields))
    if unknown_fields:
        raise PipelineError(f"Mapping has unknown output field(s): {', '.join(unknown_fields)}")

    validator = Draft202012Validator(observation_schema, format_checker=FormatChecker())
    mapped_rows: list[dict[str, Any]] = []
    failures: list[str] = []
    for row_number, source_row in enumerate(input_rows, start=2):
        context: dict[str, Any] = {
            **source_row,
            "row_number": row_number,
            "source_id": mapping["source_id"],
            "source_edition_id": mapping["source_edition_id"],
            "mapping_id": mapping["mapping_id"],
        }
        output: dict[str, Any] = {}
        for field in output_fields:
            rule = field_rules.get(field)
            if rule is None:
                output[field] = (
                    None if _allows_null(observation_schema["properties"][field]) else ""
                )
                continue
            try:
                output[field] = _evaluate_rule(rule, context)
            except Exception as exc:
                failures.append(f"input row {row_number}, field {field}: {exc}")
                output[field] = ""
        errors = sorted(validator.iter_errors(output), key=lambda error: list(error.path))
        for error in errors:
            field = ".".join(str(part) for part in error.path)
            failures.append(f"input row {row_number}, {field or '<row>'}: {error.message}")
        mapped_rows.append(output)

    if failures:
        preview = "\n".join(f"- {message}" for message in failures[:50])
        extra = "" if len(failures) <= 50 else f"\n... {len(failures) - 50} additional failure(s)"
        raise PipelineError(f"Mapped output failed validation:\n{preview}{extra}")

    mapped_rows.sort(key=lambda row: str(row["observation_id"]))
    write_csv(output_path, output_fields, mapped_rows)
    return {
        "mapping_id": mapping["mapping_id"],
        "input_path": str(input_path),
        "output_path": str(output_path),
        "input_rows": len(input_rows),
        "output_rows": len(mapped_rows),
        "input_headers": headers,
    }


def promote_observations(
    project: Project,
    input_path: Path,
    gold_path: Path,
    quarantine_path: Path,
    report_path: Path,
) -> dict[str, Any]:
    """Promote eligible silver observations and quarantine every other record with reasons."""

    headers, raw_rows = read_csv(input_path)
    observation_schema = read_json(project.root / "schemas" / "observation.schema.json")
    expected_headers = list(observation_schema["properties"])
    if headers != expected_headers:
        missing = sorted(set(expected_headers) - set(headers))
        extra = sorted(set(headers) - set(expected_headers))
        raise PipelineError(
            f"Input contract does not match observation schema; missing={missing}, extra={extra}"
        )

    validator = Draft202012Validator(observation_schema, format_checker=FormatChecker())
    gold_rows: list[dict[str, Any]] = []
    quarantine_rows: list[dict[str, Any]] = []
    reason_counts: Counter[str] = Counter()
    seen_ids: set[str] = set()

    for _row_number, raw in enumerate(raw_rows, start=2):
        typed = coerce_row(raw, observation_schema)
        reasons: list[str] = []
        schema_errors = sorted(validator.iter_errors(typed), key=lambda error: list(error.path))
        reasons.extend(f"schema:{error.message}" for error in schema_errors)
        observation_id = str(typed.get("observation_id") or "")
        if observation_id in seen_ids:
            reasons.append("duplicate_observation_id")
        seen_ids.add(observation_id)
        reasons.extend(_promotion_reasons(typed))

        if reasons:
            for reason in reasons:
                reason_counts[reason.split(":", 1)[0]] += 1
            quarantine_rows.append({**raw, "quarantine_reasons": ";".join(reasons)})
        else:
            gold_rows.append(typed)

    gold_rows.sort(key=lambda row: str(row["observation_id"]))
    quarantine_rows.sort(key=lambda row: str(row.get("observation_id", "")))
    write_csv(gold_path, expected_headers, gold_rows)
    write_csv(quarantine_path, [*expected_headers, "quarantine_reasons"], quarantine_rows)
    report = {
        "schema_version": "1.0",
        "input_path": str(input_path),
        "gold_path": str(gold_path),
        "quarantine_path": str(quarantine_path),
        "input_rows": len(raw_rows),
        "promoted_rows": len(gold_rows),
        "quarantined_rows": len(quarantine_rows),
        "reason_counts": dict(sorted(reason_counts.items())),
    }
    write_json(report_path, report)
    return report


def build_lineage_index(project: Project, observation_path: Path, output_path: Path) -> int:
    headers, rows = read_csv(observation_path)
    required = {
        "observation_id",
        "source_id",
        "source_edition_id",
        "provenance_locator",
        "extraction_id",
        "transformation_rule_id",
        "review_id",
    }
    if not required.issubset(headers):
        raise PipelineError(
            f"Observation file lacks lineage fields: {sorted(required - set(headers))}"
        )
    lineage_headers = [
        "observation_id",
        "source_id",
        "source_edition_id",
        "extraction_id",
        "transformation_rule_id",
        "review_id",
        "provenance_locator",
    ]
    lineage = [{key: row.get(key, "") for key in lineage_headers} for row in rows]
    lineage.sort(key=lambda row: row["observation_id"])
    write_csv(output_path, lineage_headers, lineage)
    return len(lineage)


def _read_csv_with_options(
    path: Path,
    *,
    delimiter: str,
    encoding: str,
) -> tuple[list[str], list[dict[str, str]]]:
    import csv

    if len(delimiter) != 1:
        raise PipelineError("CSV delimiter must be exactly one character")
    with path.open("r", encoding=encoding, newline="") as handle:
        reader = csv.DictReader(handle, delimiter=delimiter)
        if reader.fieldnames is None:
            return [], []
        return list(reader.fieldnames), [dict(row) for row in reader]


def _evaluate_rule(rule: Mapping[str, Any], context: Mapping[str, Any]) -> Any:
    sources = [key for key in ("constant", "column", "template") if key in rule]
    if len(sources) > 1:
        raise PipelineError(f"Rule has multiple value sources: {sources}")
    if "constant" in rule:
        value: Any = rule["constant"]
    elif "column" in rule:
        column = str(rule["column"])
        if column not in context:
            raise PipelineError(f"input column {column!r} is missing")
        value = context[column]
    elif "template" in rule:
        try:
            value = str(rule["template"]).format_map(_StrictFormatDict(context))
        except KeyError as exc:
            raise PipelineError(f"template variable {exc.args[0]!r} is missing") from exc
    else:
        value = rule.get("default", "")

    if (value is None or value == "") and "default" in rule:
        value = rule["default"]
    for transform in rule.get("transforms", []):
        value = _apply_transform(value, transform)
    if bool(rule.get("required", False)) and (value is None or str(value).strip() == ""):
        raise PipelineError("required mapped value is blank")
    return value


def _apply_transform(value: Any, transform: Any) -> Any:
    if isinstance(transform, str):
        name = transform
        options: dict[str, Any] = {}
    elif isinstance(transform, dict):
        name = str(transform.get("name", ""))
        options = dict(transform)
    else:
        raise PipelineError(f"Invalid transform {transform!r}")

    if name == "strip":
        return str(value).strip()
    if name == "normalise_whitespace":
        return re.sub(r"\s+", " ", str(value)).strip()
    if name == "lower":
        return str(value).lower()
    if name == "upper":
        return str(value).upper()
    if name == "parse_number":
        return _parse_number(value)
    if name == "parse_integer":
        number = _parse_number(value)
        if not float(number).is_integer():
            raise PipelineError(f"{value!r} is not an integer")
        return int(number)
    if name == "parse_boolean":
        normalised = str(value).strip().lower()
        if normalised in {"true", "yes", "1", "y"}:
            return True
        if normalised in {"false", "no", "0", "n"}:
            return False
        raise PipelineError(f"Cannot parse boolean from {value!r}")
    if name == "parse_date":
        formats = options.get("formats", ["%Y-%m-%d"])
        for format_string in formats:
            try:
                return datetime.strptime(str(value).strip(), str(format_string)).date().isoformat()
            except ValueError:
                continue
        raise PipelineError(f"Cannot parse date {value!r} with formats {formats}")
    if name == "multiply":
        return _parse_number(value) * float(options["factor"])
    if name == "divide":
        divisor = float(options["divisor"])
        if divisor == 0:
            raise PipelineError("divide transform has zero divisor")
        return _parse_number(value) / divisor
    if name == "replace":
        return str(value).replace(str(options.get("old", "")), str(options.get("new", "")))
    if name == "null_if":
        candidates = {str(item) for item in options.get("values", [])}
        return None if str(value).strip() in candidates else value
    raise PipelineError(f"Unsupported transform {name!r}")


def _parse_number(value: Any) -> float:
    if isinstance(value, bool):
        raise PipelineError("Boolean is not a numeric value")
    if isinstance(value, (int, float)):
        number = float(value)
    else:
        text = str(value).strip().replace(",", "")
        if text.startswith("(") and text.endswith(")"):
            text = "-" + text[1:-1]
        text = re.sub(r"^[^0-9+-.]+", "", text)
        text = re.sub(r"[^0-9eE+-.]+$", "", text)
        try:
            number = float(text)
        except ValueError as exc:
            raise PipelineError(f"Cannot parse number from {value!r}") from exc
    if not math.isfinite(number):
        raise PipelineError(f"Non-finite numeric value {value!r}")
    return number


def _promotion_reasons(row: Mapping[str, Any]) -> list[str]:
    reasons: list[str] = []
    required_lineage = [
        "source_edition_id",
        "extraction_id",
        "review_id",
        "transformation_rule_id",
        "provenance_locator",
    ]
    for field in required_lineage:
        if row.get(field) is None or str(row.get(field)).strip() == "":
            reasons.append(f"lineage_missing:{field}")
    if row.get("record_status") != "accepted":
        reasons.append("record_not_accepted")
    if row.get("review_status") != "accepted":
        reasons.append("review_not_accepted")
    if row.get("second_reviewed") is not True:
        reasons.append("second_review_missing")
    if not str(row.get("second_reviewer") or "").strip():
        reasons.append("second_reviewer_missing")
    if row.get("quality_grade") not in {"A", "B", "C"}:
        reasons.append("quality_below_gold")
    if row.get("comparability_tier") not in {1, 2}:
        reasons.append("comparability_below_gold")
    if row.get("release_eligible") is not True:
        reasons.append("not_release_eligible")
    if row.get("suppression_status") == "suppressed":
        reasons.append("suppressed")
    return reasons


def _allows_null(fragment: Mapping[str, Any]) -> bool:
    schema_type = fragment.get("type")
    return isinstance(schema_type, list) and "null" in schema_type
