"""Fail-closed semantic verification for the G2 search-index-only stage."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit

from jsonschema import Draft202012Validator, FormatChecker


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def _canonical_https_html_url(value: str, official_domain: str) -> tuple[str, str] | None:
    parsed = urlsplit(value)
    host = (parsed.hostname or "").rstrip(".").lower()
    allowed = official_domain.rstrip(".").lower()
    if parsed.scheme.lower() != "https" or not host:
        return None
    if host != allowed and not host.endswith(f".{allowed}"):
        return None
    if parsed.username or parsed.password or parsed.port not in (None, 443):
        return None
    file_suffixes = {".pdf", ".xls", ".xlsx", ".csv", ".zip", ".doc", ".docx"}
    if Path(parsed.path.lower()).suffix in file_suffixes:
        return None
    canonical = urlunsplit(("https", host, parsed.path or "/", parsed.query, ""))
    return canonical, host


def _canonical_exposure_url(value: str) -> str:
    parsed = urlsplit(value)
    host = (parsed.hostname or "").rstrip(".").lower()
    if parsed.scheme.lower() not in {"http", "https"} or not host:
        return value
    scheme = parsed.scheme.lower()
    return urlunsplit((scheme, host, parsed.path or "/", parsed.query, ""))


def _collect_denied_urls(
    root: Path, descriptor: dict[str, str], *, seen: set[str] | None = None, depth: int = 0
) -> tuple[set[str], list[str]]:
    seen = set() if seen is None else seen
    if depth > 8:
        return set(), ["exposure predecessor depth exceeded"]
    relative = descriptor["path"]
    if relative in seen:
        return set(), ["exposure predecessor cycle"]
    seen.add(relative)
    path = root / relative
    if not path.is_file() or _sha(path) != descriptor["sha256"]:
        return set(), ["predecessor exposure ledger binding mismatch"]
    ledger = json.loads(path.read_text())
    denied = {_canonical_exposure_url(url) for url in ledger.get("denied_urls", [])}
    for entry in ledger.get("entries", []):
        for key in ("url", "landing_page_url"):
            if entry.get(key):
                denied.add(_canonical_exposure_url(entry[key]))
        denied.update(_canonical_exposure_url(url) for url in entry.get("urls", []))
    predecessor = ledger.get("predecessor")
    errors: list[str] = []
    if predecessor:
        inherited, inherited_errors = _collect_denied_urls(
            root, predecessor, seen=seen, depth=depth + 1
        )
        denied.update(inherited)
        errors.extend(inherited_errors)
    return denied, errors


def verify_search_index_bundle(root: Path, bundle: dict[str, Any]) -> list[str]:
    design = root / "data/methods/g2/G2HOLDOUT-METADATA-EXPANSION-20260815-01/design"
    schema = json.loads((design / "search-index-execution-bundle.schema.json").read_text())
    errors = [
        error.message
        for error in Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(
            bundle
        )
    ]
    if errors:
        return sorted(errors)
    descriptor = bundle["query_manifest"]
    manifest_path = root / descriptor["path"]
    if not manifest_path.is_file() or _sha(manifest_path) != descriptor["sha256"]:
        errors.append("query manifest binding mismatch")
        return errors
    manifest = json.loads(manifest_path.read_text())
    denied_urls, exposure_errors = _collect_denied_urls(root, bundle["predecessor_exposure_ledger"])
    errors.extend(exposure_errors)
    if exposure_errors:
        return errors
    if bundle["provider_config"] != manifest["provider_config"]:
        errors.append("provider configuration mismatch")
    all_urls: list[str] = []
    official_urls: list[str] = []
    for expected, event in zip(manifest["queries"], bundle["query_events"], strict=True):
        for key in ("query_order", "query_id", "query_text", "language"):
            if event[key] != expected[key]:
                errors.append(f"query {expected['query_id']} {key} mismatch")
        if event["query_sha256"] != hashlib.sha256(event["query_text"].encode()).hexdigest():
            errors.append(f"query {expected['query_id']} digest mismatch")
        if event["result_count"] != len(event["results"]):
            errors.append(f"query {expected['query_id']} result count mismatch")
        if event["result_sha256"] != hashlib.sha256(_canonical(event["results"])).hexdigest():
            errors.append(f"query {expected['query_id']} result digest mismatch")
        if [result["rank"] for result in event["results"]] != list(
            range(1, len(event["results"]) + 1)
        ):
            errors.append(f"query {expected['query_id']} result ranks invalid")
        for result in event["results"]:
            parsed = _canonical_https_html_url(result["url"], expected["official_domain"])
            if parsed is None:
                errors.append(f"query {expected['query_id']} result URL is not allowed HTML")
                continue
            canonical_url, host = parsed
            if result["domain"].rstrip(".").lower() != host:
                errors.append(f"query {expected['query_id']} result domain mismatch")
            all_urls.append(canonical_url)
            if result["official_host_candidate"]:
                official_urls.append(canonical_url)
    if bundle["candidate_hypotheses"] != sorted(set(all_urls)):
        errors.append("candidate hypothesis projection mismatch")
    if bundle["proposed_official_html_allowlist"] != sorted(set(official_urls)):
        errors.append("official HTML allowlist projection mismatch")
    exposure = sorted(event["url"] for event in bundle["exposure_events"])
    if exposure != sorted(set(all_urls)):
        errors.append("exposure projection mismatch")
    checked = bundle["non_overlap_receipt"]["checked_urls"]
    if checked != sorted(set(all_urls)):
        errors.append("non-overlap checked URL projection mismatch")
    if {_canonical_exposure_url(url) for url in all_urls} & denied_urls:
        errors.append("candidate overlaps predecessor exposure ledger")
    return sorted(set(errors))
