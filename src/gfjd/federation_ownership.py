"""Scoped canonical responsibility declarations, not authenticated ownership.

No native identifier is resolved and no partner authority code is executed.
Only compiler/helper implementation fingerprints read files.
"""

import hashlib
import json
import re
from pathlib import Path
from typing import Any, cast

from gfjd import federation_metadata, federation_rdf_input, federation_references, medallion_estate
from gfjd.federation_metadata import MetadataError, parse_json, require

VERSION = "gfjd-canonical-ownership-declarations-v1"


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _encode(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    ).encode()


def _assess(
    raw: bytes,
    expected_sha256: str,
    scope_raw: bytes,
    expected_scope_sha256: str,
    metadata_bank: dict[str, bytes],
    estate_inputs: dict[str, bytes],
) -> dict[str, Any]:
    refs = federation_references.reconcile_references(
        scope_raw, expected_scope_sha256, metadata_bank, estate_inputs
    )
    require(type(raw) is bytes and 0 < len(raw) <= 1024 * 1024)
    require(
        type(expected_sha256) is str and re.fullmatch(r"[0-9a-f]{64}", expected_sha256) is not None
    )
    require(_sha(raw) == expected_sha256)
    document = parse_json(raw)
    require(
        type(document) is dict
        and set(document) == {"contract_version", "state", "scope_sha256", "objects"}
    )
    require(document["contract_version"] == VERSION and document["state"] == "preparation")
    require(document["scope_sha256"] == expected_scope_sha256)
    objects = document["objects"]
    require(type(objects) is list and 1 <= len(objects) <= 100)
    scoped = {obj["object_id"]: obj for obj in refs["objects"]}
    seen: set[str] = set()
    targets: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for obj in objects:
        require(
            type(obj) is dict
            and set(obj)
            == {"object_id", "canonical_id", "content_sha256", "relationship", "target"}
        )
        identity = obj["object_id"]
        require(type(identity) is str and identity in scoped and identity not in seen)
        seen.add(identity)
        require(
            all(
                obj[key] == scoped[identity][key]
                for key in ("object_id", "canonical_id", "content_sha256")
            )
        )
        relationship = obj["relationship"]
        require(
            type(relationship) is str and relationship in {"canonical", "reference", "unresolved"}
        )
        target = obj["target"]
        if relationship == "unresolved":
            require(target is None)
            continue
        require(type(target) is dict and set(target) == {"owner_id", "native_object_id"})
        owner = target["owner_id"]
        native = target["native_object_id"]
        require(type(owner) is str)
        require(type(native) is str and 0 < len(native) <= 512 and bool(native.strip()))
        if relationship == "canonical":
            require(owner == "gfjd" and native == obj["canonical_id"])
        else:
            require(owner in refs["partners"])
            targets.setdefault((owner, native), []).append(obj)
    require(seen == set(scoped))
    groups = []
    for (owner, native), members in sorted(targets.items()):
        hashes = {obj["content_sha256"] for obj in members if obj["content_sha256"] is not None}
        require(len(hashes) <= 1)
        if len(members) > 1:
            groups.append(
                {
                    "owner_id": owner,
                    "native_object_id": native,
                    "object_ids": sorted(obj["object_id"] for obj in members),
                    "declared_nonnull_content_sha256": sorted(hashes),
                    "missing_content_ids": sorted(
                        obj["object_id"] for obj in members if obj["content_sha256"] is None
                    ),
                }
            )
    components = (
        federation_references,
        federation_metadata,
        federation_rdf_input,
        medallion_estate,
    )
    return {
        "contract_version": "gfjd-canonical-ownership-report-v1",
        "declaration_consistency": "verified",
        "coverage": "scoped-responsibility-declarations-only",
        "declaration_sha256": expected_sha256,
        "scope_sha256": expected_scope_sha256,
        "estate_manifest_sha256": refs["estate_manifest_sha256"],
        "estate_input_sha256": {name: _sha(value) for name, value in sorted(estate_inputs.items())},
        "metadata_sha256": sorted(metadata_bank),
        "reference_report_sha256": _sha(_encode(refs)),
        "implementation_sha256": _sha(Path(__file__).read_bytes()),
        "component_implementation_sha256": {
            module.__name__: _sha(Path(cast(str, module.__file__)).read_bytes())
            for module in components
        },
        "objects": sorted(objects, key=lambda obj: obj["object_id"]),
        "object_count": len(objects),
        "shared_target_groups": groups,
        "unresolved_ids": sorted(
            obj["object_id"] for obj in objects if obj["relationship"] == "unresolved"
        ),
        "missing_content_ids": sorted(
            obj["object_id"] for obj in objects if obj["content_sha256"] is None
        ),
        "factual_states": dict.fromkeys(
            (
                "authenticated_ownership",
                "legal_rights",
                "transfers",
                "partner_acceptance",
                "observed_custody",
                "semantic_equivalence",
                "estate_wide_zero_copy",
            ),
            "unverified",
        ),
        "authority": {**refs["authority"], "ownership_transfer": False, "execution": False},
        "filesystem_access": "compiler-and-helper-implementation-fingerprints-only",
        "limitations": [
            "gfjd-reference-handles-do-not-assign-partner-ownership",
            "equal-bytes-do-not-merge-identities",
            "null-content-bindings-not-inferred",
            "no-partner-authority-or-transfer-execution",
        ],
    }


def assess_ownership_references(
    raw: bytes,
    expected_sha256: str,
    scope_raw: bytes,
    expected_scope_sha256: str,
    metadata_bank: dict[str, bytes],
    estate_inputs: dict[str, bytes],
) -> dict[str, Any]:
    """Reconcile the complete scope first, then check declarations without authentication."""
    try:
        return _assess(
            raw, expected_sha256, scope_raw, expected_scope_sha256, metadata_bank, estate_inputs
        )
    except Exception:
        raise MetadataError("Ownership declaration contract violation") from None


def verify_ownership_references(
    raw: bytes,
    expected_sha256: str,
    scope_raw: bytes,
    expected_scope_sha256: str,
    metadata_bank: dict[str, bytes],
    estate_inputs: dict[str, bytes],
    report: dict[str, Any],
) -> None:
    """Recompute every report field with JSON-type-sensitive comparison."""
    try:
        expected = assess_ownership_references(
            raw, expected_sha256, scope_raw, expected_scope_sha256, metadata_bank, estate_inputs
        )
        require(type(report) is dict and _encode(report) == _encode(expected))
    except Exception:
        raise MetadataError("Ownership declaration contract violation") from None
