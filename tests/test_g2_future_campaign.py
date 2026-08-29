from __future__ import annotations

import json
from pathlib import Path

import pytest

from gfjd.g2_future_campaign import (
    CONTROL_ROOT,
    ROLES,
    G2FutureCampaignError,
    build_selection_receipt,
    verify_candidate_registry,
    verify_pre_source_interlock,
    verify_query_manifest,
    verify_selection_receipt,
)
from gfjd.g2_future_exposure import build_exposure_snapshot, canonical_request_identity
from gfjd.io import sha256_file, write_json


def _artifact(root: Path, path: Path) -> dict[str, str]:
    return {"path": path.relative_to(root).as_posix(), "sha256": sha256_file(path)}


def _setup(project_root: Path, root: Path) -> None:
    destination = root / CONTROL_ROOT
    destination.mkdir(parents=True)
    for name in (
        "query-manifest.schema.json",
        "candidate-registry.schema.json",
        "selection-receipt.schema.json",
        "pre-source-interlock.schema.json",
    ):
        destination.joinpath(name).write_bytes(
            project_root.joinpath(CONTROL_ROOT, name).read_bytes()
        )


def _query_manifest() -> dict[str, object]:
    queries = [
        {
            "ordinal": index,
            "query_id": f"G2FCQ-FICTIONAL_{index:02d}",
            "route_stratum": stratum,
            "query_text": f"fictional official {stratum} edition",
        }
        for index, stratum in enumerate(
            ("api_or_json", "html_or_dashboard", "spreadsheet", "pdf"), 1
        )
    ]
    return {
        "schema_version": "1.0",
        "campaign_id": "G2PROSPECTIVE-CALIBRATION-20260829-01",
        "manifest_id": "G2FC-QUERY-FICTIONAL_01",
        "status": "frozen_before_candidate_registration",
        "ordering": "ascending_query_ordinal_zero_retries",
        "call_policy": {
            "one_query_per_call": True,
            "zero_retries": True,
            "maximum_calls": 4,
            "maximum_results_per_query": 5,
        },
        "queries": queries,
        "authority_boundary": {
            "candidate_registration": True,
            "result_url_opening_during_registration": False,
            "source_access_before_interlock": False,
            "rights_clearance": False,
            "publication": False,
            "release": False,
            "g2_passage": False,
        },
    }


def _candidate(index: int, stratum: str) -> dict[str, object]:
    jurisdiction = ("FIC-A", "FIC-B", "FIC-C", "FIC-A")[index - 1]
    return {
        "result_rank": 1,
        "candidate_id": f"G2CAND-FICTIONAL_{index:02d}",
        "edition_id": f"FIC-EDITION-{index}",
        "source_series_id": f"FIC-SERIES-{index}",
        "jurisdiction_id": jurisdiction,
        "route_stratum": stratum,
        "canonical_url": f"https://example{index}.invalid/edition-{index}",
        "edition_aliases": [f"Fictional edition {index}"],
        "request_method": "GET",
        "request_body_sha256": None,
        "request_identity": canonical_request_identity(
            method="GET", url=f"https://example{index}.invalid/edition-{index}"
        ),
        "source_sha256": None,
        "official_publisher": True,
        "exact_edition_identity": True,
        "source_content_accessed": False,
        "prior_exposure_overlap": False,
        "eligible_for_selection": True,
        "rejection_reasons": [],
    }


def _campaign_files(project_root: Path, root: Path) -> tuple[Path, Path, Path]:
    _setup(project_root, root)
    query_path = root / "query.json"
    write_json(query_path, _query_manifest())
    exposure_path = root / "exposure.json"
    write_json(exposure_path, {"observations": []})
    exposure_input_path = root / "exposure-input.json"
    exposure_input = {
        "schema_version": "1.0",
        "lineage_id": "G2PROSPECTIVE-CALIBRATION-20260829-01",
        "inputs": [{**_artifact(root, exposure_path), "kind": "registrar_observations"}],
    }
    write_json(exposure_input_path, exposure_input)
    exposure_snapshot_path = root / "exposure-snapshot.json"
    write_json(exposure_snapshot_path, build_exposure_snapshot(root, exposure_input))
    manifest = _query_manifest()
    events = [
        {
            "ordinal": query["ordinal"],
            "query_id": query["query_id"],
            "route_stratum": query["route_stratum"],
            "status": "completed",
            "provider_call_id": f"fictional-call-{query['ordinal']}",
            "observed_results": [_candidate(int(query["ordinal"]), str(query["route_stratum"]))],
        }
        for query in manifest["queries"]  # type: ignore[index]
    ]
    registry = {
        "schema_version": "1.0",
        "campaign_id": "G2PROSPECTIVE-CALIBRATION-20260829-01",
        "registry_id": "G2FC-REGISTRY-FICTIONAL_01",
        "query_manifest": _artifact(root, query_path),
        "exposure_input_manifest": _artifact(root, exposure_input_path),
        "exposure_snapshot": _artifact(root, exposure_snapshot_path),
        "execution": {
            "calls_attempted": 4,
            "retries": 0,
            "query_order_preserved": True,
            "all_observed_results_recorded": True,
            "result_urls_requested": False,
        },
        "events": events,
        "authority_boundary": {
            "source_access": False,
            "extraction": False,
            "rights_clearance": False,
            "publication": False,
            "release": False,
            "g2_passage": False,
        },
    }
    registry_path = root / "registry.json"
    write_json(registry_path, registry)
    return query_path, exposure_path, registry_path


def test_query_and_registry_verify(project_root: Path, tmp_path: Path) -> None:
    query, _, registry = _campaign_files(project_root, tmp_path)
    assert verify_query_manifest(tmp_path, query) == []
    assert verify_candidate_registry(tmp_path, registry) == []


def test_query_manifest_rejects_order_and_budget_drift(project_root: Path, tmp_path: Path) -> None:
    query, _, _ = _campaign_files(project_root, tmp_path)
    value = json.loads(query.read_text())
    value["queries"][0], value["queries"][1] = value["queries"][1], value["queries"][0]
    write_json(query, value)
    assert "ordinals" in verify_query_manifest(tmp_path, query)[0]
    value = _query_manifest()
    value["call_policy"]["maximum_calls"] = 5  # type: ignore[index]
    write_json(query, value)
    assert "maximum_calls" in verify_query_manifest(tmp_path, query)[0]


def test_registry_rejects_missing_reordered_or_failed_call(
    project_root: Path, tmp_path: Path
) -> None:
    _, _, registry = _campaign_files(project_root, tmp_path)
    value = json.loads(registry.read_text())
    value["events"][0], value["events"][1] = value["events"][1], value["events"][0]
    write_json(registry, value)
    assert "frozen query order" in verify_candidate_registry(tmp_path, registry)[0]
    _, _, registry = _campaign_files(project_root, tmp_path / "again")
    value = json.loads(registry.read_text())
    value["events"][0]["status"] = "failed"
    write_json(registry, value)
    assert "frozen query order" in verify_candidate_registry(tmp_path / "again", registry)[0]


def test_registry_recomputes_prior_exposure(project_root: Path, tmp_path: Path) -> None:
    _, exposure, registry = _campaign_files(project_root, tmp_path)
    write_json(exposure, {"observations": [{"url": "https://example1.invalid/edition-1"}]})
    value = json.loads(registry.read_text())
    input_path = tmp_path / value["exposure_input_manifest"]["path"]
    input_value = json.loads(input_path.read_text())
    input_value["inputs"][0]["sha256"] = sha256_file(exposure)
    write_json(input_path, input_value)
    snapshot_path = tmp_path / value["exposure_snapshot"]["path"]
    write_json(snapshot_path, build_exposure_snapshot(tmp_path, input_value))
    value["exposure_input_manifest"] = _artifact(tmp_path, input_path)
    value["exposure_snapshot"] = _artifact(tmp_path, snapshot_path)
    write_json(registry, value)
    assert "prior-exposure claim differs" in verify_candidate_registry(tmp_path, registry)[0]


def test_registry_rejects_noncanonical_url(project_root: Path, tmp_path: Path) -> None:
    _, _, registry = _campaign_files(project_root, tmp_path)
    value = json.loads(registry.read_text())
    value["events"][0]["observed_results"][0]["canonical_url"] = (
        "https://EXAMPLE1.invalid/edition-1#fragment"
    )
    write_json(registry, value)
    assert "not canonical" in verify_candidate_registry(tmp_path, registry)[0]


def test_selection_is_deterministic_and_meets_scope(project_root: Path, tmp_path: Path) -> None:
    _, _, registry = _campaign_files(project_root, tmp_path)
    first = build_selection_receipt(
        tmp_path,
        registry_path=registry,
        selection_id="G2FC-SELECTION-FICTIONAL_01",
        generated_at="2026-08-29T00:00:00Z",
    )
    second = build_selection_receipt(
        tmp_path,
        registry_path=registry,
        selection_id="G2FC-SELECTION-FICTIONAL_01",
        generated_at="2026-08-29T00:00:00Z",
    )
    assert first == second
    assert first["status"] == "selected_pre_source_access"
    assert len(first["selected"]) == 4
    assert {row["route_stratum"] for row in first["selected"]} == {
        "api_or_json",
        "html_or_dashboard",
        "spreadsheet",
        "pdf",
    }


@pytest.mark.parametrize("duplicate_field", ["edition_id", "source_series_id", "canonical_url"])
def test_selection_stops_on_cross_stratum_identity_reuse(
    project_root: Path, tmp_path: Path, duplicate_field: str
) -> None:
    _, _, registry = _campaign_files(project_root, tmp_path)
    value = json.loads(registry.read_text())
    value["events"][1]["observed_results"][0][duplicate_field] = value["events"][0][
        "observed_results"
    ][0][duplicate_field]
    if duplicate_field == "canonical_url":
        value["events"][1]["observed_results"][0]["request_identity"] = value["events"][0][
            "observed_results"
        ][0]["request_identity"]
    write_json(registry, value)
    receipt = build_selection_receipt(
        tmp_path,
        registry_path=registry,
        selection_id="G2FC-SELECTION-FICTIONAL_02",
        generated_at="2026-08-29T00:00:00Z",
    )
    assert receipt["status"] == "terminal_stop_insufficient_scope"
    assert receipt["selected"] == []


def test_selection_stops_when_jurisdiction_cap_or_minimum_fails(
    project_root: Path, tmp_path: Path
) -> None:
    _, _, registry = _campaign_files(project_root, tmp_path)
    value = json.loads(registry.read_text())
    for event in value["events"]:
        event["observed_results"][0]["jurisdiction_id"] = "FIC-A"
    write_json(registry, value)
    receipt = build_selection_receipt(
        tmp_path,
        registry_path=registry,
        selection_id="G2FC-SELECTION-FICTIONAL_03",
        generated_at="2026-08-29T00:00:00Z",
    )
    assert receipt["status"] == "terminal_stop_insufficient_scope"


def test_selection_verifier_rejects_result_repair(project_root: Path, tmp_path: Path) -> None:
    _, _, registry = _campaign_files(project_root, tmp_path)
    receipt = build_selection_receipt(
        tmp_path,
        registry_path=registry,
        selection_id="G2FC-SELECTION-FICTIONAL_04",
        generated_at="2026-08-29T00:00:00Z",
    )
    receipt["selected"][0]["candidate_id"] = "G2CAND-REPAIRED"  # type: ignore[index]
    path = tmp_path / "selection.json"
    write_json(path, receipt)
    assert "does not reproduce" in verify_selection_receipt(tmp_path, path)[0]


def _interlock(project_root: Path, root: Path) -> Path:
    query, _, registry = _campaign_files(project_root, root)
    selection = build_selection_receipt(
        root,
        registry_path=registry,
        selection_id="G2FC-SELECTION-FICTIONAL_05",
        generated_at="2026-08-29T00:00:00Z",
    )
    selection_path = root / "selection.json"
    write_json(selection_path, selection)
    preparation = root / "preparation.json"
    write_json(
        preparation,
        {
            "bundle_id": "G2PROSPECTIVE-CALIBRATION-PREPARATION-20260829-01",
            "status": "prepared_not_frozen_not_authorized",
            "candidate_state": {"candidate_count": 0},
            "bindings": [_artifact(root, query)],
            "authorization": {
                "candidate_selection": False,
                "network_access": False,
                "source_access": False,
                "extraction": False,
                "comparison": False,
                "rights_clearance": False,
                "publication": False,
                "release": False,
                "g2_passage": False,
                "separate_execution_decision_required": True,
            },
        },
    )
    decision_packet = root / "decision-packet.md"
    authorization_record = root / "authorization-record.md"
    preparation_manifest = root / "PREPARATION_MANIFEST.sha256"
    decision_packet.write_text("fictional decision packet\n", encoding="utf-8")
    authorization_record.write_text("fictional authorization record\n", encoding="utf-8")
    preparation_manifest.write_text("fictional preparation manifest\n", encoding="utf-8")
    owner = root / "owner.json"
    write_json(
        owner,
        {
            "decision": "authorize_option_a_staged_future_calibration_campaign",
            "decision_packet": _artifact(root, decision_packet),
            "owner_authorization_record": _artifact(root, authorization_record),
            "preparation_bundle": _artifact(root, preparation),
            "preparation_manifest": _artifact(root, preparation_manifest),
            "authorization": {
                "candidate_registration_and_selection": True,
                "bounded_network_and_source_access": True,
                "controlled_aggregate_only_processing": True,
                "fresh_artifact_isolated_extractors": 2,
                "network_disabled_exact_comparator": 1,
                "role_separated_non_independent_advisory_review": 1,
            },
            "pre_source_access_interlock": {
                "required": True,
                "satisfied_at_decision_time": False,
            },
            "non_authorizations": {
                "rights_clearance": False,
                "gold_promotion": False,
                "g2_c04_acceptance": False,
                "g2_c07_acceptance": False,
                "m06_promotion": False,
                "g2_passage": False,
                "publication": False,
                "release": False,
            },
        },
    )
    role_descriptors = []
    selected_urls = sorted(row["canonical_url"] for row in selection["selected"])
    for role in ROLES:
        allowlist = {
            "schema_version": "1.0",
            "campaign_id": "G2PROSPECTIVE-CALIBRATION-20260829-01",
            "role": role,
            "network_mode": "exact_allowlist_only" if role == "orchestrator" else "none",
            "network_url_allowlist": selected_urls if role == "orchestrator" else [],
            "input_artifact_classes": ["frozen_campaign_contract"],
            "output_prefix": f"build/g2-future/{role}",
            "prohibited_artifact_classes": ["prior_extraction_output"],
        }
        role_path = root / f"{role}.json"
        write_json(role_path, allowlist)
        role_descriptors.append({"role": role, "artifact": _artifact(root, role_path)})
    receipt = {
        "schema_version": "1.0",
        "campaign_id": "G2PROSPECTIVE-CALIBRATION-20260829-01",
        "receipt_id": "G2FC-INTERLOCK-FICTIONAL_01",
        "owner_authorization": _artifact(root, owner),
        "preparation_bundle": _artifact(root, preparation),
        "query_manifest": _artifact(root, query),
        "candidate_registry": _artifact(root, registry),
        "exposure_input_manifest": selection["exposure_input_manifest"],
        "exposure_snapshot": selection["exposure_snapshot"],
        "selection_receipt": _artifact(root, selection_path),
        "role_allowlists": role_descriptors,
        "checks": {
            "bindings_verified": True,
            "query_contract_verified": True,
            "all_results_recorded": True,
            "prior_exposure_zero": True,
            "selection_reproduced": True,
            "strata_and_caps_verified": True,
            "role_allowlists_verified": True,
            "artifact_digests_verified": True,
        },
        "status": "pass_pre_source_access",
        "generated_at": "2026-08-29T00:01:00Z",
        "authority_boundary": {
            "bounded_source_access": True,
            "aggregate_only_processing": True,
            "rights_clearance": False,
            "gold_promotion": False,
            "g2_c04_acceptance": False,
            "g2_c07_acceptance": False,
            "m06_promotion": False,
            "g2_passage": False,
            "publication": False,
            "release": False,
        },
    }
    path = root / "interlock.json"
    write_json(path, receipt)
    return path


def test_pre_source_interlock_recomputes_all_controls(project_root: Path, tmp_path: Path) -> None:
    path = _interlock(project_root, tmp_path)
    assert verify_pre_source_interlock(tmp_path, path) == []


def test_interlock_rejects_digest_and_network_role_drift(
    project_root: Path, tmp_path: Path
) -> None:
    path = _interlock(project_root, tmp_path)
    value = json.loads(path.read_text())
    value["owner_authorization"]["sha256"] = "0" * 64
    write_json(path, value)
    assert "digest mismatch" in verify_pre_source_interlock(tmp_path, path)[0]

    other = tmp_path / "other"
    path = _interlock(project_root, other)
    value = json.loads(path.read_text())
    descriptor = next(item for item in value["role_allowlists"] if item["role"] == "extractor_a")
    allowlist_path = other / descriptor["artifact"]["path"]
    allowlist = json.loads(allowlist_path.read_text())
    allowlist["network_mode"] = "exact_allowlist_only"
    allowlist["network_url_allowlist"] = ["https://example1.invalid/edition-1"]
    write_json(allowlist_path, allowlist)
    descriptor["artifact"] = _artifact(other, allowlist_path)
    write_json(path, value)
    assert "network-disabled" in verify_pre_source_interlock(other, path)[0]


def test_interlock_cannot_pass_a_terminal_selection(project_root: Path, tmp_path: Path) -> None:
    path = _interlock(project_root, tmp_path)
    receipt = json.loads(path.read_text())
    registry = tmp_path / receipt["candidate_registry"]["path"]
    value = json.loads(registry.read_text())
    value["events"][-1]["observed_results"] = []
    write_json(registry, value)
    selection = build_selection_receipt(
        tmp_path,
        registry_path=registry,
        selection_id="G2FC-SELECTION-FICTIONAL_06",
        generated_at="2026-08-29T00:00:00Z",
    )
    assert selection["status"] == "terminal_stop_insufficient_scope"
    selection_path = tmp_path / "selection.json"
    write_json(selection_path, selection)
    # A terminal selection cannot be smuggled into a syntactically passing receipt.
    receipt["candidate_registry"] = _artifact(tmp_path, registry)
    updated_registry = json.loads(registry.read_text())
    receipt["exposure_input_manifest"] = updated_registry["exposure_input_manifest"]
    receipt["exposure_snapshot"] = updated_registry["exposure_snapshot"]
    receipt["selection_receipt"] = _artifact(tmp_path, selection_path)
    write_json(path, receipt)
    assert "complete selection" in verify_pre_source_interlock(tmp_path, path)[0]


def test_build_selection_rejects_registry_digest_drift(project_root: Path, tmp_path: Path) -> None:
    _, _, registry = _campaign_files(project_root, tmp_path)
    value = json.loads(registry.read_text())
    value["query_manifest"]["sha256"] = "0" * 64
    write_json(registry, value)
    with pytest.raises(G2FutureCampaignError, match="digest mismatch"):
        build_selection_receipt(
            tmp_path,
            registry_path=registry,
            selection_id="G2FC-SELECTION-FICTIONAL_07",
            generated_at="2026-08-29T00:00:00Z",
        )


def test_repository_query_manifest_and_execution_contract_are_frozen(
    project_root: Path,
) -> None:
    query = project_root / CONTROL_ROOT / "query-manifest.json"
    assert verify_query_manifest(project_root, query) == []
    contract = json.loads((project_root / CONTROL_ROOT / "execution-contract.json").read_text())
    assert contract["status"] == "prospectively_frozen_before_formal_candidate_registration"
    for descriptor in [contract["owner_authorization"], *contract["bindings"]]:
        path = project_root / descriptor["path"]
        assert sha256_file(path) == descriptor["sha256"]
