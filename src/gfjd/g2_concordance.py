"""Deterministic concordance comparison for blinded G2 extraction outputs."""

from __future__ import annotations

import json
import math
from collections.abc import Iterable, Mapping, Sequence
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
    expected_source_keys: Sequence[str] | None = None,
    required_component_values: Mapping[str, Sequence[str]] | None = None,
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
    expected_keys = _normalised_source_keys(expected_source_keys)
    component_requirements = _normalised_component_requirements(
        required_component_values,
        expected_keys if expected_keys is not None else primary_keys | secondary_keys,
    )
    matched_keys = sorted(primary_keys & secondary_keys)
    primary_only = sorted(primary_keys - secondary_keys)
    secondary_only = sorted(secondary_keys - primary_keys)

    differences: list[dict[str, Any]] = []
    differences.extend(_expected_scope_differences(primary_keys, secondary_keys, expected_keys))
    differences.extend(
        _required_component_differences(primary_by_key, secondary_by_key, component_requirements)
    )
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
    critical_difference_count = len(differences)

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
    if expected_keys is not None:
        receipt["expected_source_keys"] = sorted(expected_keys)
    if required_component_values is not None:
        receipt["required_component_values"] = {
            key: sorted(values) for key, values in sorted(component_requirements.items())
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


def _normalised_source_keys(keys: Sequence[str] | None) -> set[str] | None:
    if keys is None:
        return None
    normalised = [str(key) for key in keys]
    if len(set(normalised)) != len(normalised):
        raise G2ConcordanceError("expected_source_keys contains duplicates")
    invalid = sorted(key for key in normalised if not _is_source_key(key))
    if invalid:
        raise G2ConcordanceError(f"invalid expected_source_keys: {', '.join(invalid)}")
    return set(normalised)


def _normalised_component_requirements(
    requirements: Mapping[str, Sequence[str]] | None,
    scope_keys: set[str],
) -> dict[str, set[str]]:
    if requirements is None:
        return {}
    normalised: dict[str, set[str]] = {}
    for raw_key, raw_components in requirements.items():
        key = str(raw_key)
        if not _is_source_key(key):
            raise G2ConcordanceError(f"invalid required component source key: {key}")
        components = [str(component) for component in raw_components]
        if len(set(components)) != len(components):
            raise G2ConcordanceError(f"required components for {key} contain duplicates")
        invalid = sorted(
            component
            for component in components
            if not component
            or not all(char.islower() or char.isdigit() or char == "_" for char in component)
        )
        if invalid:
            raise G2ConcordanceError(f"invalid required components for {key}: {', '.join(invalid)}")
        normalised[key] = set(components)
    missing_requirements = sorted(scope_keys - set(normalised))
    outside_scope = sorted(set(normalised) - scope_keys)
    if missing_requirements or outside_scope:
        details: list[str] = []
        if missing_requirements:
            details.append("missing source keys: " + ", ".join(missing_requirements))
        if outside_scope:
            details.append("outside scope: " + ", ".join(outside_scope))
        raise G2ConcordanceError(
            "required_component_values must exactly cover the comparison scope ("
            + "; ".join(details)
            + ")"
        )
    return normalised


def _is_source_key(key: str) -> bool:
    return len(key) == 64 and all(char in "0123456789abcdef" for char in key)


def _expected_scope_differences(
    primary_keys: set[str], secondary_keys: set[str], expected_keys: set[str] | None
) -> list[dict[str, Any]]:
    if expected_keys is None:
        return []
    differences: list[dict[str, Any]] = []
    for key in sorted(expected_keys - (primary_keys | secondary_keys)):
        differences.append(
            {
                "source_record_key": key,
                "difference_type": "missing_expected_row_both",
                "field": "source_record_key",
                "critical": True,
                "primary_value": None,
                "secondary_value": None,
            }
        )
    for key in sorted((primary_keys & secondary_keys) - expected_keys):
        differences.append(
            {
                "source_record_key": key,
                "difference_type": "unexpected_row_both",
                "field": "source_record_key",
                "critical": True,
                "primary_value": "present",
                "secondary_value": "present",
            }
        )
    return differences


def _required_component_differences(
    primary_by_key: Mapping[str, Mapping[str, Any]],
    secondary_by_key: Mapping[str, Mapping[str, Any]],
    requirements: Mapping[str, set[str]],
) -> list[dict[str, Any]]:
    differences: list[dict[str, Any]] = []
    for source_key, required in sorted(requirements.items()):
        for extraction, rows in (
            ("primary", primary_by_key),
            ("secondary", secondary_by_key),
        ):
            row = rows.get(source_key)
            if row is None:
                differences.append(
                    {
                        "source_record_key": source_key,
                        "difference_type": f"{extraction}_missing_required_component_row",
                        "field": "component_values",
                        "critical": True,
                        "primary_value": None if extraction == "primary" else "not_checked",
                        "secondary_value": None if extraction == "secondary" else "not_checked",
                    }
                )
                continue
            components = row.get("component_values")
            component_map = components if isinstance(components, dict) else {}
            actual = set(component_map)
            for component in sorted(required - actual):
                differences.append(
                    _component_constraint_difference(
                        source_key, extraction, component, "missing", None
                    )
                )
            for component in sorted(actual - required):
                differences.append(
                    _component_constraint_difference(
                        source_key,
                        extraction,
                        component,
                        "unexpected",
                        component_map[component],
                    )
                )
            for component in sorted(required & actual):
                value = component_map[component]
                if not _populated_numeric(value):
                    differences.append(
                        _component_constraint_difference(
                            source_key, extraction, component, "not_populated_numeric", value
                        )
                    )
    return differences


def _component_constraint_difference(
    source_key: str,
    extraction: str,
    component: str,
    condition: str,
    value: Any,
) -> dict[str, Any]:
    return {
        "source_record_key": source_key,
        "difference_type": f"{extraction}_required_component_{condition}",
        "field": f"component_values.{component}",
        "critical": True,
        "primary_value": value if extraction == "primary" else "not_checked",
        "secondary_value": value if extraction == "secondary" else "not_checked",
    }


def _populated_numeric(value: Any) -> bool:
    return not isinstance(value, bool) and isinstance(value, (int, float)) and math.isfinite(value)


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
