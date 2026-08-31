"""Fictional lifecycle declarations; never actual public operations."""

from pathlib import Path

import pytest
from blake3 import blake3

from gfjd import medallion_lifecycle as lifecycle
from gfjd.medallion_qualification_inputs import canonical, sha


def artifact(layer="gold", revision="one", edition="FICTIONAL-EDITION"):
    source = b"FICTIONAL source"
    raw = source if layer == "b0" else f"FICTIONAL {layer} {revision}".encode()
    result = {
        "object_id": "FICTIONAL",
        "edition_id": edition,
        "layer": layer,
        "source_sha256": sha(source),
        "content_sha256": sha(raw),
        "content_blake3": blake3(raw).hexdigest(),
        "size_bytes": len(raw),
    }
    return {**result, "artifact_id": sha(canonical(result))}


def journal(steps=None, *, checkpoint_count=0):
    """Each step is operation, artifact, predecessor, new state, provider statuses."""
    if steps is None:
        a, b = artifact(), artifact(revision="two")
        steps = [
            ("register", a, None, "active", ("available", "available")),
            ("correct", b, a, "active", ("available", "unknown")),
            ("observe", a, None, "withdrawn", ("withdrawn", "withdrawn")),
            ("withdraw", b, None, "withdrawn", ("withdrawn", "withdrawn")),
            ("republish", b, None, "active", ("available", "available")),
            ("withdraw", b, None, "withdrawn", ("withdrawn", "withdrawn")),
            ("tombstone", b, None, "tombstoned", ("tombstone_visible", "tombstone_visible")),
        ]
    artifacts, events, receipts, order = {}, {}, {}, []
    previous = None
    for i, (operation, item, predecessor, state, statuses) in enumerate(steps):
        artifacts[item["artifact_id"]] = item
        if predecessor:
            artifacts[predecessor["artifact_id"]] = predecessor
        clock = f"2026-09-01T00:{i // 60:02d}:{i % 60:02d}Z"
        operation_id = f"FICTIONAL-{i}"
        reason = {"register": "initial", "correct": "correction", "supersede": "supersession"}.get(
            operation, "policy"
        )
        base = {
            "operation_id": operation_id,
            "artifact_id": item["artifact_id"],
            "recorded_at": clock,
        }
        disposition = canonical(
            {
                **base,
                "contract_version": "gfjd-lifecycle-disposition-v1",
                "reason_code": reason,
                "state": "preparation",
            }
        )
        receipts[sha(disposition)] = disposition
        provider_refs = []
        for provider, status in zip(("github", "huggingface"), statuses, strict=True):
            raw = canonical(
                {
                    **base,
                    "contract_version": "gfjd-lifecycle-provider-v1",
                    "provider": provider,
                    "declared_status": status,
                }
            )
            receipts[sha(raw)] = raw
            provider_refs.append(sha(raw))
        event = {
            **base,
            "contract_version": "gfjd-lifecycle-event-v1",
            "previous_event_id": previous,
            "operation": operation,
            "predecessor_artifact_id": predecessor["artifact_id"] if predecessor else None,
            "new_state": state,
            "reason_code": reason,
            "disposition_sha256": sha(disposition),
            "receipt_sha256": provider_refs,
        }
        event["event_id"] = sha(canonical(event))
        previous = event["event_id"]
        raw = canonical(event)
        order.append(sha(raw))
        events[sha(raw)] = raw
    scope = canonical(
        {"contract_version": "gfjd-lifecycle-scope-v1", "artifacts": list(artifacts.values())}
    )
    checkpoint = canonical(
        {
            "contract_version": "gfjd-lifecycle-checkpoint-v1",
            "event_sha256": order[:checkpoint_count],
        }
    )
    contract = (Path(__file__).parents[1] / "config/medallion_layers.json").read_bytes()
    plan = canonical(
        {
            "contract_version": "gfjd-lifecycle-plan-v1",
            "state": "preparation",
            "scope_sha256": sha(scope),
            "layer_contract_sha256": sha(contract),
            "checkpoint_sha256": sha(checkpoint),
            "event_sha256": order,
            "receipt_sha256": sorted(receipts),
            "as_of": "2026-09-02T00:00:00Z",
        }
    )
    return plan, sha(plan), scope, contract, checkpoint, events, receipts


def test_complete_history_has_no_fallback_or_authority():
    args = journal(checkpoint_count=3)
    report = lifecycle.assess_lifecycle_journal(*args)
    assert len(report["inventory"]) == 2
    assert len(report["history"]) == 7
    assert report["heads"][0]["state"] == "tombstoned"
    assert report["heads"][0]["active_artifact_id"] is None
    assert report["declared_provider_backlog"] == []
    assert not any(report["authority"].values())
    lifecycle.verify_lifecycle_journal(*args, report)


def test_intervals_preserve_implicit_withdrawal_without_observation_split():
    report = lifecycle.assess_lifecycle_journal(*journal())
    first_id = artifact()["artifact_id"]
    intervals = [row for row in report["state_intervals"] if row["artifact_id"] == first_id]
    assert [(row["state"], row["recorded_from"], row["recorded_until"]) for row in intervals] == [
        ("active", "2026-09-01T00:00:00Z", "2026-09-01T00:00:01Z"),
        ("withdrawn", "2026-09-01T00:00:01Z", None),
    ]
    assert intervals[1]["event_id"] == report["history"][1]["event_id"]
    assert report["history"][2]["operation"] == "observe"
    assert report["history"][2]["changes"] == []
    assert len(report["state_intervals"]) == 7


def test_implicit_withdrawal_recomputes_historical_provider_backlog():
    a, b = artifact(), artifact(revision="two")
    report = lifecycle.assess_lifecycle_journal(
        *journal(
            [
                ("register", a, None, "active", ("available", "available")),
                ("supersede", b, a, "active", ("available", "available")),
            ]
        )
    )
    assert len(report["declared_provider_backlog"]) == 2
    assert all(
        row["artifact_id"] == a["artifact_id"] for row in report["declared_provider_backlog"]
    )


@pytest.mark.parametrize(
    "operation,state",
    [("republish", "active"), ("register", "active"), ("quarantine", "quarantined")],
)
def test_tombstone_cannot_be_reactivated(operation, state):
    a = artifact()
    steps = [
        ("register", a, None, "active", ("available", "available")),
        ("withdraw", a, None, "withdrawn", ("withdrawn", "withdrawn")),
        ("tombstone", a, None, "tombstoned", ("tombstone_visible", "tombstone_visible")),
        (operation, a, None, state, ("available", "available")),
    ]
    with pytest.raises(ValueError):
        lifecycle.assess_lifecycle_journal(*journal(steps))


def test_no_stale_parent_and_no_cross_layer_successor():
    a, b, c = artifact(), artifact(revision="two"), artifact(layer="silver")
    with pytest.raises(ValueError):
        lifecycle.assess_lifecycle_journal(
            *journal(
                [
                    ("register", a, None, "active", ("available", "available")),
                    ("correct", b, a, "active", ("available", "available")),
                    ("supersede", c, a, "active", ("available", "available")),
                ]
            )
        )


def test_forged_public_operation_claim_rejected():
    args = journal()
    report = lifecycle.assess_lifecycle_journal(*args)
    report["public_execution"] = "verified"
    with pytest.raises(ValueError):
        lifecycle.verify_lifecycle_journal(*args, report)


def all_operations():
    members = [artifact(layer=layer) for layer in ("b0", "b1", "silver", "gold", "platinum")]
    steps = [("register", item, None, "active", ("available", "available")) for item in members]
    first = members[3]
    second, third = artifact(revision="two"), artifact(revision="three")
    steps.extend(
        [
            ("quarantine", first, None, "quarantined", ("withdrawn", "available")),
            ("withdraw", first, None, "withdrawn", ("withdrawn", "withdrawn")),
            ("republish", first, None, "active", ("available", "unavailable")),
            ("observe", first, None, "active", ("available", "available")),
            ("correct", second, first, "active", ("available", "available")),
            ("observe", first, None, "withdrawn", ("withdrawn", "withdrawn")),
            ("withdraw", second, None, "withdrawn", ("withdrawn", "withdrawn")),
            ("tombstone", second, None, "tombstoned", ("tombstone_visible", "unknown")),
            ("observe", second, None, "tombstoned", ("tombstone_visible", "tombstone_visible")),
            ("supersede", third, second, "active", ("available", "available")),
        ]
    )
    return journal(steps, checkpoint_count=8)


def test_all_operations_five_layers_keep_tombstone_and_provider_history():
    report = lifecycle.assess_lifecycle_journal(*all_operations())
    assert len(report["heads"]) == 5
    assert len(report["inventory"]) == 7
    assert len(report["history"]) == 15
    assert {item["operation"] for item in report["history"]} == {
        "register",
        "quarantine",
        "withdraw",
        "republish",
        "observe",
        "correct",
        "tombstone",
        "supersede",
    }
    assert report["declared_provider_backlog"] == []
    assert any(item["state"] == "tombstoned" for item in report["inventory"])
    assert any(
        row["assessment"] == "mismatch"
        for event in report["history"]
        for row in event["provider_declarations"]
    )
    assert report["public_execution"] == "unverified"


def test_historical_observe_cannot_change_state():
    a, b = artifact(), artifact(revision="two")
    with pytest.raises(ValueError):
        lifecycle.assess_lifecycle_journal(
            *journal(
                [
                    ("register", a, None, "active", ("available", "available")),
                    ("correct", b, a, "active", ("available", "available")),
                    ("observe", a, None, "active", ("available", "available")),
                ]
            )
        )


@pytest.mark.parametrize(
    "operation,state",
    [("withdraw", "active"), ("tombstone", "tombstoned"), ("republish", "active")],
)
def test_invalid_transition_from_active_rejected(operation, state):
    a = artifact()
    with pytest.raises(ValueError):
        lifecycle.assess_lifecycle_journal(
            *journal(
                [
                    ("register", a, None, "active", ("available", "available")),
                    (operation, a, None, state, ("available", "available")),
                ]
            )
        )
