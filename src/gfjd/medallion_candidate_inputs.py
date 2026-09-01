"""Bound complete supplied candidate inputs; no scan, loader or evidence execution."""

import hashlib
import json
import re
from typing import Any

from blake3 import blake3

from gfjd.medallion_replay import _timestamp
from gfjd.medallion_restore_inputs import _locator, preflight
from gfjd.security import SECRET_PATTERNS

MIB = 1024 * 1024
ROLES = frozenset(
    {"data", "metadata", "transformation", "package", "manifest", "dependency", "locator_record"}
)
ROOTS = {
    "qualification": "scope_raw scope_sha256 layer_contract_raw record_bank payload_bank as_of",
    "restore": "plan_raw expected_plan_sha256 scope_raw expected_scope_sha256 "
    "layer_contract_raw replica_banks",
    "lifecycle": "plan_raw expected_plan_sha256 scope_raw layer_contract_raw "
    "checkpoint_raw event_bank receipt_bank",
    "dependencies": "lock_raw sbom_raw package_bindings_raw project_name",
}


class CandidateInputError(ValueError):
    """Fixed diagnostic for rejected candidate declarations."""


def _require(value: bool) -> None:
    if not value:
        raise CandidateInputError("Candidate input contract violation")


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    ).encode()


def _keys(value: Any, names: str) -> None:
    _require(type(value) is dict and set(value) == set(names.split()))


def _digest(value: Any) -> None:
    _require(type(value) is str and re.fullmatch(r"[a-f0-9]{64}", value) is not None)


def _identity(value: Any) -> None:
    _require(
        type(value) is str and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}", value) is not None
    )


def _control_strings(value: Any) -> None:
    pending = [value]
    while pending:
        item = pending.pop()
        if type(item) is str:
            _require(not any(pattern.search(item) for _, pattern in SECRET_PATTERNS))
        elif type(item) is dict:
            pending.extend(child for pair in item.items() for child in pair)
        elif type(item) is list:
            pending.extend(item)


def _tree(value: Any) -> None:
    pending = [(value, 0)]
    nodes = byte_count = text_count = 0
    while pending:
        item, depth = pending.pop()
        nodes += 1
        _require(nodes <= 50000 and depth <= 12)
        kind = type(item)
        if kind is bytes:
            _require(len(item) <= 8 * MIB)
            byte_count += len(item)
            _require(byte_count <= 64 * MIB)
        elif kind is str:
            _require(
                len(item) <= 4096
                and all(
                    ord(c) >= 32 and not 127 <= ord(c) <= 159 and not 0xD800 <= ord(c) <= 0xDFFF
                    for c in item
                )
            )
            text_count += len(item.encode("utf-8"))
            _require(text_count <= MIB)
        elif kind is int:
            _require(abs(item).bit_length() <= 4096)
        elif kind is dict:
            _require(len(item) <= 2000 and all(type(key) is str for key in item))
            pending.extend((child, depth + 1) for pair in item.items() for child in pair)
        elif kind is list:
            _require(len(item) <= 2000)
            pending.extend((child, depth + 1) for child in item)
        else:
            _require(kind is bool or item is None)


def _descriptor(value: Any) -> Any:
    kind = type(value)
    if kind is bytes:
        return ["bytes", _sha(value), len(value)]
    if kind is dict:
        return ["dict", [[key, _descriptor(value[key])] for key in sorted(value)]]
    if kind is list:
        return ["list", [_descriptor(child) for child in value]]
    return [{str: "str", int: "int", bool: "bool", type(None): "null"}[kind], value]


def bundle_fingerprint(bundle: Any) -> str:
    """Bind a bounded typed tree, not its authenticity or semantic correctness."""
    try:
        _tree(bundle)
        return _sha(_canonical(_descriptor(bundle)))
    except Exception:
        raise CandidateInputError("Candidate input contract violation") from None


def _prepare(
    plan_raw: bytes,
    expected_plan_sha256: str,
    scope_raw: bytes,
    candidate_bank: dict[str, bytes],
    evidence_bundles: dict[str, Any],
) -> dict[str, Any]:
    plan, scope = preflight(plan_raw), preflight(scope_raw)
    _control_strings(plan)
    _control_strings(scope)
    _keys(plan, "contract_version state candidate_id as_of scope_sha256 evidence_bindings")
    _require(
        plan["contract_version"] == "gfjd-candidate-assurance-plan-v1"
        and plan["state"] == "preparation"
    )
    _identity(plan["candidate_id"])
    _timestamp(plan["as_of"])
    _digest(expected_plan_sha256)
    _digest(plan["scope_sha256"])
    _keys(scope, "contract_version candidate_id objects")
    _require(
        scope["contract_version"] == "gfjd-candidate-assurance-scope-v1"
        and scope["candidate_id"] == plan["candidate_id"]
    )
    _require(type(scope["objects"]) is list and 1 <= len(scope["objects"]) <= 1502)
    identities: set[str] = set()
    facts: dict[str, tuple[Any, ...]] = {}
    categories: dict[str, set[str]] = {role: set() for role in ROLES}
    for obj in scope["objects"]:
        _keys(
            obj,
            "object_id logical_object_id edition_id layer role lifecycle sha256 blake3 "
            "size_bytes media_type edges locators",
        )
        for key in ("object_id", "logical_object_id", "edition_id"):
            _identity(obj[key])
        _require(obj["object_id"] not in identities)
        identities.add(obj["object_id"])
        _require(
            type(obj["layer"]) is str
            and obj["layer"] in {"b0", "b1", "silver", "gold", "platinum", "cross_layer"}
        )
        _require(type(obj["role"]) is str and obj["role"] in ROLES)
        _require(
            type(obj["lifecycle"]) is str
            and obj["lifecycle"] in {"active", "quarantined", "withdrawn", "tombstoned"}
        )
        _digest(obj["sha256"])
        _digest(obj["blake3"])
        _require(type(obj["size_bytes"]) is int and 0 < obj["size_bytes"] <= 8 * MIB)
        media = obj["media_type"]
        _require(
            type(media) is str
            and len(media) <= 128
            and re.fullmatch(r"[a-z][a-z0-9.+-]*/[a-z][a-z0-9.+-]*", media) is not None
        )
        fact = obj["blake3"], obj["size_bytes"], media
        digest = obj["sha256"]
        _require(digest not in facts or facts[digest] == fact)
        facts[digest] = fact
        categories[obj["role"]].add(digest)
        _keys(obj["locators"], "github huggingface")
        for provider, host in (("github", "github.com"), ("huggingface", "huggingface.co")):
            if obj["locators"][provider] is not None:
                _locator(obj["locators"][provider], host)
    for obj in scope["objects"]:
        _require(type(obj["edges"]) is list and len(obj["edges"]) <= 2000)
        seen = set()
        for edge in obj["edges"]:
            _keys(edge, "relation target_object_id")
            _require(
                type(edge["relation"]) is str
                and edge["relation"]
                in {
                    "source",
                    "metadata",
                    "transformation",
                    "package_member",
                    "dependency",
                    "manifest",
                    "locator",
                }
            )
            _identity(edge["target_object_id"])
            pair = edge["relation"], edge["target_object_id"]
            _require(pair not in seen and edge["target_object_id"] in identities)
            seen.add(pair)
    _require(type(candidate_bank) is dict and set(candidate_bank) == set(facts))
    for digest, raw in candidate_bank.items():
        _require(type(raw) is bytes and 0 < len(raw) <= 8 * MIB and len(raw) == facts[digest][1])
    category_bytes = {
        role: sum(len(candidate_bank[d]) for d in digests) for role, digests in categories.items()
    }
    _require(all(size <= 8 * MIB for size in category_bytes.values()))
    total = sum(len(raw) for raw in candidate_bank.values())
    _require(total <= 26 * MIB)
    _keys(plan["evidence_bindings"], " ".join(ROOTS))
    selected = set()
    for name, digest in plan["evidence_bindings"].items():
        if digest is not None:
            _digest(digest)
            selected.add(name)
    _require(type(evidence_bundles) is dict and set(evidence_bundles) == selected)
    _tree(evidence_bundles)
    for name, bundle in evidence_bundles.items():
        _keys(bundle, ROOTS[name])
        for key, value in bundle.items():
            required = (
                bytes
                if key.endswith("_raw")
                else dict
                if key.endswith("_bank") or key == "replica_banks"
                else str
            )
            _require(type(value) is required)
    # Every candidate and evidence budget is established before any hash work.
    _require(_sha(plan_raw) == expected_plan_sha256 and _sha(scope_raw) == plan["scope_sha256"])
    for digest, raw in candidate_bank.items():
        _require(_sha(raw) == digest and blake3(raw).hexdigest() == facts[digest][0])
    fingerprints = {
        name: _sha(_canonical(_descriptor(bundle)))
        for name, bundle in sorted(evidence_bundles.items())
    }
    _require(
        all(plan["evidence_bindings"][name] == digest for name, digest in fingerprints.items())
    )
    return {
        "plan": plan,
        "scope": scope,
        "candidate_bank": candidate_bank,
        "evidence_bundles": evidence_bundles,
        "bundle_fingerprints": fingerprints,
        "inventory_report": {
            "object_count": len(identities),
            "unique_content_count": len(facts),
            "unique_bytes": total,
            "category_bytes": category_bytes,
            "category_counts": {role: len(values) for role, values in categories.items()},
            "fixity": "verified",
        },
    }


def prepare_candidate_inputs(
    plan_raw: bytes,
    expected_plan_sha256: str,
    scope_raw: bytes,
    candidate_bank: dict[str, bytes],
    evidence_bundles: dict[str, Any],
) -> dict[str, Any]:
    """Preflight all bytes and bind declarations without executing native evidence."""
    try:
        return _prepare(plan_raw, expected_plan_sha256, scope_raw, candidate_bank, evidence_bundles)
    except Exception:
        raise CandidateInputError("Candidate input contract violation") from None
