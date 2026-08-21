"""Contract checks for the known-source multi-format G2 pilot packet."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
PACKET_DIR = ROOT / "data/methods/g2/G2REAL-PILOT-20260821-01"
SCHEMA_PATH = PACKET_DIR / "multiformat_extraction_row.schema.json"
PACKET_PATH = ROOT / "data/methods/g2/G2REAL-PILOT-20260821-01/packet.json"
BUNDLE_PATH = PACKET_DIR / "secondary_access_bundle.json"
RECALIBRATION_DIR = ROOT / "data/methods/g2/G2REAL-PILOT-20260821-02"
RECALIBRATION_PACKET_PATH = RECALIBRATION_DIR / "packet.json"
RECALIBRATION_BUNDLE_PATH = RECALIBRATION_DIR / "secondary_access_bundle.json"


def test_g2_multiformat_packet_binds_current_row_schema() -> None:
    schema = json.loads(SCHEMA_PATH.read_text())
    packet = json.loads(PACKET_PATH.read_text())

    Draft202012Validator.check_schema(schema)
    assert packet["row_schema"] == (
        "data/methods/g2/G2REAL-PILOT-20260821-01/multiformat_extraction_row.schema.json"
    )
    assert packet["row_schema_sha256"] == hashlib.sha256(SCHEMA_PATH.read_bytes()).hexdigest()
    assert packet["critical_concordance_required"] == 1.0
    assert packet["overall_populated_field_concordance_required"] == 0.99
    assert {source["source_format"] for source in packet["sources"]} == {
        "spreadsheet",
        "dashboard",
        "pdf",
    }
    for source in packet["sources"]:
        assert len(source["source_sha256"]) == 64
        assert int(source["source_sha256"], 16) >= 0
        assert len(source["source_record_key"]) == 64
        assert int(source["source_record_key"], 16) >= 0


def test_g2_multiformat_row_locators_are_format_specific() -> None:
    schema = json.loads(SCHEMA_PATH.read_text())
    validator = Draft202012Validator(schema)
    base = {
        "schema_version": "1.0",
        "extracted_row_id": "G2ROW-EXAMPLE_001",
        "sample_key": "EXAMPLE_SOURCE_001",
        "source_record_key": "0" * 64,
        "candidate_id": "G2-EXAMPLE-001",
        "source_id": "EXAMPLE_SOURCE",
        "source_edition_id": "EXAMPLE_EDITION",
        "source_sha256": "1" * 64,
        "domain_code": "family_justice",
        "matter_type_code": "family_case",
        "indicator_code": "family_case_filing_or_disposition_count",
        "statistic_type": "count",
        "unit_code": "count",
        "value": 1,
        "period_label_source": "2026 Q1",
        "period_start": None,
        "period_end": None,
        "time_basis": "source_defined",
        "counted_entity_code": "applications",
        "population_scope_code": "national",
        "ambiguity_codes": [],
        "quarantine_status": "quarantine",
        "extraction_uncertainty": "none",
        "notes": None,
    }
    locators = {
        "spreadsheet": {
            "kind": "spreadsheet_cell",
            "sheet": "Table_2",
            "row": 86,
            "column": "D",
            "header": "Total",
        },
        "dashboard": {
            "kind": "dashboard_visible_table",
            "page": "Volumes",
            "visual_title": "Volumes",
            "filters": {"Period": "Annually"},
            "row_label": "2026",
            "column_label": "Total",
        },
        "pdf": {
            "kind": "pdf_table",
            "pdf_page": 102,
            "printed_page": 83,
            "table_label": "Table 3.3.1(a)",
        },
    }

    for source_format, source_locator in locators.items():
        row = base | {"source_format": source_format, "source_locator": source_locator}
        assert not list(validator.iter_errors(row))


def test_g2_secondary_bundle_is_packet_bound_and_excludes_primary_output() -> None:
    packet = json.loads(PACKET_PATH.read_text())
    bundle = json.loads(BUNDLE_PATH.read_text())

    assert bundle["assignment"] == "secondary"
    assert bundle["packet"]["sha256"] == hashlib.sha256(PACKET_PATH.read_bytes()).hexdigest()
    assert bundle["row_schema"]["sha256"] == hashlib.sha256(SCHEMA_PATH.read_bytes()).hexdigest()
    assert {item["sample_key"] for item in bundle["permitted_source_editions"]} == {
        source["sample_key"] for source in packet["sources"]
    }
    assert any("/primary/" in path for path in bundle["prohibited_artifact_paths"])


def test_g2_two_row_recalibration_is_predecessor_bound_and_dashboard_free() -> None:
    packet = json.loads(RECALIBRATION_PACKET_PATH.read_text())
    bundle = json.loads(RECALIBRATION_BUNDLE_PATH.read_text())

    assert packet["predecessor_packet"] == "G2PKT-REAL-PILOT-20260821-01"
    assert packet["row_schema_sha256"] == hashlib.sha256(SCHEMA_PATH.read_bytes()).hexdigest()
    assert packet["critical_concordance_required"] == 1.0
    assert packet["overall_populated_field_concordance_required"] == 0.99
    assert {source["source_format"] for source in packet["sources"]} == {"spreadsheet", "pdf"}
    assert (
        bundle["packet"]["sha256"]
        == hashlib.sha256(RECALIBRATION_PACKET_PATH.read_bytes()).hexdigest()
    )
    assert {item["sample_key"] for item in bundle["permitted_source_editions"]} == {
        source["sample_key"] for source in packet["sources"]
    }
    assert any("/primary" in path for path in bundle["prohibited_artifact_paths"])
