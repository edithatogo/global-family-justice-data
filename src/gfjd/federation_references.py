"""Digest-bound canonical reference declarations; no transport or source loader.

The estate compiler reads its own implementation file for its fingerprint. No
metadata locators, partner repositories or source payloads are accessed. This
artifact is reference-only; it does not establish estate-wide zero-copy custody.
JSON metadata is only syntax-checked, never interpreted as JSON-LD or executed.
"""

import hashlib
import json
import re
from typing import Any

from gfjd.federation_metadata import MetadataError, parse_json, require, safe_url
from gfjd.federation_rdf_input import parse_metadata
from gfjd.medallion_estate import prepare_estate

VERSION = "gfjd-federation-reference-scope-v1"
KINDS = frozenset(
    {
        "jurisdiction",
        "institution",
        "source",
        "edition",
        "acquisition",
        "observation",
        "transformation",
        "release",
    }
)
PARTNERS = frozenset(
    {"archive-govt-nz", "global-medicines-atlas", "reimbursement-atlas", "dataset-estate-registry"}
)
MEDIA_TYPES = frozenset({"application/json", "application/ld+json", "application/n-triples"})
OBJECT_KEYS = frozenset(
    {
        "object_id",
        "canonical_id",
        "kind",
        "role",
        "content_sha256",
        "metadata_sha256",
        "media_type",
        "references",
    }
)


def _digest(value: Any) -> None:
    require(isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None)


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _reconcile(
    scope_raw: bytes,
    expected_sha256: str,
    metadata_bank: dict[str, bytes],
    estate_inputs: dict[str, bytes],
) -> dict[str, Any]:
    require(type(scope_raw) is bytes and 0 < len(scope_raw) <= 1024 * 1024)
    _digest(expected_sha256)
    require(_sha(scope_raw) == expected_sha256)
    scope = parse_json(scope_raw)
    require(
        isinstance(scope, dict)
        and set(scope)
        == {"contract_version", "state", "estate_manifest_sha256", "objects", "partners"}
    )
    require(scope["contract_version"] == VERSION and scope["state"] == "preparation")
    _digest(scope["estate_manifest_sha256"])
    # Recompute, never trust a caller's parsed estate manifest or pass assertion.
    estate_raw = prepare_estate(estate_inputs)["estate-manifest.json"]
    require(_sha(estate_raw) == scope["estate_manifest_sha256"])
    estate = parse_json(estate_raw)
    roles = {role["id"] for role in estate["roles"]}
    partners = scope["partners"]
    require(isinstance(partners, list) and len(partners) <= len(PARTNERS))
    require(all(isinstance(partner, str) and partner in PARTNERS for partner in partners))
    require(len(set(partners)) == len(partners))
    objects = scope["objects"]
    require(isinstance(objects, list) and 1 <= len(objects) <= 100)
    require(type(metadata_bank) is dict and 1 <= len(metadata_bank) <= 100)
    total = 0
    for digest, raw in metadata_bank.items():
        _digest(digest)
        require(type(raw) is bytes and 0 < len(raw) <= 1024 * 1024)
        total += len(raw)
        require(total <= 8 * 1024 * 1024)
        require(_sha(raw) == digest)
    logical: set[str] = set()
    canonical: set[str] = set()
    metadata_digests: set[str] = set()
    records = []
    for obj in objects:
        require(isinstance(obj, dict) and set(obj) == OBJECT_KEYS)
        object_id = obj["object_id"]
        require(
            isinstance(object_id, str)
            and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}", object_id) is not None
        )
        require(object_id not in logical)
        logical.add(object_id)
        kind = obj["kind"]
        require(isinstance(kind, str) and kind in KINDS)
        urn = obj["canonical_id"]
        require(isinstance(urn, str) and len(urn) <= 256)
        require(
            re.fullmatch(r"urn:gfjd:" + kind + r":[A-Za-z0-9][A-Za-z0-9._:-]*", urn) is not None
        )
        require(urn not in canonical)
        canonical.add(urn)
        require(isinstance(obj["role"], str) and obj["role"] in roles)
        if obj["content_sha256"] is not None:
            _digest(obj["content_sha256"])
        digest = obj["metadata_sha256"]
        _digest(digest)
        metadata_digests.add(digest)
        require(digest in metadata_bank)
        media = obj["media_type"]
        require(isinstance(media, str) and media in MEDIA_TYPES)
        if media == "application/n-triples":
            parse_metadata(metadata_bank[digest])
        else:
            require(isinstance(parse_json(metadata_bank[digest]), dict))
        refs = obj["references"]
        require(isinstance(refs, list) and len(refs) <= 20)
        for ref in refs:
            safe_url(ref)
        require(len(set(refs)) == len(refs))
        records.append({**obj, "references": sorted(refs)})
    require(metadata_digests == set(metadata_bank))
    return {
        "contract_version": "gfjd-federation-reference-report-v1",
        "state": "reference_only_preparation",
        "scope_sha256": expected_sha256,
        "estate_manifest_sha256": _sha(estate_raw),
        "metadata_sha256": sorted(metadata_digests),
        "metadata_bytes": total,
        "objects": sorted(records, key=lambda obj: obj["object_id"]),
        "object_count": len(records),
        "pending_content_count": sum(obj["content_sha256"] is None for obj in records),
        "partners": sorted(partners),
        "partner_registration": "unverified",
        "content_custody": "unverified",
        "semantic_equivalence": "unverified",
        "factual_evidence": "unverified",
        "coverage": "declared-identities-and-metadata-syntax-only",
        "filesystem_access": "estate-compiler-implementation-fingerprint-only",
        "authority": dict.fromkeys(
            (
                "network",
                "source_access",
                "publication",
                "release",
                "rights_clearance",
                "custody",
                "gold_promotion",
                "maturity",
                "gate_acceptance",
                "partner_registration",
            ),
            False,
        ),
    }


def reconcile_references(
    scope_raw: bytes,
    expected_sha256: str,
    metadata_bank: dict[str, bytes],
    estate_inputs: dict[str, bytes],
) -> dict[str, Any]:
    """Reconcile exact supplied scope, metadata membership and recomputed estate roles."""
    try:
        return _reconcile(scope_raw, expected_sha256, metadata_bank, estate_inputs)
    except Exception:
        raise MetadataError("Metadata profile contract violation") from None


def verify_references(
    scope_raw: bytes,
    expected_sha256: str,
    metadata_bank: dict[str, bytes],
    estate_inputs: dict[str, bytes],
    report: dict[str, Any],
) -> None:
    """Compare the full recomputed report, not supplied success fields or self-hashes."""
    try:
        expected = reconcile_references(scope_raw, expected_sha256, metadata_bank, estate_inputs)
        require(type(report) is dict and report == expected)
        require(
            json.dumps(report, sort_keys=True, allow_nan=False)
            == json.dumps(expected, sort_keys=True)
        )
    except Exception:
        raise MetadataError("Metadata profile contract violation") from None
