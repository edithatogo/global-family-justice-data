from __future__ import annotations

import csv
from pathlib import Path

from gfjd.pipeline import build_lineage_index, promote_observations
from gfjd.project import load_project
from tests.helpers import eligible_observation, observation_headers


def test_promotion_accepts_and_quarantines_with_reasons(project_root: Path, tmp_path: Path) -> None:
    project = load_project(project_root)
    headers = observation_headers(project_root)
    good = eligible_observation()
    bad = eligible_observation(
        {
            "observation_id": "OBS_TEST_0002",
            "second_reviewed": "false",
            "second_reviewer": "",
        }
    )
    input_path = tmp_path / "silver.csv"
    with input_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers, lineterminator="\n")
        writer.writeheader()
        writer.writerows([bad, good])

    gold_path = tmp_path / "gold.csv"
    quarantine_path = tmp_path / "quarantine.csv"
    report_path = tmp_path / "promotion-report.json"
    result = promote_observations(
        project,
        input_path,
        gold_path,
        quarantine_path,
        report_path,
    )

    assert result["promoted_rows"] == 1
    assert result["quarantined_rows"] == 1
    assert "OBS_TEST_0001" in gold_path.read_text(encoding="utf-8")
    quarantine = quarantine_path.read_text(encoding="utf-8")
    assert "OBS_TEST_0002" in quarantine
    assert "second_review_missing" in quarantine
    assert "second_reviewer_missing" in quarantine

    lineage_path = tmp_path / "lineage.csv"
    assert build_lineage_index(project, gold_path, lineage_path) == 1
    assert "EXT-AUS-2025-001" in lineage_path.read_text(encoding="utf-8")


def test_declarative_mapping_builds_schema_valid_observation(
    project_root: Path, tmp_path: Path
) -> None:
    import json

    from gfjd.io import read_csv
    from gfjd.pipeline import map_structured_csv

    project = load_project(project_root)
    headers = observation_headers(project_root)
    source_path = tmp_path / "source.csv"
    source_path.write_text(
        "duration,count,start,reviewed,description\n"
        '" 1,234 ",1000,31/12/2025,yes,"  Filing   to disposition  "\n',
        encoding="utf-8",
    )
    base = eligible_observation()
    fields: dict[str, dict[str, object]] = {}
    for field in headers:
        value: object = base[field]
        if value == "":
            value = None
        elif field in {"value", "denominator_value"}:
            value = float(value)
        elif field == "comparability_tier":
            value = int(value)
        elif field in {"second_reviewed", "release_eligible", "break_in_series"}:
            value = value == "true"
        fields[field] = {"constant": value}
    fields["value"] = {"column": "duration", "transforms": ["strip", "parse_number"]}
    fields["denominator_value"] = {"column": "count", "transforms": ["parse_integer"]}
    fields["period_end"] = {
        "column": "start",
        "transforms": [{"name": "parse_date", "formats": ["%d/%m/%Y"]}],
    }
    fields["second_reviewed"] = {"column": "reviewed", "transforms": ["parse_boolean"]}
    fields["definition_original"] = {
        "column": "description",
        "transforms": ["normalise_whitespace"],
    }
    mapping = {
        "schema_version": "1.0",
        "mapping_id": "MAP_TEST_01",
        "source_id": "AUS-FCFCOA-AR",
        "source_edition_id": "ED-AUS-FCFCOA-2025",
        "input": {"delimiter": ",", "encoding": "utf-8"},
        "fields": fields,
    }
    mapping_path = tmp_path / "mapping.json"
    mapping_path.write_text(json.dumps(mapping), encoding="utf-8")
    output_path = tmp_path / "mapped.csv"

    result = map_structured_csv(project, mapping_path, source_path, output_path)
    assert result["output_rows"] == 1
    _, rows = read_csv(output_path)
    assert rows[0]["value"] == "1234.0"
    assert rows[0]["denominator_value"] == "1000"
    assert rows[0]["period_end"] == "2025-12-31"
    assert rows[0]["definition_original"] == "Filing to disposition"


def test_mapping_rejects_missing_required_input_column(project_root: Path, tmp_path: Path) -> None:
    import json

    import pytest

    from gfjd.pipeline import PipelineError, map_structured_csv

    project = load_project(project_root)
    source_path = tmp_path / "source.csv"
    source_path.write_text("present\nvalue\n", encoding="utf-8")
    mapping = {
        "schema_version": "1.0",
        "mapping_id": "MAP_TEST_BAD",
        "source_id": "AUS-FCFCOA-AR",
        "source_edition_id": "ED-AUS-FCFCOA-2025",
        "fields": {"observation_id": {"column": "missing", "required": True}},
    }
    mapping_path = tmp_path / "mapping.json"
    mapping_path.write_text(json.dumps(mapping), encoding="utf-8")
    with pytest.raises(PipelineError, match="input column 'missing' is missing"):
        map_structured_csv(project, mapping_path, source_path, tmp_path / "out.csv")
