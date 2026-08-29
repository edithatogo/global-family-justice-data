from datetime import UTC, datetime
from pathlib import Path

import pytest

from gfjd.g2_official_publication_feed import evaluate_response, write_exposure_ledger

CUTOFF = datetime(2026, 8, 29, 5, 17, 40, tzinfo=UTC)


def _evaluate(payload: dict, *, count: int = 100):
    return evaluate_response(
        payload,
        cutoff=CUTOFF,
        endpoint_count=count,
        allowed_locator_hosts={"www.gov.uk"},
        allowed_link_prefixes={"/government/statistics/"},
        eligible_formats={"official_statistics", "national_statistics"},
        minimum_candidate_count=2,
    )


def test_evaluates_complete_structured_publication_response(tmp_path: Path) -> None:
    payload = {
        "total": 2,
        "results": [
            {
                "link": "/government/statistics/family-a",
                "public_timestamp": "2026-08-30T09:30:00Z",
                "title": "Family A",
                "format": "official_statistics",
            },
            {
                "link": "/government/statistics/family-b",
                "public_timestamp": "2026-08-31T09:30:00Z",
                "title": "Family B",
                "format": "national_statistics",
            },
        ],
    }
    observations, summary = _evaluate(payload)
    assert summary["outcome"] == "candidate_threshold_met"
    assert summary["eligible_post_cutoff_count"] == 2
    digest = write_exposure_ledger(observations, tmp_path / "exposure.jsonl")
    assert len(digest) == 64
    assert (tmp_path / "exposure.jsonl").read_text().count("\n") == 2


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        ({"total": 2, "results": []}, "incomplete single-page enumeration"),
        ({"total": 101, "results": []}, "incomplete single-page enumeration"),
        ({"total": "0", "results": []}, "response total"),
        ({"total": 0, "results": {}}, "response results"),
    ],
)
def test_rejects_incomplete_or_invalid_enumeration(payload: dict, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        _evaluate(payload)


@pytest.mark.parametrize(
    ("result", "message"),
    [
        (
            {
                "link": "https://other.example/statistics/a",
                "public_timestamp": "2026-08-30T00:00:00Z",
                "title": "A",
                "format": "official_statistics",
            },
            "non-canonical link",
        ),
        (
            {
                "link": "/government/guidance/a",
                "public_timestamp": "2026-08-30T00:00:00Z",
                "title": "A",
                "format": "official_statistics",
            },
            "prohibited link path",
        ),
        (
            {
                "link": "/government/statistics/a",
                "public_timestamp": "not-a-date",
                "title": "A",
                "format": "official_statistics",
            },
            "invalid public timestamp",
        ),
        (
            {
                "link": "/government/statistics/a",
                "public_timestamp": "2026-08-30T00:00:00Z",
                "title": "",
                "format": "official_statistics",
            },
            "lacks required metadata",
        ),
    ],
)
def test_rejects_invalid_result_metadata(result: dict, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        _evaluate({"total": 1, "results": [result]})


def test_rejects_duplicate_locator() -> None:
    result = {
        "link": "/government/statistics/a",
        "public_timestamp": "2026-08-30T00:00:00Z",
        "title": "A",
        "format": "official_statistics",
    }
    with pytest.raises(ValueError, match="duplicates a locator"):
        _evaluate({"total": 2, "results": [result, result]})


def test_pre_cutoff_or_ineligible_publication_is_not_candidate() -> None:
    observations, summary = _evaluate(
        {
            "total": 2,
            "results": [
                {
                    "link": "/government/statistics/a",
                    "public_timestamp": "2026-08-29T05:17:40Z",
                    "title": "A",
                    "format": "official_statistics",
                },
                {
                    "link": "/government/statistics/b",
                    "public_timestamp": "2026-08-30T00:00:00Z",
                    "title": "B",
                    "format": "research",
                },
            ],
        }
    )
    assert len(observations) == 2
    assert summary == {
        "observed_locator_count": 2,
        "eligible_post_cutoff_count": 0,
        "outcome": "monitor_no_candidates",
    }
