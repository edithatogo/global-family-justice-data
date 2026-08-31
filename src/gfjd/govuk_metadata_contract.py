"""Pure prospective GOV.UK metadata shape checks, isolated from frozen runtimes.

No transport or selection is implemented. Fingerprints account for string links
encountered in structurally bounded JSON, not anonymization or safe-URL approval.
The pinned presenter interface is not evidence of a deployed response shape.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from datetime import datetime
from typing import Any

MAX_BYTES = 2 * 1024 * 1024
MAX_RESULTS = 100
MAX_DEPTH = 16
MAX_NODES = 10_000
MAX_ARRAY_ITEMS = 1000
MAX_OBJECT_MEMBERS = 128
MAX_STRING_CHARS = 4096
ROOT_REQUIRED = frozenset({"results", "total", "start"})
ROOT_OPTIONAL = frozenset(
    {"aggregates", "suggested_queries", "suggested_autocomplete", "es_cluster"}
)
ROW_REQUIRED = frozenset({"link", "title", "format", "public_timestamp"})
ROW_OPTIONAL = frozenset(
    {"first_published_at", "index", "es_score", "_id", "elasticsearch_type", "document_type"}
)
BOUNDARY_KEYS = (
    "network",
    "returned_locator_access",
    "source_access",
    "extraction",
    "eligibility",
    "selection",
    "rights_clearance",
    "publication",
    "release",
    "maturity",
    "g2_acceptance",
)


class _Stop(ValueError):
    """Internal exception carrying a fixed diagnostic code, never input text."""


def _require(condition: bool, code: str) -> None:
    if not condition:
        raise _Stop(code)


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        _require(key not in result, "duplicate_json_key")
        result[key] = value
    return result


def _nonfinite(value: str) -> None:
    raise _Stop("nonfinite_json")


def _bound_tree(root: Any) -> None:
    """Root depth is one; object keys count as string nodes at child depth."""
    pending = [(root, 1)]
    nodes = 0
    while pending:
        value, depth = pending.pop()
        nodes += 1
        _require(nodes <= MAX_NODES, "node_limit")
        _require(depth <= MAX_DEPTH, "depth_limit")
        if isinstance(value, dict):
            _require(len(value) <= MAX_OBJECT_MEMBERS, "object_member_limit")
            pending.extend((key, depth + 1) for key in value)
            pending.extend((item, depth + 1) for item in value.values())
        elif isinstance(value, list):
            _require(len(value) <= MAX_ARRAY_ITEMS, "array_item_limit")
            pending.extend((item, depth + 1) for item in value)
        elif isinstance(value, str):
            _require(len(value) <= MAX_STRING_CHARS, "string_limit")
            _require(not any(0xD800 <= ord(char) <= 0xDFFF for char in value), "invalid_unicode")
        elif isinstance(value, float):
            _require(math.isfinite(value), "nonfinite_json")


def _exposures(root: Any) -> tuple[list[dict[str, Any]], bool]:
    if not isinstance(root, dict) or not isinstance(root.get("results"), list):
        return [], False
    exposures = []
    complete = True
    for row in root["results"]:
        if not isinstance(row, dict) or not isinstance(row.get("link"), str):
            complete = False
            continue
        exposures.append(
            {
                "locator_sha256": hashlib.sha256(row["link"].encode("utf-8")).hexdigest(),
                "requested": False,
            }
        )
    return exposures, complete


def _shape(value: Any, required: frozenset[str], optional: frozenset[str], code: str) -> None:
    _require(isinstance(value, dict), code)
    _require(required <= value.keys() and value.keys() <= required | optional, code)


def _date(value: Any) -> str | None:
    if value is None:
        return None
    _require(isinstance(value, str), "invalid_date")
    _require(
        re.fullmatch(
            r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-5][0-9]:[0-5][0-9]"
            r"(?:\.[0-9]+)?(?:Z|[+-][0-9]{2}:[0-5][0-9])",
            value,
        )
        is not None,
        "invalid_date",
    )
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise _Stop("invalid_date") from None
    _require(parsed.tzinfo is not None and parsed.utcoffset() is not None, "invalid_date")
    return str(value)


def _observations(root: Any) -> list[dict[str, Any]]:
    _shape(root, ROOT_REQUIRED, ROOT_OPTIONAL, "root_shape")
    rows = root["results"]
    _require(isinstance(rows, list), "results_type")
    _require(len(rows) <= MAX_RESULTS, "result_limit")
    _require(type(root["start"]) is int and root["start"] == 0, "incomplete_enumeration")
    _require(type(root["total"]) is int and root["total"] == len(rows), "incomplete_enumeration")
    observations = []
    seen: set[str] = set()
    for row in rows:
        _shape(row, ROW_REQUIRED, ROW_OPTIONAL, "row_shape")
        link = row["link"]
        _require(isinstance(link, str), "invalid_locator")
        _require(
            re.fullmatch(r"/government/statistics/[a-z0-9][a-z0-9-]*", link) is not None,
            "invalid_locator",
        )
        _require(link not in seen, "duplicate_locator")
        seen.add(link)
        _require(isinstance(row["title"], str) and bool(row["title"].strip()), "invalid_title")
        _require(
            all(ord(char) >= 32 and not 0x7F <= ord(char) <= 0x9F for char in row["title"]),
            "invalid_title",
        )
        _require(
            isinstance(row["format"], str)
            and row["format"] in {"official_statistics", "national_statistics"},
            "invalid_format",
        )
        observations.append(
            {
                "locator": link,
                "update_time": _date(row["public_timestamp"]),
                "first_publication_time": _date(row.get("first_published_at")),
            }
        )
    return observations


def evaluate(raw: bytes) -> dict[str, Any]:
    """Return metadata-only shape evidence, never eligibility or source authority.

    Incidental values are structurally bounded, discarded, and never used in
    semantic selection. All metadata rows are withheld on any failure. String
    link hashes remain on semantic failures, even for unsafe links or over-cap
    result sets. Parse/bounds failures cannot claim complete exposure accounting.
    Update and first-publication timestamps stay distinct; no date fallback is
    permitted. Root/object key nodes count toward the depth and node budgets.
    """
    report: dict[str, Any] = {
        "schema_version": "1.0",
        "status": "terminal_failure",
        "stop_code": None,
        "observations": [],
        "exposures": [],
        "exposure_complete": False,
        "boundary": dict.fromkeys(BOUNDARY_KEYS, False),
    }
    try:
        _require(isinstance(raw, bytes), "input_type")
        _require(len(raw) <= MAX_BYTES, "response_byte_limit")
        root = json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs, parse_constant=_nonfinite)
        _bound_tree(root)
        report["exposures"], report["exposure_complete"] = _exposures(root)
        observations = _observations(root)
    except _Stop as exc:
        report["stop_code"] = str(exc)
    except (ValueError, RecursionError, OverflowError):
        report["stop_code"] = "invalid_json"
    else:
        report["status"] = "metadata_shape_valid"
        report["observations"] = observations
    return report
