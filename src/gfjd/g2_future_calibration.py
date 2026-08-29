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
COMPARATOR_CONTRACT_PATH = Path(
    "data/methods/g2/G2PROSPECTIVE-CALIBRATION-PREPARATION-20260829-01/comparator-contract.json"
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
    bound_paths = {artifact["path"] for artifact in bundle["bindings"]}
    if COMPARATOR_CONTRACT_PATH.as_posix() not in bound_paths:
        errors.append("prospective comparator contract is not bound")
    else:
        errors.extend(_validate_comparator_contract(root, bundle))
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


def _validate_comparator_contract(root: Path, bundle: Mapping[str, Any]) -> list[str]:
    contract = load_json(root / COMPARATOR_CONTRACT_PATH)
    row_schema_path = root / str(contract.get("row_schema_path", ""))
    if not row_schema_path.is_file():
        return ["comparator contract row schema is missing"]
    row_schema = load_json(row_schema_path)
    schema_fields = set(row_schema.get("properties", {}))
    critical = contract.get("critical_fields")
    ignored = contract.get("ignored_fields")
    if not isinstance(critical, list) or not critical:
        return ["comparator contract requires nonempty critical_fields"]
    if not isinstance(ignored, list):
        return ["comparator contract requires ignored_fields"]
    errors: list[str] = []
    unknown = sorted((set(critical) | set(ignored)) - schema_fields)
    if unknown:
        errors.append("comparator contract contains unknown row fields: " + ", ".join(unknown))
    overlap = sorted(set(critical) & set(ignored))
    if overlap:
        errors.append("comparator critical and ignored fields overlap: " + ", ".join(overlap))
    if contract.get("implementation") != "gfjd.g2_concordance.compare_g2_extractions":
        errors.append("unexpected comparator implementation")
    comparison = bundle["comparison_policy"]
    if contract.get("critical_threshold") != comparison["critical_concordance"]:
        errors.append("comparator critical threshold differs from bundle")
    if contract.get("overall_populated_threshold") != comparison["overall_populated_concordance"]:
        errors.append("comparator overall threshold differs from bundle")
    for control in (
        "exact_only",
        "fuzzy_matching",
        "critical_waiver",
        "repair_or_reuse",
        "automatic_rerun",
    ):
        bundle_key = "exact" if control == "exact_only" else control
        if contract.get(control) != comparison[bundle_key]:
            errors.append(f"comparator {control} differs from bundle")
    return errors


def _all_keys(value: Any) -> set[str]:
    if isinstance(value, Mapping):
        return {str(key) for key in value} | {
            key for child in value.values() for key in _all_keys(child)
        }
    if isinstance(value, list):
        return {key for child in value for key in _all_keys(child)}
    return set()
