"""Source-recomputed append-only full-partition corrections and temporal replay.

Only implementation fingerprinting reads a file. Sources are supplied bytes;
there is no acquisition, custody assessment, merge, or promotion authority.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from .medallion_replay import replay_projection

VERSION = "gfjd-medallion-history-v1"
MAX_EVENTS = 100
MAX_SOURCE_BYTES = 8 * 1024 * 1024
EVENT_KEYS = frozenset(
    {
        "history_version",
        "partition",
        "supersedes",
        "source_sha256",
        "projection_contract",
        "projection_receipt",
        "valid_from",
        "valid_until",
        "recorded_at",
        "implementation_sha256",
        "event_id",
    }
)


class MedallionHistoryError(ValueError):
    """Invalid journal, source, or query; no partial replay is returned."""


def _require(condition: bool) -> None:
    if not condition:
        raise MedallionHistoryError("medallion history contract violation")


def _canonical(value: Any) -> bytes:
    try:
        return json.dumps(
            value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode("utf-8")
    except (ValueError, TypeError, UnicodeError, RecursionError):
        raise MedallionHistoryError("medallion history requires canonical JSON") from None


def _sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _digest(value: Any) -> None:
    _require(isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None)


def _partition(value: Any) -> None:
    _require(
        isinstance(value, str)
        and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", value) is not None
    )


def _timestamp(value: Any) -> None:
    _require(
        isinstance(value, str)
        and re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z", value)
        is not None
    )
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise MedallionHistoryError("medallion history timestamp invalid") from None


def build_event(
    source: bytes,
    projection_contract: dict[str, Any],
    *,
    partition: str,
    valid_until: str | None,
    supersedes: str | None,
) -> dict[str, Any]:
    """Bind a full-partition revision to exact source-recomputed projection bytes.

    Chain membership and correction ordering require replay_history. Returned
    contracts/receipts are detached from caller objects. Source-valid time may
    remain unknown, but an unknown start cannot have a known end.
    """
    _partition(partition)
    if supersedes is not None:
        _digest(supersedes)
    try:
        projection = replay_projection(source, projection_contract)
    except (ValueError, TypeError, KeyError, RecursionError, OSError):
        raise MedallionHistoryError("medallion history projection replay failed") from None
    valid_from = projection["valid_from"]
    if valid_until is not None:
        _timestamp(valid_until)
        _require(valid_from is not None and valid_from < valid_until)
    event = {
        "history_version": VERSION,
        "partition": partition,
        "supersedes": supersedes,
        "source_sha256": projection["source_sha256"],
        "projection_contract": json.loads(_canonical(projection_contract)),
        "projection_receipt": projection,
        "valid_from": valid_from,
        "valid_until": valid_until,
        "recorded_at": projection["recorded_at"],
        "implementation_sha256": _sha(Path(__file__).read_bytes()),
    }
    event["event_id"] = _sha(_canonical(event))
    return event


def _sources(sources: dict[str, bytes]) -> None:
    _require(isinstance(sources, dict) and len(sources) <= MAX_EVENTS)
    total = 0
    for digest, source in sources.items():
        _digest(digest)
        _require(isinstance(source, bytes))
        total += len(source)
        _require(total <= MAX_SOURCE_BYTES)
        _require(_sha(source) == digest)


def replay_history(events: list[dict[str, Any]], sources: dict[str, bytes]) -> dict[str, Any]:
    """Recompute every event from supplied sources, then derive recorded intervals.

    Historical implementation changes intentionally invalidate exact replay with
    this implementation. Supply its original version; never bless a self-hash.
    Global clocks are nondecreasing; each partition clock is strictly increasing.
    """
    _require(isinstance(events, list) and len(events) <= MAX_EVENTS)
    _sources(sources)
    heads: dict[str, dict[str, Any]] = {}
    seen: set[str] = set()
    revisions: list[dict[str, Any]] = []
    previous_clock: str | None = None
    for event in events:
        _require(isinstance(event, dict) and set(event) == EVENT_KEYS)
        _digest(event["event_id"])
        _digest(event["source_sha256"])
        _require(event["event_id"] not in seen and event["source_sha256"] in sources)
        expected = build_event(
            sources[event["source_sha256"]],
            event["projection_contract"],
            partition=event["partition"],
            valid_until=event["valid_until"],
            supersedes=event["supersedes"],
        )
        _require(_canonical(event) == _canonical(expected))
        partition = expected["partition"]
        recorded_at = expected["recorded_at"]
        _require(previous_clock is None or recorded_at >= previous_clock)
        parent = heads.get(partition)
        if parent is None:
            _require(expected["supersedes"] is None)
        else:
            _require(expected["supersedes"] == parent["event_id"])
            _require(recorded_at > parent["recorded_at"])
            parent["recorded_until"] = recorded_at
        revision = {
            "event_id": expected["event_id"],
            "partition": partition,
            "source_sha256": expected["source_sha256"],
            "snapshot_sha256": expected["projection_receipt"]["snapshot_sha256"],
            "valid_from": expected["valid_from"],
            "valid_until": expected["valid_until"],
            "recorded_at": recorded_at,
            "recorded_until": None,
        }
        revisions.append(revision)
        heads[partition] = revision
        seen.add(expected["event_id"])
        previous_clock = recorded_at
    receipt = {
        "history_version": VERSION,
        "history_sha256": _sha(_canonical(events)),
        "implementation_sha256": _sha(Path(__file__).read_bytes()),
        "event_count": len(events),
        "revisions": revisions,
        "partition_heads": {
            partition: head["event_id"] for partition, head in sorted(heads.items())
        },
        "promotion_authorized": False,
    }
    receipt["receipt_sha256"] = _sha(_canonical(receipt))
    return receipt


def replay_partition(
    events: list[dict[str, Any]],
    sources: dict[str, bytes],
    *,
    partition: str,
    recorded_as_of: str,
    valid_as_of: str | None = None,
) -> dict[str, Any]:
    """Query the latest recorded full-partition revision, never an older fallback.

    With no valid_as_of, replay uses only recorded time and explicitly reports
    whether valid time is known. Unknown valid time cannot satisfy a valid query.
    Recorded and known valid intervals are half-open [start, end).
    """
    _partition(partition)
    _timestamp(recorded_as_of)
    if valid_as_of is not None:
        _timestamp(valid_as_of)
    history = replay_history(events, sources)
    chosen = None
    for revision in history["revisions"]:
        if revision["partition"] == partition and revision["recorded_at"] <= recorded_as_of:
            chosen = revision
    result: dict[str, Any] = {
        "history_version": VERSION,
        "history_sha256": history["history_sha256"],
        "partition": partition,
        "recorded_as_of": recorded_as_of,
        "valid_as_of": valid_as_of,
        "status": "not_recorded",
        "revision": chosen,
        "valid_time_known": None,
        "rows": [],
        "field_lineage": [],
        "promotion_authorized": False,
    }
    if chosen is None:
        return result
    result["valid_time_known"] = chosen["valid_from"] is not None
    if valid_as_of is not None:
        if chosen["valid_from"] is None:
            result["status"] = "valid_time_unknown"
            return result
        if valid_as_of < chosen["valid_from"] or (
            chosen["valid_until"] is not None and valid_as_of >= chosen["valid_until"]
        ):
            result["status"] = "outside_valid_interval"
            return result
    event = next(event for event in events if event["event_id"] == chosen["event_id"])
    # Rebuild again instead of copying untrusted serialized projection fields.
    projection = replay_projection(sources[event["source_sha256"]], event["projection_contract"])
    result.update(
        status="replayed", rows=projection["rows"], field_lineage=projection["field_lineage"]
    )
    return result


def verify_append_only(
    old: list[dict[str, Any]],
    new: list[dict[str, Any]],
    sources: dict[str, bytes],
) -> dict[str, Any]:
    """Recompute both journals and require the exact canonical old event prefix."""
    replay_history(old, sources)
    receipt = replay_history(new, sources)
    _require(len(new) >= len(old) and _canonical(new[: len(old)]) == _canonical(old))
    return receipt
