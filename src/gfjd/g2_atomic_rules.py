"""Source-independent atomic field rules for future G2 extraction contracts."""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Mapping
from typing import Any

ATOMIC_LOCATOR_FIELDS = (
    "locator_pdf_page",
    "locator_printed_page",
    "locator_section_source",
    "locator_object_source",
)
SOURCE_TEXT_FIELDS = (
    "locator_section_source",
    "locator_object_source",
    "domain_label_source",
    "matter_label_source",
    "measure_label_source",
    "series_label_source",
    "denominator_definition_quote",
    "period_label_source",
    "clock_label_source",
    "cohort_definition_quote",
    "coverage_limitation_quote",
)
CONTROLLED_CODE_FIELDS = (
    "domain_code",
    "matter_type_code",
    "indicator_code",
    "series_code",
    "statistic_type",
    "unit_code",
    "denominator_code",
    "clock_code",
    "cohort_code",
    "counted_entity_code",
    "population_scope_code",
)

_WHITESPACE = re.compile(r"\s+")
_YEAR_OR_PERIOD_ONLY = re.compile(r"^(?:fy\s*)?\d{4}(?:\s*[/–-]\s*\d{2,4})?$", re.IGNORECASE)
_CODE = re.compile(r"^[a-z][a-z0-9_]*$")


def normalize_source_text(value: str) -> str:
    """Apply only the frozen source-text normalization: NFC and whitespace collapse."""

    if not isinstance(value, str):
        raise TypeError("source text must be a string")
    normalized = _WHITESPACE.sub(" ", unicodedata.normalize("NFC", value)).strip()
    if not normalized:
        raise ValueError("source text must not be empty")
    return normalized


def explicit_time_basis(label: str | None) -> str:
    """Classify only explicit clock wording; a year or period label is insufficient."""

    if label is None:
        return "unknown"
    normalized = normalize_source_text(label)
    if _YEAR_OR_PERIOD_ONLY.fullmatch(normalized):
        return "unknown"
    folded = normalized.casefold()
    if "calendar" in folded:
        return "calendar"
    if "working day" in folded or "business day" in folded:
        return "working"
    return "source_defined"


def validate_atomic_field_contract(row: Mapping[str, Any]) -> list[str]:
    """Check cross-field atomicity rules not expressible in the base JSON schema."""

    errors: list[str] = []
    legacy = {"provenance_locator", "measure_original", "unit", "cohort_basis", "population_scope"}
    for field in sorted(legacy & row.keys()):
        errors.append(f"legacy composite field is prohibited: {field}")

    for field in ATOMIC_LOCATOR_FIELDS:
        if field not in row:
            errors.append(f"atomic locator field is missing: {field}")

    for field in SOURCE_TEXT_FIELDS:
        value = row.get(field)
        if value is None:
            continue
        if not isinstance(value, str):
            errors.append(f"source-text field must be text or null: {field}")
            continue
        try:
            normalized = normalize_source_text(value)
        except (TypeError, ValueError) as exc:
            errors.append(f"invalid source-text field {field}: {exc}")
            continue
        if value != normalized:
            errors.append(f"source-text field is not NFC/whitespace normalized: {field}")

    for field in CONTROLLED_CODE_FIELDS:
        value = row.get(field)
        if value is not None and (not isinstance(value, str) or not _CODE.fullmatch(value)):
            errors.append(f"controlled-code field is invalid: {field}")

    period_label = row.get("period_label_source")
    if (
        isinstance(period_label, str)
        and _YEAR_OR_PERIOD_ONLY.fullmatch(normalize_source_text(period_label))
        and row.get("time_basis") != "unknown"
    ):
        errors.append("year or financial-period label alone requires time_basis=unknown")

    if row.get("period_start") is None and row.get("period_start_provenance") != "not_stated":
        errors.append("null period_start requires period_start_provenance=not_stated")
    if row.get("period_end") is None and row.get("period_end_provenance") != "not_stated":
        errors.append("null period_end requires period_end_provenance=not_stated")
    return errors
