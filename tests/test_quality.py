from __future__ import annotations

from gfjd.quality import assess_gold_eligibility


def eligible_row() -> dict[str, object]:
    return {
        "observation_id": "OBS_TEST_0001",
        "jurisdiction_id": "AUS",
        "indicator_id": "TIME_FILE_TO_DISP_MEDIAN",
        "source_id": "AUS-FCFCOA-AR",
        "matter_type_original": "parenting",
        "matter_type_harmonised": "MAT_PARENTING_PRIVATE",
        "measure_original": "median duration",
        "statistic_type": "median",
        "unit": "calendar_days",
        "value": 120,
        "period_start": "2025-01-01",
        "period_end": "2025-12-31",
        "cohort_basis": "completed matters",
        "definition_original": "Elapsed time from filing to finalisation",
        "definition_english": "Elapsed time from filing to finalisation",
        "provenance_locator": "Table 2, row parenting",
        "extraction_method": "pdf_table",
        "second_reviewed": True,
        "quality_grade": "A",
        "comparability_tier": "1",
        "stage_start": "filing",
        "stage_end": "final_disposition",
    }


def test_eligible_gold_row() -> None:
    decision = assess_gold_eligibility(eligible_row())
    assert decision.eligible
    assert decision.reasons == ()


def test_gold_rejects_unreviewed_or_incompatible_row() -> None:
    row = eligible_row()
    row["second_reviewed"] = False
    row["comparability_tier"] = "4"
    decision = assess_gold_eligibility(row)
    assert not decision.eligible
    assert "second_review_required" in decision.reasons
    assert "comparability_tier_must_be_1_or_2" in decision.reasons


def test_percent_range_is_enforced() -> None:
    row = eligible_row()
    row["indicator_id"] = "FLOW_CLEARANCE"
    row["unit"] = "percent"
    row["value"] = 150
    row["stage_start"] = None
    row["stage_end"] = None
    decision = assess_gold_eligibility(row)
    assert "percent_out_of_range" in decision.reasons
