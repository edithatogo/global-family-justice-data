"""Fictional declared coverage; references alone never establish qualification."""

import copy
from pathlib import Path

import pytest

from gfjd.medallion import record_sha256
from gfjd.medallion_qualification_inputs import (
    LAYERS,
    VERSION,
    QualificationInputError,
    bind_layer_records,
    canonical,
    parse,
    parse_scope,
    sha,
    verify_bindings,
)


def scope() -> dict:
    return {
        "contract_version": VERSION,
        "objects": [
            {
                "object_id": "FICTIONAL-OBJECT",
                "edition_id": "FICTIONAL-EDITION",
                "layers": {
                    layer: {"state": "active", "reason_codes": [], "disposition_reference": None}
                    for layer in LAYERS
                },
            }
        ],
    }


def wrapper() -> dict:
    return {
        "object_id": "FICTIONAL-OBJECT",
        "edition_id": "FICTIONAL-EDITION",
        "record": {
            "contract_version": "gfjd-medallion-layers-v1",
            "object_id": "FICTIONAL-OBJECT",
            "layer": "b0",
            "previous_layer": None,
            "lifecycle_state": "active",
            "evidence": {
                "source_edition_id": "FICTIONAL-EDITION",
                "content_sha256": "a" * 64,
                "content_blake3": "b" * 64,
                "size_bytes": 10,
                "media_type": "application/pdf",
                "capture_receipt_sha256": "c" * 64,
                "safety_receipt_sha256": "d" * 64,
                "custody_receipt_sha256": "e" * 64,
            },
        },
        "artifacts": {"source": "a" * 64},
    }


def evaluate(project_root: Path, expected: dict, wrappers: list[dict]) -> dict:
    raw = canonical(expected)
    bank = {sha(canonical(item)): canonical(item) for item in wrappers}
    return bind_layer_records(
        raw, sha(raw), (project_root / "config/medallion_layers.json").read_bytes(), bank
    )


def test_scope_is_independent_denominator_and_references_are_not_proof(project_root: Path) -> None:
    result = evaluate(project_root, scope(), [wrapper()])
    assert result["declared_object_count"] == 1
    assert result["expected_layer_cell_count"] == 5
    assert result["present_record_count"] == 1
    assert result["coverage"][0]["record_status"] == "structurally_valid"
    assert [r["record_status"] for r in result["coverage"]][1:] == ["missing"] * 4
    assert all(
        not r["evidence_meaning_verified"] and not r["promotion_authorized"]
        for r in result["coverage"]
    )
    assert result["acceptance_not_assessed"] is True
    assert result == evaluate(project_root, scope(), [wrapper()])


@pytest.mark.parametrize("state", ["quarantined", "withdrawn", "tombstoned", "absent"])
def test_inactive_layers_remain_visible_without_payloads(project_root: Path, state: str) -> None:
    expected = scope()
    item = expected["objects"][0]["layers"]["b1"]
    item["state"] = state
    if state != "absent":
        item.update(reason_codes=["FICTIONAL-REASON"], disposition_reference="FICTIONAL-DECISION")
    report = evaluate(project_root, expected, [wrapper()])
    assert len(report["coverage"]) == 5
    assert report["coverage"][0]["record_status"] == "structurally_valid"
    assert report["coverage"][1]["record_status"] == (
        "absent" if state == "absent" else "lifecycle_blocked"
    )
    assert report["coverage"][2]["dependency_blockers"]


@pytest.mark.parametrize(
    "change", ["extra", "edition", "duplicate", "state", "absent", "digest", "role"]
)
def test_scope_and_record_binding_failures(project_root: Path, change: str) -> None:
    expected, first = scope(), wrapper()
    records = [first]
    if change == "extra":
        first["object_id"] = first["record"]["object_id"] = "OTHER"
    elif change == "edition":
        first["edition_id"] = "OTHER"
    elif change == "duplicate":
        other = copy.deepcopy(first)
        other["artifacts"] = {}
        records.append(other)
    elif change in {"state", "absent"}:
        expected["objects"][0]["layers"]["b0"]["state"] = "absent"
        if change == "absent":
            first["record"]["lifecycle_state"] = "absent"
    elif change == "digest":
        first["artifacts"]["source"] = True
    else:
        first["artifacts"] = {"unsafe/path": "a" * 64}
    with pytest.raises(QualificationInputError):
        evaluate(project_root, expected, records)


@pytest.mark.parametrize("change", ["fields", "edition", "size", "malformed"])
def test_structural_failure_is_not_missing_evidence(project_root: Path, change: str) -> None:
    item = wrapper()
    if change == "fields":
        del item["record"]["evidence"]["content_sha256"]
    elif change == "edition":
        item["record"]["evidence"]["source_edition_id"] = "OTHER"
    elif change == "size":
        item["record"]["evidence"]["size_bytes"] = True
    else:
        item["record"]["evidence"] = []
    result = evaluate(project_root, scope(), [item])
    assert result["coverage"][0]["record_status"] == "invalid"
    assert result["coverage"][1]["dependency_blockers"] == [
        "immediate_predecessor_structure_invalid"
    ]


def test_predecessor_binding_is_checked_without_borrowing_evidence(project_root: Path) -> None:
    first = wrapper()
    second = copy.deepcopy(first)
    second["record"].update(
        layer="b1",
        previous_layer="b0",
        evidence={
            "predecessor_receipt_sha256": record_sha256(first["record"]),
            "extraction_contract_sha256": "f" * 64,
            "transformation_receipt_sha256": "f" * 64,
            "source_labels_preserved": True,
        },
    )
    result = evaluate(project_root, scope(), [first, second])
    assert result["coverage"][1]["record_status"] == "structurally_valid"
    assert not result["coverage"][1]["evidence_meaning_verified"]
    second["record"]["evidence"]["predecessor_receipt_sha256"] = "0" * 64
    assert (
        "predecessor_binding_invalid"
        in evaluate(project_root, scope(), [first, second])["coverage"][1]["errors"]
    )


def test_tampering_and_contract_weakening_cannot_rehash_to_pass(project_root: Path) -> None:
    raw = canonical(scope())
    record = canonical(wrapper())
    contract = (project_root / "config/medallion_layers.json").read_bytes()
    bank = {sha(record): record}
    result = bind_layer_records(raw, sha(raw), contract, bank)
    verify_bindings(raw, sha(raw), contract, bank, result)
    result["coverage"][0]["evidence_meaning_verified"] = True
    with pytest.raises(QualificationInputError):
        verify_bindings(raw, sha(raw), contract, bank, result)
    for scope_digest, layer_contract, records in [
        ("0" * 64, contract, bank),
        (sha(raw), contract + b" ", bank),
        (sha(raw), contract, {sha(record): record + b" "}),
    ]:
        with pytest.raises(QualificationInputError):
            bind_layer_records(raw, scope_digest, layer_contract, records)


@pytest.mark.parametrize("raw", [b'{"x":1,"x":2}', b'{"x":NaN}', b"[]", b"x" * (1024 * 1024 + 1)])
def test_malformed_scope_fails_safely(raw: bytes) -> None:
    with pytest.raises(QualificationInputError):
        parse_scope(raw, sha(raw))


def test_scope_rejects_duplicate_objects_and_unexplained_quarantine() -> None:
    expected = scope()
    expected["objects"].append(copy.deepcopy(expected["objects"][0]))
    with pytest.raises(QualificationInputError):
        parse_scope(canonical(expected), sha(canonical(expected)))
    expected = scope()
    expected["objects"][0]["layers"]["b0"]["state"] = "quarantined"
    with pytest.raises(QualificationInputError):
        parse_scope(canonical(expected), sha(canonical(expected)))


@pytest.mark.parametrize("raw", [b'{"x":1e9999}', b'{"x":"\\ud800"}'])
def test_nonfinite_and_unpaired_surrogate_rejected(raw: bytes) -> None:
    with pytest.raises(QualificationInputError):
        parse(raw)


@pytest.mark.parametrize("ancestor", ["missing", "invalid", "quarantined"])
def test_ancestor_blocks_all_descendants_not_their_structure(
    project_root: Path, ancestor: str
) -> None:
    expected = scope()
    base = wrapper()
    if ancestor == "invalid":
        del base["record"]["evidence"]["content_sha256"]
    elif ancestor == "quarantined":
        expected["objects"][0]["layers"]["b0"].update(
            state="quarantined", reason_codes=["FICTIONAL"], disposition_reference="FICTIONAL"
        )
        base["record"]["lifecycle_state"] = "quarantined"
    first = wrapper()
    first["record"].update(
        layer="b1",
        previous_layer="b0",
        evidence={
            "predecessor_receipt_sha256": record_sha256(base["record"]),
            "extraction_contract_sha256": "f" * 64,
            "transformation_receipt_sha256": "f" * 64,
            "source_labels_preserved": True,
        },
    )
    second = copy.deepcopy(first)
    second["record"].update(
        layer="silver",
        previous_layer="b1",
        evidence={
            "predecessor_receipt_sha256": record_sha256(first["record"]),
            "mapping_contract_sha256": "a" * 64,
            "field_lineage_sha256": "b" * 64,
            "semantic_review_reference": "FICTIONAL",
            "valid_from": "2026-01-01T00:00:00Z",
            "recorded_at": "2026-01-01T00:00:00Z",
        },
    )
    # Another declared object must not inherit this object's blockers.
    other = copy.deepcopy(expected["objects"][0])
    other.update(object_id="OTHER-OBJECT", edition_id="OTHER-EDITION")
    other["layers"] = scope()["objects"][0]["layers"]
    expected["objects"].append(other)
    other_record = wrapper()
    other_record.update(object_id="OTHER-OBJECT", edition_id="OTHER-EDITION")
    other_record["record"]["object_id"] = "OTHER-OBJECT"
    other_record["record"]["evidence"]["source_edition_id"] = "OTHER-EDITION"
    records = [first, second, other_record]
    if ancestor != "missing":
        records.append(base)
    report = evaluate(project_root, expected, records)
    assert report["coverage"][2]["record_status"] == "structurally_valid"
    assert report["coverage"][2]["dependency_blockers"] == ["upstream_dependency_unresolved"]
    assert report["coverage"][4]["dependency_blockers"]
    assert report["coverage"][5]["record_status"] == "structurally_valid"
    assert report["coverage"][5]["dependency_blockers"] == []
