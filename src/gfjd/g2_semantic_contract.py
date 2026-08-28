"""Fail-closed validation and leakage checks for prospective G2 semantics."""

from __future__ import annotations

import unicodedata
from collections.abc import Iterable, Mapping
from typing import Any

from jsonschema import Draft202012Validator

REQUIRED_CODEBOOKS = frozenset(
    {
        "domain_code",
        "matter_type_code",
        "indicator_code",
        "series_code",
        "statistic_type",
        "denominator_code",
        "clock_code",
        "cohort_code",
        "counted_entity_code",
        "population_scope_code",
    }
)


def validate_prospective_semantic_bundle(
    contract: Mapping[str, Any], schema: Mapping[str, Any]
) -> list[str]:
    """Apply the frozen JSON Schema before cross-field invariant validation."""

    schema_errors = [
        f"{error.json_path}: {error.message}"
        for error in sorted(
            Draft202012Validator(dict(schema)).iter_errors(dict(contract)),
            key=lambda item: list(item.path),
        )
    ]
    if schema_errors:
        return schema_errors
    return validate_prospective_semantic_contract(contract)


def validate_prospective_semantic_contract(contract: Mapping[str, Any]) -> list[str]:
    """Validate invariants that complement the JSON Schema contract."""

    errors: list[str] = []
    codebooks = contract.get("codebooks")
    if not isinstance(codebooks, Mapping):
        return ["codebooks must be an object"]
    names = {str(name) for name in codebooks}
    if names != REQUIRED_CODEBOOKS:
        errors.append("codebooks must exactly match the required semantic fields")
    for name, raw_values in codebooks.items():
        if not isinstance(raw_values, list) or not all(
            isinstance(value, str) for value in raw_values
        ):
            errors.append(f"codebook must be an array of strings: {name}")
            continue
        values = raw_values
        if values != sorted(values):
            errors.append(f"codebook must use deterministic lexical order: {name}")
        if len(values) != len(set(values)):
            errors.append(f"codebook contains duplicates: {name}")
        if "unknown" not in values:
            errors.append(f"codebook lacks fail-closed unknown fallback: {name}")
    for name in {
        "domain_code",
        "matter_type_code",
        "indicator_code",
        "series_code",
        "statistic_type",
        "denominator_code",
        "clock_code",
        "cohort_code",
        "counted_entity_code",
        "population_scope_code",
    }:
        values = codebooks.get(name, [])
        if "source_defined" not in values:
            errors.append(f"codebook lacks source_defined fallback: {name}")

    comparison = contract.get("comparison_policy", {})
    expected_comparison = {
        "critical_concordance": 1.0,
        "overall_populated_concordance": 0.99,
        "exact": True,
        "fuzzy_matching": False,
        "critical_waiver": False,
        "failed_output_repair_or_reuse": False,
        "automatic_rerun": False,
    }
    if comparison != expected_comparison:
        errors.append("comparison policy weakens or changes the frozen exact thresholds")
    component_policy = contract.get("component_policy", {})
    if component_policy.get("mode") != "empty_only_until_component_provenance_schema":
        errors.append("components must remain empty until provenance is representable")
    leakage = contract.get("leakage_policy", {})
    if leakage.get("sample_specific_content_allowed") is not False:
        errors.append("sample-specific content must be prohibited")
    for authority in (
        "execution_authorized",
        "source_access_authorized",
        "publication_authorized",
        "release_authorized",
        "g2_passage",
    ):
        if contract.get(authority) is not False:
            errors.append(f"prospective preparation cannot set {authority}=true")
    return errors


def find_prohibited_semantic_leakage(text: str, prohibited_terms: Iterable[str]) -> list[str]:
    """Find case, punctuation and whitespace-insensitive prohibited terms."""

    normalized_text = _semantic_fold(text)
    matches: list[str] = []
    for term in prohibited_terms:
        normalized_term = _semantic_fold(term)
        if normalized_term and normalized_term in normalized_text:
            matches.append(term)
    return sorted(set(matches), key=str.casefold)


def _semantic_fold(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).casefold()
    return "".join(character for character in normalized if character.isalnum())
