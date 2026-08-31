"""Append-only lifecycle declarations; no public operation or source access.

Only implementation fingerprint files are read. Provider receipts remain
unauthenticated declarations, including apparent recovery after provider loss.
"""

from pathlib import Path
from typing import Any

from . import medallion_lifecycle_inputs
from .medallion_qualification_inputs import canonical, sha

DESIRED = {
    "active": "available",
    "quarantined": "withdrawn",
    "withdrawn": "withdrawn",
    "tombstoned": "tombstone_visible",
}


def _require(condition: bool) -> None:
    if not condition:
        raise ValueError("lifecycle journal contract failed")


def _providers(item: dict[str, Any]) -> list[dict[str, Any]]:
    desired = DESIRED[item["state"]]
    return [
        {
            "provider": receipt["provider"],
            "desired_status": desired,
            "declared_status": receipt["declared_status"],
            "receipt_sha256": receipt["receipt_sha256"],
            "assessment": (
                "unknown"
                if receipt["declared_status"] == "unknown"
                else "match"
                if receipt["declared_status"] == desired
                else "mismatch"
            ),
            "authenticated": False,
        }
        for receipt in item["latest_provider_declarations"]
    ]


def assess_lifecycle_journal(
    plan_raw: bytes,
    expected_plan_sha256: str,
    scope_raw: bytes,
    layer_contract_raw: bytes,
    checkpoint_raw: bytes,
    event_bank: dict[str, bytes],
    receipt_bank: dict[str, bytes],
) -> dict[str, Any]:
    """Replay every event and retain every artifact, without older-active fallback."""
    inputs = medallion_lifecycle_inputs.prepare_journal(
        plan_raw,
        expected_plan_sha256,
        scope_raw,
        layer_contract_raw,
        checkpoint_raw,
        event_bank,
        receipt_bank,
    )
    inventory: dict[str, dict[str, Any]] = {}
    heads: dict[tuple[str, str], str] = {}
    intervals: list[dict[str, Any]] = []
    open_intervals: dict[str, dict[str, Any]] = {}
    history = []
    for event, file_sha in zip(inputs["events"], inputs["event_file_sha256"], strict=True):
        artifact_id = event["artifact_id"]
        artifact = inputs["artifacts"][artifact_id]
        series = (artifact["object_id"], artifact["layer"])
        operation, state = event["operation"], event["new_state"]
        predecessor = event["predecessor_artifact_id"]
        changes: list[dict[str, Any]] = []

        def transition(
            identity: str,
            new_state: str,
            event: dict[str, Any] = event,
            changes: list[dict[str, Any]] = changes,
        ) -> None:
            current = inventory[identity]
            before = current.get("state")
            if identity in open_intervals:
                open_intervals[identity]["recorded_until"] = event["recorded_at"]
            interval = {
                "artifact_id": identity,
                "state": new_state,
                "recorded_from": event["recorded_at"],
                "recorded_until": None,
                "event_id": event["event_id"],
            }
            intervals.append(interval)
            open_intervals[identity] = interval
            current["state"] = new_state
            current["last_transition_event_id"] = event["event_id"]
            changes.append({"artifact_id": identity, "prior_state": before, "new_state": new_state})

        if operation in {"register", "correct", "supersede"}:
            _require(artifact_id not in inventory and state in {"active", "quarantined"})
            if operation == "register":
                _require(series not in heads and predecessor is None)
            else:
                _require(series in heads and predecessor == heads[series])
                previous = inventory[predecessor]
                _require((previous["object_id"], previous["layer"]) == series)
                _require(previous["successor_artifact_id"] is None)
                if previous["state"] in {"active", "quarantined"}:
                    transition(predecessor, "withdrawn")
                previous["successor_artifact_id"] = artifact_id
            inventory[artifact_id] = {
                **artifact,
                "successor_artifact_id": None,
                "predecessor_artifact_id": predecessor,
                "latest_provider_declarations": [],
            }
            heads[series] = artifact_id
            transition(artifact_id, state)
        else:
            _require(artifact_id in inventory and predecessor is None)
            current = inventory[artifact_id]
            if operation == "observe":
                _require(state == current["state"])
            else:
                _require(heads.get(series) == artifact_id)
                allowed = {
                    "quarantine": ({"active"}, "quarantined"),
                    "withdraw": ({"active", "quarantined"}, "withdrawn"),
                    "tombstone": ({"withdrawn"}, "tombstoned"),
                    "republish": ({"withdrawn"}, "active"),
                }
                _require(operation in allowed)
                from_states, desired = allowed[operation]
                _require(current["state"] in from_states and state == desired)
                transition(artifact_id, state)
        current = inventory[artifact_id]
        current["latest_provider_declarations"] = [
            {**inputs["receipts"][digest], "receipt_sha256": digest}
            for digest in event["receipt_sha256"]
        ]
        current["last_observation_event_id"] = event["event_id"]
        history.append(
            {
                "event_id": event["event_id"],
                "event_file_sha256": file_sha,
                "operation_id": event["operation_id"],
                "operation": operation,
                "artifact_id": artifact_id,
                "recorded_at": event["recorded_at"],
                "reason_code": event["reason_code"],
                "disposition_sha256": event["disposition_sha256"],
                "changes": changes,
                "provider_declarations": _providers(current),
            }
        )
    _require(set(inventory) == set(inputs["artifacts"]))
    backlog = []
    for identity, item in sorted(inventory.items()):
        item["provider_reconciliation"] = _providers(item)
        for row in item["provider_reconciliation"]:
            if row["assessment"] != "match":
                backlog.append({"artifact_id": identity, **row})
    report = {
        "contract_version": "gfjd-lifecycle-rehearsal-v1",
        "plan_sha256": expected_plan_sha256,
        "as_of": inputs["plan"]["as_of"],
        "inventory_binding": inputs["inventory_report"],
        "checkpoint_prefix_length": len(inputs["checkpoint"]["event_sha256"]),
        "checkpoint_consistency": "verified",
        "checkpoint_authentication": "unverified",
        "inventory": [inventory[key] for key in sorted(inventory)],
        "heads": [
            {
                "object_id": series[0],
                "layer": series[1],
                "artifact_id": identity,
                "state": inventory[identity]["state"],
                "active_artifact_id": identity
                if inventory[identity]["state"] == "active"
                else None,
            }
            for series, identity in sorted(heads.items())
        ],
        "history": history,
        "state_intervals": intervals,
        "declared_provider_backlog": backlog,
        "declared_provider_alignment": "blocked" if backlog else "aligned_declarations_only",
        "public_execution": "unverified",
        "source_fixity": "unverified",
        "implementation_sha256": sha(Path(__file__).read_bytes()),
        "input_implementation_sha256": sha(Path(medallion_lifecycle_inputs.__file__).read_bytes()),
        "limitations": [
            "No actual withdrawal, tombstone, republication or provider recovery performed.",
            "Closed metadata syntax is not certification that identifiers are non-identifying.",
            "Active declarations do not establish maturity, rights or publication authority.",
            "Complete declared inventory is not source-byte acquisition or retention proof.",
        ],
        "authority": dict.fromkeys(
            [
                "network",
                "source_access",
                "rights",
                "promotion",
                "publication",
                "transfer",
                "release",
                "gate_acceptance",
            ],
            False,
        ),
    }
    report["report_sha256"] = sha(canonical(report))
    return report


def verify_lifecycle_journal(
    plan_raw: bytes,
    expected_plan_sha256: str,
    scope_raw: bytes,
    layer_contract_raw: bytes,
    checkpoint_raw: bytes,
    event_bank: dict[str, bytes],
    receipt_bank: dict[str, bytes],
    report: dict[str, Any],
) -> None:
    expected = assess_lifecycle_journal(
        plan_raw,
        expected_plan_sha256,
        scope_raw,
        layer_contract_raw,
        checkpoint_raw,
        event_bank,
        receipt_bank,
    )
    _require(canonical(report) == canonical(expected))
