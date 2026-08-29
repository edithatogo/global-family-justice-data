"""Streaming, fail-closed helpers for prospective official sitemap intake."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import BinaryIO
from xml.etree import ElementTree


@dataclass(frozen=True)
class SitemapEntry:
    url: str
    lastmod: str | None


def parse_timestamp(value: str) -> datetime | None:
    """Return an aware timestamp; date-only or invalid values are uncertain."""

    if "T" not in value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(UTC)


def iter_sitemap_entries(stream: BinaryIO) -> Iterator[SitemapEntry]:
    """Yield entries incrementally and clear parsed elements to bound memory."""

    for _event, element in ElementTree.iterparse(stream, events=("end",)):
        local = element.tag.rsplit("}", 1)[-1]
        if local not in {"url", "sitemap"}:
            continue
        values = {child.tag.rsplit("}", 1)[-1]: (child.text or "").strip() for child in element}
        locator = values.get("loc")
        if locator:
            yield SitemapEntry(locator, values.get("lastmod") or None)
        element.clear()


def child_requires_request(lastmod: str | None, *, cutoff: datetime) -> bool:
    """Request children changed after cutoff or whose timestamp is uncertain."""

    if lastmod is None:
        return True
    parsed = parse_timestamp(lastmod)
    return parsed is None or parsed > cutoff.astimezone(UTC)
