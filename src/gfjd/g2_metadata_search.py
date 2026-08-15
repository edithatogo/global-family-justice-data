"""Fail-closed semantic verification for the G2 search-index-only stage."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


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
        for result in event["results"]:
            all_urls.append(result["url"])
            if result["official_host_candidate"]:
                official_urls.append(result["url"])
    if bundle["candidate_hypotheses"] != sorted(set(all_urls)):
        errors.append("candidate hypothesis projection mismatch")
    if bundle["proposed_official_html_allowlist"] != sorted(set(official_urls)):
        errors.append("official HTML allowlist projection mismatch")
    exposure = sorted(event["url"] for event in bundle["exposure_events"])
    if exposure != sorted(set(all_urls)):
        errors.append("exposure projection mismatch")
    return sorted(set(errors))
