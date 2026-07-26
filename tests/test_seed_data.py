from __future__ import annotations

import csv

from gfjd.validate import ROOT, run_validation, validate


def test_seed_registers_validate() -> None:
    assert validate() == []


def test_validation_reports_all_seed_tables() -> None:
    report = run_validation()
    assert report.ok
    expected_tables = {
        "jurisdictions",
        "sources",
        "indicators",
        "evidence",
        "institutions",
        "transformations",
        "releases",
        "observation_template",
    }
    assert expected_tables.issubset(report.row_counts)


def test_observation_template_has_lineage_and_release_fields() -> None:
    path = ROOT / "data/seed/observation_template.csv"
    with path.open(encoding="utf-8", newline="") as handle:
        headers = next(csv.reader(handle))
    required = {
        "schema_version",
        "source_version",
        "transformation_id",
        "review_status",
        "reviewed_at",
        "release_id",
    }
    assert required.issubset(headers)


def test_v1_release_criteria_exist() -> None:
    path = ROOT / "docs/strategy/V1_RELEASE_CRITERIA.md"
    text = path.read_text(encoding="utf-8")
    assert "Gate 12" in text
    assert "Meaning of “stable”" in text
