"""Bounded Parquet references, not payload inspection or verified custody.

Only supplied metadata is parsed. Existing estate helpers and this compiler
read their implementation files for fingerprints; no locator is accessed.
Hashes are declarations: unknown bytes cannot reveal a format from their hash.
"""

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from gfjd.federation_metadata import MetadataError, parse_json, require, safe_url
from gfjd.federation_references import reconcile_references

VERSION = "gfjd-parquet-reference-declarations-v1"


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _digest(value: Any) -> None:
    require(type(value) is str and re.fullmatch(r"[0-9a-f]{64}", value) is not None)


def _keys(value: Any, keys: str) -> dict[str, Any]:
    require(type(value) is dict and set(value) == set(keys.split()))
    return value  # type: ignore[no-any-return]


def _assess(
    declaration_raw: bytes,
    expected_declaration_sha256: str,
    scope_raw: bytes,
    expected_scope_sha256: str,
    metadata_bank: dict[str, bytes],
    estate_inputs: dict[str, bytes],
) -> dict[str, Any]:
    require(type(declaration_raw) is bytes and 0 < len(declaration_raw) <= 1024 * 1024)
    _digest(expected_declaration_sha256)
    require(_sha(declaration_raw) == expected_declaration_sha256)
    doc = _keys(parse_json(declaration_raw), "contract_version scope_sha256 state objects")
    require(doc["contract_version"] == VERSION and doc["state"] == "preparation")
    require(doc["scope_sha256"] == expected_scope_sha256)
    reference_report = reconcile_references(
        scope_raw, expected_scope_sha256, metadata_bank, estate_inputs
    )
    scoped = {obj["object_id"]: obj for obj in reference_report["objects"]}
    objects = doc["objects"]
    require(type(objects) is list and len(objects) <= 100)
    covered: set[str] = set()
    records: list[dict[str, Any]] = []
    issues: list[str] = []
    for item in objects:
        obj = _keys(
            item, "object_id canonical_id content_format content_sha256 blake3 byte_count locations"
        )
        identifier = obj["object_id"]
        require(type(identifier) is str and identifier in scoped and identifier not in covered)
        covered.add(identifier)
        require(obj["canonical_id"] == scoped[identifier]["canonical_id"])
        require(obj["content_format"] == "parquet")
        require(obj["content_sha256"] == scoped[identifier]["content_sha256"])
        for field in ("content_sha256", "blake3"):
            if obj[field] is None:
                issues.append(identifier + ":missing_" + field)
            else:
                _digest(obj[field])
        # Bank bytes have already been checked as JSON objects or restricted
        # N-Triples. Equal hashes are a concrete contradiction, not format inference.
        require(obj["content_sha256"] not in metadata_bank)
        size = obj["byte_count"]
        if size is None:
            issues.append(identifier + ":missing_byte_count")
        else:
            require(type(size) is int and 0 <= size <= 2**63 - 1)
        locations = obj["locations"]
        require(type(locations) is list and len(locations) <= 20)
        if not locations:
            issues.append(identifier + ":missing_locations")
        urls: set[str] = set()
        normalized = []
        for item in locations:
            location = _keys(item, "url revision")
            url = safe_url(location["url"])
            require(url not in urls)
            urls.add(url)
            revision = location["revision"]
            if revision is None:
                issues.append(identifier + ":missing_location_revision")
            else:
                revision = _keys(revision, "kind value")
                kind, value = revision["kind"], revision["value"]
                if kind == "git_commit":
                    require(type(value) is str and re.fullmatch(r"[0-9a-f]{40}", value) is not None)
                elif kind == "content_sha256":
                    _digest(value)
                    require(obj["content_sha256"] is not None and value == obj["content_sha256"])
                else:
                    require(kind == "persistent_id")
                    safe_url(value)
            normalized.append(location)
        records.append({**obj, "locations": sorted(normalized, key=lambda loc: loc["url"])})
    pending = sorted(set(scoped) - covered)
    return {
        "contract_version": VERSION,
        "state": "reference_only_preparation",
        "status": "declarations_incomplete" if issues or pending else "declarations_complete",
        "declaration_sha256": expected_declaration_sha256,
        "scope_sha256": expected_scope_sha256,
        "estate_manifest_sha256": reference_report["estate_manifest_sha256"],
        "metadata_sha256": reference_report["metadata_sha256"],
        "implementation_sha256": _sha(Path(__file__).read_bytes()),
        "objects": sorted(records, key=lambda obj: obj["object_id"]),
        "covered_object_ids": sorted(covered),
        "pending_object_ids": pending,
        "issues": sorted(set(issues)),
        "parquet_format_verified": False,
        "payload_digest_verified": False,
        "rights": "unverified",
        "custody": "unverified",
        "ownership": "unverified",
        "remote_availability": "unverified",
        "semantic_equivalence": "unverified",
        "immutable_location_verified": False,
        "factual_evidence": "unverified",
        "full_conformance": "unverified",
        "coverage": "supplied-parquet-declarations-only",
        "zero_copy_scope": "generated-reference-artifact-only",
        "filesystem_access": "estate-helper-and-compiler-implementation-fingerprints-only",
        "authority": dict(reference_report["authority"]),
    }


def assess_parquet_references(
    declaration_raw: bytes,
    expected_declaration_sha256: str,
    scope_raw: bytes,
    expected_scope_sha256: str,
    metadata_bank: dict[str, bytes],
    estate_inputs: dict[str, bytes],
) -> dict[str, Any]:
    """Reconcile declared Parquet identities without retrieving or inspecting payloads."""
    try:
        return _assess(
            declaration_raw,
            expected_declaration_sha256,
            scope_raw,
            expected_scope_sha256,
            metadata_bank,
            estate_inputs,
        )
    except Exception:
        raise MetadataError("Parquet reference contract violation") from None


def verify_parquet_references(
    declaration_raw: bytes,
    expected_declaration_sha256: str,
    scope_raw: bytes,
    expected_scope_sha256: str,
    metadata_bank: dict[str, bytes],
    estate_inputs: dict[str, bytes],
    report: dict[str, Any],
) -> None:
    """Recompute the whole report; supplied hashes and authority cannot replace checks."""
    try:
        expected = assess_parquet_references(
            declaration_raw,
            expected_declaration_sha256,
            scope_raw,
            expected_scope_sha256,
            metadata_bank,
            estate_inputs,
        )
        require(type(report) is dict and report == expected)
        require(
            json.dumps(report, sort_keys=True, allow_nan=False)
            == json.dumps(expected, sort_keys=True)
        )
    except Exception:
        raise MetadataError("Parquet reference contract violation") from None
