"""Frozen offline qualification-history interface, version 1.

assess_history(history_raw, checkpoint_raw, *, object_id, edition_id,
expected_projection) returns exact full-journal replay plus supplied-checkpoint
consistency. verify_history_checks takes the same inputs and a third positional
report, and recomputes everything. Neither API authenticates a checkpoint.

Both envelopes are exact-key JSON, at most 1 MiB each. Journals and source banks
are capped at 100 entries; canonical source rows total at most 8 MiB. Structural
limits are depth 16, 100000 nodes, 128 object members and 65536 characters per
string. No payload paths, network, time inference or historical-tip fallback.
Only implementation fingerprinting reads files; caller supplies fictional or
separately authorized row bytes. There is no authority to obtain new sources.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any

from . import medallion_history, medallion_replay

VERSION = "gfjd-qualification-history-v1"
MAX_BYTES = 1024 * 1024
MAX_ENTRIES = 100
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_NODES = 100000
MAX_DEPTH = 16
MAX_STRING_CHARS = 65536
HISTORY_FIELDS = frozenset({"version", "object_id", "edition_id", "events", "sources"})
CHECKPOINT_FIELDS = frozenset(
    {
        "version",
        "object_id",
        "edition_id",
        "previous_events",
        "previous_events_sha256",
    }
)


class HistoryChecksError(ValueError):
    """Malformed or mismatched replay inputs; no partial report is returned."""


def _require(condition: bool) -> None:
    if not condition:
        raise HistoryChecksError("history checks contract violation")


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _identifier(value: Any) -> None:
    _require(
        isinstance(value, str)
        and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", value) is not None
    )


def _digest(value: Any) -> None:
    _require(isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None)


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    _require(len(pairs) <= 128)
    result = {}
    for key, value in pairs:
        _require(key not in result)
        result[key] = value
    return result


def _nonfinite(_value: str) -> None:
    raise HistoryChecksError("invalid JSON constant")


def _bound(root: Any) -> None:
    pending = [(root, 1)]
    nodes = 0
    while pending:
        value, depth = pending.pop()
        nodes += 1
        _require(nodes <= MAX_NODES and depth <= MAX_DEPTH)
        if isinstance(value, dict):
            _require(len(value) <= 128 and all(isinstance(key, str) for key in value))
            pending.extend((item, depth + 1) for item in value)
            pending.extend((item, depth + 1) for item in value.values())
        elif isinstance(value, list):
            _require(len(value) <= MAX_NODES)
            pending.extend((item, depth + 1) for item in value)
        elif isinstance(value, str):
            _require(len(value) <= MAX_STRING_CHARS)
            _require(not any(0xD800 <= ord(char) <= 0xDFFF for char in value))
        elif isinstance(value, float):
            _require(math.isfinite(value))
        else:
            _require(value is None or type(value) in {bool, int})


def _load(raw: bytes, keys: frozenset[str]) -> dict[str, Any]:
    _require(isinstance(raw, bytes) and 0 < len(raw) <= MAX_BYTES)
    result = json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs, parse_constant=_nonfinite)
    _bound(result)
    _require(isinstance(result, dict) and set(result) == keys)
    _require(result["version"] == VERSION)
    return dict(result)


def _sources(descriptors: Any, events: list[dict[str, Any]]) -> dict[str, bytes]:
    _require(isinstance(descriptors, list) and 1 <= len(descriptors) <= MAX_ENTRIES)
    sources = {}
    total = 0
    for item in descriptors:
        _require(isinstance(item, dict) and set(item) == {"sha256", "rows"})
        identity = item["sha256"]
        _digest(identity)
        _require(identity not in sources)
        rows = item["rows"]
        _require(isinstance(rows, list) and 1 <= len(rows) <= medallion_replay.MAX_ROWS)
        for row in rows:
            _require(isinstance(row, dict) and 1 <= len(row) <= medallion_replay.MAX_FIELDS)
            _require(all(isinstance(value, str) for value in row.values()))
        raw = _canonical(rows)
        _require(len(raw) <= medallion_replay.MAX_BYTES and _sha(raw) == identity)
        total += len(raw)
        _require(total <= MAX_SOURCE_BYTES)
        sources[identity] = raw
    required = set()
    for event in events:
        _require(isinstance(event, dict))
        _digest(event.get("source_sha256"))
        required.add(event["source_sha256"])
    _require(set(sources) == required)
    return sources


def _assess(
    history_raw: bytes,
    checkpoint_raw: bytes,
    object_id: str,
    edition_id: str,
    expected_projection: dict[str, Any],
) -> dict[str, Any]:
    _identifier(object_id)
    _identifier(edition_id)
    history = _load(history_raw, HISTORY_FIELDS)
    checkpoint = _load(checkpoint_raw, CHECKPOINT_FIELDS)
    for envelope in (history, checkpoint):
        _require(envelope["object_id"] == object_id and envelope["edition_id"] == edition_id)
    events, previous = history["events"], checkpoint["previous_events"]
    _require(isinstance(events, list) and 1 <= len(events) <= MAX_ENTRIES)
    _require(isinstance(previous, list) and len(previous) <= MAX_ENTRIES)
    _require(
        all(
            isinstance(event, dict) and event.get("partition") == object_id
            for event in [*previous, *events]
        )
    )
    _digest(checkpoint["previous_events_sha256"])
    _require(_sha(_canonical(previous)) == checkpoint["previous_events_sha256"])
    sources = _sources(history["sources"], events)
    # This verifier replays both the full old journal and full new journal,
    # then compares their exact prefix. Supplied checkpoint provenance is NOT
    # established by its digest or by the replay of its contents.
    replay = medallion_history.verify_append_only(previous, events, sources)
    _require(isinstance(expected_projection, dict))
    _bound(expected_projection)
    expected_raw = _canonical(expected_projection)
    _require(len(expected_raw) <= MAX_BYTES)
    _require(_canonical(events[-1]["projection_receipt"]) == expected_raw)
    report = {
        "version": VERSION,
        "object_id": object_id,
        "edition_id": edition_id,
        "history_input_sha256": _sha(history_raw),
        "checkpoint_input_sha256": _sha(checkpoint_raw),
        "expected_projection_sha256": _sha(expected_raw),
        "implementation_sha256": _sha(Path(__file__).read_bytes()),
        "history_implementation_sha256": _sha(Path(medallion_history.__file__).read_bytes()),
        "projection_implementation_sha256": _sha(Path(medallion_replay.__file__).read_bytes()),
        "source_count": len(sources),
        "source_bytes": sum(len(raw) for raw in sources.values()),
        "previous_event_count": len(previous),
        "scoped_replay": "verified",
        "checkpoint_consistency": "verified",
        "checkpoint_authenticity": False,
        "historical_preservation_verified": False,
        "promotion_authorized": False,
        "full_replay": replay,
        "limitations": [
            "supplied_checkpoint_only_no_trusted_external_anchor",
            "exact_final_projection_only_no_older_or_future_fallback",
            "no_source_valid_clock_inference_or_current_time_assessment",
            "no_remote_restore_or_source_truth_verified",
            "named_module_hashes_not_complete_transitive_runtime",
            "no_source_access_rights_publication_or_release_authority",
        ],
    }
    report["report_sha256"] = _sha(_canonical(report))
    return report


def assess_history(
    history_raw: bytes,
    checkpoint_raw: bytes,
    *,
    object_id: str,
    edition_id: str,
    expected_projection: dict[str, Any],
) -> dict[str, Any]:
    """Recompute all events and exact final projection; authenticate nothing."""
    try:
        return _assess(history_raw, checkpoint_raw, object_id, edition_id, expected_projection)
    except (ValueError, TypeError, KeyError, RecursionError, OverflowError, OSError):
        raise HistoryChecksError("history checks input invalid") from None


def verify_history_checks(
    history_raw: bytes,
    checkpoint_raw: bytes,
    report: dict[str, Any],
    *,
    object_id: str,
    edition_id: str,
    expected_projection: dict[str, Any],
) -> None:
    """Recompute complete report rather than trusting its status or self-hash."""
    try:
        expected = assess_history(
            history_raw,
            checkpoint_raw,
            object_id=object_id,
            edition_id=edition_id,
            expected_projection=expected_projection,
        )
        _bound(report)
        _require(_canonical(report) == _canonical(expected))
    except (ValueError, TypeError, RecursionError, OverflowError):
        raise HistoryChecksError("history checks report mismatch") from None
