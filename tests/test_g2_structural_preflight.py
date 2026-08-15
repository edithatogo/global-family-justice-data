from __future__ import annotations

import hashlib
import json
import tempfile
from copy import deepcopy
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from gfjd.g2_structural_preflight import (
    DESIGN_MANIFEST_FILES,
    G2StructuralPreflightError,
    _assign_structural_slots,
    classify_structural_record,
    compare_holdout_extractions,
    prepare_structural_preflight_design,
    select_structural_scope,
    verify_artifact_access_receipt,
    verify_structural_preflight_design,
)

GENERATED_AT = "2026-08-15T05:15:00Z"


def _read(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def test_prepare_structural_preflight_freezes_unauthorized_frame(
    project_root: Path,
) -> None:
    with tempfile.TemporaryDirectory(dir=project_root / "build") as temporary:
        output = Path(temporary)
        frame_path, manifest_path, receipt_path = prepare_structural_preflight_design(
            project_root, output_dir=output, generated_at=GENERATED_AT
        )
        frame = _read(frame_path)
        candidates = frame["candidates"]
        assert isinstance(candidates, list)
        assert len(candidates) == 44
        assert [item["frame_rank"] for item in candidates] == list(range(1, 45))
        assert len({item["candidate_id"] for item in candidates}) == 44
        assert len({item["edition_id"] for item in candidates}) == 44
        assert len({item["source_series_id"] for item in candidates}) == 44
        assert all(item["source_access_authorized"] is False for item in candidates)
        assert all(item["source_content_accessed"] is False for item in candidates)
        assert [item["frame_score"] for item in candidates] == sorted(
            item["frame_score"] for item in candidates
        )

        manifest = _read(manifest_path)
        assert manifest["status"] == "proposed_not_authorized"
        assert manifest["source_request_performed"] is False
        entries = manifest["entries"]
        assert isinstance(entries, list)
        assert len(entries) == 11
        assert len({item["requested_entrypoint"] for item in entries}) == 11
        assert all(item["entrypoint_kind"] == "exact_pdf_url" for item in entries)
        assert all(item["actual_sha256"] is None for item in entries)
        assert all(item["stored_path"] is None for item in entries)
        resolution = _read(output / "proposed-url-resolution-manifest.json")
        assert resolution["entry_count"] == 33
        assert all(item["resolved_exact_pdf_url"] is None for item in resolution["entries"])

        receipt = _read(receipt_path)
        assert receipt["source_access_authorized"] is False
        assert receipt["source_access_performed"] is False
        assert verify_structural_preflight_design(project_root, output_dir=output) == []


def test_verify_structural_preflight_rejects_frame_tampering(
    project_root: Path,
) -> None:
    with tempfile.TemporaryDirectory(dir=project_root / "build") as temporary:
        output = Path(temporary)
        frame_path, _, _ = prepare_structural_preflight_design(
            project_root, output_dir=output, generated_at=GENERATED_AT
        )
        frame = _read(frame_path)
        candidates = frame["candidates"]
        assert isinstance(candidates, list)
        candidates[0]["edition_title"] = "tampered"
        frame_path.write_text(json.dumps(frame, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        assert verify_structural_preflight_design(project_root, output_dir=output) == [
            "frame does not reproduce"
        ]


def test_plan_keeps_all_execution_authorities_false(project_root: Path) -> None:
    plan = _read(project_root / "config/g2_structural_preflight_plan.json")
    authorization = plan["authorization"]
    assert isinstance(authorization, dict)
    assert authorization["metadata_reuse"] is True
    assert not any(value for key, value in authorization.items() if key != "metadata_reuse")
    stages = plan["stages"]
    assert isinstance(stages, dict)
    preflight = stages["structural_preflight"]
    extraction = stages["extraction"]
    assert preflight["target_extraction_or_transcription_allowed"] is False
    assert preflight["persist_source_text_screenshots_ocr_or_target_locators"] is False
    assert extraction["extractors_may_read_preflight_outputs"] is False
    assert extraction["reserve_substitution_after_seal"] is False


def test_plan_schema_rejects_fail_open_mutations(project_root: Path) -> None:
    plan = _read(project_root / "config/g2_structural_preflight_plan.json")
    schema = _read(project_root / "schemas/g2_structural_preflight_plan.schema.json")
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    mutations = []
    empty_stages = deepcopy(plan)
    empty_stages["stages"] = {}
    mutations.append(empty_stages)
    zero_budget = deepcopy(plan)
    zero_budget["resource_budget"]["maximum_candidates"] = 0
    mutations.append(zero_budget)
    arbitrary_stop = deepcopy(plan)
    arbitrary_stop["experiment_stop_codes"] = ["ignore_failure"]
    mutations.append(arbitrary_stop)
    for mutation in mutations:
        assert list(validator.iter_errors(mutation))


def test_role_schema_rejects_duplicate_or_changed_roles(project_root: Path) -> None:
    payload = _read(project_root / "config/g2_structural_role_bundles.json")
    schema = _read(project_root / "schemas/g2_structural_role_bundles.schema.json")
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    mutation = deepcopy(payload)
    mutation["roles"][1]["role"] = mutation["roles"][0]["role"]
    assert list(validator.iter_errors(mutation))


def test_supplemental_contracts_and_panels_are_schema_and_digest_bound(
    project_root: Path,
) -> None:
    pairs = (
        (
            "config/g2_structural_eligibility_policy.json",
            "schemas/g2_structural_eligibility_policy.schema.json",
        ),
        (
            "config/g2_holdout_generic_extraction_contract.json",
            "schemas/g2_holdout_extraction_contract.schema.json",
        ),
        (
            "config/g2_holdout_semantic_vocabulary.json",
            "schemas/g2_holdout_semantic_vocabulary.schema.json",
        ),
        (
            "config/g2_structural_role_bundles.json",
            "schemas/g2_structural_role_bundles.schema.json",
        ),
        (
            "config/g2_structural_selection_policy.json",
            "schemas/g2_structural_selection_policy.schema.json",
        ),
    )
    for payload_path, schema_path in pairs:
        payload = _read(project_root / payload_path)
        schema = _read(project_root / schema_path)
        errors = list(
            Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(payload)
        )
        assert errors == []

    panel_schema = _read(project_root / "schemas/agent_panel_report.schema.json")
    panel_root = project_root / "data/methods/g2/G2HOLDOUT-STRUCTURAL-PREFLIGHT-20260815-01/panels"
    for panel_path in panel_root.glob("*.json"):
        panel = _read(panel_path)
        errors = list(
            Draft202012Validator(panel_schema, format_checker=FormatChecker()).iter_errors(panel)
        )
        assert errors == []
        evidence_inputs = panel["evidence_inputs"]
        assert isinstance(evidence_inputs, list)
        for artifact in evidence_inputs:
            path = project_root / artifact["path"]
            assert hashlib.sha256(path.read_bytes()).hexdigest() == artifact["sha256"]


def test_detached_design_manifest_verifies_exact_artifact_set(project_root: Path) -> None:
    manifest = (
        project_root
        / "data/methods/g2/G2HOLDOUT-STRUCTURAL-PREFLIGHT-20260815-01/DESIGN_MANIFEST.sha256"
    )
    entries: set[str] = set()
    for line in manifest.read_text(encoding="utf-8").splitlines():
        digest, relative = line.split("  ", 1)
        assert relative not in entries
        entries.add(relative)
        assert hashlib.sha256((project_root / relative).read_bytes()).hexdigest() == digest
    assert "config/g2_structural_preflight_plan.json" in entries
    assert "config/g2_holdout_generic_extraction_contract.json" in entries
    assert any(path.endswith("security-access-report.json") for path in entries)
    assert entries == set(DESIGN_MANIFEST_FILES)


def test_structural_record_schema_rejects_persisted_source_content(
    project_root: Path,
) -> None:
    schema = _read(project_root / "schemas/g2_structural_preflight_record.schema.json")
    assert schema["additionalProperties"] is False
    assert "source_text" not in schema["properties"]
    contract = _read(project_root / "config/g2_holdout_generic_extraction_contract.json")
    assert contract["sample_specific_packet01_through_packet05_mappings_allowed"] is False
    assert contract["critical_concordance"] == 1.0
    assert contract["overall_populated_concordance"] == 0.99


def _structural_record(**changes: object) -> dict[str, object]:
    record: dict[str, object] = {
        "schema_version": "1.0",
        "record_id": "G2STRUCT-TEST01",
        "plan_id": "G2HOLDOUT-STRUCTURAL-PREFLIGHT-20260815-01",
        "candidate_id": "G2CAND-TEST001",
        "source_id": "SOURCE-TEST001",
        "edition_id": "ED-TEST001",
        "jurisdiction_id": "TEST-J01",
        "source_series_id": "SERIES-TEST001",
        "source_url": "https://example.org/test.pdf",
        "source_sha256": "a" * 64,
        "frame_rank": 1,
        "role_session_id": "SESSION-001",
        "role_bundle_sha256": "b" * 64,
        "tool_bundle_sha256": "c" * 64,
        "acquisition_receipt_sha256": "d" * 64,
        "binary_security_receipt_sha256": "e" * 64,
        "access_receipt_sha256": "f" * 64,
        "owner_authorization_sha256": "1" * 64,
        "telemetry_tool_receipt_sha256": "2" * 64,
        "exact_edition_confirmed": True,
        "pdf_magic_valid": True,
        "encrypted": False,
        "malformed": False,
        "active_content": False,
        "embedded_files": False,
        "external_launch_actions": False,
        "page_count": 10,
        "text_page_ratio": 0.9,
        "raster_page_ratio": 0.1,
        "complex_page_ratio": 0.1,
        "primary_language_code": "en",
        "aggregate_only": True,
        "personal_or_case_level_data": False,
        "prohibited_data": False,
        "critical_or_high_security_finding": False,
        "local_private_processing_approved": True,
        "assigned_stratum": "english_text_native",
        "disposition": "structurally_eligible",
        "reason_codes": [],
        "source_text_persisted": False,
        "target_fact_persisted": False,
        "screenshots_persisted": False,
        "generated_at": GENERATED_AT,
    }
    record.update(changes)
    return record


def test_structural_classifier_fails_closed(project_root: Path) -> None:
    assert classify_structural_record(project_root, _structural_record()) == "english_text_native"
    bad = _structural_record(aggregate_only=False)
    try:
        classify_structural_record(project_root, bad)
    except Exception as exc:
        assert "True was expected" in str(exc) or "required safe condition" in str(exc)
    else:
        raise AssertionError("unsafe eligible record passed")
    wrong = _structural_record(assigned_stratum="embedded_raster_or_dashboard_pdf")
    try:
        classify_structural_record(project_root, wrong)
    except Exception as exc:
        assert "inconsistent stratum" in str(exc)
    else:
        raise AssertionError("inconsistent stratum passed")


def test_deterministic_selector_enforces_exact_scope(project_root: Path) -> None:
    strata = [
        "embedded_raster_or_dashboard_pdf",
        "structurally_complex_mixed_layout_pdf",
        "non_english_text_native",
        "english_text_native",
    ]
    records = []
    for index in range(30):
        reserve_index = index - 24 if index < 28 else index - 28
        stratum = strata[min(index // 6, 3)] if index < 24 else strata[reserve_index]
        records.append(
            {
                "candidate_id": f"G2CAND-SEL{index:03d}",
                "edition_id": f"ED-SEL{index:03d}",
                "jurisdiction_id": f"J{index:03d}",
                "source_series_id": f"SERIES-{index:03d}",
                "source_url": f"https://example.org/{index}.pdf",
                "assigned_stratum": stratum,
                "frame_rank": index + 1,
                "disposition": "structurally_eligible",
            }
        )
    policy = _read(project_root / "config/g2_structural_selection_policy.json")
    result = _assign_structural_slots(records, policy)
    assert result is not None
    primary, reserves = result
    assert len(primary) == 24
    assert len(reserves) == 6
    assert _assign_structural_slots(records[:29], policy) is None
    duplicate = deepcopy(records)
    duplicate[-1]["source_series_id"] = duplicate[0]["source_series_id"]
    assert _assign_structural_slots(duplicate, policy) is None
    cap_breach = deepcopy(records)
    for item in cap_breach[:3]:
        item["jurisdiction_id"] = "J-CAPPED"
    assert _assign_structural_slots(cap_breach, policy) is None


def test_selector_validates_digest_bound_frame_handoff(project_root: Path) -> None:
    frame_path = project_root / (
        "data/methods/g2/G2HOLDOUT-STRUCTURAL-PREFLIGHT-20260815-01/"
        "design/oversampled-metadata-frame.json"
    )
    frame = _read(frame_path)
    with tempfile.TemporaryDirectory(dir=project_root / "build") as temporary:
        work = Path(temporary)
        test_frame = deepcopy(frame)
        for framed in test_frame["candidates"][:9]:
            if framed["source_url"] is None:
                framed["source_url"] = framed["landing_page_url"]
        test_frame_path = work / "frame.json"
        test_frame_path.write_text(json.dumps(test_frame, sort_keys=True) + "\n", encoding="utf-8")

        def artifact(path: Path) -> dict[str, str]:
            return {
                "path": path.relative_to(project_root).as_posix(),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }

        record_artifacts = []
        for framed in test_frame["candidates"][:9]:
            is_last = framed["frame_rank"] == 9
            record = _structural_record(
                candidate_id=framed["candidate_id"],
                edition_id=framed["edition_id"],
                jurisdiction_id=framed["jurisdiction_id"],
                source_series_id=framed["source_series_id"],
                source_url=framed["source_url"],
                frame_rank=framed["frame_rank"],
                disposition="structurally_eligible" if is_last else "candidate_rejected",
                reason_codes=[] if is_last else ["not_official_or_not_exact_edition"],
            )
            record_path = work / f"record-{framed['frame_rank']}.json"
            record_path.write_text(json.dumps(record, sort_keys=True) + "\n", encoding="utf-8")
            record_artifacts.append(artifact(record_path))

        receipt = {
            "schema_version": "1.0",
            "receipt_id": "ELIGIBILITY-TEST001",
            "plan_id": "G2HOLDOUT-STRUCTURAL-PREFLIGHT-20260815-01",
            "frame": artifact(test_frame_path),
            "structural_policy": artifact(
                project_root / "config/g2_structural_eligibility_policy.json"
            ),
            "selection_policy": artifact(
                project_root / "config/g2_structural_selection_policy.json"
            ),
            "inspected_prefix_end_rank": 9,
            "records": record_artifacts,
            "generated_at": GENERATED_AT,
        }
        receipt_path = work / "eligibility-receipt.json"
        receipt_path.write_text(json.dumps(receipt, sort_keys=True) + "\n", encoding="utf-8")
        assert select_structural_scope(project_root, receipt_path) is None
        receipt["records"].pop(0)
        receipt_path.write_text(json.dumps(receipt, sort_keys=True) + "\n", encoding="utf-8")
        with pytest.raises(Exception, match="every rank"):
            select_structural_scope(project_root, receipt_path)


def _holdout_row(index: int = 0, **changes: object) -> dict[str, object]:
    row: dict[str, object] = {
        "schema_version": "1.0",
        "extracted_row_id": "G2ROW-HOLDOUT001",
        "sample_key": f"SAMPLE_HOLDOUT{index:03d}",
        "source_record_key": hashlib.sha256(f"holdout-{index}".encode()).hexdigest(),
        "candidate_id": f"G2CAND-HOLDOUT{index:03d}",
        "source_id": f"SOURCE_HOLDOUT{index:03d}",
        "source_edition_id": f"EDITION_HOLDOUT{index:03d}",
        "locator_pdf_page": 1,
        "locator_printed_page": None,
        "locator_section_source": "Section",
        "locator_object_source": "Table 1",
        "domain_label_source": "Family",
        "domain_code": "family_justice",
        "matter_label_source": "Applications",
        "matter_type_code": "family_case",
        "measure_label_source": "Total",
        "indicator_code": "family_case_filing_or_disposition_count",
        "series_label_source": None,
        "series_code": None,
        "statistic_type": "count",
        "unit_code": "count",
        "value": 10,
        "component_values": {},
        "denominator_value": None,
        "denominator_definition_quote": None,
        "denominator_code": "not_applicable",
        "period_label_source": "2025",
        "period_start": None,
        "period_end": None,
        "period_start_provenance": "not_stated",
        "period_end_provenance": "not_stated",
        "time_basis": "not_applicable",
        "clock_label_source": None,
        "clock_code": "not_applicable",
        "cohort_definition_quote": "Filed in period",
        "cohort_code": "filed_in_period",
        "counted_entity_code": "applications",
        "population_scope_code": "statewide",
        "coverage_limitation_quote": None,
        "ambiguity_codes": [],
        "ambiguity_evidence_quote": None,
        "quarantine_status": "quarantine",
        "suppression_or_disclosure_note": None,
        "extraction_uncertainty": "none",
        "notes": None,
    }
    row.update(changes)
    return row


def test_generic_comparator_binds_contract_and_rejects_semantic_mismatch(
    project_root: Path,
) -> None:
    with tempfile.TemporaryDirectory(dir=project_root / "build") as temporary:
        work = Path(temporary)
        primary = work / "primary.json"
        secondary = work / "secondary.json"
        owner = (
            project_root
            / "docs/governance/g2-blind-holdout-intake-stop-owner-decision-2026-08-15.md"
        )
        contract = project_root / "config/g2_holdout_generic_extraction_contract.json"
        row_schema = project_root / "schemas/g2_holdout_extraction_row.schema.json"
        role_bundles = project_root / "config/g2_structural_role_bundles.json"
        selection_policy = project_root / "config/g2_structural_selection_policy.json"
        structural_policy = project_root / "config/g2_structural_eligibility_policy.json"

        def artifact(path: Path) -> dict[str, str]:
            return {
                "path": path.relative_to(project_root).as_posix(),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }

        base_frame = _read(
            project_root / "data/methods/g2/G2HOLDOUT-STRUCTURAL-PREFLIGHT-20260815-01/"
            "design/oversampled-metadata-frame.json"
        )
        test_frame = deepcopy(base_frame)
        strata = [
            "embedded_raster_or_dashboard_pdf",
            "structurally_complex_mixed_layout_pdf",
            "non_english_text_native",
            "english_text_native",
        ]
        reserve_strata = [strata[0], strata[1], strata[2], strata[3], strata[0], strata[1]]
        record_artifacts = []
        source_paths: dict[str, Path] = {}
        for index in range(30):
            source_path = work / f"source-{index}.pdf"
            source_path.write_bytes(f"%PDF-1.4\n{index}\n%%EOF\n".encode())
            source_sha = hashlib.sha256(source_path.read_bytes()).hexdigest()
            framed = test_frame["candidates"][index]
            framed["source_url"] = f"https://example.org/source-{index}.pdf"
            framed["jurisdiction_id"] = f"J-TEST-{index:03d}"
            framed["retrieval_entrypoint"] = framed["source_url"]
            framed["retrieval_entrypoint_kind"] = "exact_pdf_url"
            source_id = f"SOURCE-HOLDOUT{index:03d}"
            stratum = strata[index // 6] if index < 24 else reserve_strata[index - 24]
            ratios = {
                "raster_page_ratio": 0.6 if stratum == strata[0] else 0.1,
                "complex_page_ratio": 0.3 if stratum == strata[1] else 0.1,
                "primary_language_code": "fr" if stratum == strata[2] else "en",
            }
            record = _structural_record(
                record_id=f"G2STRUCT-TEST{index:03d}",
                candidate_id=framed["candidate_id"],
                source_id=source_id,
                edition_id=framed["edition_id"],
                jurisdiction_id=framed["jurisdiction_id"],
                source_series_id=framed["source_series_id"],
                source_url=framed["source_url"],
                source_sha256=source_sha,
                frame_rank=index + 1,
                assigned_stratum=stratum,
                **ratios,
            )
            record_path = work / f"structural-{index}.json"
            record_path.write_text(json.dumps(record, sort_keys=True) + "\n", encoding="utf-8")
            record_artifacts.append(artifact(record_path))
            source_paths[str(framed["candidate_id"])] = source_path
        frame_path = work / "resolved-frame.json"
        frame_path.write_text(json.dumps(test_frame, sort_keys=True) + "\n", encoding="utf-8")
        eligibility = {
            "schema_version": "1.0",
            "receipt_id": "ELIGIBILITY-COMPARATOR-TEST",
            "plan_id": "G2HOLDOUT-STRUCTURAL-PREFLIGHT-20260815-01",
            "frame": artifact(frame_path),
            "structural_policy": artifact(structural_policy),
            "selection_policy": artifact(selection_policy),
            "inspected_prefix_end_rank": 30,
            "records": record_artifacts,
            "generated_at": GENERATED_AT,
        }
        eligibility_path = work / "eligibility.json"
        eligibility_path.write_text(
            json.dumps(eligibility, sort_keys=True) + "\n", encoding="utf-8"
        )
        reproduced = select_structural_scope(project_root, eligibility_path)
        assert reproduced is not None

        def selection_entry(record: dict[str, object]) -> dict[str, object]:
            rank_index = int(record["frame_rank"]) - 1
            return {
                "source_record_key": hashlib.sha256(f"holdout-{rank_index}".encode()).hexdigest(),
                "candidate_id": record["candidate_id"],
                "source_id": record["source_id"],
                "source_edition_id": record["edition_id"],
                "source_sha256": record["source_sha256"],
                "assigned_stratum": record["assigned_stratum"],
                "frame_rank": record["frame_rank"],
            }

        primary_entries = [selection_entry(record) for record in reproduced["primary"]]
        reserve_entries = [selection_entry(record) for record in reproduced["reserves"]]
        rows = [
            _holdout_row(
                int(entry["frame_rank"]) - 1,
                candidate_id=entry["candidate_id"],
                source_id=entry["source_id"],
                source_edition_id=entry["source_edition_id"],
            )
            for entry in primary_entries
        ]
        primary.write_text(json.dumps(rows, sort_keys=True) + "\n", encoding="utf-8")
        secondary.write_text(json.dumps(rows, sort_keys=True) + "\n", encoding="utf-8")
        primary_editions = [
            {
                "candidate_id": entry["candidate_id"],
                "source_id": entry["source_id"],
                "source_edition_id": entry["source_edition_id"],
                "source_sha256": entry["source_sha256"],
                "private_source_path": source_paths[str(entry["candidate_id"])]
                .relative_to(project_root)
                .as_posix(),
            }
            for entry in primary_entries
        ]
        selection = {
            "schema_version": "1.0",
            "selection_id": "SELECTION-TEST001",
            "plan_id": "G2HOLDOUT-STRUCTURAL-PREFLIGHT-20260815-01",
            "eligibility_receipt": artifact(eligibility_path),
            "selection_policy": artifact(selection_policy),
            "prefix_end_rank": 30,
            "primary": primary_entries,
            "reserves": reserve_entries,
            "scope_complete": True,
            "generated_at": GENERATED_AT,
        }
        selection_path = work / "sealed-selection.json"
        selection_path.write_text(json.dumps(selection, sort_keys=True) + "\n", encoding="utf-8")
        bundle = {
            "schema_version": "1.0",
            "bundle_id": "BUNDLE-TEST001",
            "plan_id": "G2HOLDOUT-STRUCTURAL-PREFLIGHT-20260815-01",
            "owner_authorization": artifact(owner),
            "extraction_contract": artifact(contract),
            "row_schema": artifact(row_schema),
            "primary_count": 24,
            "primary_editions": primary_editions,
            "reserve_information_included": False,
            "rejected_candidate_information_included": False,
            "prior_experiment_information_included": False,
            "generated_at": GENERATED_AT,
        }
        bundle_path = work / "extractor-bundle.json"
        bundle_path.write_text(json.dumps(bundle, sort_keys=True) + "\n", encoding="utf-8")

        def write_receipt(
            role: str, output: Path, extractor_bundle_path: Path = bundle_path
        ) -> Path:
            access_output_class = f"{role.removesuffix('_extractor')}_extraction_output"
            access = {
                "schema_version": "1.0",
                "receipt_id": f"ACCESS-{role.upper()}",
                "plan_id": "G2HOLDOUT-STRUCTURAL-PREFLIGHT-20260815-01",
                "role": role,
                "session_id": f"SESSION-{role.upper()}",
                "fresh_session_attested": True,
                "role_bundle": artifact(role_bundles),
                "authority": artifact(owner),
                "network_mode": "none",
                "network_url_allowlist": [],
                "input_bundle": artifact(extractor_bundle_path),
                "path_allowlist": [extractor_bundle_path.relative_to(project_root).as_posix()],
                "artifact_class_denylist": [
                    "candidate_metadata",
                    "exposure_ledger",
                    "prior_evidence",
                    "structural_receipt",
                    "eligibility_receipt",
                    "reserve_metadata",
                    "extraction_output",
                    "comparison_output",
                ],
                "output_prefix": work.relative_to(project_root).as_posix(),
                "access_events": [
                    {"artifact_class": "extractor_bundle", **artifact(extractor_bundle_path)}
                ],
                "denied_access_attempts": [],
                "violations": [],
                "started_at": GENERATED_AT,
                "ended_at": GENERATED_AT,
                "tool_bundle": artifact(row_schema),
                "outputs": [{"artifact_class": access_output_class, **artifact(output)}],
            }
            access_path = work / f"access-{role}.json"
            access_path.write_text(json.dumps(access, sort_keys=True) + "\n", encoding="utf-8")
            run = {
                "schema_version": "1.0",
                "receipt_id": f"RUN-{role.upper()}",
                "plan_id": "G2HOLDOUT-STRUCTURAL-PREFLIGHT-20260815-01",
                "role": role,
                "session_id": f"SESSION-{role.upper()}",
                "fresh_session_attested": True,
                "extractor_bundle": artifact(extractor_bundle_path),
                "sealed_selection": artifact(selection_path),
                "extraction_contract": artifact(contract),
                "row_schema": artifact(row_schema),
                "output": artifact(output),
                "source_commit": "e" * 40,
                "access_receipt": artifact(access_path),
                "generated_at": GENERATED_AT,
                "violations": [],
            }
            run_path = work / f"run-{role}.json"
            run_path.write_text(json.dumps(run, sort_keys=True) + "\n", encoding="utf-8")
            return run_path

        primary_run = write_receipt("primary_extractor", primary)
        secondary_run = write_receipt("secondary_extractor", secondary)
        common = {
            "primary_path": primary,
            "secondary_path": secondary,
            "output_dir": work / "pass",
            "comparison_id": "G2CMP-HOLDOUT01",
            "packet_id": "G2PKT-HOLDOUT01",
            "packet_sha256": "a" * 64,
            "sealed_selection_path": selection_path,
            "primary_run_receipt_path": primary_run,
            "secondary_run_receipt_path": secondary_run,
            "owner_authorization_path": owner,
            "source_commit": "e" * 40,
            "generated_at": GENERATED_AT,
        }
        assert compare_holdout_extractions(project_root, **common).threshold_passed is True
        wrong_bundle = deepcopy(bundle)
        wrong_bundle["owner_authorization"] = artifact(contract)
        wrong_bundle_path = work / "extractor-bundle-wrong-authority.json"
        wrong_bundle_path.write_text(
            json.dumps(wrong_bundle, sort_keys=True) + "\n", encoding="utf-8"
        )
        wrong_primary_run = write_receipt("primary_extractor", primary, wrong_bundle_path)
        common["primary_run_receipt_path"] = wrong_primary_run
        with pytest.raises(G2StructuralPreflightError, match="owner authorization binding differs"):
            compare_holdout_extractions(project_root, **common)
        primary_run = write_receipt("primary_extractor", primary)
        common["primary_run_receipt_path"] = primary_run
        primary_run_value = _read(primary_run)
        primary_run_value["session_id"] = "SESSION-TAMPERED"
        primary_run.write_text(
            json.dumps(primary_run_value, sort_keys=True) + "\n", encoding="utf-8"
        )
        with pytest.raises(G2StructuralPreflightError, match="role or session differs"):
            compare_holdout_extractions(project_root, **common)
        primary_run = write_receipt("primary_extractor", primary)
        common["primary_run_receipt_path"] = primary_run
        selection_value = _read(selection_path)
        selection_value["selection_policy"] = artifact(contract)
        selection_path.write_text(
            json.dumps(selection_value, sort_keys=True) + "\n", encoding="utf-8"
        )
        with pytest.raises(G2StructuralPreflightError, match="policy binding differs"):
            compare_holdout_extractions(project_root, **common)
        selection_path.write_text(json.dumps(selection, sort_keys=True) + "\n", encoding="utf-8")
        primary_run = write_receipt("primary_extractor", primary)
        secondary_run = write_receipt("secondary_extractor", secondary)
        common["primary_run_receipt_path"] = primary_run
        common["secondary_run_receipt_path"] = secondary_run
        secondary.write_text(
            json.dumps(
                [*rows[:-1], _holdout_row(23, domain_code="domestic_family_violence")],
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        secondary_run = write_receipt("secondary_extractor", secondary)
        common["secondary_run_receipt_path"] = secondary_run
        common["output_dir"] = work / "fail"
        assert compare_holdout_extractions(project_root, **common).threshold_passed is False
        incomplete = dict(common)
        tampered_selection = deepcopy(selection)
        tampered_selection["primary"].pop()
        selection_path.write_text(
            json.dumps(tampered_selection, sort_keys=True) + "\n", encoding="utf-8"
        )
        with pytest.raises(G2StructuralPreflightError):
            compare_holdout_extractions(project_root, **incomplete)


def test_access_receipt_verifier_enforces_role_matrix(project_root: Path) -> None:
    with tempfile.TemporaryDirectory(dir=project_root / "build") as temporary:
        work = Path(temporary)
        source = project_root / "config/g2_structural_selection_policy.json"
        relative = source.relative_to(project_root).as_posix()
        output_dir = work / "outputs"
        output_dir.mkdir()
        output = output_dir / "frame.json"
        output.write_text("{}\n", encoding="utf-8")

        def artifact(path: Path) -> dict[str, str]:
            return {
                "path": path.relative_to(project_root).as_posix(),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }

        bundles = project_root / "config/g2_structural_role_bundles.json"
        receipt = {
            "schema_version": "1.0",
            "receipt_id": "ACCESS-TEST001",
            "plan_id": "G2HOLDOUT-STRUCTURAL-PREFLIGHT-20260815-01",
            "role": "frame_freezer",
            "session_id": "SESSION-ACCESS001",
            "fresh_session_attested": True,
            "role_bundle": artifact(bundles),
            "authority": artifact(source),
            "network_mode": "none",
            "network_url_allowlist": [],
            "input_bundle": artifact(source),
            "path_allowlist": [relative],
            "artifact_class_denylist": [
                "source_bytes",
                "extraction_contract",
                "extraction_output",
                "comparison_output",
            ],
            "output_prefix": output_dir.relative_to(project_root).as_posix(),
            "access_events": [
                {
                    "artifact_class": "selection_policy",
                    "path": relative,
                    "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                }
            ],
            "denied_access_attempts": [],
            "violations": [],
            "started_at": GENERATED_AT,
            "ended_at": GENERATED_AT,
            "tool_bundle": artifact(source),
            "outputs": [{"artifact_class": "frozen_frame", **artifact(output)}],
        }
        path = work / "receipt.json"
        path.write_text(json.dumps(receipt, sort_keys=True) + "\n", encoding="utf-8")
        assert (
            verify_artifact_access_receipt(
                project_root,
                path,
                expected_role="frame_freezer",
                authority_path=source,
                input_bundle_path=source,
                tool_bundle_path=source,
            )
            == []
        )
        empty = deepcopy(receipt)
        empty["access_events"] = []
        path.write_text(json.dumps(empty, sort_keys=True) + "\n", encoding="utf-8")
        assert verify_artifact_access_receipt(
            project_root,
            path,
            expected_role="frame_freezer",
            authority_path=source,
            input_bundle_path=source,
            tool_bundle_path=source,
        )
        receipt["authority"] = artifact(bundles)
        path.write_text(json.dumps(receipt, sort_keys=True) + "\n", encoding="utf-8")
        assert (
            "authority binding differs"
            in verify_artifact_access_receipt(
                project_root,
                path,
                expected_role="frame_freezer",
                authority_path=source,
                input_bundle_path=source,
                tool_bundle_path=source,
            )[0]
        )
        receipt["authority"] = artifact(source)
        receipt["input_bundle"] = artifact(bundles)
        path.write_text(json.dumps(receipt, sort_keys=True) + "\n", encoding="utf-8")
        assert (
            "input_bundle binding differs"
            in verify_artifact_access_receipt(
                project_root,
                path,
                expected_role="frame_freezer",
                authority_path=source,
                input_bundle_path=source,
                tool_bundle_path=source,
            )[0]
        )
        receipt["input_bundle"] = artifact(source)
        receipt["access_events"][0]["artifact_class"] = "source_bytes"
        path.write_text(json.dumps(receipt, sort_keys=True) + "\n", encoding="utf-8")
        assert (
            "forbidden class"
            in verify_artifact_access_receipt(
                project_root,
                path,
                expected_role="frame_freezer",
                authority_path=source,
                input_bundle_path=source,
                tool_bundle_path=source,
            )[0]
        )

        resolution_manifest = (
            project_root / "data/methods/g2/G2HOLDOUT-STRUCTURAL-PREFLIGHT-20260815-01/design/"
            "proposed-url-resolution-manifest.json"
        )
        expected_urls = list(
            dict.fromkeys(row["landing_page_url"] for row in _read(resolution_manifest)["entries"])
        )
        resolver_output = output_dir / "resolved.json"
        resolver_output.write_text("{}\n", encoding="utf-8")
        resolver = deepcopy(receipt)
        resolver.update(
            {
                "role": "metadata_url_resolver",
                "authority": artifact(source),
                "network_mode": "exact_allowlist_only",
                "network_url_allowlist": expected_urls,
                "input_bundle": artifact(resolution_manifest),
                "path_allowlist": [resolution_manifest.relative_to(project_root).as_posix()],
                "artifact_class_denylist": [
                    "source_bytes",
                    "extraction_contract",
                    "prior_evidence",
                    "extraction_output",
                    "comparison_output",
                ],
                "access_events": [
                    {"artifact_class": "url_resolution_manifest", **artifact(resolution_manifest)}
                ],
                "outputs": [
                    {"artifact_class": "resolved_url_metadata_receipt", **artifact(resolver_output)}
                ],
            }
        )
        path.write_text(json.dumps(resolver, sort_keys=True) + "\n", encoding="utf-8")
        assert (
            verify_artifact_access_receipt(
                project_root,
                path,
                expected_role="metadata_url_resolver",
                authority_path=source,
                input_bundle_path=resolution_manifest,
                tool_bundle_path=source,
            )
            == []
        )
        resolver["network_url_allowlist"] = [*expected_urls[:-1], "https://example.org/"]
        path.write_text(json.dumps(resolver, sort_keys=True) + "\n", encoding="utf-8")
        assert (
            "network URL allowlist differs"
            in verify_artifact_access_receipt(
                project_root,
                path,
                expected_role="metadata_url_resolver",
                authority_path=source,
                input_bundle_path=resolution_manifest,
                tool_bundle_path=source,
            )[0]
        )
