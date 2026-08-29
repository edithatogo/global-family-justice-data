from datetime import UTC, datetime

import pytest

from gfjd.g2_statcan_metadata import evaluate_metadata


def _payload(release: str = "2026-03-26T08:30") -> list[dict[str, object]]:
    return [
        {
            "status": "SUCCESS",
            "object": {
                "productId": "35100222",
                "cubeTitleEn": "Family law cases, by type of case",
                "cubeEndDate": "2024-01-01",
                "releaseTime": release,
                "issueDate": "2026-03-26",
            },
        }
    ]


def test_pre_cutoff_metadata_is_monitor_only() -> None:
    rows, summary = evaluate_metadata(
        _payload(),
        product_ids=[35100222],
        expected_titles={"35100222": "Family law cases, by type of case"},
        cutoff=datetime(2026, 8, 29, 5, 17, 40, tzinfo=UTC),
    )
    assert rows[0]["post_cutoff_update"] is False
    assert summary["outcome"] == "monitor_no_update"
    assert summary["eligibility_established"] is False


def test_post_cutoff_metadata_requires_review() -> None:
    _, summary = evaluate_metadata(
        _payload("2027-03-26T08:30"),
        product_ids=[35100222],
        expected_titles={"35100222": "Family law cases, by type of case"},
        cutoff=datetime(2026, 8, 29, 5, 17, 40, tzinfo=UTC),
    )
    assert summary["outcome"] == "review_required"


def test_title_drift_fails_closed() -> None:
    with pytest.raises(ValueError, match="title drift"):
        evaluate_metadata(
            _payload(),
            product_ids=[35100222],
            expected_titles={"35100222": "Wrong"},
            cutoff=datetime(2026, 8, 29, 5, 17, 40, tzinfo=UTC),
        )
