"""Deterministic evaluation for prospective G2 sitemap monitoring."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Collection, Iterable
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from .g2_sitemap_stream import SitemapEntry, parse_timestamp


@dataclass(frozen=True)
class ObservedLocator:
    endpoint_ordinal: int
    endpoint: str
    ordinal: int
    url: str
    lastmod: str | None


def evaluate_entries(
    endpoint_entries: Iterable[tuple[str, Iterable[SitemapEntry]]],
    *,
    cutoff: datetime,
    allowed_hosts: Collection[str],
    maximum_locator_count: int,
) -> tuple[list[ObservedLocator], dict[str, int | str]]:
    """Validate and classify a complete ordered sitemap observation set."""

    observations: list[ObservedLocator] = []
    unique_urls: set[str] = set()
    post_cutoff = 0
    uncertain = 0
    for endpoint_ordinal, (endpoint, entries) in enumerate(endpoint_entries, 1):
        for ordinal, entry in enumerate(entries, 1):
            parsed = urlparse(entry.url)
            if parsed.scheme != "https" or parsed.hostname not in allowed_hosts:
                raise ValueError(f"prohibited locator at {endpoint_ordinal}:{ordinal}")
            observations.append(
                ObservedLocator(endpoint_ordinal, endpoint, ordinal, entry.url, entry.lastmod)
            )
            if len(observations) > maximum_locator_count:
                raise ValueError("locator budget exceeded")
            unique_urls.add(entry.url)
            timestamp = parse_timestamp(entry.lastmod) if entry.lastmod else None
            if timestamp is None:
                uncertain += 1
            elif timestamp > cutoff:
                post_cutoff += 1
    return observations, {
        "observed_locator_count": len(observations),
        "unique_locator_count": len(unique_urls),
        "duplicate_locator_count": len(observations) - len(unique_urls),
        "uncertain_lastmod_count": uncertain,
        "post_cutoff_lastmod_count": post_cutoff,
        "outcome": "candidate_threshold_met" if post_cutoff >= 2 else "monitor_no_candidates",
    }


def write_exposure_ledger(observations: Iterable[ObservedLocator], output: Path) -> str:
    """Write canonical JSONL and return its SHA-256 digest."""

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="\n") as stream:
        for observation in observations:
            stream.write(json.dumps(asdict(observation), sort_keys=True, separators=(",", ":")))
            stream.write("\n")
    return hashlib.sha256(output.read_bytes()).hexdigest()
