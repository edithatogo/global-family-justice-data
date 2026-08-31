"""Bounded lifecycle metadata inputs; no observed public operations.

All bytes are supplied. This helper validates complete historical inventory,
chains and scoped preparation receipts, not operation transitions or authority.
No source, locator, filesystem or network loader is invoked.
"""

import hashlib
import json
import re
from typing import Any

from gfjd.medallion_qualification_inputs import LAYER_CONTRACT_SHA256, LAYERS
from gfjd.medallion_replay import _timestamp
from gfjd.medallion_restore_inputs import preflight

MIB = 1024 * 1024
OPERATIONS = frozenset(
    {
        "register",
        "quarantine",
        "withdraw",
        "tombstone",
        "correct",
        "supersede",
        "republish",
        "observe",
    }
)
STATES = frozenset({"active", "quarantined", "withdrawn", "tombstoned"})
REASONS = frozenset(
    {
        "initial",
        "correction",
        "supersession",
        "withdrawal",
        "disclosure",
        "security",
        "rights",
        "policy",
        "restoration",
        "provider_loss",
        "monitoring",
    }
)
PROVIDER_STATUS = frozenset(
    {"available", "withdrawn", "tombstone_visible", "unavailable", "unknown"}
)


class LifecycleInputError(ValueError):
    """Invalid lifecycle input with fixed public diagnostics."""


def _require(value: bool) -> None:
    if not value:
        raise LifecycleInputError("Lifecycle input contract violation")


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    ).encode()


def _digest(value: Any) -> None:
    _require(type(value) is str and re.fullmatch(r"[a-f0-9]{64}", value) is not None)


def _identity(value: Any) -> None:
    _require(
        type(value) is str and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}", value) is not None
    )


def _keys(value: Any, names: str) -> None:
    _require(type(value) is dict and set(value) == set(names.split()))


def _digest_list(value: Any, limit: int, minimum: int = 0) -> None:
    _require(type(value) is list and minimum <= len(value) <= limit)
    for digest in value:
        _digest(digest)
    _require(len(set(value)) == len(value))


def _bank(bank: dict[str, bytes], expected: list[str], limit: int) -> int:
    _require(type(bank) is dict and len(bank) <= limit and set(bank) == set(expected))
    total = 0
    for digest, raw in bank.items():
        _digest(digest)
        _require(type(raw) is bytes and 0 < len(raw) <= MIB)
        total += len(raw)
    _require(total <= 8 * MIB)
    return total


def _prepare(
    plan_raw: bytes,
    expected_plan_sha256: str,
    scope_raw: bytes,
    layer_contract_raw: bytes,
    checkpoint_raw: bytes,
    event_bank: dict[str, bytes],
    receipt_bank: dict[str, bytes],
) -> dict[str, Any]:
    plan = preflight(plan_raw)
    _keys(
        plan,
        "contract_version state scope_sha256 layer_contract_sha256 checkpoint_sha256 "
        "event_sha256 receipt_sha256 as_of",
    )
    _require(
        plan["contract_version"] == "gfjd-lifecycle-plan-v1" and plan["state"] == "preparation"
    )
    _timestamp(plan["as_of"])
    for digest in (
        expected_plan_sha256,
        plan["scope_sha256"],
        plan["layer_contract_sha256"],
        plan["checkpoint_sha256"],
    ):
        _digest(digest)
    _require(plan["layer_contract_sha256"] == LAYER_CONTRACT_SHA256)
    _digest_list(plan["event_sha256"], 500, 1)
    _digest_list(plan["receipt_sha256"], 1500)
    event_bytes = _bank(event_bank, plan["event_sha256"], 500)
    receipt_bytes = _bank(receipt_bank, plan["receipt_sha256"], 1500)
    scope = preflight(scope_raw)
    preflight(layer_contract_raw)
    checkpoint = preflight(checkpoint_raw)
    events = [preflight(event_bank[digest]) for digest in plan["event_sha256"]]
    receipts = {digest: preflight(raw) for digest, raw in sorted(receipt_bank.items())}
    # Every individual/aggregate bound precedes all digest work.
    _require(_sha(plan_raw) == expected_plan_sha256)
    _require(_sha(scope_raw) == plan["scope_sha256"])
    _require(_sha(layer_contract_raw) == LAYER_CONTRACT_SHA256)
    _require(_sha(checkpoint_raw) == plan["checkpoint_sha256"])
    for bank in (event_bank, receipt_bank):
        for digest, raw in bank.items():
            _require(_sha(raw) == digest)
    _keys(checkpoint, "contract_version event_sha256")
    _require(checkpoint["contract_version"] == "gfjd-lifecycle-checkpoint-v1")
    _digest_list(checkpoint["event_sha256"], 500)
    prefix = checkpoint["event_sha256"]
    _require(plan["event_sha256"][: len(prefix)] == prefix)
    _keys(scope, "contract_version artifacts")
    _require(scope["contract_version"] == "gfjd-lifecycle-scope-v1")
    _require(type(scope["artifacts"]) is list and 1 <= len(scope["artifacts"]) <= 500)
    artifacts = {}
    edition_sources: dict[tuple[str, str], str] = {}
    content_facts: dict[str, tuple[str, int]] = {}
    for artifact in scope["artifacts"]:
        _keys(
            artifact,
            "artifact_id object_id edition_id layer source_sha256 content_sha256 "
            "content_blake3 size_bytes",
        )
        for key in ("artifact_id", "source_sha256", "content_sha256", "content_blake3"):
            _digest(artifact[key])
        _identity(artifact["object_id"])
        _identity(artifact["edition_id"])
        _require(type(artifact["layer"]) is str and artifact["layer"] in LAYERS)
        _require(type(artifact["size_bytes"]) is int and artifact["size_bytes"] >= 0)
        identity = artifact["artifact_id"]
        _require(identity not in artifacts)
        _require(
            _sha(
                _canonical({key: value for key, value in artifact.items() if key != "artifact_id"})
            )
            == identity
        )
        edition = artifact["object_id"], artifact["edition_id"]
        _require(
            edition not in edition_sources or edition_sources[edition] == artifact["source_sha256"]
        )
        edition_sources[edition] = artifact["source_sha256"]
        if artifact["layer"] == "b0":
            _require(artifact["content_sha256"] == artifact["source_sha256"])
        content = artifact["content_sha256"]
        facts = artifact["content_blake3"], artifact["size_bytes"]
        _require(content not in content_facts or content_facts[content] == facts)
        content_facts[content] = facts
        artifacts[identity] = artifact
    used_artifacts: set[str] = set()
    used_receipts: set[str] = set()
    event_ids: set[str] = set()
    operations: set[str] = set()
    previous_id = None
    previous_time = None
    for event in events:
        _keys(
            event,
            "contract_version event_id previous_event_id operation_id operation recorded_at "
            "artifact_id predecessor_artifact_id new_state reason_code "
            "disposition_sha256 receipt_sha256",
        )
        _require(event["contract_version"] == "gfjd-lifecycle-event-v1")
        for key in ("event_id", "artifact_id", "disposition_sha256"):
            _digest(event[key])
        _require(event["event_id"] not in event_ids)
        _require(
            _sha(_canonical({key: value for key, value in event.items() if key != "event_id"}))
            == event["event_id"]
        )
        _require(event["previous_event_id"] == previous_id)
        previous_id = event["event_id"]
        event_ids.add(previous_id)
        _identity(event["operation_id"])
        _require(event["operation_id"] not in operations)
        operations.add(event["operation_id"])
        _timestamp(event["recorded_at"])
        _require(previous_time is None or event["recorded_at"] > previous_time)
        _require(event["recorded_at"] <= plan["as_of"])
        previous_time = event["recorded_at"]
        for key, allowed in (
            ("operation", OPERATIONS),
            ("new_state", STATES),
            ("reason_code", REASONS),
        ):
            _require(type(event[key]) is str and event[key] in allowed)
        required_reason = {
            "register": "initial",
            "correct": "correction",
            "supersede": "supersession",
        }.get(event["operation"])
        _require(required_reason is None or event["reason_code"] == required_reason)
        _require(event["artifact_id"] in artifacts)
        used_artifacts.add(event["artifact_id"])
        predecessor = event["predecessor_artifact_id"]
        if predecessor is not None:
            _digest(predecessor)
            _require(predecessor in artifacts)
            used_artifacts.add(predecessor)
        _digest_list(event["receipt_sha256"], 2, 2)
        for digest in [event["disposition_sha256"], *event["receipt_sha256"]]:
            _require(digest in receipts)
            used_receipts.add(digest)
        disposition = receipts[event["disposition_sha256"]]
        _keys(
            disposition, "contract_version operation_id artifact_id recorded_at reason_code state"
        )
        _require(
            disposition["contract_version"] == "gfjd-lifecycle-disposition-v1"
            and disposition["state"] == "preparation"
        )
        _require(
            all(
                disposition[key] == event[key]
                for key in ("operation_id", "artifact_id", "recorded_at", "reason_code")
            )
        )
        for provider, digest in zip(
            ("github", "huggingface"), event["receipt_sha256"], strict=True
        ):
            receipt = receipts[digest]
            _keys(
                receipt,
                "contract_version operation_id artifact_id recorded_at provider declared_status",
            )
            _require(
                receipt["contract_version"] == "gfjd-lifecycle-provider-v1"
                and receipt["provider"] == provider
            )
            _require(
                all(
                    receipt[key] == event[key]
                    for key in ("operation_id", "artifact_id", "recorded_at")
                )
            )
            _require(
                type(receipt["declared_status"]) is str
                and receipt["declared_status"] in PROVIDER_STATUS
            )
    _require(used_artifacts == set(artifacts) and used_receipts == set(receipts))
    return {
        "plan": plan,
        "artifacts": artifacts,
        "events": events,
        "receipts": receipts,
        "checkpoint": checkpoint,
        "event_file_sha256": list(plan["event_sha256"]),
        "inventory_report": {
            "artifact_count": len(artifacts),
            "event_count": len(events),
            "receipt_count": len(receipts),
            "event_bytes": event_bytes,
            "receipt_bytes": receipt_bytes,
            "scope_sha256": plan["scope_sha256"],
            "checkpoint_sha256": plan["checkpoint_sha256"],
        },
    }


def prepare_journal(
    plan_raw: bytes,
    expected_plan_sha256: str,
    scope_raw: bytes,
    layer_contract_raw: bytes,
    checkpoint_raw: bytes,
    event_bank: dict[str, bytes],
    receipt_bank: dict[str, bytes],
) -> dict[str, Any]:
    """Validate all historical metadata; leave state transitions to the replay engine."""
    try:
        return _prepare(
            plan_raw,
            expected_plan_sha256,
            scope_raw,
            layer_contract_raw,
            checkpoint_raw,
            event_bank,
            receipt_bank,
        )
    except Exception:
        raise LifecycleInputError("Lifecycle input contract violation") from None
