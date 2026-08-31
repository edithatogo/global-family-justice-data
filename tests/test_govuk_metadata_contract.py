"""Fictional metadata fixtures; no transport or source-response access."""

import hashlib
import json

import pytest

from gfjd.govuk_metadata_contract import evaluate


def row() -> dict:
    return {
        "link": "/government/statistics/fictional-test",
        "title": "Fictional title",
        "format": "official_statistics",
        "public_timestamp": "2026-08-31T01:02:03Z",
        "first_published_at": "2020-01-01T00:00:00+00:00",
    }


def payload(rows: list | None = None, **extras: object) -> bytes:
    rows = [row()] if rows is None else rows
    return json.dumps({"results": rows, "total": len(rows), "start": 0, **extras}).encode()


def test_retains_only_separate_metadata_dates_and_exposure() -> None:
    result = evaluate(payload())
    assert result["status"] == "metadata_shape_valid"
    assert result["observations"] == [
        {
            "locator": row()["link"],
            "update_time": row()["public_timestamp"],
            "first_publication_time": row()["first_published_at"],
        }
    ]
    assert result["exposures"] == [
        {"locator_sha256": hashlib.sha256(row()["link"].encode()).hexdigest(), "requested": False}
    ]
    assert result["exposure_complete"] is True
    assert all(value is False for value in result["boundary"].values())
    assert "Fictional title" not in json.dumps(result)


@pytest.mark.parametrize(
    "extras", [None, True, 1, "fictional incidental", [1, None], {"nested": False}]
)
def test_documented_incidental_values_bounded_but_not_typed_or_retained(extras: object) -> None:
    item = row()
    item.update(
        dict.fromkeys(["index", "es_score", "_id", "elasticsearch_type", "document_type"], extras)
    )
    result = evaluate(
        payload(
            [item],
            **dict.fromkeys(
                ["aggregates", "suggested_queries", "suggested_autocomplete", "es_cluster"], extras
            ),
        )
    )
    assert result == evaluate(payload())


@pytest.mark.parametrize("first", [None, "absent"])
def test_first_publication_never_falls_back_to_update(first: object) -> None:
    item = row()
    if first == "absent":
        del item["first_published_at"]
    else:
        item["first_published_at"] = first
    result = evaluate(payload([item]))
    assert result["observations"][0]["first_publication_time"] is None
    assert result["observations"][0]["update_time"] is not None


@pytest.mark.parametrize(
    "link",
    [
        "https://www.gov.uk/government/statistics/x",
        "//evil.example/x",
        "/government/statistics/../x",
        "/government/statistics/a?x=y",
        "/government/statistics/a#x",
        "/government/statistics/%61",
        "/government/statistics/A",
        "/government/statistics/a/b",
    ],
)
def test_unsafe_links_hashed_but_not_retained(link: str) -> None:
    item = row()
    item["link"] = link
    result = evaluate(payload([item]))
    assert result["status"] == "terminal_failure"
    assert result["observations"] == []
    assert result["exposures"][0]["locator_sha256"] == hashlib.sha256(link.encode()).hexdigest()
    assert result["exposure_complete"] is True
    assert link not in json.dumps(result)


@pytest.mark.parametrize(
    "raw", [b"not JSON", b"\xff", b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":Infinity}', b'{"x":1e999}']
)
def test_strict_parse_failures_are_fixed_and_no_raw_values(raw: bytes) -> None:
    result = evaluate(raw)
    assert result["status"] == "terminal_failure"
    assert result["observations"] == result["exposures"] == []
    assert result["exposure_complete"] is False


@pytest.mark.parametrize(
    "extras",
    [
        {"total": True},
        {"start": True},
        {"total": 2},
        {"start": 1},
        {"unknown_private_key": "fictional private value"},
    ],
)
def test_root_failure_still_accounts_for_links(extras: dict) -> None:
    result = evaluate(payload(**extras))
    assert result["status"] == "terminal_failure"
    assert len(result["exposures"]) == 1
    assert result["exposure_complete"] is True
    assert "private" not in json.dumps(result)


def test_duplicate_locators_and_row_limit_keep_all_exposures() -> None:
    for rows in ([row(), row()], [row()] * 101):
        result = evaluate(payload(rows))
        assert result["status"] == "terminal_failure"
        assert result["observations"] == []
        assert len(result["exposures"]) == len(rows)


@pytest.mark.parametrize(
    "field,value",
    [
        ("format", "news_article"),
        ("title", ""),
        ("title", None),
        ("public_timestamp", "2026-08-31"),
        ("first_published_at", "2026-08-31T00:00:00"),
        ("first_published_at", True),
    ],
)
def test_row_semantics_fail_without_partial_records(field: str, value: object) -> None:
    item = row()
    item[field] = value
    result = evaluate(payload([item]))
    assert result["status"] == "terminal_failure"
    assert result["observations"] == []
    assert result["exposure_complete"] is True


def test_missing_and_nonstring_links_make_exposure_incomplete() -> None:
    for invalid in ({"title": "fictional"}, {"link": None}, "fictional"):
        result = evaluate(payload([row(), invalid]))
        assert result["exposure_complete"] is False
        assert len(result["exposures"]) == 1
        assert result["observations"] == []


def test_empty_complete_is_not_eligibility() -> None:
    result = evaluate(payload([]))
    assert result["status"] == "metadata_shape_valid"
    assert result["observations"] == result["exposures"] == []
    assert result["exposure_complete"] is True
    assert all(value is False for value in result["boundary"].values())


def test_structural_bounds() -> None:
    deep: object = None
    for _ in range(17):
        deep = [deep]
    for raw in (
        b"x" * (2 * 1024 * 1024 + 1),
        payload(aggregates=[None] * 1001),
        payload(aggregates={str(i): None for i in range(129)}),
        payload(aggregates="x" * 4097),
        payload(aggregates=deep),
        payload(aggregates=[[None] * 1000 for _ in range(10)]),
    ):
        result = evaluate(raw)
        assert result["status"] == "terminal_failure"
        assert result["exposure_complete"] is False
        assert result["exposures"] == []


def test_unknown_row_key_withholds_all_passing_observations() -> None:
    second = row()
    second["link"] = "/government/statistics/fictional-second"
    second["untrusted_unknown_key"] = "untrusted_unknown_value"
    result = evaluate(payload([row(), second]))
    assert result["stop_code"] == "row_shape"
    assert result["observations"] == []
    assert len(result["exposures"]) == 2
    assert "untrusted" not in json.dumps(result)


@pytest.mark.parametrize("title", ["\x00fictional", "fictional\ntext", "\x7f", "   "])
def test_title_control_characters(title: str) -> None:
    item = row()
    item["title"] = title
    assert evaluate(payload([item]))["stop_code"] == "invalid_title"


def test_unpaired_surrogate_stops_before_fingerprint_encoding() -> None:
    item = row()
    item["link"] = "\ud800"
    result = evaluate(payload([item]))
    assert result["stop_code"] == "invalid_unicode"
    assert result["exposure_complete"] is False
    assert result["exposures"] == []


def test_nullable_update_and_first_publication_dates() -> None:
    item = row()
    item.update(public_timestamp=None, first_published_at=None, format="national_statistics")
    result = evaluate(payload([item]))
    assert result["status"] == "metadata_shape_valid"
    assert result["observations"][0]["update_time"] is None
    assert result["observations"][0]["first_publication_time"] is None


@pytest.mark.parametrize("date", ["2026-08-31T00:00:00+01:99", "2026-02-30T00:00:00Z"])
def test_invalid_calendar_dates_and_offsets(date: str) -> None:
    item = row()
    item["first_published_at"] = date
    assert evaluate(payload([item]))["stop_code"] == "invalid_date"
