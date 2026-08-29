"""Fail-closed evaluation of an official structured publication index."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Collection, Mapping
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from .g2_sitemap_stream import parse_timestamp


@dataclass(frozen=True)
class PublicationObservation:
    """Metadata-only exposure observed in an official publication index."""

    ordinal: int
    url: str
    public_timestamp: str
    title: str
    publication_format: str


def evaluate_response(
    payload: Mapping[str, object],
    *,
    cutoff: datetime,
    endpoint_count: int,
    allowed_locator_hosts: Collection[str],
    allowed_link_prefixes: Collection[str],
    eligible_formats: Collection[str],
    minimum_candidate_count: int,
) -> tuple[list[PublicationObservation], dict[str, int | str]]:
    """Validate a complete single-page response and classify its observations."""

    raw_total = payload.get("total")
    results = payload.get("results")
    if not isinstance(raw_total, int) or isinstance(raw_total, bool) or raw_total < 0:
        raise ValueError("response total must be a non-negative integer")
    if not isinstance(results, list):
        raise ValueError("response results must be an array")
    if raw_total > endpoint_count or len(results) != raw_total:
        raise ValueError("incomplete single-page enumeration")

    observations: list[PublicationObservation] = []
    seen_urls: set[str] = set()
    candidates = 0
    for ordinal, result in enumerate(results, 1):
        if not isinstance(result, dict):
            raise ValueError(f"result {ordinal} must be an object")
        link = result.get("link")
        timestamp_text = result.get("public_timestamp")
        title = result.get("title")
        publication_format = result.get("format")
        if not isinstance(link, str) or not link:
            raise ValueError(f"result {ordinal} lacks required metadata")
        if not isinstance(timestamp_text, str) or not timestamp_text:
            raise ValueError(f"result {ordinal} lacks required metadata")
        if not isinstance(title, str) or not title:
            raise ValueError(f"result {ordinal} lacks required metadata")
        if not isinstance(publication_format, str) or not publication_format:
            raise ValueError(f"result {ordinal} lacks publication format")
        if not link.startswith("/") or link.startswith("//"):
            raise ValueError(f"result {ordinal} has a non-canonical link")
        if not any(link.startswith(prefix) for prefix in allowed_link_prefixes):
            raise ValueError(f"result {ordinal} has a prohibited link path")
        url = f"https://www.gov.uk{link}"
        parsed = urlparse(url)
        if parsed.hostname not in allowed_locator_hosts or parsed.query or parsed.fragment:
            raise ValueError(f"result {ordinal} has a prohibited locator")
        if url in seen_urls:
            raise ValueError(f"result {ordinal} duplicates a locator")
        seen_urls.add(url)
        timestamp = parse_timestamp(timestamp_text)
        if timestamp is None:
            raise ValueError(f"result {ordinal} has an invalid public timestamp")
        if timestamp > cutoff and publication_format in eligible_formats:
            candidates += 1
        observations.append(
            PublicationObservation(
                ordinal=ordinal,
                url=url,
                public_timestamp=timestamp_text,
                title=title,
                publication_format=publication_format,
            )
        )

    return observations, {
        "observed_locator_count": len(observations),
        "eligible_post_cutoff_count": candidates,
        "outcome": (
            "candidate_threshold_met"
            if candidates >= minimum_candidate_count
            else "monitor_no_candidates"
        ),
    }


def write_exposure_ledger(observations: Collection[PublicationObservation], output: Path) -> str:
    """Write canonical JSONL and return its SHA-256 digest."""

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="\n") as stream:
        for observation in observations:
            stream.write(json.dumps(asdict(observation), sort_keys=True, separators=(",", ":")))
            stream.write("\n")
    return hashlib.sha256(output.read_bytes()).hexdigest()
