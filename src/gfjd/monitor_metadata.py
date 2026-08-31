"""Offline, shape-qualified validation of original monitor metadata bytes.

This does not classify personal data, reconstruct source responses or exposure
baselines, establish rights, or accept G2 evidence. Unknown shapes fail closed.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from datetime import datetime
from typing import Any
from urllib.parse import unquote, urlsplit

MAX_FILE_BYTES = 8 * 1024 * 1024
MAX_LEDGER_ROWS = 10_000
BOUNDARIES = {
    "sitemap": "candidate_document_access extraction g2_acceptance returned_locator_access",
    "feed": (
        "candidate_document_access extraction g2_acceptance publication release "
        "result_url_access rights_clearance"
    ),
    "nz": (
        "extraction g2_acceptance publication release returned_locator_access "
        "rights_clearance source_file_access"
    ),
    "calendar": "extraction g2_acceptance publication release release_access source_url_access",
}


def _require(condition: bool) -> None:
    if not condition:
        raise ValueError("monitor metadata contract violation")


def _keys(value: Any, keys: str) -> dict[str, Any]:
    _require(isinstance(value, dict) and set(value) == set(keys.split()))
    return dict(value)


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        _require(key not in result)
        result[key] = value
    return result


def _nonfinite(value: str) -> None:
    raise ValueError("nonfinite JSON metadata forbidden")


def _json(payload: bytes) -> Any:
    return json.loads(payload.decode("utf-8"), object_pairs_hook=_pairs, parse_constant=_nonfinite)


def _text(value: Any, limit: int = 512, *, empty: bool = False) -> str:
    _require(isinstance(value, str))
    _require((empty or bool(value)) and len(value) <= limit)
    _require(all(ord(char) >= 32 and not 0x7F <= ord(char) <= 0x9F for char in value))
    return str(value)


def _count(value: Any) -> int:
    _require(type(value) is int and value >= 0)
    return int(value)


def _timestamp(value: Any) -> datetime:
    text = _text(value, 64)
    result = datetime.fromisoformat(text.replace("Z", "+00:00"))
    _require(result.tzinfo is not None and result.utcoffset() is not None)
    return result


def _digest(value: Any, payload: bytes | None = None) -> None:
    _require(isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None)
    if payload is not None:
        _require(value == hashlib.sha256(payload).hexdigest())


def _url(value: Any, hosts: set[str]) -> str:
    text = _text(value, 4096)
    parsed = urlsplit(text)
    _require(parsed.scheme == "https" and parsed.hostname in hosts)
    _require(parsed.username is None and parsed.password is None and not parsed.fragment)
    _require(parsed.port in {None, 443} and "\\" not in text)
    _require(not any(ord(char) < 32 for char in unquote(text)))
    return text


def _ledger(payload: bytes) -> list[dict[str, Any]]:
    lines = payload.splitlines()
    _require(len(lines) <= MAX_LEDGER_ROWS)
    return [_keys(_json(line), "endpoint endpoint_ordinal lastmod ordinal url") for line in lines]


def _request(value: Any, endpoint: str, route: str, *, terminal: bool) -> dict[str, Any]:
    if route in {"nz", "calendar"}:
        keys = "url method"
        if not terminal or (isinstance(value, dict) and "response_bytes" in value):
            keys += " response_bytes response_sha256"
    else:
        keys = "url http_status content_type response_bytes response_sha256"
        if route == "sitemap":
            keys += " ordinal locator_count"
    request = _keys(value, keys)
    _require(request["url"] == endpoint)
    if "method" in request:
        _require(request["method"] == "GET")
    else:
        _require(type(request["http_status"]) is int and request["http_status"] == 200)
        allowed = {"application/json"} if route == "feed" else {"text/xml", "application/xml"}
        _require(request["content_type"] in allowed)
    if "response_bytes" in request:
        _count(request["response_bytes"])
        _digest(request["response_sha256"])
    return request


def _observation(value: Any, route: str) -> None:
    if route == "nz":
        observation = _keys(
            value, "page_date_text datetime_attribute datetime_attribute_accepted locators"
        )
        _text(observation["page_date_text"], 128)
        _text(observation["datetime_attribute"], 128, empty=True)
        _require(observation["datetime_attribute_accepted"] is False)
        locators = observation["locators"]
        _require(isinstance(locators, list) and 0 < len(locators) <= 100)
        for locator in locators:
            text = _text(locator, 2048)
            parsed = urlsplit(text)
            _require(text.startswith("/assets/Documents/Publications/"))
            _require(
                not parsed.scheme and not parsed.netloc and not parsed.query and not parsed.fragment
            )
            decoded = unquote(text)
            _require(
                "\\" not in decoded and all(part not in {".", ".."} for part in decoded.split("/"))
            )
        _require(len(set(locators)) == len(locators) and sorted(locators) == locators)
    else:
        observation = _keys(value, "title source_url schedule_text")
        _text(observation["title"], 256)
        _text(observation["schedule_text"], 1024)
        _require("Next publication:" in observation["schedule_text"])
        source_url = _url(observation["source_url"], {"www.gov.uk"})
        _require(source_url.startswith("https://www.gov.uk/government/collections/"))
        _require(not urlsplit(source_url).query)


def _validate(
    files: dict[str, bytes],
    *,
    run_id: str,
    source_commit: str,
    campaign_id: str,
    endpoints: tuple[str, ...],
    route: str,
) -> dict[str, Any]:
    _require(route in BOUNDARIES and isinstance(endpoints, tuple) and bool(endpoints))
    hosts = {str(urlsplit(endpoint).hostname) for endpoint in endpoints}
    for endpoint in endpoints:
        _url(endpoint, hosts)
    _require(len(set(endpoints)) == len(endpoints))
    _require(route == "sitemap" or len(endpoints) == 1)
    _require(isinstance(files, dict) and "receipt.json" in files and len(files) <= 3)
    for payload in files.values():
        _require(isinstance(payload, bytes) and len(payload) <= MAX_FILE_BYTES)
    receipt = _json(files["receipt.json"])
    _require(isinstance(receipt, dict))
    terminal = receipt.get("status") == "terminal_failure"
    keys = "schema_version campaign_id checked_at source_commit run_id boundary status summary"
    if route in {"sitemap", "feed"}:
        keys += " cutoff exposure_ledger_sha256 " + (
            "requests" if route == "sitemap" else "request"
        )
    else:
        keys += " request" + ("" if terminal else " observation")
    if terminal:
        keys += " error"
    receipt = _keys(receipt, keys)
    _require(receipt["schema_version"] == "1.0")
    _require(receipt["run_id"] == run_id and receipt["source_commit"] == source_commit)
    _require(receipt["campaign_id"] == campaign_id)
    _require(receipt["status"] in {"complete", "action_required", "terminal_failure"})
    _timestamp(receipt["checked_at"])
    boundary = _keys(receipt["boundary"], BOUNDARIES[route])
    _require(all(value is False for value in boundary.values()))
    if terminal:
        _require(receipt["error"] == "<urlopen error timed out>")
    expected_files = {"receipt.json"}
    if route in {"sitemap", "feed"}:
        expected_files.add("exposure-ledger.jsonl")
        if not terminal:
            expected_files.add("novel-exposure-ledger.jsonl")
    _require(set(files) == expected_files)
    gaps = ["response_bytes_not_preserved"]
    if route in {"nz", "calendar"}:
        _request(receipt["request"], endpoints[0], route, terminal=terminal)
        summary = _keys(receipt["summary"], "outcome candidate_eligibility")
        _require(summary["candidate_eligibility"] is False)
        expected_outcome = (
            "terminal_failure"
            if terminal
            else ("baseline_unchanged" if receipt["status"] == "complete" else "review_required")
        )
        _require(summary["outcome"] == expected_outcome)
        if not terminal:
            _observation(receipt["observation"], route)
        return {
            "receipt_status": receipt["status"],
            "observed_rows": 0 if terminal else 1,
            "original_digest_gaps": gaps,
        }
    cutoff = _timestamp(receipt["cutoff"])
    ledger = files["exposure-ledger.jsonl"]
    _digest(receipt["exposure_ledger_sha256"], ledger)
    rows = _ledger(ledger)
    if route == "feed":
        _require(not rows and ledger == b"")
        if receipt["request"] is not None or not terminal:
            _request(receipt["request"], endpoints[0], route, terminal=terminal)
        summary_keys = (
            "outcome"
            if terminal
            else (
                "eligible_post_cutoff_count novel_exposure_count novel_exposure_ledger_sha256 "
                "observed_locator_count outcome"
            )
        )
    else:
        requests = receipt["requests"]
        _require(isinstance(requests, list) and len(requests) <= len(endpoints))
        _require(terminal or len(requests) == len(endpoints))
        total_bytes = 0
        position = 0
        for ordinal, request in enumerate(requests, 1):
            request = _request(request, endpoints[ordinal - 1], route, terminal=terminal)
            _require(_count(request["ordinal"]) == ordinal)
            count = _count(request["locator_count"])
            group = rows[position : position + count]
            _require(len(group) == count)
            for index, row in enumerate(group, 1):
                _require(row["endpoint"] == endpoints[ordinal - 1])
                _require(
                    _count(row["endpoint_ordinal"]) == ordinal and _count(row["ordinal"]) == index
                )
                _url(row["url"], hosts)
                if row["lastmod"] is not None:
                    _text(row["lastmod"], 128, empty=True)
            position += count
            total_bytes += _count(request["response_bytes"])
        _require(position == len(rows))
        summary_keys = (
            "completed_endpoint_count outcome total_response_bytes"
            if terminal
            else (
                "observed_locator_count unique_locator_count duplicate_locator_count "
                "uncertain_lastmod_count post_cutoff_lastmod_count outcome novel_exposure_count "
                "novel_exposure_ledger_sha256 total_response_bytes"
            )
        )
    summary = _keys(receipt["summary"], summary_keys)
    for key, value in summary.items():
        if key.endswith("_count") or key == "total_response_bytes":
            _count(value)
    if route == "sitemap":
        _require(summary["total_response_bytes"] == total_bytes)
        if terminal:
            _require(summary["completed_endpoint_count"] == len(requests))
        else:
            unique = len({row["url"] for row in rows})
            uncertain = post_cutoff = 0
            for row in rows:
                try:
                    _require(isinstance(row["lastmod"], str) and "T" in row["lastmod"])
                    timestamp = _timestamp(row["lastmod"])
                except (ValueError, TypeError):
                    uncertain += 1
                else:
                    post_cutoff += timestamp > cutoff
            _require(summary["unique_locator_count"] == unique)
            _require(summary["duplicate_locator_count"] == len(rows) - unique)
            _require(summary["uncertain_lastmod_count"] == uncertain)
            _require(summary["post_cutoff_lastmod_count"] == post_cutoff)
    if terminal:
        _require(summary["outcome"] == "terminal_failure")
    else:
        _require(summary["observed_locator_count"] == len(rows))
        novel = files["novel-exposure-ledger.jsonl"]
        _digest(summary["novel_exposure_ledger_sha256"], novel)
        novel_rows = _ledger(novel)
        _require(summary["novel_exposure_count"] == len(novel_rows))

        def canonical(row: dict[str, Any]) -> str:
            return json.dumps(row, sort_keys=True, separators=(",", ":"))

        _require(not (Counter(map(canonical, novel_rows)) - Counter(map(canonical, rows))))
        if route == "feed":
            _require(novel == b"" and summary["eligible_post_cutoff_count"] == 0)
        outcome = "monitor_no_candidates"
        if route == "sitemap" and summary["post_cutoff_lastmod_count"] >= 2:
            outcome = "candidate_threshold_met"
        elif novel_rows:
            outcome = "unconsolidated_exposure"
        _require(summary["outcome"] == outcome)
        _require(
            receipt["status"]
            == ("complete" if outcome == "monitor_no_candidates" else "action_required")
        )
        gaps.append("novelty_baseline_not_checked")
    return {
        "receipt_status": receipt["status"],
        "observed_rows": len(rows),
        "original_digest_gaps": gaps,
    }


def validate_monitor_metadata(
    files: dict[str, bytes],
    *,
    run_id: str,
    source_commit: str,
    campaign_id: str,
    endpoints: tuple[str, ...],
    route: str,
) -> dict[str, Any]:
    """Validate reviewed metadata shapes without writes, requests, or acceptance.

    Errors deliberately omit untrusted values. Feed support is restricted to an
    empty batch. Novel rows are checked as a multiset subset, not re-derived from
    an unavailable exposure baseline. Source-response digests cannot be replayed.
    """
    try:
        return _validate(
            files,
            run_id=run_id,
            source_commit=source_commit,
            campaign_id=campaign_id,
            endpoints=endpoints,
            route=route,
        )
    except (ValueError, TypeError, KeyError, OverflowError, RecursionError, AttributeError):
        raise ValueError("monitor metadata validation failed") from None
