"""Executable fail-closed contracts for GFJD medallion layer promotion."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from .io import canonical_json_bytes


class MedallionContractError(ValueError):
    """Raised when a layer contract or promotion record is invalid."""


def load_layer_contract(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise MedallionContractError(f"invalid layer contract: {exc}") from exc
    if not isinstance(payload, dict):
        raise MedallionContractError("layer contract must be an object")
    contract: dict[str, Any] = payload
    errors = verify_layer_contract(contract)
    if errors:
        raise MedallionContractError("; ".join(errors))
    return contract


def verify_layer_contract(contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if contract.get("contract_version") != "gfjd-medallion-layers-v1":
        errors.append("unsupported contract_version")
    layers = contract.get("layers")
    if not isinstance(layers, list):
        return [*errors, "layers must be an array"]
    expected = ["b0", "b1", "silver", "gold", "platinum"]
    ids = [item.get("id") for item in layers if isinstance(item, dict)]
    ordinals = [item.get("ordinal") for item in layers if isinstance(item, dict)]
    if (
        ids != expected
        or ordinals != list(range(len(expected)))
        or any(type(ordinal) is not int for ordinal in ordinals)
    ):
        errors.append("layers and ordinals must be the canonical ordered sequence")
    for item in layers:
        required = item.get("required_evidence") if isinstance(item, dict) else None
        if (
            not isinstance(required, list)
            or not required
            or not all(isinstance(field, str) and field.strip() for field in required)
            or len(required) != len(set(required))
        ):
            errors.append("each layer requires unique non-empty evidence fields")
    quarantine = contract.get("quarantine", {})
    if not isinstance(quarantine, dict):
        return [*errors, "quarantine must be an object"]
    if quarantine.get("orthogonal") is not True:
        errors.append("quarantine must be orthogonal")
    if quarantine.get("visible_in_coverage") is not True:
        errors.append("quarantine must remain visible in coverage")
    if quarantine.get("promotion_prohibited") is not True:
        errors.append("quarantine must prohibit promotion")
    if quarantine.get("required_fields") != ["reason_codes", "disposition_reference"]:
        errors.append("quarantine required fields are not canonical")
    if contract.get("lifecycle_states") != [
        "active",
        "quarantined",
        "withdrawn",
        "tombstoned",
    ]:
        errors.append("lifecycle states are not canonical")
    return errors


def verify_layer_record(record: dict[str, Any], contract: dict[str, Any]) -> list[str]:
    """Validate one independently evidenced layer record without inferring maturity."""

    errors = verify_layer_contract(contract)
    if errors:
        return errors
    layer_index = {item["id"]: item for item in contract["layers"]}
    layer = record.get("layer")
    if not isinstance(layer, str) or layer not in layer_index:
        return ["record layer is not canonical"]
    if record.get("contract_version") != contract["contract_version"]:
        errors.append("record contract_version does not match")
    if not _nonblank(record.get("object_id")):
        errors.append("object_id is required")
    state = record.get("lifecycle_state")
    if state not in contract["lifecycle_states"]:
        errors.append("lifecycle_state is not canonical")
    evidence = record.get("evidence")
    if not isinstance(evidence, dict):
        return [*errors, "evidence must be an object"]
    for field in layer_index[layer]["required_evidence"]:
        if not _nonblank(evidence.get(field)):
            errors.append(f"{layer} evidence is missing {field}")
    for field, value in evidence.items():
        if field.endswith("_sha256") and not _is_digest(value):
            errors.append(f"{field} must be a lowercase SHA-256 digest")
    if layer == "b0":
        if not _is_digest(evidence.get("content_blake3")):
            errors.append("content_blake3 must be a lowercase BLAKE3 digest")
        size = evidence.get("size_bytes")
        if isinstance(size, bool) or not isinstance(size, int) or size <= 0:
            errors.append("size_bytes must be a positive integer")
        if not isinstance(evidence.get("media_type"), str) or "/" not in evidence["media_type"]:
            errors.append("media_type must be an explicit type/subtype")
    if layer == "b1" and evidence.get("source_labels_preserved") is not True:
        errors.append("source_labels_preserved must be true")
    ordinal = int(layer_index[layer]["ordinal"])
    expected_previous = None if ordinal == 0 else contract["layers"][ordinal - 1]["id"]
    if record.get("previous_layer") != expected_previous:
        errors.append(f"previous_layer must be {expected_previous!r}")
    quarantine = record.get("quarantine")
    if state == "quarantined":
        if not isinstance(quarantine, dict):
            errors.append("quarantined records require quarantine evidence")
        else:
            reasons = quarantine.get("reason_codes")
            if (
                not isinstance(reasons, list)
                or not reasons
                or not all(_nonblank(x) for x in reasons)
            ):
                errors.append("quarantine reason_codes must be a non-empty array")
            if not _nonblank(quarantine.get("disposition_reference")):
                errors.append("quarantine disposition_reference is required")
    elif quarantine not in (None, {}):
        errors.append("quarantine evidence is only valid for quarantined records")
    return errors


def verify_promotion(
    previous: dict[str, Any], candidate: dict[str, Any], contract: dict[str, Any]
) -> list[str]:
    """Require an immediate, active predecessor and independently valid candidate."""

    errors = [f"previous: {error}" for error in verify_layer_record(previous, contract)]
    errors.extend(f"candidate: {error}" for error in verify_layer_record(candidate, contract))
    if errors:
        return errors
    if previous["object_id"] != candidate["object_id"]:
        errors.append("promotion cannot change object_id")
    if previous["lifecycle_state"] != "active":
        errors.append("only active records may be promoted")
    if candidate["lifecycle_state"] != "active":
        errors.append("promotion candidate must be active")
    if candidate["previous_layer"] != previous["layer"]:
        errors.append("promotion must use the immediate predecessor layer")
    predecessor_digest = hashlib.sha256(canonical_json_bytes(previous)).hexdigest()
    if candidate["evidence"].get("predecessor_receipt_sha256") != predecessor_digest:
        errors.append("candidate predecessor receipt digest does not match")
    return errors


def record_sha256(record: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json_bytes(record)).hexdigest()


def _nonblank(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return True
    return isinstance(value, str) and bool(value.strip())


def _is_digest(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None
