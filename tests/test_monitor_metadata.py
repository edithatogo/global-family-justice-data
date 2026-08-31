"""Fictional in-memory metadata preservation checks; never source requests."""

import hashlib
import json

import pytest

from gfjd.monitor_metadata import BOUNDARIES, validate_monitor_metadata

ENDPOINT = "https://fictional.example/sitemap.xml"
BOUNDARY = {
    key: False
    for key in (
        "candidate_document_access",
        "extraction",
        "g2_acceptance",
        "returned_locator_access",
    )
}


def fixture() -> tuple[dict, dict[str, bytes]]:
    ledger = b'{"endpoint":"https://fictional.example/sitemap.xml","endpoint_ordinal":1,"ordinal":1,"url":"https://fictional.example/fictional","lastmod":null}\n'
    receipt = {
        "schema_version": "1.0",
        "campaign_id": "FICTIONAL",
        "run_id": "123-1",
        "source_commit": "a" * 40,
        "checked_at": "2026-08-31T00:00:00Z",
        "cutoff": "2026-08-30T00:00:00Z",
        "boundary": BOUNDARY.copy(),
        "status": "complete",
        "requests": [
            {
                "ordinal": 1,
                "url": ENDPOINT,
                "http_status": 200,
                "content_type": "application/xml",
                "response_bytes": 100,
                "response_sha256": "b" * 64,
                "locator_count": 1,
            }
        ],
        "exposure_ledger_sha256": hashlib.sha256(ledger).hexdigest(),
        "summary": {
            "observed_locator_count": 1,
            "unique_locator_count": 1,
            "duplicate_locator_count": 0,
            "uncertain_lastmod_count": 1,
            "post_cutoff_lastmod_count": 0,
            "outcome": "monitor_no_candidates",
            "novel_exposure_count": 0,
            "novel_exposure_ledger_sha256": hashlib.sha256(b"").hexdigest(),
            "total_response_bytes": 100,
        },
    }
    return receipt, {"exposure-ledger.jsonl": ledger, "novel-exposure-ledger.jsonl": b""}


def validate(receipt: dict, files: dict[str, bytes]) -> dict:
    return validate_monitor_metadata(
        {**files, "receipt.json": json.dumps(receipt).encode()},
        run_id="123-1",
        source_commit="a" * 40,
        campaign_id="FICTIONAL",
        endpoints=(ENDPOINT,),
        route="sitemap",
    )


def test_fictional_complete() -> None:
    receipt, files = fixture()
    result = validate(receipt, files)
    assert result["receipt_status"] == "complete"
    assert result["observed_rows"] == 1


@pytest.mark.parametrize(
    "key,value",
    [
        ("run_id", "other"),
        ("source_commit", "b" * 40),
        ("schema_version", "2.0"),
        ("checked_at", "2026-08-31"),
        ("status", "in_progress"),
        ("unexpected", "text"),
    ],
)
def test_root_fail_closed(key: str, value: object) -> None:
    receipt, files = fixture()
    receipt[key] = value
    with pytest.raises(ValueError):
        validate(receipt, files)


@pytest.mark.parametrize("field", ["run_id", "source_commit", "boundary", "summary"])
def test_missing_fields(field: str) -> None:
    receipt, files = fixture()
    del receipt[field]
    with pytest.raises(ValueError):
        validate(receipt, files)


@pytest.mark.parametrize("value", [True, 0, None, "false"])
def test_boundary_strict_false(value: object) -> None:
    receipt, files = fixture()
    receipt["boundary"]["extraction"] = value
    with pytest.raises(ValueError):
        validate(receipt, files)


@pytest.mark.parametrize("value", [True, -1, 1.0, "1", 2])
def test_counts_not_coerced(value: object) -> None:
    receipt, files = fixture()
    receipt["summary"]["observed_locator_count"] = value
    with pytest.raises(ValueError):
        validate(receipt, files)


@pytest.mark.parametrize("payload", [b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":Infinity}', b"\xff"])
def test_strict_json(payload: bytes) -> None:
    with pytest.raises(ValueError):
        validate_monitor_metadata(
            {"receipt.json": payload},
            run_id="123-1",
            source_commit="a" * 40,
            campaign_id="FICTIONAL",
            endpoints=(ENDPOINT,),
            route="sitemap",
        )


def test_terminal_preserves_partial_ledger_without_novel() -> None:
    receipt, files = fixture()
    receipt["status"] = "terminal_failure"
    receipt["error"] = "<urlopen error timed out>"
    receipt["summary"] = {
        "outcome": "terminal_failure",
        "completed_endpoint_count": 1,
        "total_response_bytes": 100,
    }
    del files["novel-exposure-ledger.jsonl"]
    assert validate(receipt, files)["observed_rows"] == 1
    receipt["error"] = "arbitrary unreviewed source text"
    with pytest.raises(ValueError):
        validate(receipt, files)


def test_ledger_digest_failure() -> None:
    receipt, files = fixture()
    files["exposure-ledger.jsonl"] += b"\n"
    with pytest.raises(ValueError):
        validate(receipt, files)


def other_fixture(route: str) -> tuple[dict, dict[str, bytes]]:
    receipt, _ = fixture()
    del receipt["requests"]
    receipt["boundary"] = dict.fromkeys(BOUNDARIES[route].split(), False)
    receipt["request"] = {"url": ENDPOINT, "response_bytes": 100, "response_sha256": "b" * 64}
    if route == "feed":
        receipt["request"].update(http_status=200, content_type="application/json")
        receipt["exposure_ledger_sha256"] = hashlib.sha256(b"").hexdigest()
        receipt["summary"] = {
            "observed_locator_count": 0,
            "eligible_post_cutoff_count": 0,
            "novel_exposure_count": 0,
            "novel_exposure_ledger_sha256": hashlib.sha256(b"").hexdigest(),
            "outcome": "monitor_no_candidates",
        }
        return receipt, {"exposure-ledger.jsonl": b"", "novel-exposure-ledger.jsonl": b""}
    del receipt["cutoff"], receipt["exposure_ledger_sha256"]
    receipt["request"]["method"] = "GET"
    receipt["summary"] = {"outcome": "baseline_unchanged", "candidate_eligibility": False}
    receipt["observation"] = (
        {
            "page_date_text": "Fictional date",
            "datetime_attribute": "fictional",
            "datetime_attribute_accepted": False,
            "locators": ["/assets/Documents/Publications/fictional.xlsx"],
        }
        if route == "nz"
        else {
            "title": "Fictional calendar",
            "schedule_text": "Next publication: fictional",
            "source_url": "https://www.gov.uk/government/collections/fictional",
        }
    )
    return receipt, {}


def validate_other(receipt: dict, files: dict[str, bytes], route: str) -> dict:
    return validate_monitor_metadata(
        {**files, "receipt.json": json.dumps(receipt).encode()},
        run_id="123-1",
        source_commit="a" * 40,
        campaign_id="FICTIONAL",
        endpoints=(ENDPOINT,),
        route=route,
    )


@pytest.mark.parametrize("route", ["feed", "nz", "calendar"])
def test_other_qualified_routes(route: str) -> None:
    receipt, files = other_fixture(route)
    assert validate_other(receipt, files, route)["receipt_status"] == "complete"
    receipt["request"]["unknown"] = "unreviewed"
    with pytest.raises(ValueError):
        validate_other(receipt, files, route)


@pytest.mark.parametrize("route", ["feed", "nz", "calendar"])
def test_other_terminal_routes(route: str) -> None:
    receipt, files = other_fixture(route)
    receipt["status"] = "terminal_failure"
    receipt["error"] = "<urlopen error timed out>"
    receipt["summary"] = {"outcome": "terminal_failure"}
    if route == "feed":
        del files["novel-exposure-ledger.jsonl"]
        receipt["request"] = None
    else:
        del receipt["observation"]
        receipt["summary"]["candidate_eligibility"] = False
        receipt["request"] = {"url": ENDPOINT, "method": "GET"}
    assert validate_other(receipt, files, route)["receipt_status"] == "terminal_failure"


@pytest.mark.parametrize("route", ["nz", "calendar"])
def test_observation_shape_and_origin_rejected(route: str) -> None:
    receipt, files = other_fixture(route)
    if route == "nz":
        receipt["observation"]["locators"] = ["/assets/Documents/Publications/%2e%2e/private"]
    else:
        receipt["observation"]["source_url"] = "https://evil.example/government/collections/a"
    with pytest.raises(ValueError):
        validate_other(receipt, files, route)


@pytest.mark.parametrize(
    "url",
    [
        "https://evil.example/a",
        "https://user@fictional.example/a",
        "https://fictional.example/a#fragment",
        "http://fictional.example/a",
    ],
)
def test_ledger_url_validation_even_with_valid_digest(url: str) -> None:
    receipt, files = fixture()
    row = json.loads(files["exposure-ledger.jsonl"])
    row["url"] = url
    files["exposure-ledger.jsonl"] = json.dumps(row).encode() + b"\n"
    receipt["exposure_ledger_sha256"] = hashlib.sha256(files["exposure-ledger.jsonl"]).hexdigest()
    with pytest.raises(ValueError):
        validate(receipt, files)


def test_novel_subset_enforced_and_baseline_gap_reported() -> None:
    receipt, files = fixture()
    files["novel-exposure-ledger.jsonl"] = files["exposure-ledger.jsonl"]
    receipt["summary"].update(
        novel_exposure_count=1,
        outcome="unconsolidated_exposure",
        novel_exposure_ledger_sha256=receipt["exposure_ledger_sha256"],
    )
    receipt["status"] = "action_required"
    assert "novelty_baseline_not_checked" in validate(receipt, files)["original_digest_gaps"]
    files["novel-exposure-ledger.jsonl"] *= 2
    receipt["summary"].update(
        novel_exposure_count=2,
        novel_exposure_ledger_sha256=hashlib.sha256(
            files["novel-exposure-ledger.jsonl"]
        ).hexdigest(),
    )
    with pytest.raises(ValueError):
        validate(receipt, files)


def test_feed_nonempty_fails_closed() -> None:
    receipt, files = other_fixture("feed")
    files["exposure-ledger.jsonl"] = fixture()[1]["exposure-ledger.jsonl"]
    receipt["exposure_ledger_sha256"] = hashlib.sha256(files["exposure-ledger.jsonl"]).hexdigest()
    with pytest.raises(ValueError):
        validate_other(receipt, files, "feed")


def test_size_and_row_limits() -> None:
    receipt, files = fixture()
    files["exposure-ledger.jsonl"] *= 10_001
    receipt["exposure_ledger_sha256"] = hashlib.sha256(files["exposure-ledger.jsonl"]).hexdigest()
    with pytest.raises(ValueError):
        validate(receipt, files)
    files["exposure-ledger.jsonl"] = b"x" * (8 * 1024 * 1024 + 1)
    with pytest.raises(ValueError):
        validate(receipt, files)


def test_untrusted_values_not_in_error_message() -> None:
    receipt, files = fixture()
    receipt["checked_at"] = "fictional_untrusted_value"
    with pytest.raises(ValueError, match="^monitor metadata validation failed$") as error:
        validate(receipt, files)
    assert error.value.__suppress_context__
