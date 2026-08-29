from datetime import UTC, datetime
from pathlib import Path

import pytest

from gfjd.g2_future_monitor import evaluate_entries, write_exposure_ledger
from gfjd.g2_sitemap_stream import SitemapEntry


def test_evaluates_complete_monitor_observations(tmp_path: Path) -> None:
    cutoff = datetime(2026, 8, 29, 5, 17, 40, tzinfo=UTC)
    observations, summary = evaluate_entries(
        [
            (
                "https://example.test/sitemap/1/",
                [
                    SitemapEntry("https://example.test/a", "2026-08-30T00:00:00Z"),
                    SitemapEntry("https://example.test/b", "2026-08-31T00:00:00Z"),
                ],
            )
        ],
        cutoff=cutoff,
        allowed_hosts={"example.test"},
        maximum_locator_count=10,
    )
    assert summary["outcome"] == "candidate_threshold_met"
    assert summary["post_cutoff_lastmod_count"] == 2
    digest = write_exposure_ledger(observations, tmp_path / "ledger.jsonl")
    assert len(digest) == 64
    assert (tmp_path / "ledger.jsonl").read_text().count("\n") == 2


def test_rejects_cross_host_locator() -> None:
    with pytest.raises(ValueError, match="prohibited locator"):
        evaluate_entries(
            [("https://example.test/sitemap/", [SitemapEntry("https://other.test/a", None)])],
            cutoff=datetime(2026, 8, 29, tzinfo=UTC),
            allowed_hosts={"example.test"},
            maximum_locator_count=10,
        )


def test_stops_on_locator_budget() -> None:
    with pytest.raises(ValueError, match="locator budget exceeded"):
        evaluate_entries(
            [
                (
                    "https://example.test/sitemap/",
                    [SitemapEntry("https://example.test/a", None)],
                )
            ],
            cutoff=datetime(2026, 8, 29, tzinfo=UTC),
            allowed_hosts={"example.test"},
            maximum_locator_count=0,
        )
