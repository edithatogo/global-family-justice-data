"""Fictional full-journal/checkpoint consistency, never preservation evidence."""

import copy
import hashlib
import json

import pytest

from gfjd.medallion_history import build_event
from gfjd.medallion_history_checks import (
    VERSION,
    HistoryChecksError,
    assess_history,
    verify_history_checks,
)
from gfjd.medallion_replay import VERSION as PROJECTION_VERSION


def canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def inputs() -> tuple[dict, dict, dict]:
    events = []
    sources = []
    for month, value in (("01", "FICTIONAL-OLD"), ("02", "FICTIONAL-CORRECTED")):
        rows = [{"fictional_source_label": value}]
        contract = {
            "contract_version": PROJECTION_VERSION,
            "source_sha256": digest(rows),
            "projection": {"fictional_output": "fictional_source_label"},
            "valid_from": None,
            "recorded_at": f"2026-{month}-01T00:00:00Z",
        }
        event = build_event(
            canonical(rows),
            contract,
            partition="FICTIONAL-OBJECT",
            valid_until=None,
            supersedes=events[-1]["event_id"] if events else None,
        )
        events.append(event)
        sources.append({"sha256": digest(rows), "rows": rows})
    history = {
        "version": VERSION,
        "object_id": "FICTIONAL-OBJECT",
        "edition_id": "FICTIONAL-EDITION",
        "events": events,
        "sources": sources,
    }
    checkpoint = {
        "version": VERSION,
        "object_id": "FICTIONAL-OBJECT",
        "edition_id": "FICTIONAL-EDITION",
        "previous_events": events[:1],
        "previous_events_sha256": digest(events[:1]),
    }
    scope = {
        "object_id": "FICTIONAL-OBJECT",
        "edition_id": "FICTIONAL-EDITION",
        "expected_projection": events[-1]["projection_receipt"],
    }
    return history, checkpoint, scope


def test_complete_scoped_replay_checkpoint_is_not_authenticated() -> None:
    history, checkpoint, scope = inputs()
    report = assess_history(canonical(history), canonical(checkpoint), **scope)
    assert report["scoped_replay"] == "verified"
    assert report["checkpoint_consistency"] == "verified"
    assert report["checkpoint_authenticity"] is False
    assert report["promotion_authorized"] is False
    assert report["full_replay"]["event_count"] == 2
    assert all(item["valid_from"] is None for item in report["full_replay"]["revisions"])
    assert verify_history_checks(canonical(history), canonical(checkpoint), report, **scope) is None


@pytest.mark.parametrize(
    "mode",
    [
        "source",
        "extra_rows",
        "extra_source",
        "duplicate_source",
        "empty",
        "partition",
        "projection",
        "wrong_object",
        "wrong_edition",
        "checkpoint_digest",
        "prefix",
        "extra_field",
    ],
)
def test_substitution_and_scope_fail_closed(mode: str) -> None:
    history, checkpoint, scope = inputs()
    if mode == "source":
        history["sources"][0]["rows"][0]["fictional_source_label"] = "FICTIONAL-FORGED"
    elif mode == "extra_rows":
        history["sources"][0]["rows"].append({"fictional_source_label": "FICTIONAL-EXTRA"})
    elif mode == "extra_source":
        rows = [{"fictional_source_label": "UNUSED-FICTIONAL"}]
        history["sources"].append({"sha256": digest(rows), "rows": rows})
    elif mode == "duplicate_source":
        history["sources"].append(copy.deepcopy(history["sources"][0]))
    elif mode == "empty":
        history["events"] = []
    elif mode == "partition":
        history["events"][0]["partition"] = "FICTIONAL-OTHER"
    elif mode == "projection":
        scope["expected_projection"] = history["events"][0]["projection_receipt"]
    elif mode == "wrong_object":
        scope["object_id"] = "FICTIONAL-OTHER"
    elif mode == "wrong_edition":
        checkpoint["edition_id"] = "FICTIONAL-OTHER"
    elif mode == "checkpoint_digest":
        checkpoint["previous_events_sha256"] = "0" * 64
    elif mode == "prefix":
        checkpoint["previous_events"] = copy.deepcopy(history["events"])
        checkpoint["previous_events"][0]["valid_from"] = "2026-01-01T00:00:00Z"
        checkpoint["previous_events_sha256"] = digest(checkpoint["previous_events"])
    else:
        history["extra"] = True
    with pytest.raises(HistoryChecksError):
        assess_history(canonical(history), canonical(checkpoint), **scope)


def test_recomputed_full_replacement_still_fails_old_prefix() -> None:
    history, checkpoint, scope = inputs()
    changed = copy.deepcopy(history["events"][0])
    contract = changed["projection_contract"]
    contract["recorded_at"] = "2025-12-01T00:00:00Z"
    replacement = build_event(
        canonical(history["sources"][0]["rows"]),
        contract,
        partition=scope["object_id"],
        valid_until=None,
        supersedes=None,
    )
    history["events"][0] = replacement
    second = history["events"][1]
    history["events"][1] = build_event(
        canonical(history["sources"][1]["rows"]),
        second["projection_contract"],
        partition=scope["object_id"],
        valid_until=None,
        supersedes=replacement["event_id"],
    )
    scope["expected_projection"] = history["events"][-1]["projection_receipt"]
    with pytest.raises(HistoryChecksError):
        assess_history(canonical(history), canonical(checkpoint), **scope)


@pytest.mark.parametrize(
    "raw",
    [
        b"[]",
        b"{}",
        b"not JSON",
        b"\xff",
        b'{"events":[],"events":[]}',
        b'{"value":NaN}',
        b'{"value":1e9999}',
        b"x" * (1024 * 1024 + 1),
    ],
)
def test_malformed_or_oversized_inputs(raw: bytes) -> None:
    history, checkpoint, scope = inputs()
    with pytest.raises(HistoryChecksError):
        assess_history(raw, canonical(checkpoint), **scope)
    with pytest.raises(HistoryChecksError):
        assess_history(canonical(history), raw, **scope)


def test_initial_empty_checkpoint_not_historical_authentication() -> None:
    history, checkpoint, scope = inputs()
    checkpoint.update(previous_events=[], previous_events_sha256=digest([]))
    report = assess_history(canonical(history), canonical(checkpoint), **scope)
    assert report["checkpoint_consistency"] == "verified"
    assert report["checkpoint_authenticity"] is False


def test_forged_report_with_new_self_hash_rejected() -> None:
    history, checkpoint, scope = inputs()
    report = assess_history(canonical(history), canonical(checkpoint), **scope)
    report["checkpoint_authenticity"] = True
    del report["report_sha256"]
    report["report_sha256"] = digest(report)
    with pytest.raises(HistoryChecksError):
        verify_history_checks(canonical(history), canonical(checkpoint), report, **scope)


@pytest.mark.parametrize(
    "mode",
    [
        "events",
        "sources",
        "previous",
        "depth",
        "nonstring_rows",
        "duplicate_nested_keys",
        "missing_source",
        "scope_type",
    ],
)
def test_limits_and_nested_types(mode: str) -> None:
    history, checkpoint, scope = inputs()
    if mode == "events":
        history["events"] = [history["events"][0]] * 101
    elif mode == "sources":
        history["sources"] = [history["sources"][0]] * 101
    elif mode == "previous":
        checkpoint["previous_events"] = [history["events"][0]] * 101
        checkpoint["previous_events_sha256"] = digest(checkpoint["previous_events"])
    elif mode == "depth":
        nested: object = None
        for _ in range(20):
            nested = [nested]
        history["sources"][0]["rows"] = nested
    elif mode == "nonstring_rows":
        history["sources"][0]["rows"] = [{"fictional_source_label": True}]
        history["sources"][0]["sha256"] = digest(history["sources"][0]["rows"])
    elif mode == "missing_source":
        history["sources"] = history["sources"][:1]
    elif mode == "scope_type":
        scope["object_id"] = True
    history_bytes = canonical(history)
    if mode == "duplicate_nested_keys":
        history_bytes = history_bytes.replace(
            b'"fictional_source_label":"FICTIONAL-OLD"',
            b'"fictional_source_label":"FICTIONAL-OLD","fictional_source_label":"FORGED"',
        )
    with pytest.raises(HistoryChecksError):
        assess_history(history_bytes, canonical(checkpoint), **scope)


def test_no_report_mutation_or_row_values_returned() -> None:
    history, checkpoint, scope = inputs()
    expected = copy.deepcopy(scope["expected_projection"])
    report = assess_history(canonical(history), canonical(checkpoint), **scope)
    assert scope["expected_projection"] == expected
    assert "FICTIONAL-CORRECTED" not in json.dumps(report)
    assert "FICTIONAL-OLD" not in json.dumps(report)
