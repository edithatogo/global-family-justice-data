"""Complete supplied replica inventory preparation, not public retrieval.

Payload/auxiliary bytes receive fixity only. Structured roots and wrappers are
preflighted before older qualification parsers. Only existing helper compiler
fingerprints read files; provider locators and source identifiers are not opened.
"""

import hashlib
import json
import math
import re
from typing import Any
from urllib.parse import urlsplit

from blake3 import blake3

from gfjd import medallion_qualification_inputs as inputs
from gfjd.medallion_qualification_payloads import ROLES
from gfjd.medallion_replay import _timestamp

MIB = 1024 * 1024
PROVIDERS = {"github": "github.com", "huggingface": "huggingface.co"}


class RestoreInputError(ValueError):
    """Invalid supplied inventory, without input-bearing diagnostics."""


def _require(value: bool) -> None:
    if not value:
        raise RestoreInputError("Replica input contract violation")


def _digest(value: Any) -> None:
    _require(type(value) is str and re.fullmatch(r"[0-9a-f]{64}", value) is not None)


def _identity(value: Any) -> None:
    _require(
        type(value) is str and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}", value) is not None
    )


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    _require(len(pairs) <= 2000)
    result = {}
    for key, value in pairs:
        _require(key not in result)
        result[key] = value
    return result


def preflight(raw: bytes) -> Any:
    """Strict bounded structured metadata only; never apply to arbitrary payloads."""
    try:
        _require(type(raw) is bytes and 0 < len(raw) <= MIB)
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs)
        pending = [(value, 0)]
        nodes = 0
        while pending:
            item, depth = pending.pop()
            nodes += 1
            _require(nodes <= 50000 and depth <= 16)
            if isinstance(item, str):
                _require(
                    len(item) <= 4096
                    and all(
                        ord(char) >= 32
                        and not 127 <= ord(char) <= 159
                        and not 0xD800 <= ord(char) <= 0xDFFF
                        for char in item
                    )
                )
            elif isinstance(item, (dict, list)):
                _require(len(item) <= 2000)
                if isinstance(item, dict):
                    pending.extend((key, depth + 1) for key in item)
                    pending.extend((child, depth + 1) for child in item.values())
                else:
                    pending.extend((child, depth + 1) for child in item)
            elif isinstance(item, float):
                _require(math.isfinite(item))
        return value
    except Exception:
        raise RestoreInputError("Replica input contract violation") from None


def _keys(value: Any, fields: set[str]) -> None:
    _require(type(value) is dict and set(value) == fields)


def _locator(value: Any, host: str) -> None:
    _require(type(value) is str and value.isascii() and 0 < len(value) <= 4096)
    _require(all(32 < ord(c) < 127 for c in value))
    _require(not re.search(r'[\\<>"{}|^`?#]', value))
    _require(re.search(r"%(?![A-Fa-f0-9]{2})", value) is None)
    parsed = urlsplit(value)
    _require(parsed.scheme == "https" and parsed.netloc == host and bool(parsed.path))
    _require(not parsed.query and not parsed.fragment)


def _prepare(
    plan_raw: bytes,
    expected_plan_sha256: str,
    scope_raw: bytes,
    expected_scope_sha256: str,
    layer_contract_raw: bytes,
    replica_bank: dict[str, bytes],
    provider: str,
) -> dict[str, Any]:
    plan = preflight(plan_raw)
    _keys(
        plan,
        {
            "contract_version",
            "state",
            "release_id",
            "scope_sha256",
            "layer_contract_sha256",
            "as_of",
            "expected_qualification_sha256",
            "record_sha256",
            "payload_sha256",
            "auxiliary_sha256",
            "inventory",
            "providers",
        },
    )
    _require(
        plan["contract_version"] == "gfjd-two-replica-restore-plan-v1"
        and plan["state"] == "preparation"
    )
    _identity(plan["release_id"])
    _timestamp(plan["as_of"])
    for digest in (
        expected_plan_sha256,
        expected_scope_sha256,
        plan["scope_sha256"],
        plan["layer_contract_sha256"],
        plan["expected_qualification_sha256"],
    ):
        _digest(digest)
    _require(plan["scope_sha256"] == expected_scope_sha256)
    _require(plan["layer_contract_sha256"] == inputs.LAYER_CONTRACT_SHA256)
    categories = {}
    for key, field in (
        ("records", "record_sha256"),
        ("payloads", "payload_sha256"),
        ("auxiliary", "auxiliary_sha256"),
    ):
        values = plan[field]
        _require(type(values) is list and len(values) <= 500)
        for digest in values:
            _digest(digest)
        _require(len(set(values)) == len(values))
        categories[key] = set(values)
    categories["roots"] = {expected_scope_sha256, inputs.LAYER_CONTRACT_SHA256}
    expected = set().union(*categories.values())
    _require(len(expected) <= 1502)
    inventory = plan["inventory"]
    _require(type(inventory) is list and len(inventory) == len(expected))
    declared = {}
    for item in inventory:
        _keys(item, {"sha256", "blake3", "size_bytes"})
        _digest(item["sha256"])
        _digest(item["blake3"])
        _require(type(item["size_bytes"]) is int and 0 <= item["size_bytes"] <= 8 * MIB)
        _require(item["sha256"] not in declared)
        declared[item["sha256"]] = item
    _require(set(declared) == expected)
    _keys(plan["providers"], set(PROVIDERS))
    _require(type(provider) is str and provider in PROVIDERS)
    for name, host in PROVIDERS.items():
        declaration = plan["providers"][name]
        _keys(declaration, {"locators"})
        _require(type(declaration["locators"]) is dict and set(declaration["locators"]) == expected)
        for value in declaration["locators"].values():
            _locator(value, host)
    _require(type(replica_bank) is dict and set(replica_bank) == expected)
    for raw in replica_bank.values():
        _require(type(raw) is bytes and len(raw) <= 8 * MIB)
    category_bytes = {
        name: sum(len(replica_bank[digest]) for digest in members)
        for name, members in categories.items()
    }
    _require(all(category_bytes[name] <= 8 * MIB for name in ("records", "payloads", "auxiliary")))
    unique_bytes = sum(len(raw) for raw in replica_bank.values())
    _require(unique_bytes <= 26 * MIB)
    # Preflight roots and every wrapper before any hashing or legacy parsing.
    preflight(scope_raw)
    preflight(layer_contract_raw)
    for digest in categories["roots"]:
        preflight(replica_bank[digest])
    wrappers = {digest: preflight(replica_bank[digest]) for digest in sorted(categories["records"])}
    payload_union: set[str] = set()
    edges = []
    for digest, wrapper in wrappers.items():
        _keys(wrapper, {"object_id", "edition_id", "record", "artifacts"})
        _identity(wrapper["object_id"])
        _identity(wrapper["edition_id"])
        record = wrapper["record"]
        _require(type(record) is dict)
        _require(type(wrapper["artifacts"]) is dict and len(wrapper["artifacts"]) <= 32)
        for role, reference in sorted(wrapper["artifacts"].items()):
            _identity(role)
            _digest(reference)
            payload_union.add(reference)
            edges.append(
                {
                    "record_sha256": digest,
                    "object_id": wrapper["object_id"],
                    "edition_id": wrapper["edition_id"],
                    "layer": record.get("layer"),
                    "lifecycle": record.get("lifecycle_state"),
                    "artifact_role": role,
                    "payload_sha256": reference,
                    "processing_eligible": False,
                }
            )
    _require(payload_union == categories["payloads"])
    _require(hashlib.sha256(plan_raw).hexdigest() == expected_plan_sha256)
    _require(hashlib.sha256(scope_raw).hexdigest() == expected_scope_sha256)
    _require(hashlib.sha256(layer_contract_raw).hexdigest() == inputs.LAYER_CONTRACT_SHA256)
    _require(replica_bank[expected_scope_sha256] == scope_raw)
    _require(replica_bank[inputs.LAYER_CONTRACT_SHA256] == layer_contract_raw)
    for digest, raw in sorted(replica_bank.items()):
        item = declared[digest]
        _require(item["size_bytes"] == len(raw))
        _require(hashlib.sha256(raw).hexdigest() == digest)
        _require(blake3(raw).hexdigest() == item["blake3"])
    records = {digest: replica_bank[digest] for digest in sorted(categories["records"])}
    binding = inputs.bind_layer_records(
        replica_bank[expected_scope_sha256],
        expected_scope_sha256,
        replica_bank[inputs.LAYER_CONTRACT_SHA256],
        records,
    )
    eligible_records = set()
    for cell in binding["coverage"]:
        if cell["record_status"] == "structurally_valid":
            _require(set(cell["artifacts"]) <= ROLES[cell["layer"]])
            eligible_records.add(cell["record_sha256"])
    eligible_payloads = set()
    for edge in edges:
        edge["processing_eligible"] = edge["record_sha256"] in eligible_records
        if edge["processing_eligible"]:
            eligible_payloads.add(edge["payload_sha256"])
    return {
        "scope_raw": replica_bank[expected_scope_sha256],
        "layer_contract_raw": replica_bank[inputs.LAYER_CONTRACT_SHA256],
        "record_bank": records,
        "eligible_payload_bank": {
            digest: replica_bank[digest] for digest in sorted(eligible_payloads)
        },
        "plan": plan,
        "binding": binding,
        "preservation_edges": edges,
        "inventory_report": {
            "provider": provider,
            "inventory_count": len(expected),
            "unique_bytes": unique_bytes,
            "category_counts": {name: len(members) for name, members in categories.items()},
            "category_bytes": category_bytes,
            "inventory": [declared[digest] for digest in sorted(declared)],
            "fixity": "verified",
        },
    }


def prepare_replica(
    plan_raw: bytes,
    expected_plan_sha256: str,
    scope_raw: bytes,
    expected_scope_sha256: str,
    layer_contract_raw: bytes,
    replica_bank: dict[str, bytes],
    provider: str,
) -> dict[str, Any]:
    """Prepare one complete supplied bank; no peer borrowing or payload decoding."""
    try:
        return _prepare(
            plan_raw,
            expected_plan_sha256,
            scope_raw,
            expected_scope_sha256,
            layer_contract_raw,
            replica_bank,
            provider,
        )
    except Exception:
        raise RestoreInputError("Replica input contract violation") from None
