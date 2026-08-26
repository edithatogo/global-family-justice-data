from __future__ import annotations

import pytest

from gfjd.g2_atomic_rules import (
    explicit_time_basis,
    normalize_source_text,
    validate_atomic_field_contract,
)


def _row() -> dict[str, object]:
    return {
        "locator_pdf_page": 7,
        "locator_printed_page": 3,
        "locator_section_source": "Section Alpha",
        "locator_object_source": "Table One",
        "domain_label_source": "Example domain",
        "domain_code": "example_domain",
        "matter_label_source": "Example matters",
        "matter_type_code": "example_matter",
        "measure_label_source": "Example count",
        "indicator_code": "example_count",
        "series_label_source": None,
        "series_code": None,
        "statistic_type": "count",
        "unit_code": "count",
        "denominator_definition_quote": None,
        "denominator_code": "not_applicable",
        "period_label_source": "2025",
        "period_start": None,
        "period_end": None,
        "period_start_provenance": "not_stated",
        "period_end_provenance": "not_stated",
        "time_basis": "unknown",
        "clock_label_source": None,
        "clock_code": "unknown",
        "cohort_definition_quote": "All example matters",
        "cohort_code": "source_defined",
        "counted_entity_code": "matters",
        "population_scope_code": "source_defined",
        "coverage_limitation_quote": None,
    }


def test_source_text_normalization_is_narrow_and_deterministic() -> None:
    assert normalize_source_text("  Café\n  matters  ") == "Café matters"
    assert normalize_source_text("Cafe\u0301") == "Café"
    with pytest.raises(ValueError, match="must not be empty"):
        normalize_source_text(" \n ")


@pytest.mark.parametrize(
    ("label", "expected"),
    [
        (None, "unknown"),
        ("2025", "unknown"),
        ("2024/2025", "unknown"),
        ("FY 2024-25", "unknown"),
        ("Calendar days", "calendar"),
        ("Working days", "working"),
        ("Rolling reporting period", "source_defined"),
    ],
)
def test_time_basis_requires_explicit_clock_wording(label: str | None, expected: str) -> None:
    assert explicit_time_basis(label) == expected


def test_atomic_contract_accepts_separated_source_and_code_facets() -> None:
    assert validate_atomic_field_contract(_row()) == []


def test_atomic_contract_rejects_composite_legacy_fields() -> None:
    row = _row()
    row["provenance_locator"] = "page=7 | table=One"
    row["population_scope"] = "translated scope"
    assert validate_atomic_field_contract(row) == [
        "legacy composite field is prohibited: population_scope",
        "legacy composite field is prohibited: provenance_locator",
    ]


def test_atomic_contract_rejects_inferred_calendar_and_rewritten_source_text() -> None:
    row = _row()
    row["time_basis"] = "calendar"
    row["measure_label_source"] = "Example  count"
    assert validate_atomic_field_contract(row) == [
        "source-text field is not NFC/whitespace normalized: measure_label_source",
        "year or financial-period label alone requires time_basis=unknown",
    ]


def test_atomic_contract_rejects_semantic_text_in_code_field() -> None:
    row = _row()
    row["population_scope_code"] = "Example matters nationwide"
    assert validate_atomic_field_contract(row) == [
        "controlled-code field is invalid: population_scope_code"
    ]


def test_atomic_contract_requires_null_date_provenance() -> None:
    row = _row()
    row["period_end_provenance"] = "exact_edition"
    assert validate_atomic_field_contract(row) == [
        "null period_end requires period_end_provenance=not_stated"
    ]
