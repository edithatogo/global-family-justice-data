from datetime import UTC, datetime, timedelta

from scripts.capture_github_controls import classify_response, verify_capture


def test_capture_distinguishes_forbidden_and_not_found() -> None:
    assert classify_response(403, {})["state"] == "forbidden"
    assert classify_response(404, {})["state"] == "not_found_or_unavailable"
    assert classify_response(200, {"ok": True})["state"] == "available"


def test_capture_verifier_is_fail_closed_and_fresh() -> None:
    capture = {
        "recorded_at": (datetime.now(UTC) - timedelta(days=8)).isoformat(),
        "endpoints": {"repository": {"state": "available"}},
    }
    assert "capture is stale" in verify_capture(capture)
    assert "missing endpoint observations" in verify_capture(
        {"recorded_at": capture["recorded_at"]}
    )
