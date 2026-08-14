"""Deterministic concordance comparison for blinded G2 extraction outputs."""

from __future__ import annotations

import json
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from .io import canonical_json_bytes, sha256_bytes, sha256_file, write_json


class G2ConcordanceError(ValueError):
    """Raised when extraction inputs or comparator configuration are invalid."""


DEFAULT_CRITICAL_FIELDS = (
    "candidate_id",
    "source_id",
    "source_edition_id",
    "provenance_locator",
    "measure_original",
    "matter_type_original",
    "statistic_type",
    "unit",
    "value",
    "component_values",
    "denominator_value",
    "denominator_definition",
    "period_start",
    "period_end",
    "time_basis",
    "cohort_basis",
    "population_scope",
)

DEFAULT_IGNORED_FIELDS = ("extracted_row_id", "source_record_key")


@dataclass(frozen=True, slots=True)
class G2ConcordanceResult:
    receipt_path: Path
    difference_path: Path
    threshold_passed: bool
    critical_concordance: float
    overall_concordance: float


def compare_g2_extractions(
    root: Path,
    *,
    primary_path: Path,
    secondary_path: Path,
    output_dir: Path,
    comparison_id: str,
    packet_id: str,
    packet_sha256: str,
    primary_receipt: dict[str, str],
    secondary_receipt: dict[str, str],
    threshold_policy: dict[str, str],
    source_commit: str,
    generated_at: str,
    critical_fields: Sequence[str] = DEFAULT_CRITICAL_FIELDS,
    overall_threshold: float = 0.99,
    ignored_fields: Sequence[str] = DEFAULT_IGNORED_FIELDS,
    limitations: Sequence[str] = (),
) -> G2ConcordanceResult:
    """Validate and compare two blinded extraction arrays.

    Rows are matched only by ``source_record_key``. Critical fields require exact
    concordance. Overall concordance is calculated across fields populated in at
    least one extraction. Unmatched rows and critical differences always fail the
    result; callers cannot configure a lower critical threshold.
    """

    resolved_root = root.expanduser().resolve()
    primary = _confined(resolved_root, primary_path)
    secondary = _confined(resolved_root, secondary_path)
    destination = _confined(resolved_root, output_dir, require_exists=False)
    schema_path = resolved_root / "schemas/g2_extraction_row.schema.json"
    receipt_schema_path = resolved_root / "schemas/g2_concordance.schema.json"
    if not 0.99 <= overall_threshold <= 1:
        raise G2ConcordanceError("overall_threshold must be between 0.99 and 1")
    if not schema_path.is_file() or not receipt_schema_path.is_file():
        raise G2ConcordanceError("required G2 concordance schemas are missing")

    row_schema = _load_object(schema_path)
    primary_rows = _load_array(primary)
    secondary_rows = _load_array(secondary)
    _validate_rows(primary_rows, row_schema, label="primary")
    _validate_rows(secondary_rows, row_schema, label="secondary")

    schema_fields = set(row_schema.get("properties", {}))
    critical = _normalised_fields(critical_fields, schema_fields, label="critical")
    if not critical:
        raise G2ConcordanceError("at least one critical field is required")
    ignored = _normalised_fields(ignored_fields, schema_fields, label="ignored")
    if critical & ignored:
        overlap = ", ".join(sorted(critical & ignored))
        raise G2ConcordanceError(f"critical fields cannot be ignored: {overlap}")
    comparable_fields = sorted(schema_fields - ignored)

    primary_by_key = _index_rows(primary_rows, label="primary")
    secondary_by_key = _index_rows(secondary_rows, label="secondary")
    primary_keys = set(primary_by_key)
    secondary_keys = set(secondary_by_key)
    matched_keys = sorted(primary_keys & secondary_keys)
    primary_only = sorted(primary_keys - secondary_keys)
    secondary_only = sorted(secondary_keys - primary_keys)

    differences: list[dict[str, Any]] = []
    for key in primary_only:
        differences.append(
            {
                "source_record_key": key,
                "difference_type": "primary_only_row",
                "field": None,
                "critical": True,
                "primary_value": "present",
                "secondary_value": None,
            }
        )
    for key in secondary_only:
        differences.append(
            {
                "source_record_key": key,
                "difference_type": "secondary_only_row",
                "field": None,
                "critical": True,
                "primary_value": None,
                "secondary_value": "present",
            }
        )

    field_counts: dict[str, dict[str, int | bool]] = {}
    critical_comparisons = 0
    critical_matches = 0
    overall_comparisons = 0
    overall_matches = 0
    critical_difference_count = len(primary_only) + len(secondary_only)

    for key in matched_keys:
        primary_row = primary_by_key[key]
        secondary_row = secondary_by_key[key]
        for field in comparable_fields:
            for metric_field, left, right in _field_values(
                field, primary_row.get(field), secondary_row.get(field)
            ):
                is_critical = field in critical
                counts = field_counts.setdefault(
                    metric_field,
                    {"comparisons": 0, "matches": 0, "critical": is_critical},
                )
                if is_critical:
                    critical_comparisons += 1
                    if _equal(left, right):
                        critical_matches += 1
                    else:
                        critical_difference_count += 1
                if not _populated(left) and not _populated(right):
                    continue
                counts["comparisons"] = int(counts["comparisons"]) + 1
                overall_comparisons += 1
                if _equal(left, right):
                    counts["matches"] = int(counts["matches"]) + 1
                    overall_matches += 1
                else:
                    differences.append(
                        {
                            "source_record_key": key,
                            "difference_type": "field_mismatch",
                            "field": metric_field,
                            "critical": is_critical,
                            "primary_value": left,
                            "secondary_value": right,
                        }
                    )

    critical_concordance = _ratio(critical_matches, critical_comparisons)
    overall_concordance = _ratio(overall_matches, overall_comparisons)
    threshold_passed = (
        not primary_only
        and not secondary_only
        and bool(matched_keys)
        and critical_difference_count == 0
        and critical_concordance == 1.0
        and overall_concordance >= overall_threshold
    )

    field_metrics = {
        field: {
            "comparisons": int(counts["comparisons"]),
            "matches": int(counts["matches"]),
            "concordance": _ratio(int(counts["matches"]), int(counts["comparisons"])),
            "critical": bool(counts["critical"]),
        }
        for field, counts in sorted(field_counts.items())
        if counts["comparisons"] or counts["critical"]
    }
    difference_payload = {
        "schema_version": "1.0",
        "comparison_id": comparison_id,
        "packet_id": packet_id,
        "primary_output_sha256": sha256_file(primary),
        "secondary_output_sha256": sha256_file(secondary),
        "difference_count": len(differences),
        "differences": differences,
    }

    destination.mkdir(parents=True, exist_ok=True)
    difference_path = destination / "differences.json"
    write_json(difference_path, difference_payload)
    difference_artifact = {
        "path": difference_path.relative_to(resolved_root).as_posix(),
        "sha256": sha256_file(difference_path),
    }
    receipt = {
        "schema_version": "1.0",
        "comparison_id": comparison_id,
        "packet_id": packet_id,
        "packet_sha256": packet_sha256,
        "primary_receipt": primary_receipt,
        "secondary_receipt": secondary_receipt,
        "primary_output": _artifact(resolved_root, primary),
        "secondary_output": _artifact(resolved_root, secondary),
        "comparator": {
            "name": "gfjd-g2-concordance",
            "version": "1.0",
            "source_commit": source_commit,
        },
        "threshold_policy": threshold_policy,
        "critical_fields": sorted(critical),
        "critical_threshold": 1.0,
        "overall_threshold": overall_threshold,
        "matched_rows": len(matched_keys),
        "primary_only_rows": len(primary_only),
        "secondary_only_rows": len(secondary_only),
        "critical_field_comparisons": critical_comparisons,
        "critical_field_matches": critical_matches,
        "overall_field_comparisons": overall_comparisons,
        "overall_field_matches": overall_matches,
        "critical_concordance": critical_concordance,
        "overall_concordance": overall_concordance,
        "field_metrics": field_metrics,
        "difference_artifact": difference_artifact,
        "threshold_passed": threshold_passed,
        "status": "pass" if threshold_passed else "fail",
        "generated_at": generated_at,
        "limitations": list(limitations),
    }
    _validate_object(receipt, _load_object(receipt_schema_path), label="receipt")
    receipt_path = destination / "concordance.json"
    write_json(receipt_path, receipt)
    return G2ConcordanceResult(
        receipt_path=receipt_path,
        difference_path=difference_path,
        threshold_passed=threshold_passed,
        critical_concordance=critical_concordance,
        overall_concordance=overall_concordance,
    )


def _load_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise G2ConcordanceError(f"cannot read JSON object {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise G2ConcordanceError(f"JSON root must be an object: {path}")
    return payload


def _load_array(path: Path) -> list[dict[str, Any]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise G2ConcordanceError(f"cannot read extraction array {path}: {exc}") from exc
    if not isinstance(payload, list) or not all(isinstance(item, dict) for item in payload):
        raise G2ConcordanceError(f"extraction root must be an array of objects: {path}")
    return payload


def _validate_rows(rows: Sequence[dict[str, Any]], schema: dict[str, Any], *, label: str) -> None:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors: list[str] = []
    for index, row in enumerate(rows):
        errors.extend(
            f"{label}[{index}] {error.json_path}: {error.message}"
            for error in sorted(validator.iter_errors(row), key=lambda item: list(item.path))
        )
    if errors:
        raise G2ConcordanceError("; ".join(errors))


def _validate_object(payload: dict[str, Any], schema: dict[str, Any], *, label: str) -> None:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(payload), key=lambda item: list(item.path))
    if errors:
        raise G2ConcordanceError(
            "; ".join(f"{label} {error.json_path}: {error.message}" for error in errors)
        )


def _index_rows(rows: Iterable[dict[str, Any]], *, label: str) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for row in rows:
        key = str(row["source_record_key"])
        if key in indexed:
            raise G2ConcordanceError(f"duplicate source_record_key in {label}: {key}")
        indexed[key] = row
    return indexed


def _normalised_fields(fields: Sequence[str], schema_fields: set[str], *, label: str) -> set[str]:
    normalised = {str(field) for field in fields}
    unknown = sorted(normalised - schema_fields)
    if unknown:
        raise G2ConcordanceError(f"unknown {label} fields: {', '.join(unknown)}")
    return normalised


def _populated(value: Any) -> bool:
    return value is not None and value != "" and value != [] and value != {}


def _field_values(field: str, left: Any, right: Any) -> list[tuple[str, Any, Any]]:
    """Expand structured component values into stable field-level comparisons."""

    if field != "component_values":
        return [(field, left, right)]
    left_components = left if isinstance(left, dict) else {}
    right_components = right if isinstance(right, dict) else {}
    return [
        (
            f"component_values.{component}",
            left_components.get(component),
            right_components.get(component),
        )
        for component in sorted(set(left_components) | set(right_components))
    ]


def _equal(left: Any, right: Any) -> bool:
    return canonical_json_bytes(left) == canonical_json_bytes(right)


def _ratio(matches: int, comparisons: int) -> float:
    return 1.0 if comparisons == 0 else matches / comparisons


def _artifact(root: Path, path: Path) -> dict[str, str]:
    return {"path": path.relative_to(root).as_posix(), "sha256": sha256_file(path)}


def _confined(root: Path, path: Path, *, require_exists: bool = True) -> Path:
    candidate = path if path.is_absolute() else root / path
    resolved = candidate.expanduser().resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise G2ConcordanceError(f"path escapes repository root: {path}") from exc
    if require_exists and not resolved.is_file():
        raise G2ConcordanceError(f"input file does not exist: {path}")
    return resolved


def difference_payload_sha256(payload: dict[str, Any]) -> str:
    """Return the canonical digest used for deterministic difference payload tests."""

    return sha256_bytes(canonical_json_bytes(payload))
