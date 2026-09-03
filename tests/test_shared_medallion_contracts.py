"""Portable cross-repository medallion contract conformance."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from gfjd.shared_medallion_contracts import (
    GFJD_LAYER_PROJECTION,
    MAPPING_PROFILE_SHA256,
    SHARED_CONTRACTS,
    SharedMedallionError,
    _validate_v4_layers,
    _validate_v4_lifecycle,
    _validate_v4_recovery,
    build_compatibility_report,
    project_gfjd_layer,
    validate_shared_document,
    verify_compatibility_report,
    verify_contract_assets,
)

ROOT = Path(__file__).resolve().parents[1]


def _fixture(version: str, name: str) -> bytes:
    return (ROOT / "contracts" / "medallion" / version / "fixtures" / name).read_bytes()


def test_all_shared_contract_assets_are_pinned_and_v4_copy_is_identical() -> None:
    report = verify_contract_assets()
    assert report["status"] == "verified"
    assert report["versions"] == ["v1", "v2", "v3", "v4"]
    assert report["schema_sha256"] == {
        version: item["sha256"] for version, item in SHARED_CONTRACTS.items()
    }
    assert report["mapping_profile_sha256"] == MAPPING_PROFILE_SHA256
    assert report["repository_copy_verified"] is True
    assert (ROOT / "contracts/medallion/v4/federation.schema.json").read_bytes() == (
        ROOT / "src/gfjd/federation_specs/partner-gma-federation.schema.json"
    ).read_bytes()


@pytest.mark.parametrize(
    ("version", "fixture"),
    [
        ("v1", "valid.json"),
        ("v2", "valid-field-lineage.json"),
        ("v3", "valid-backfill-replay.json"),
        ("v4", "valid.json"),
    ],
)
def test_portable_positive_canaries_pass_schema_and_semantics(version: str, fixture: str) -> None:
    report = validate_shared_document(version, _fixture(version, fixture))
    assert report["status"] == "conformant"
    assert report["schema_sha256"] == SHARED_CONTRACTS[version]["sha256"]
    assert report["authority"] == {
        "gate_acceptance": False,
        "gold_promotion": False,
        "publication": False,
        "release": False,
        "rights_clearance": False,
    }


@pytest.mark.parametrize(
    ("version", "fixture"),
    [
        ("v1", "invalid-missing-gate.json"),
        ("v2", "invalid-unversioned-code.json"),
        ("v3", "invalid-overwrite-policy.json"),
        ("v4", "invalid-mismatched-digest.json"),
    ],
)
def test_portable_negative_canaries_fail_closed(version: str, fixture: str) -> None:
    with pytest.raises(SharedMedallionError):
        validate_shared_document(version, _fixture(version, fixture))


def test_v4_semantic_identity_mismatch_fails_after_schema_validation() -> None:
    document = json.loads(_fixture("v4", "valid.json"))
    document["verification"]["sha256"] = "f" * 64
    with pytest.raises(SharedMedallionError):
        validate_shared_document("v4", json.dumps(document).encode())


def test_v4_declared_schema_digest_must_match_the_pinned_contract() -> None:
    document = json.loads(_fixture("v4", "valid.json"))
    document["authority"]["schema_sha256"] = "f" * 64
    with pytest.raises(SharedMedallionError, match="declared schema digest"):
        validate_shared_document("v4", json.dumps(document).encode())


def test_v4_rights_identity_must_match_the_bound_location() -> None:
    document = json.loads(_fixture("v4", "valid.json"))
    document["rights"]["subject_sha256"] = "f" * 64
    with pytest.raises(SharedMedallionError, match="authorization identity"):
        validate_shared_document("v4", json.dumps(document).encode())


@pytest.mark.parametrize("change", ["status", "decision_id", "scope"])
def test_v1_approved_promotion_requires_identical_approved_artifact_rights(
    change: str,
) -> None:
    document = json.loads(_fixture("v1", "valid.json"))
    rights = document["artifacts"][0]["rights_decision"]
    if change == "status":
        rights["status"] = "pending"
    else:
        rights[change] += "-different"
    with pytest.raises(SharedMedallionError, match="artifact rights decision"):
        validate_shared_document("v1", json.dumps(document).encode())


@pytest.mark.parametrize(
    "change",
    ["b0", "stratum", "raw", "projection", "derived", "index", "cohort"],
)
def test_v4_layer_semantic_mutations_fail_closed(change: str) -> None:
    document = json.loads(_fixture("v4", "valid.json"))
    source = document["source"]
    if change == "b0":
        source.update(bronze_stratum="B0", representation="raw")
    elif change == "stratum":
        source.update(layer="silver", bronze_stratum="B2")
    elif change == "raw":
        source.update(layer="silver", bronze_stratum=None, representation="raw")
    elif change == "projection":
        source.update(representation="projection")
    elif change == "derived":
        source.update(layer="silver", bronze_stratum=None, representation="projection")
        document["lineage"]["inputs"] = [{"sha256": "a" * 64}]
    elif change == "index":
        source.update(bronze_stratum="B2", representation="index")
    else:
        source["comparison_cohort"] = "official"
    with pytest.raises(SharedMedallionError):
        _validate_v4_layers(document)


@pytest.mark.parametrize("change", ["producer", "time", "cache_time", "cleanup"])
def test_v4_lifecycle_semantic_mutations_fail_closed(change: str) -> None:
    document = json.loads(_fixture("v4", "valid.json"))
    if change == "producer":
        document["publication"]["run"] = "https://github.com/other/repo/actions/runs/1"
    elif change == "time":
        document["source"]["retrieved_at"] = "2026-08-30T00:06:00Z"
    elif change == "cache_time":
        document["cache"]["expires_at"] = document["cache"]["created_at"]
    else:
        document["cache"]["cleanup_receipt"] = None
    with pytest.raises(SharedMedallionError):
        _validate_v4_lifecycle(document)


@pytest.mark.parametrize("change", ["incomplete", "false_independence", "role_mismatch"])
def test_v4_recovery_semantic_mutations_fail_closed(change: str) -> None:
    recovery = json.loads(_fixture("v4", "valid.json"))["recovery"]
    if change == "incomplete":
        recovery.update(role="independent_replica", independent=True)
    elif change == "false_independence":
        recovery.update(role="compatibility_replica", independent=True)
    else:
        recovery["independent"] = True
    with pytest.raises(SharedMedallionError):
        _validate_v4_recovery(recovery)


@pytest.mark.parametrize("raw", [b"", b"[]", "not-bytes"])
def test_shared_document_input_boundaries_fail_closed(raw: object) -> None:
    with pytest.raises(SharedMedallionError):
        validate_shared_document("v1", raw)  # type: ignore[arg-type]


def test_gfjd_native_layers_are_projected_without_direct_aliasing() -> None:
    assert set(GFJD_LAYER_PROJECTION) == {"B0", "B1", "Silver", "Gold", "Platinum"}
    assert project_gfjd_layer("B0") == {
        "native_layer": "B0",
        "shared_layer": "bronze_b2",
        "semantic_role": "immutable_raw_evidence",
        "direct_alias": False,
        "v1_promotion_boundary": True,
    }
    assert project_gfjd_layer("B1")["shared_layer"] == "silver"
    assert project_gfjd_layer("Silver")["shared_layer"] == "silver"
    assert (
        project_gfjd_layer("B1")["semantic_role"] != project_gfjd_layer("Silver")["semantic_role"]
    )
    assert project_gfjd_layer("Silver")["v1_promotion_boundary"] is False
    with pytest.raises(SharedMedallionError):
        project_gfjd_layer("Bronze")


def test_validator_has_no_network_path(monkeypatch: pytest.MonkeyPatch) -> None:
    import socket
    import urllib.request

    def forbidden(*args: object, **kwargs: object) -> None:
        raise AssertionError("network requested")

    monkeypatch.setattr(socket, "socket", forbidden)
    monkeypatch.setattr(urllib.request, "urlopen", forbidden)
    assert validate_shared_document("v1", _fixture("v1", "valid.json"))["status"] == "conformant"


def test_mutated_document_cannot_reuse_a_valid_report() -> None:
    raw = _fixture("v2", "valid-field-lineage.json")
    document = json.loads(raw)
    changed = copy.deepcopy(document)
    changed["records"][0]["output_field"] += "_changed"
    original = validate_shared_document("v2", raw)
    mutated = validate_shared_document("v2", json.dumps(changed).encode())
    assert original["document_sha256"] != mutated["document_sha256"]


def test_compatibility_report_is_deterministic_recomputed_and_non_authoritative() -> None:
    report = build_compatibility_report()
    assert report == build_compatibility_report()
    assert report["status"] == "repository_compatibility_verified"
    assert report["upstream_contract_revisions"] == {
        "archive-govt-nz": "dcc8f37f5642fc6b4337c49bd482b126325e6b6c",
        "global-medicines-atlas": "0190183f6b313ad21746c5b15b7cf4bd7153085c",
    }
    assert all(item["rejected"] for item in report["negative_canaries"])
    assert not any(report["authority"].values())
    verify_compatibility_report(report)


def test_compatibility_report_cannot_be_forged() -> None:
    report = build_compatibility_report()
    report["authority"]["publication"] = True
    with pytest.raises(SharedMedallionError):
        verify_compatibility_report(report)


def test_retained_compatibility_report_is_current_and_canonical() -> None:
    path = ROOT / "data/federation/shared-medallion-contracts-2026-09-03/report.json"
    raw = path.read_bytes()
    report = json.loads(raw)
    verify_compatibility_report(report)
    assert raw == (json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()


@pytest.mark.parametrize("version", ["", "1", "v5", "../../v1"])
def test_unknown_or_unsafe_contract_version_is_rejected(version: str) -> None:
    with pytest.raises(SharedMedallionError):
        validate_shared_document(version, b"{}")
