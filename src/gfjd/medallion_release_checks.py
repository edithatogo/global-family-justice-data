"""Bounded internal Platinum composition checks; no release or Gold acceptance.

Only implementation fingerprinting reads a file; all evidence is supplied bytes.
Media types are declarations, not inferred
content validation. Federation identity checks do not establish standards
conformance, canonical identity authenticity, or public snapshot availability.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any

VERSION = "gfjd-platinum-composition-v1"
MAX_OBJECTS = 100
MAX_JSON_BYTES = 1024 * 1024
MAX_ARTIFACT_BYTES = 8 * 1024 * 1024


def _require(condition: bool) -> None:
    if not condition:
        raise ValueError("release composition validation failed")


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result = {}
    for key, value in pairs:
        _require(key not in result)
        result[key] = value
    return result


def _nonfinite(value: str) -> None:
    raise ValueError("release composition validation failed")


def _json(raw: bytes) -> Any:
    _require(isinstance(raw, bytes) and len(raw) <= MAX_JSON_BYTES)
    value = json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs, parse_constant=_nonfinite)
    pending = [value]
    while pending:
        item = pending.pop()
        if isinstance(item, dict):
            pending.extend(item.values())
        elif isinstance(item, list):
            pending.extend(item)
        elif isinstance(item, float):
            _require(math.isfinite(item))
    return value


def _keys(value: Any, keys: str) -> dict[str, Any]:
    _require(isinstance(value, dict) and set(value) == set(keys.split()))
    return dict(value)


def _identity(value: Any) -> str:
    _require(
        isinstance(value, str)
        and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}", value) is not None
    )
    return str(value)


def _digest(value: Any) -> str:
    _require(isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None)
    return str(value)


def _objects(value: Any, keys: str) -> dict[str, dict[str, Any]]:
    _require(isinstance(value, list) and len(value) <= MAX_OBJECTS)
    objects = {}
    for item in value:
        item = _keys(item, keys)
        identity = _identity(item["object_id"])
        _require(identity not in objects)
        objects[identity] = item
    return objects


def _assess(
    manifest_raw: bytes,
    federation_raw: bytes,
    artifacts: dict[str, bytes],
    expected_scope_raw: bytes,
) -> dict[str, Any]:
    manifest = _keys(
        _json(manifest_raw), "contract_version release_id scope_sha256 federation_sha256 objects"
    )
    federation = _keys(_json(federation_raw), "contract_version release_id objects")
    scope = _keys(_json(expected_scope_raw), "contract_version release_id object_ids")
    _require(manifest["contract_version"] == VERSION)
    _require(federation["contract_version"] == "gfjd-federation-composition-v1")
    _require(scope["contract_version"] == "gfjd-platinum-scope-v1")
    release_id = _identity(manifest["release_id"])
    _require(federation["release_id"] == scope["release_id"] == release_id)
    _require(_digest(manifest["scope_sha256"]) == _sha(expected_scope_raw))
    _require(_digest(manifest["federation_sha256"]) == _sha(federation_raw))
    expected = scope["object_ids"]
    _require(isinstance(expected, list) and 0 < len(expected) <= MAX_OBJECTS)
    expected_ids = [_identity(identity) for identity in expected]
    _require(len(set(expected_ids)) == len(expected_ids))
    declared = _objects(manifest["objects"], "object_id layer sha256 size_bytes media_type")
    federated = _objects(federation["objects"], "object_id content_sha256 canonical_object_id")
    _require(set(declared) == set(federated) == set(expected_ids))
    _require(isinstance(artifacts, dict) and len(artifacts) <= MAX_OBJECTS)
    total = 0
    for digest, raw in artifacts.items():
        _digest(digest)
        _require(isinstance(raw, bytes))
        total += len(raw)
        _require(total <= MAX_ARTIFACT_BYTES)
        _require(_sha(raw) == digest)
    canonical_ids: set[str] = set()
    content_ids: set[str] = set()
    members = []
    for identity in sorted(declared):
        item, peer = declared[identity], federated[identity]
        _require(item["layer"] == "gold")
        digest = _digest(item["sha256"])
        _require(digest in artifacts)
        _require(type(item["size_bytes"]) is int and item["size_bytes"] == len(artifacts[digest]))
        media = item["media_type"]
        _require(
            isinstance(media, str)
            and len(media) <= 128
            and re.fullmatch(
                r"[A-Za-z0-9][A-Za-z0-9!#$&^_.+-]*/[A-Za-z0-9][A-Za-z0-9!#$&^_.+-]*", media
            )
            is not None
        )
        _require(_digest(peer["content_sha256"]) == digest)
        canonical_id = _identity(peer["canonical_object_id"])
        _require(canonical_id not in canonical_ids)
        canonical_ids.add(canonical_id)
        content_ids.add(digest)
        members.append(
            {
                "object_id": identity,
                "canonical_object_id": canonical_id,
                "layer": "gold",
                "sha256": digest,
                "size_bytes": len(artifacts[digest]),
                "media_type": media,
                "content_verified": True,
                "scope_member_verified": True,
                "federation_binding_verified": True,
            }
        )
    _require(set(artifacts) == content_ids)
    report = {
        "contract_version": VERSION,
        "release_id": release_id,
        "status": "composition_verified",
        "manifest_sha256": _sha(manifest_raw),
        "federation_sha256": _sha(federation_raw),
        "scope_sha256": _sha(expected_scope_raw),
        "implementation_sha256": _sha(Path(__file__).read_bytes()),
        "object_count": len(members),
        "artifact_count": len(artifacts),
        "artifact_bytes": total,
        "members": members,
        "technical_checks": dict.fromkeys(
            (
                "exact_scope_membership",
                "artifact_fixity",
                "byte_counts",
                "federation_identity_bindings",
            ),
            "verified",
        ),
        "factual_requirements": dict.fromkeys(
            (
                "accepted_gold",
                "public_snapshot",
                "release_authority",
                "federation_standard_conformance",
            ),
            "pending",
        ),
        "authority": dict.fromkeys(
            ("network", "source_access", "promotion", "publication", "release", "gate_acceptance"),
            False,
        ),
    }
    report["report_sha256"] = _sha(_canonical(report))
    return report


def assess_release(
    manifest_raw: bytes,
    federation_raw: bytes,
    artifacts: dict[str, bytes],
    expected_scope_raw: bytes,
) -> dict[str, Any]:
    """Recompute composition against independently supplied digest-pinned scope.

    Object/canonical/release identifiers use bounded opaque identifier syntax;
    media types use a bounded parameter-free type/subtype declaration. Raw input
    hashes preserve exact input identity even when equivalent arrays are reordered.
    Artifact contents are hashed only, never decoded, extracted, or followed.
    """
    try:
        return _assess(manifest_raw, federation_raw, artifacts, expected_scope_raw)
    except (
        ValueError,
        TypeError,
        KeyError,
        AttributeError,
        OverflowError,
        RecursionError,
        OSError,
    ):
        raise ValueError("release composition validation failed") from None


def verify_release_composition(
    manifest_raw: bytes,
    federation_raw: bytes,
    artifacts: dict[str, bytes],
    expected_scope_raw: bytes,
    report: dict[str, Any],
) -> None:
    """Verify all report fields by full recomputation, not a claimed self-hash."""
    expected = assess_release(manifest_raw, federation_raw, artifacts, expected_scope_raw)
    try:
        _require(_canonical(expected) == _canonical(report))
    except (ValueError, TypeError, OverflowError, RecursionError):
        raise ValueError("release composition validation failed") from None
