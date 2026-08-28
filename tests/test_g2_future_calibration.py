from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

from gfjd.g2_future_calibration import validate_preparation_bundle, validate_row

ROOT = Path("data/methods/g2/G2PROSPECTIVE-CALIBRATION-PREPARATION-20260829-01")


def _json(project_root: Path, relative: Path) -> dict[str, object]:
    return json.loads((project_root / relative).read_text(encoding="utf-8"))


def _fictional_row() -> dict[str, object]:
    return {
        "schema_version": "2.0",
        "extracted_row_id": "G2ROW-FICTIONAL_01",
        "sample_key": "FICTIONAL_SAMPLE_01",
        "source_record_key": "a" * 64,
        "candidate_id": "G2CAND-FICTIONAL_01",
        "source_id": "FICTIONAL_SOURCE",
        "source_edition_id": "FICTIONAL_EDITION",
        "source_format": "html",
        "locator": {
            "pdf_page": None,
            "printed_page": None,
            "section_source": None,
            "object_source": None,
            "machine_locator": "table[1]/row[1]",
        },
        "domain_label_source": None,
        "domain_code": "unknown",
        "matter_label_source": "Fictional matter",
        "matter_type_code": "source_defined",
        "measure_label_source": "Fictional measure",
        "indicator_code": "source_defined",
        "series_label_source": None,
        "series_code": None,
        "statistic_label_source": "Fictional count",
        "statistic_type": "source_defined",
        "unit_label_source": "fictional units",
        "unit_code": "source_defined",
        "value": 123,
        "component_values": {},
        "denominator_value": None,
        "denominator_definition_quote": None,
        "denominator_code": "not_applicable",
        "period_label_source": "Fictional period",
        "period_start": None,
        "period_end": None,
        "period_start_provenance": "not_stated",
        "period_end_provenance": "not_stated",
        "clock_label_source": None,
        "clock_code": "unknown",
        "cohort_definition_quote": None,
        "cohort_code": "unknown",
        "counted_entity_label_source": None,
        "counted_entity_code": "unknown",
        "population_scope_label_source": None,
        "population_scope_code": "unknown",
        "coverage_limitation_quote": None,
        "ambiguity_codes": [],
        "ambiguity_evidence_quote": None,
        "quarantine_status": "hard_quarantine",
        "suppression_or_disclosure_note": None,
        "extraction_uncertainty": "none",
        "notes": "Wholly fictional schema fixture",
    }


def test_preparation_bundle_is_bound_and_non_executable(project_root: Path) -> None:
    bundle = _json(project_root, ROOT / "preparation-bundle.json")
    schema = _json(project_root, ROOT / "preparation-bundle.schema.json")
    assert validate_preparation_bundle(project_root, bundle, schema) == []


def test_preparation_bundle_rejects_authority_and_candidate_content(project_root: Path) -> None:
    bundle = _json(project_root, ROOT / "preparation-bundle.json")
    schema = _json(project_root, ROOT / "preparation-bundle.schema.json")
    authorized = copy.deepcopy(bundle)
    authorized["authorization"]["source_access"] = True  # type: ignore[index]
    assert validate_preparation_bundle(project_root, authorized, schema)
    leaked = copy.deepcopy(bundle)
    leaked["candidate_id"] = "G2CAND-NOT_ALLOWED"
    assert validate_preparation_bundle(project_root, leaked, schema)


def test_preparation_bundle_rejects_digest_drift_and_repository_escape(
    project_root: Path,
) -> None:
    bundle = _json(project_root, ROOT / "preparation-bundle.json")
    schema = _json(project_root, ROOT / "preparation-bundle.schema.json")
    drifted = copy.deepcopy(bundle)
    drifted["bindings"][0]["sha256"] = "0" * 64  # type: ignore[index]
    assert any(
        "digest mismatch" in error
        for error in validate_preparation_bundle(project_root, drifted, schema)
    )
    escaped = copy.deepcopy(bundle)
    escaped["bindings"][0]["path"] = "docs/../../outside.json"  # type: ignore[index]
    assert any(
        "escapes repository" in error
        for error in validate_preparation_bundle(project_root, escaped, schema)
    )


def test_detached_preparation_manifest_verifies_exact_artifact_set(
    project_root: Path,
) -> None:
    manifest = project_root / ROOT / "PREPARATION_MANIFEST.sha256"
    entries: set[str] = set()
    for line in manifest.read_text(encoding="utf-8").splitlines():
        digest, relative = line.split("  ", 1)
        assert relative not in entries
        entries.add(relative)
        assert hashlib.sha256((project_root / relative).read_bytes()).hexdigest() == digest
    assert entries == {
        (ROOT / "preparation-bundle.json").as_posix(),
        (ROOT / "preparation-bundle.schema.json").as_posix(),
        (ROOT / "row.schema.json").as_posix(),
        "src/gfjd/g2_future_calibration.py",
        "tests/test_g2_future_calibration.py",
    }


def test_fictional_row_accepts_truthful_nulls_and_hard_quarantine(project_root: Path) -> None:
    schema = _json(project_root, ROOT / "row.schema.json")
    assert validate_row(_fictional_row(), schema) == []


def test_row_rejects_pdf_without_page_open_components_and_unsupported_semantics(
    project_root: Path,
) -> None:
    schema = _json(project_root, ROOT / "row.schema.json")
    row = _fictional_row()
    row["source_format"] = "pdf"
    row["component_values"] = {"invented_component": 1}
    row["domain_code"] = "invented_code"
    errors = validate_row(row, schema)
    assert len(errors) >= 3


def test_row_requires_source_text_for_source_defined_codes(project_root: Path) -> None:
    schema = _json(project_root, ROOT / "row.schema.json")
    row = _fictional_row()
    row["matter_label_source"] = None
    assert validate_row(row, schema)


def test_unknown_with_source_text_requires_conflict_evidence(project_root: Path) -> None:
    schema = _json(project_root, ROOT / "row.schema.json")
    row = _fictional_row()
    row["domain_label_source"] = "Conflicting fictional domain"
    assert validate_row(row, schema) == [
        "domain_code=unknown with source text requires ontology_conflict"
    ]
    row["ambiguity_codes"] = ["ontology_conflict"]
    row["ambiguity_evidence_quote"] = "Two fictional labels conflict"
    row["extraction_uncertainty"] = "unresolved"
    assert validate_row(row, schema) == []
