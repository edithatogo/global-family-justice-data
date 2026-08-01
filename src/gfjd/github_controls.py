"""Pure helpers for fail-closed GitHub control evidence verification."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


def classify_response(status: int, payload: Any) -> dict[str, Any]:
    if status == 200:
        return {"state": "available", "payload": payload}
    if status == 403:
        return {"state": "forbidden", "payload": payload}
    if status == 404:
        return {"state": "not_found_or_unavailable", "payload": payload}
    return {"state": "error", "status": status, "payload": payload}


def verify_capture(capture: dict[str, Any], *, max_age_days: int = 7) -> list[str]:
    errors: list[str] = []
    recorded = capture.get("recorded_at")
    if not isinstance(recorded, str):
        return ["missing recorded_at"]
    try:
        age = datetime.now(UTC) - datetime.fromisoformat(recorded)
    except ValueError:
        return ["invalid recorded_at"]
    if age.days > max_age_days:
        errors.append("capture is stale")
    endpoints = capture.get("endpoints")
    if not isinstance(endpoints, dict) or not endpoints:
        errors.append("missing endpoint observations")
    return errors
