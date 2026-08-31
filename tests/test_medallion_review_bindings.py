"""Fictional review claims cannot become authenticated acceptance."""

import copy
import hashlib
import json

import pytest

from gfjd.medallion_review_bindings import (
    VERSION,
    ReviewBindingError,
    assess_review,
    verify_review,
)


def record() -> dict:
    return {
        "contract_version": VERSION,
        "object_id": "FICTIONAL-OBJECT",
        "edition_id": "FICTIONAL-EDITION",
        "layer": "gold",
        "content_sha256": "a" * 64,
        "review_kind": "owner",
        "decision_reference": "FICTIONAL-DECISION",
        "reviewer_reference": "FICTIONAL-REVIEWER",
        "issued_at": "2026-08-01T00:00:00Z",
        "expires_at": "2026-09-01T00:00:00Z",
        "status": "accepted",
        "conditions": [],
        "conflicts": [],
    }


def scope() -> dict:
    return {
        "object_id": "FICTIONAL-OBJECT",
        "edition_id": "FICTIONAL-EDITION",
        "layer": "gold",
        "content_sha256": "a" * 64,
        "as_of": "2026-08-31T00:00:00Z",
    }


def raw(value: dict | None = None) -> bytes:
    return json.dumps(record() if value is None else value).encode()


def test_current_bound_record_is_not_acceptance() -> None:
    report = assess_review(raw(), **scope())
    assert report["scope_status"] == "scoped_record_bound"
    assert report["temporal_status"] == "current"
    assert report["declared_status"] == "accepted"
    assert report["authenticity_verified"] is False
    assert report["substantive_acceptance"] is False
    assert report["promotion_authorized"] is False
    assert verify_review(raw(), report, **scope()) is None
    assert report == assess_review(raw(), **scope())


@pytest.mark.parametrize(
    "instant,expected",
    [
        ("2026-07-31T23:59:59.999999Z", "future"),
        ("2026-08-01T00:00:00Z", "current"),
        ("2026-09-01T00:00:00Z", "expired"),
        ("2026-09-01T01:00:00+01:00", "expired"),
    ],
)
def test_exact_temporal_boundaries(instant: str, expected: str) -> None:
    desired = scope()
    desired["as_of"] = instant
    assert assess_review(raw(), **desired)["temporal_status"] == expected


def test_conditions_conflicts_and_reviewer_label_remain_claims() -> None:
    item = record()
    item.update(conditions=["FICTIONAL-CONDITION"], conflicts=["FICTIONAL-CONFLICT"])
    result = assess_review(raw(item), **scope())
    assert result["conditions_present"] is True
    assert result["conflicts_present"] is True
    assert result["conditions"] == item["conditions"]
    assert result["conflicts"] == item["conflicts"]
    assert result["authenticity_verified"] is False
    assert result["substantive_acceptance"] is False


@pytest.mark.parametrize(
    "field,value",
    [
        ("object_id", "FICTIONAL-OTHER"),
        ("edition_id", "FICTIONAL-OTHER"),
        ("layer", "silver"),
        ("content_sha256", "b" * 64),
    ],
)
def test_wrong_scope(field: str, value: str) -> None:
    desired = scope()
    desired[field] = value
    with pytest.raises(ReviewBindingError):
        assess_review(raw(), **desired)


@pytest.mark.parametrize(
    "field,value",
    [
        ("issued_at", "2026-02-30T00:00:00Z"),
        ("issued_at", "2026-08-01T00:00:00+00:60"),
        ("issued_at", "2026-08-01T00:00:00+24:00"),
        ("issued_at", "2026-08-01T24:00:00Z"),
        ("issued_at", "2026-08-01T00:00:60Z"),
        ("issued_at", "2026-08-01T00:00:00"),
        ("issued_at", "2026-08-01T00:00:00-00:00"),
        ("expires_at", "2026-08-01T00:00:00Z"),
        ("expires_at", "2026-07-31T00:00:00Z"),
        ("status", "verified"),
        ("status", True),
        ("review_kind", "admin"),
        ("decision_reference", "https://example.invalid/decision"),
        ("reviewer_reference", "x" * 129),
        ("conditions", ["x"] * 101),
        ("conditions", ["duplicate", "duplicate"]),
        ("conflicts", [True]),
        ("extra", "not permitted"),
    ],
)
def test_invalid_contract_fields(field: str, value: object) -> None:
    item = record()
    item[field] = value
    with pytest.raises(ReviewBindingError):
        assess_review(raw(item), **scope())


@pytest.mark.parametrize(
    "payload",
    [
        b'{"status":"accepted","status":"pending"}',
        b'{"status":NaN}',
        b'{"status":1e9999}',
        b"[]",
        b"\xff",
        b"not JSON",
        b"x" * (1024 * 1024 + 1),
    ],
)
def test_malformed_envelopes(payload: bytes) -> None:
    with pytest.raises(ReviewBindingError):
        assess_review(payload, **scope())


@pytest.mark.parametrize("status", ["accepted", "rejected", "pending"])
def test_spoofed_status_or_rehash_never_authenticates(status: str) -> None:
    item = record()
    item["status"] = status
    result = assess_review(raw(item), **scope())
    assert result["declared_status"] == status
    assert result["authenticity_verified"] is False
    forged = copy.deepcopy(result)
    forged["authenticity_verified"] = True
    del forged["report_sha256"]
    forged["report_sha256"] = hashlib.sha256(
        json.dumps(forged, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    with pytest.raises(ReviewBindingError):
        verify_review(raw(item), forged, **scope())


@pytest.mark.parametrize("kind", ["rights", "semantic", "disclosure", "owner", "restore"])
def test_every_review_kind_remains_unverified(kind: str) -> None:
    item = record()
    item["review_kind"] = kind
    report = assess_review(raw(item), **scope())
    assert report["review_kind"] == kind
    assert report["authenticity_verified"] is False
    assert report["substantive_acceptance"] is False


def test_scope_clock_malformed_and_missing_field() -> None:
    desired = scope()
    desired["as_of"] = "2026-08-31"
    with pytest.raises(ReviewBindingError):
        assess_review(raw(), **desired)
    item = record()
    del item["conditions"]
    with pytest.raises(ReviewBindingError):
        assess_review(raw(item), **scope())
    with pytest.raises(ReviewBindingError):
        assess_review("not bytes", **scope())  # type: ignore[arg-type]


def test_mutated_declared_status_conflicts_and_temporal_result_fail_verification() -> None:
    item = record()
    item.update(
        status="pending", conditions=["FICTIONAL-CONDITION"], conflicts=["FICTIONAL-CONFLICT"]
    )
    report = assess_review(raw(item), **scope())
    for field, value in (
        ("declared_status", "accepted"),
        ("conditions", []),
        ("conflicts", []),
        ("temporal_status", "expired"),
    ):
        forged = copy.deepcopy(report)
        forged[field] = value
        with pytest.raises(ReviewBindingError):
            verify_review(raw(item), forged, **scope())
