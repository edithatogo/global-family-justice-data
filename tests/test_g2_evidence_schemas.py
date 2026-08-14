from __future__ import annotations

import csv
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

SHA = "a" * 64
COMMIT = "b" * 40
PACKET_ID = "G2PKT-TEST01"


def _schema(project_root: Path, name: str) -> dict[str, object]:
    return json.loads((project_root / "schemas" / name).read_text(encoding="utf-8"))


def _artifact(path: str = "evidence/item.json") -> dict[str, str]:
    return {"path": path, "sha256": SHA}


def _validate(project_root: Path, name: str, payload: dict[str, object]) -> None:
    validator = Draft202012Validator(_schema(project_root, name), format_checker=FormatChecker())
    assert list(validator.iter_errors(payload)) == []


def test_g2_evidence_chain_schemas_accept_bounded_receipts(project_root: Path) -> None:
    packet = {
        "schema_version": "1.0",
        "packet_id": PACKET_ID,
        "created_at": "2026-08-15T00:00:00Z",
        "source_commit": COMMIT,
        "contract_version": "0.3",
        "ontology_version": "0.3",
        "cohort": ["AUS"],
        "source_editions": [
            {
                "candidate_id": "AUS",
                "source_id": "AUS-FCFCOA-AR",
                "source_edition_id": "ED-AUS-TEST",
                "acquisition_manifest": _artifact("data/raw/manifests/test.json"),
                "content_sha256": SHA,
                "storage_class": "local_private",
                "rights_status": "unknown",
            }
        ],
        "methods_contracts": [_artifact("docs/methods/contract.json")],
        "schema_bindings": [_artifact("schemas/g2_extraction_row.schema.json")],
        "extraction_instructions": _artifact("docs/methods/instructions.md"),
        "concordance_policy": _artifact("docs/quality/concordance.md"),
        "excluded_inputs": ["other-agent-output"],
        "packet_manifest": _artifact("data/methods/g2/test/MANIFEST.sha256"),
    }
    _validate(project_root, "g2_evidence_packet.schema.json", packet)

    extraction_row = {
        "schema_version": "1.0",
        "extracted_row_id": "G2ROW-TEST01",
        "source_record_key": SHA,
        "candidate_id": "AUS",
        "source_id": "AUS-FCFCOA-AR",
        "source_edition_id": "ED-AUS-TEST",
        "provenance_locator": "page 1 table 1 row 1",
        "measure_original": "Applications",
        "matter_type_original": "Family",
        "statistic_type": "count",
        "unit": "applications",
        "value": 10,
        "denominator_value": None,
        "denominator_definition": None,
        "period_start": "2025-01-01",
        "period_end": "2025-12-31",
        "time_basis": "not_applicable",
        "cohort_basis": "filed",
        "population_scope": "national",
        "suppression_or_disclosure_note": None,
        "extraction_uncertainty": "low",
        "notes": None,
    }
    _validate(project_root, "g2_extraction_row.schema.json", extraction_row)

    run = {
        "schema_version": "1.0",
        "run_id": "G2EXT-PRIMARY01",
        "packet_id": PACKET_ID,
        "packet_sha256": SHA,
        "assignment": "primary",
        "agent_role": "primary extraction analyst agent",
        "agent_session_id": "agent-primary",
        "tool_or_model": "agent",
        "tool_or_model_version": "1",
        "instructions_sha256": SHA,
        "blindness_declaration": "No secondary extraction output was supplied or inspected.",
        "excluded_artifact_paths": ["secondary/output.csv"],
        "started_at": "2026-08-15T00:00:00Z",
        "completed_at": "2026-08-15T00:01:00Z",
        "input_editions": [_artifact("data/raw/manifests/test.json")],
        "output": {**_artifact("build/g2/primary.csv"), "row_count": 1},
        "row_schema": _artifact("schemas/g2_extraction_row.schema.json"),
        "validation_status": "passed",
        "warnings": [],
        "limitations": ["Procedural rather than cryptographic blinding"],
        "status": "complete",
    }
    _validate(project_root, "g2_extraction_run.schema.json", run)

    concordance = {
        "schema_version": "1.0",
        "comparison_id": "G2CMP-TEST01",
        "packet_id": PACKET_ID,
        "packet_sha256": SHA,
        "primary_receipt": _artifact("primary.json"),
        "secondary_receipt": _artifact("secondary.json"),
        "primary_output": _artifact("primary.csv"),
        "secondary_output": _artifact("secondary.csv"),
        "comparator": {"name": "gfjd-concordance", "version": "1", "source_commit": COMMIT},
        "threshold_policy": _artifact("concordance-policy.json"),
        "matched_rows": 1,
        "primary_only_rows": 0,
        "secondary_only_rows": 0,
        "critical_field_comparisons": 10,
        "critical_field_matches": 10,
        "overall_field_comparisons": 20,
        "overall_field_matches": 20,
        "critical_concordance": 1.0,
        "overall_concordance": 1.0,
        "field_metrics": {
            "value": {"comparisons": 1, "matches": 1, "concordance": 1.0, "critical": True}
        },
        "difference_artifact": _artifact("differences.csv"),
        "threshold_passed": True,
        "status": "pass",
        "generated_at": "2026-08-15T00:02:00Z",
        "limitations": [],
    }
    _validate(project_root, "g2_concordance.schema.json", concordance)


def test_g2_panel_rights_operations_and_owner_schemas_preserve_boundaries(
    project_root: Path,
) -> None:
    panel = {
        "schema_version": "1.0",
        "report_id": "PANEL-G2TEST01",
        "packet_id": PACKET_ID,
        "packet_sha256": SHA,
        "role": "rights and security advisory agent",
        "agent_session_id": "agent-rights",
        "tool_or_model": "agent",
        "tool_or_model_version": "1",
        "generated_at": "2026-08-15T00:03:00Z",
        "evidence_inputs": [_artifact()],
        "verdict": "conditional",
        "findings": [],
        "options": [
            {
                "option_id": "A",
                "description": "Keep metadata only",
                "trade_offs": ["No byte redistribution"],
                "limitations": ["No legal conclusion"],
                "contingency": "Quarantine",
            }
        ],
        "recommendation": "Retain metadata-only routing",
        "rationale": "Exact-edition rights remain unclear",
        "conflicts": [],
        "abstentions": ["No legal conclusion"],
        "dissent": [],
        "authority_boundary": "advisory_only_no_gate_rights_legal_or_release_authority",
    }
    _validate(project_root, "agent_panel_report.schema.json", panel)

    inspection = {"method": "bounded inspection", "status": "passed", "evidence": _artifact()}
    rights = {
        "schema_version": "1.0",
        "review_id": "G2RS-TEST01",
        "packet_id": PACKET_ID,
        "packet_sha256": SHA,
        "candidate_id": "AUS",
        "source_id": "AUS-FCFCOA-AR",
        "source_edition_id": "ED-AUS-TEST",
        "content_sha256": SHA,
        "canonical_url": "https://example.org/source",
        "acquisition_receipt": _artifact(),
        "terms_evidence": [{**_artifact(), "accessed_at": "2026-08-15T00:00:00Z"}],
        "rights_observations": {
            "copyright": "ambiguous",
            "database_rights": "not_applicable",
            "third_party_components": "ambiguous",
            "signed_agreement": "none",
        },
        "permitted_acts": ["metadata citation"],
        "prohibited_acts": ["unapproved redistribution"],
        "attribution_conditions": ["attribute publisher"],
        "privacy_inspection": inspection,
        "binary_security_inspection": inspection,
        "disclosure_inspection": inspection,
        "findings": [],
        "critical_finding_count": 0,
        "high_finding_count": 0,
        "proposed_disposition": "metadata_only",
        "uncertainties": ["No legal conclusion"],
        "owner_decision_required": True,
        "panel_report": _artifact("panel.json"),
        "authority_boundary": "factual_agent_review_not_legal_advice_or_rights_clearance",
    }
    _validate(project_root, "g2_rights_security_review.schema.json", rights)

    operations = {
        "schema_version": "1.0",
        "rehearsal_id": "G2OPS-TEST01",
        "packet_id": PACKET_ID,
        "packet_sha256": SHA,
        "source_commit": COMMIT,
        "lockfile_sha256": SHA,
        "input_manifest": _artifact(),
        "build_command_id": "gfjd-g2-build",
        "first_build": _artifact("first.zip"),
        "second_build": _artifact("second.zip"),
        "deterministic_match": True,
        "validation_receipts": [_artifact()],
        "pre_correction_bundle": _artifact("pre.zip"),
        "correction_scenario": "Correct a rehearsed metadata defect",
        "correction_reference": _artifact("correction.json"),
        "post_correction_bundle": _artifact("post.zip"),
        "rollback_or_republish_result": "passed",
        "backup_receipt": _artifact("backup.json"),
        "restore_receipt": _artifact("restore.json"),
        "restored_payload_sha256": SHA,
        "restore_verified": True,
        "restricted_source_inventory": _artifact("restricted.json"),
        "build_elapsed_seconds": 1.0,
        "restore_elapsed_seconds": 1.0,
        "errors": [],
        "findings": [],
        "operations_panel_report": _artifact("operations-panel.json"),
        "custody_class": "local-rehearsal-only",
        "signature_status": "unsigned",
        "publication_authorized": False,
        "status": "passed",
    }
    _validate(project_root, "g2_operations_rehearsal.schema.json", operations)

    disposition = {
        "subject_id": "G2-C06",
        "decision": "defer",
        "rationale": "Factual evidence remains incomplete",
        "evidence_references": [_artifact()],
    }
    owner = {
        "schema_version": "1.0",
        "decision_id": "D-G2-TEST01",
        "decided_at": "2026-08-15T00:04:00Z",
        "owner_identity": "repository owner",
        "owner_role": "repository owner and sole accountable decision-maker",
        "packet_id": PACKET_ID,
        "packet_sha256": SHA,
        "panel_synthesis": _artifact("synthesis.json"),
        "decision_scope": "G2 evidence and gate only",
        "source_dispositions": [disposition],
        "methods_dispositions": [disposition],
        "concordance_disposition": disposition,
        "rights_security_disposition": disposition,
        "operations_disposition": disposition,
        "risk_dispositions": [disposition],
        "work_item_dispositions": [disposition],
        "maturity_dispositions": [disposition],
        "gate_decision": "defer",
        "conditions": ["No publication"],
        "review_or_expiry_date": None,
        "reopen_triggers": ["Evidence digest changes"],
        "publication_authorized": False,
        "immutable_reference": "commit-bound",
        "pre_decision_manifest_sha256": SHA,
    }
    _validate(project_root, "g2_owner_adjudication.schema.json", owner)

    invalid_operations = {**operations, "publication_authorized": True}
    validator = Draft202012Validator(_schema(project_root, "g2_operations_rehearsal.schema.json"))
    assert list(validator.iter_errors(invalid_operations))


def test_review_contract_deprecates_but_retains_independent_assurance(project_root: Path) -> None:
    schema = _schema(project_root, "review.schema.json")
    review_type = schema["properties"]["review_type"]
    assert "independent_assurance" in review_type["enum"]
    assert "independent_assurance" in review_type["x-deprecated-values"]
    assert "agent_panel_advice" in review_type["enum"]


def test_real_pilot_register_uses_agent_panel_assurance_column(project_root: Path) -> None:
    with (project_root / "data/methods/real_pilot_execution_register.csv").open(
        encoding="utf-8", newline=""
    ) as handle:
        header = next(csv.reader(handle))
    assert "agent_panel_assurance" in header
    assert "independent_assurance" not in header
