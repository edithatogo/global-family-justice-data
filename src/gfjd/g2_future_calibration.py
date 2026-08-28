"""Validation for a non-executable prospective G2 calibration bundle."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

FORBIDDEN_PREPARATION_KEYS = frozenset(
    {"candidate_id", "candidate_url", "jurisdiction", "source_edition_id", "source_url"}
)


def validate_preparation_bundle(
    root: Path,
    bundle: Mapping[str, Any],
    schema: Mapping[str, Any],
) -> list[str]:
    """Validate structure, non-execution boundaries and artifact digests."""

    errors = [
        f"{error.json_path}: {error.message}"
        for error in sorted(
            Draft202012Validator(dict(schema), format_checker=FormatChecker()).iter_errors(
                dict(bundle)
            ),
            key=lambda item: list(item.path),
        )
    ]
    if errors:
        return errors
    leaked_keys = sorted(FORBIDDEN_PREPARATION_KEYS.intersection(_all_keys(bundle)))
    if leaked_keys:
        errors.append(
            "preparation bundle contains candidate-specific keys: " + ", ".join(leaked_keys)
        )
    for artifact in bundle["bindings"]:
        path = root / artifact["path"]
        resolved = path.resolve(strict=False)
        try:
            resolved.relative_to(root.resolve())
        except ValueError:
            errors.append(f"bound artifact escapes repository: {artifact['path']}")
            continue
        if not resolved.is_file():
            errors.append(f"bound artifact is missing: {artifact['path']}")
            continue
        actual = hashlib.sha256(resolved.read_bytes()).hexdigest()
        if actual != artifact["sha256"]:
            errors.append(f"bound artifact digest mismatch: {artifact['path']}")
    return errors


def validate_row(row: Mapping[str, Any], schema: Mapping[str, Any]) -> list[str]:
    """Validate a prospective row against its exact schema."""

    errors = [
        f"{error.json_path}: {error.message}"
        for error in sorted(
            Draft202012Validator(dict(schema), format_checker=FormatChecker()).iter_errors(
                dict(row)
            ),
            key=lambda item: list(item.path),
        )
    ]
    if errors:
        return errors
    ambiguities = set(row["ambiguity_codes"])
    unknown_rules = (
        ("domain_code", "domain_label_source", "ontology_conflict"),
        ("matter_type_code", "matter_label_source", "ontology_conflict"),
        ("indicator_code", "measure_label_source", "ontology_conflict"),
        ("series_code", "series_label_source", "source_definition_conflict"),
        ("statistic_type", "statistic_label_source", "ontology_conflict"),
        ("unit_code", "unit_label_source", "ontology_conflict"),
        ("denominator_code", "denominator_definition_quote", "denominator_conflict"),
        ("clock_code", "clock_label_source", "clock_conflict"),
        ("cohort_code", "cohort_definition_quote", "cohort_conflict"),
        ("counted_entity_code", "counted_entity_label_source", "population_conflict"),
        ("population_scope_code", "population_scope_label_source", "population_conflict"),
    )
    for code_field, text_field, conflict_code in unknown_rules:
        if (
            row[code_field] == "unknown"
            and row[text_field] is not None
            and conflict_code not in ambiguities
        ):
            errors.append(f"{code_field}=unknown with source text requires {conflict_code}")
    if row["series_code"] is None and row["series_label_source"] is not None:
        errors.append("series_code=null requires series_label_source=null")
    if not ambiguities and row["ambiguity_evidence_quote"] is not None:
        errors.append("ambiguity evidence requires at least one ambiguity code")
    return errors


def load_json(path: Path) -> dict[str, Any]:
    """Load a JSON object without accepting non-object roots."""

    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _all_keys(value: Any) -> set[str]:
    if isinstance(value, Mapping):
        return {str(key) for key in value} | {
            key for child in value.values() for key in _all_keys(child)
        }
    if isinstance(value, list):
        return {key for child in value for key in _all_keys(child)}
    return set()
