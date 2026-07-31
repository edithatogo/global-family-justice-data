from __future__ import annotations

import json
from pathlib import Path


def observation_headers(project_root: Path) -> list[str]:
    schema = json.loads(
        (project_root / "schemas/observation.schema.json").read_text(encoding="utf-8")
    )
    return list(schema["properties"])


def eligible_observation(overrides: dict[str, str] | None = None) -> dict[str, str]:
    row = {
        "schema_version": "1.0",
        "observation_id": "OBS_TEST_0001",
        "record_status": "accepted",
        "jurisdiction_id": "AUS",
        "subnational_id": "",
        "institution_id": "INST-AUS-FCFCOA",
        "court_level": "national",
        "matter_type_original": "parenting",
        "matter_type_harmonised": "MAT_PARENTING_PRIVATE",
        "proceeding_type": "application",
        "measure_original": "median duration",
        "indicator_id": "TIME_FILE_TO_DISP_MEDIAN",
        "local_measure_id": "AUS-MEDIAN-DURATION",
        "stage_start": "filing",
        "stage_end": "final_disposition",
        "statistic_type": "median",
        "unit": "calendar_days",
        "count_unit": "matters",
        "value": "120",
        "denominator_value": "1000",
        "denominator_definition": "completed matters",
        "period_start": "2025-01-01",
        "period_end": "2025-12-31",
        "time_basis": "calendar",
        "cohort_basis": "completed matters",
        "population_scope": "eligible family-law matters",
        "definition_original": "Elapsed time from filing to finalisation",
        "definition_english": "Elapsed time from filing to finalisation",
        "source_id": "AUS-FCFCOA-AR",
        "source_edition_id": "ED-AUS-FCFCOA-2025",
        "provenance_locator": "Table 2, row parenting",
        "extraction_id": "EXT-AUS-2025-001",
        "transformation_rule_id": "MAP-AUS-2025-001",
        "review_id": "REV-AUS-2025-001",
        "extraction_method": "manual_pdf",
        "reviewer": "reviewer-a",
        "second_reviewer": "reviewer-b",
        "second_reviewed": "true",
        "review_status": "accepted",
        "quality_grade": "A",
        "comparability_tier": "1",
        "release_eligible": "true",
        "suppression_status": "not_required",
        "break_in_series": "false",
        "notes": "",
    }
    if overrides:
        row.update(overrides)
    return row
