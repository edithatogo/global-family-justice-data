from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

from gfjd.medallion import load_layer_contract, record_sha256, verify_layer_record, verify_promotion


def _contract(project_root: Path) -> dict[str, Any]:
    return load_layer_contract(project_root / "config/medallion_layers.json")


def _b0() -> dict[str, Any]:
    return {
        "contract_version": "gfjd-medallion-layers-v1",
        "object_id": "OBJ-001",
        "layer": "b0",
        "previous_layer": None,
        "lifecycle_state": "active",
        "evidence": {
            "source_edition_id": "ED-001",
            "content_sha256": "a" * 64,
            "content_blake3": "b" * 64,
            "size_bytes": 10,
            "media_type": "application/pdf",
            "capture_receipt_sha256": "c" * 64,
            "safety_receipt_sha256": "d" * 64,
            "custody_receipt_sha256": "e" * 64,
        },
    }


def _next(previous: dict[str, Any], layer: str, required: list[str]) -> dict[str, Any]:
    evidence: dict[str, Any] = {
        field: ("f" * 64 if field.endswith("_sha256") else f"evidence:{field}")
        for field in required
    }
    evidence["predecessor_receipt_sha256"] = record_sha256(previous)
    if "source_labels_preserved" in evidence:
        evidence["source_labels_preserved"] = True
    return {
        "contract_version": "gfjd-medallion-layers-v1",
        "object_id": previous["object_id"],
        "layer": layer,
        "previous_layer": previous["layer"],
        "lifecycle_state": "active",
        "evidence": evidence,
    }


def test_all_layers_require_independent_evidence(project_root: Path) -> None:
    contract = _contract(project_root)
    previous = _b0()
    assert verify_layer_record(previous, contract) == []
    for layer in contract["layers"][1:]:
        candidate = _next(previous, layer["id"], layer["required_evidence"])
        assert verify_promotion(previous, candidate, contract) == []
        previous = candidate


def test_later_layer_cannot_substitute_for_missing_earlier_evidence(project_root: Path) -> None:
    contract = _contract(project_root)
    gold = _next(_b0(), "gold", contract["layers"][3]["required_evidence"])
    gold["previous_layer"] = "b0"
    assert "previous_layer must be 'silver'" in verify_layer_record(gold, contract)


def test_quarantine_is_visible_but_cannot_promote(project_root: Path) -> None:
    contract = _contract(project_root)
    quarantined = _b0()
    quarantined["lifecycle_state"] = "quarantined"
    quarantined["quarantine"] = {
        "reason_codes": ["unclear_rights"],
        "disposition_reference": "DEC-001",
    }
    b1 = _next(quarantined, "b1", contract["layers"][1]["required_evidence"])
    assert verify_layer_record(quarantined, contract) == []
    assert "only active records may be promoted" in verify_promotion(quarantined, b1, contract)


def test_promotion_rejects_digest_drift_and_object_change(project_root: Path) -> None:
    contract = _contract(project_root)
    b0 = _b0()
    b1 = _next(b0, "b1", contract["layers"][1]["required_evidence"])
    b1["object_id"] = "OBJ-OTHER"
    b1["evidence"]["predecessor_receipt_sha256"] = "f" * 64
    errors = verify_promotion(b0, b1, contract)
    assert "promotion cannot change object_id" in errors
    assert "candidate predecessor receipt digest does not match" in errors


def test_each_layer_fails_when_own_evidence_is_missing(project_root: Path) -> None:
    contract = _contract(project_root)
    previous = _b0()
    for layer in contract["layers"][1:]:
        candidate = _next(previous, layer["id"], layer["required_evidence"])
        missing = layer["required_evidence"][-1]
        del candidate["evidence"][missing]
        assert f"{layer['id']} evidence is missing {missing}" in verify_layer_record(
            candidate, contract
        )
        previous = _next(previous, layer["id"], layer["required_evidence"])


def test_quarantine_requires_reason_and_disposition(project_root: Path) -> None:
    contract = _contract(project_root)
    record = copy.deepcopy(_b0())
    record["lifecycle_state"] = "quarantined"
    record["quarantine"] = {"reason_codes": [], "disposition_reference": ""}
    errors = verify_layer_record(record, contract)
    assert "quarantine reason_codes must be a non-empty array" in errors
    assert "quarantine disposition_reference is required" in errors


def test_b0_rejects_malformed_integrity_evidence(project_root: Path) -> None:
    contract = _contract(project_root)
    record = _b0()
    record["evidence"]["content_sha256"] = "not-a-digest"
    record["evidence"]["size_bytes"] = 0
    record["evidence"]["media_type"] = "unknown"
    errors = verify_layer_record(record, contract)
    assert "content_sha256 must be a lowercase SHA-256 digest" in errors
    assert "size_bytes must be a positive integer" in errors
    assert "media_type must be an explicit type/subtype" in errors
