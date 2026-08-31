"""Bounded declared-scope coverage, not evidence meaning or layer qualification.

Only supplied metadata bytes are parsed. Missing/inactive layers remain visible;
no payload, network, authority decision or promotion is accessed or performed.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any

from .medallion import record_sha256, verify_layer_record

VERSION = "gfjd-qualification-scope-v1"
LAYERS = ("b0", "b1", "silver", "gold", "platinum")
LAYER_CONTRACT_SHA256 = "5e30b90497a14281ae28c98c2dcf52a2c1509d18a7d59f85391bb991e76f9065"
MAX_JSON_BYTES = 1024 * 1024
MAX_OBJECTS = 100


class QualificationInputError(ValueError):
    """Declared scope or metadata input integrity cannot be established."""


def _require(condition: bool) -> None:
    if not condition:
        raise QualificationInputError("qualification input contract failed")


def canonical(value: Any) -> bytes:
    try:
        return json.dumps(
            value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False
        ).encode("utf-8")
    except (ValueError, TypeError, UnicodeError, RecursionError):
        raise QualificationInputError("qualification input contract failed") from None


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    _require(len(pairs) <= 100)
    result: dict[str, Any] = {}
    for key, value in pairs:
        _require(key not in result and len(key) <= 128)
        result[key] = value
    return result


def _nonfinite(value: str) -> None:
    raise QualificationInputError("qualification input contract failed")


def parse(raw: bytes) -> Any:
    try:
        _require(isinstance(raw, bytes) and 0 < len(raw) <= MAX_JSON_BYTES)
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs, parse_constant=_nonfinite)
        pending = [value]
        while pending:
            item = pending.pop()
            if isinstance(item, dict):
                pending.extend(item.keys())
                pending.extend(item.values())
            elif isinstance(item, list):
                pending.extend(item)
            elif isinstance(item, float):
                _require(math.isfinite(item))
            elif isinstance(item, str):
                _require(not any(0xD800 <= ord(char) <= 0xDFFF for char in item))
        return value
    except (ValueError, TypeError, UnicodeError, RecursionError):
        raise QualificationInputError("qualification input contract failed") from None


def _identity(value: Any) -> None:
    _require(
        isinstance(value, str)
        and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}", value) is not None
    )


def _digest(value: Any) -> None:
    _require(isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None)


def parse_scope(raw: bytes, expected_sha256: str) -> dict[str, Any]:
    """Validate a separately bound denominator; this does not authenticate its owner."""
    _digest(expected_sha256)
    _require(
        isinstance(raw, bytes) and 0 < len(raw) <= MAX_JSON_BYTES and sha(raw) == expected_sha256
    )
    scope = parse(raw)
    _require(isinstance(scope, dict) and set(scope) == {"contract_version", "objects"})
    _require(scope["contract_version"] == VERSION)
    objects = scope["objects"]
    _require(isinstance(objects, list) and 0 < len(objects) <= MAX_OBJECTS)
    seen = set()
    for item in objects:
        _require(isinstance(item, dict) and set(item) == {"object_id", "edition_id", "layers"})
        _identity(item["object_id"])
        _identity(item["edition_id"])
        _require(item["object_id"] not in seen)
        seen.add(item["object_id"])
        states = item["layers"]
        _require(isinstance(states, dict) and set(states) == set(LAYERS))
        for state in states.values():
            _require(
                isinstance(state, dict)
                and set(state) == {"state", "reason_codes", "disposition_reference"}
            )
            _require(
                isinstance(state["state"], str)
                and state["state"] in {"active", "absent", "quarantined", "withdrawn", "tombstoned"}
            )
            reasons = state["reason_codes"]
            _require(isinstance(reasons, list) and len(reasons) <= 32)
            for reason in reasons:
                _identity(reason)
            _require(len(reasons) == len(set(reasons)))
            if state["state"] in {"quarantined", "withdrawn", "tombstoned"}:
                _require(bool(reasons))
                _identity(state["disposition_reference"])
            else:
                _require(reasons == [] and state["disposition_reference"] is None)
    return dict(scope)


def bind_layer_records(
    scope_raw: bytes,
    scope_sha256: str,
    layer_contract_raw: bytes,
    record_bank: dict[str, bytes],
) -> dict[str, Any]:
    """Resolve metadata records, preserving all expected object/layer cells.

    Wrapper: object_id, edition_id, record (existing medallion record), artifacts
    (role-to-digest metadata). These references are not claimed verified evidence.
    A missing record is distinct from an invalid one; unexplained extra records
    or duplicate scope cells fail the complete input contract.
    """
    try:
        scope = parse_scope(scope_raw, scope_sha256)
        _require(
            isinstance(layer_contract_raw, bytes)
            and 0 < len(layer_contract_raw) <= MAX_JSON_BYTES
            and sha(layer_contract_raw) == LAYER_CONTRACT_SHA256
        )
        layer_contract = parse(layer_contract_raw)
        expected = {item["object_id"]: item for item in scope["objects"]}
        _require(isinstance(record_bank, dict) and len(record_bank) <= MAX_OBJECTS * len(LAYERS))
        supplied: dict[tuple[str, str], tuple[str, dict[str, Any]]] = {}
        total = 0
        for digest, raw in record_bank.items():
            _digest(digest)
            _require(isinstance(raw, bytes))
            total += len(raw)
            _require(total <= 8 * MAX_JSON_BYTES and sha(raw) == digest)
            wrapper = parse(raw)
            _require(
                isinstance(wrapper, dict)
                and set(wrapper) == {"object_id", "edition_id", "record", "artifacts"}
            )
            identity, edition = wrapper["object_id"], wrapper["edition_id"]
            _identity(identity)
            _identity(edition)
            _require(identity in expected and expected[identity]["edition_id"] == edition)
            record = wrapper["record"]
            _require(isinstance(record, dict) and record.get("object_id") == identity)
            layer = record.get("layer")
            _require(isinstance(layer, str) and layer in LAYERS)
            key = identity, layer
            _require(key not in supplied)
            _require(expected[identity]["layers"][layer]["state"] != "absent")
            _require(record.get("lifecycle_state") == expected[identity]["layers"][layer]["state"])
            refs = wrapper["artifacts"]
            _require(isinstance(refs, dict) and len(refs) <= 32)
            for role, reference in refs.items():
                _identity(role)
                _digest(reference)
            supplied[key] = digest, wrapper
        cells = []
        for identity in sorted(expected):
            item = expected[identity]
            cell_status: dict[str, str] = {}
            cell_blockers: dict[str, list[str]] = {}
            for index, layer in enumerate(LAYERS):
                lifecycle = item["layers"][layer]
                entry = supplied.get((identity, layer))
                errors: list[str] = []
                predecessor = supplied.get((identity, LAYERS[index - 1])) if index else None
                if lifecycle["state"] != "active":
                    status = "absent" if lifecycle["state"] == "absent" else "lifecycle_blocked"
                elif entry is None:
                    status = "missing"
                else:
                    record = entry[1]["record"]
                    try:
                        if verify_layer_record(record, layer_contract):
                            errors.append("record_structure_invalid")
                    except (TypeError, ValueError, KeyError, AttributeError):
                        errors.append("record_structure_invalid")
                    evidence = record.get("evidence")
                    if layer == "b0" and (
                        not isinstance(evidence, dict)
                        or evidence.get("source_edition_id") != item["edition_id"]
                    ):
                        errors.append("edition_binding_invalid")
                    if (
                        index
                        and predecessor is not None
                        and (
                            not isinstance(evidence, dict)
                            or evidence.get("predecessor_receipt_sha256")
                            != record_sha256(predecessor[1]["record"])
                        )
                    ):
                        errors.append("predecessor_binding_invalid")
                    status = "invalid" if errors else "structurally_valid"
                predecessor_state = item["layers"][LAYERS[index - 1]]["state"] if index else None
                dependency_blockers = []
                if index and (predecessor is None or predecessor_state != "active"):
                    dependency_blockers.append("immediate_predecessor_unavailable_or_inactive")
                elif index and cell_status[LAYERS[index - 1]] != "structurally_valid":
                    dependency_blockers.append("immediate_predecessor_structure_invalid")
                if index and cell_blockers[LAYERS[index - 1]]:
                    dependency_blockers.append("upstream_dependency_unresolved")
                cell_status[layer] = status
                cell_blockers[layer] = dependency_blockers
                cells.append(
                    {
                        "object_id": identity,
                        "edition_id": item["edition_id"],
                        "layer": layer,
                        "lifecycle": lifecycle,
                        "record_sha256": entry[0] if entry else None,
                        "record_status": status,
                        "errors": sorted(errors),
                        "dependency_blockers": dependency_blockers,
                        "artifacts": entry[1]["artifacts"]
                        if entry and lifecycle["state"] == "active"
                        else {},
                        "evidence_meaning_verified": False,
                        "promotion_authorized": False,
                    }
                )
        result = {
            "contract_version": VERSION,
            "scope_sha256": scope_sha256,
            "layer_contract_sha256": LAYER_CONTRACT_SHA256,
            "implementation_sha256": sha(Path(__file__).read_bytes()),
            "record_bank_sha256": sha(canonical(sorted(record_bank))),
            "declared_object_count": len(expected),
            "expected_layer_cell_count": len(expected) * len(LAYERS),
            "present_record_count": len(supplied),
            "coverage": cells,
            "coverage_basis": "separately bound declared scope; not global coverage",
            "acceptance_not_assessed": True,
            "promotion_authorized": False,
        }
        result["report_sha256"] = sha(canonical(result))
        return result
    except (
        ValueError,
        TypeError,
        KeyError,
        AttributeError,
        UnicodeError,
        RecursionError,
        OverflowError,
    ):
        raise QualificationInputError("qualification input contract failed") from None


def verify_bindings(
    scope_raw: bytes,
    scope_sha256: str,
    layer_contract_raw: bytes,
    record_bank: dict[str, bytes],
    report: dict[str, Any],
) -> None:
    _require(
        canonical(report)
        == canonical(bind_layer_records(scope_raw, scope_sha256, layer_contract_raw, record_bank))
    )
