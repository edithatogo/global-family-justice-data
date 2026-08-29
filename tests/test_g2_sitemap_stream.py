import io
from datetime import UTC, datetime

from gfjd.g2_sitemap_stream import (
    SitemapEntry,
    child_requires_request,
    iter_sitemap_entries,
    parse_timestamp,
)


def test_streams_urlset_entries() -> None:
    xml = b"""<urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'>
      <url><loc>https://example.test/a</loc><lastmod>2026-08-30T00:00:00Z</lastmod></url>
      <url><loc>https://example.test/b</loc></url>
    </urlset>"""
    assert list(iter_sitemap_entries(io.BytesIO(xml))) == [
        SitemapEntry("https://example.test/a", "2026-08-30T00:00:00Z"),
        SitemapEntry("https://example.test/b", None),
    ]


def test_child_request_policy_is_fail_closed() -> None:
    cutoff = datetime(2026, 8, 29, 5, 17, 40, tzinfo=UTC)
    assert not child_requires_request("2026-08-29T02:50:16Z", cutoff=cutoff)
    assert child_requires_request("2026-08-29T06:00:00Z", cutoff=cutoff)
    assert child_requires_request("2026-08-29", cutoff=cutoff)
    assert child_requires_request(None, cutoff=cutoff)


def test_timestamp_rejects_date_only_and_naive_values() -> None:
    assert parse_timestamp("2026-08-29") is None
    assert parse_timestamp("2026-08-29T12:00:00") is None
    assert parse_timestamp("not-a-date") is None
