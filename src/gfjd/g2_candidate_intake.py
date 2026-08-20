"""Validate offline G2 candidate metadata against cumulative exposure.

This module intentionally has no network client and cannot establish that a
publisher, URL, edition, or licence claim is factual.  It only makes future
campaign preparation fail closed when a locally supplied candidate already
appears in the complete exposure chain.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from gfjd.g2_exposure_chain import collect_bound_exposure_chain
from gfjd.g2_metadata_search_successor import canonical_url

CAMPAIGN = Path("data/methods/g2/G2EVIDENCE-CAMPAIGN-PROTOCOL-20260820-01")
SCHEMA = CAMPAIGN / "schemas/g2_evidence_campaign_candidate_intake.schema.json"
EXPOSURE_LEDGER = Path(
    "data/methods/g2/G2HOLDOUT-METADATA-EXPANSION-20260816-03/design/ledger.json"
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _descriptor(root: Path, path: Path) -> dict[str, str]:
    return {"path": path.relative_to(root).as_posix(), "sha256": _sha(path)}


def _safe_input(root: Path, path: Path) -> Path:
    if path.is_symlink():
        raise ValueError("candidate intake must be a regular file inside the repository")
    try:
        resolved_root = root.resolve()
        resolved = path.resolve()
    except OSError as error:
        raise ValueError("candidate intake path cannot be resolved") from error
    if not resolved.is_relative_to(resolved_root) or not resolved.is_file():
        raise ValueError("candidate intake must be a regular file inside the repository")
    return resolved


def _read_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("candidate intake is not valid JSON") from error
    if not isinstance(value, dict):
        raise ValueError("candidate intake must be a JSON object")
    return value


def _current_denied_urls(root: Path) -> set[str]:
    ledger = _read_object(root / EXPOSURE_LEDGER)
    denied_urls = ledger.get("denied_urls")
    if not isinstance(denied_urls, list) or not all(isinstance(url, str) for url in denied_urls):
        raise ValueError("current exposure ledger denied URLs are invalid")
    try:
        return {canonical_url(url) for url in denied_urls}
    except ValueError as error:
        raise ValueError("current exposure ledger has an invalid URL") from error


def _complete_exposure_urls(root: Path) -> tuple[set[str], list[dict[str, str]]]:
    ledger = _read_object(root / EXPOSURE_LEDGER)
    predecessor = ledger.get("predecessor")
    if not isinstance(predecessor, dict):
        raise ValueError("current exposure ledger predecessor is missing")
    prior, chain, errors = collect_bound_exposure_chain(root, predecessor)
    if errors:
        raise ValueError("; ".join(errors))
    return prior | _current_denied_urls(root), chain


def _validate_payload(root: Path, payload: dict[str, Any]) -> None:
    schema = _read_object(root / SCHEMA)
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(payload),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        raise ValueError(f"candidate intake does not validate: {errors[0].message}")


def validate_candidate_intake(root: Path, intake_path: Path) -> dict[str, Any]:
    """Return a deterministic, metadata-only screening result.

    Any duplicate or exposed proposed URL invalidates the whole intake.  A
    passing result is merely eligible for a later source-specific screen; it is
    not a rights, authenticity, or source-content finding.
    """

    root = root.resolve()
    path = _safe_input(root, intake_path)
    payload = _read_object(path)
    _validate_payload(root, payload)
    exposure_urls, chain = _complete_exposure_urls(root)

    seen_ids: set[str] = set()
    seen_urls: set[str] = set()
    candidates: list[dict[str, str]] = []
    rejections: list[dict[str, str]] = []
    for row in payload["candidates"]:
        candidate_id = row["candidate_id"]
        proposed_url = canonical_url(row["proposed_url"])
        if candidate_id in seen_ids:
            raise ValueError("candidate intake has a duplicate candidate_id")
        if proposed_url in seen_urls:
            raise ValueError("candidate intake has a duplicate canonical proposed URL")
        seen_ids.add(candidate_id)
        seen_urls.add(proposed_url)
        if proposed_url in exposure_urls:
            rejections.append(
                {"candidate_id": candidate_id, "reason_code": "CUMULATIVE_EXPOSURE_OVERLAP"}
            )
        else:
            candidates.append({**row, "proposed_url": proposed_url})

    status = "stopped_exposure_overlap" if rejections else "prepared_metadata_only"
    return {
        "schema_version": "1.0",
        "intake_id": payload["intake_id"],
        "status": status,
        "intake": _descriptor(root, path),
        "exposure_ledger": _descriptor(root, root / EXPOSURE_LEDGER),
        "complete_predecessor_chain": chain,
        "candidate_count": len(payload["candidates"]),
        "eligible_for_future_screen_count": len(candidates) if not rejections else 0,
        "external_activity_authorized": False,
        "source_content_accessed": False,
        "candidates": candidates if not rejections else [],
        "rejections": rejections,
        "limitations": [
            "A passing intake is metadata-only and does not verify a publisher, edition, or URL.",
            "No source-specific rights, privacy, security, or disclosure assessment is performed.",
            "External access still requires the single grouped campaign authorization.",
        ],
    }
