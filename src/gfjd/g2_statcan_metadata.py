"""Fail-closed evaluation of exact Statistics Canada cube metadata."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


def _parse_release(value: object) -> datetime:
    if not isinstance(value, str):
        raise ValueError("releaseTime must be a string")
    parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M").replace(
        tzinfo=UTC
    )
    return parsed


def evaluate_metadata(
    payload: object,
    *,
    product_ids: list[int],
    expected_titles: dict[str, str],
    cutoff: datetime,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Validate the exact response set and identify post-cutoff table updates."""

    if not isinstance(payload, list) or len(payload) != len(product_ids):
        raise ValueError("metadata response does not match frozen product count")
    expected = {str(value) for value in product_ids}
    observations: list[dict[str, Any]] = []
    seen: set[str] = set()
    triggered = 0
    for item in payload:
        if not isinstance(item, dict) or item.get("status") != "SUCCESS":
            raise ValueError("metadata response item failed")
        obj = item.get("object")
        if not isinstance(obj, dict):
            raise ValueError("metadata response object missing")
        pid = str(obj.get("productId"))
        if pid not in expected or pid in seen:
            raise ValueError("unexpected or duplicate productId")
        seen.add(pid)
        title = obj.get("cubeTitleEn")
        if title != expected_titles.get(pid):
            raise ValueError(f"title drift for product {pid}")
        release = _parse_release(obj.get("releaseTime"))
        issue_date = obj.get("issueDate")
        end_date = obj.get("cubeEndDate")
        if not isinstance(issue_date, str) or not isinstance(end_date, str):
            raise ValueError(f"required date metadata missing for product {pid}")
        if release > cutoff:
            triggered += 1
        observations.append(
            {
                "product_id": pid,
                "title": title,
                "issue_date": issue_date,
                "cube_end_date": end_date,
                "release_time": obj["releaseTime"],
                "post_cutoff_update": release > cutoff,
            }
        )
    if seen != expected:
        raise ValueError("metadata response omitted frozen products")
    observations.sort(key=lambda row: row["product_id"])
    return observations, {
        "observed_product_count": len(observations),
        "post_cutoff_update_count": triggered,
        "outcome": "review_required" if triggered else "monitor_no_update",
        "eligibility_established": False,
    }
