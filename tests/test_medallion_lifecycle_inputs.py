"""Fictional lifecycle metadata only; no source/provider accesses."""

import copy
import hashlib
import json
import socket
import traceback
from pathlib import Path

import pytest

from gfjd import medallion_lifecycle_inputs as module
from gfjd.medallion_lifecycle_inputs import prepare_journal


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def identity(value, key):
    value[key] = sha(canonical({k: v for k, v in value.items() if k != key}))
    return value


@pytest.fixture
def data():
    artifact = identity(
        {
            "object_id": "FICTIONAL",
            "edition_id": "EDITION-1",
            "layer": "b0",
            "source_sha256": "a" * 64,
            "content_sha256": "a" * 64,
            "content_blake3": "b" * 64,
            "size_bytes": 10,
        },
        "artifact_id",
    )
    events = []
    receipts = {}
    for i, operation in enumerate(("register", "observe")):
        common = {
            "operation_id": f"op-{i}",
            "artifact_id": artifact["artifact_id"],
            "recorded_at": f"2026-09-01T00:00:0{i}Z",
        }
        disposition = {
            "contract_version": "gfjd-lifecycle-disposition-v1",
            **common,
            "reason_code": "initial" if i == 0 else "monitoring",
            "state": "preparation",
        }
        raw = canonical(disposition)
        receipts[sha(raw)] = raw
        event = {
            "contract_version": "gfjd-lifecycle-event-v1",
            **common,
            "previous_event_id": events[-1]["event_id"] if events else None,
            "operation": operation,
            "predecessor_artifact_id": None,
            "new_state": "active",
            "reason_code": disposition["reason_code"],
            "disposition_sha256": sha(raw),
            "receipt_sha256": [],
        }
        for provider in ("github", "huggingface"):
            receipt = {
                "contract_version": "gfjd-lifecycle-provider-v1",
                **common,
                "provider": provider,
                "declared_status": "available" if provider == "github" else "unknown",
            }
            raw = canonical(receipt)
            receipts[sha(raw)] = raw
            event["receipt_sha256"].append(sha(raw))
        events.append(identity(event, "event_id"))
    return [artifact], events, receipts


def args(data, prefix=1):
    artifacts, events, receipts = data
    scope = canonical({"contract_version": "gfjd-lifecycle-scope-v1", "artifacts": artifacts})
    event_bank = {sha(canonical(event)): canonical(event) for event in events}
    checkpoint = canonical(
        {
            "contract_version": "gfjd-lifecycle-checkpoint-v1",
            "event_sha256": list(event_bank)[:prefix],
        }
    )
    contract = (Path(__file__).resolve().parents[1] / "config/medallion_layers.json").read_bytes()
    plan = canonical(
        {
            "contract_version": "gfjd-lifecycle-plan-v1",
            "state": "preparation",
            "scope_sha256": sha(scope),
            "layer_contract_sha256": sha(contract),
            "checkpoint_sha256": sha(checkpoint),
            "event_sha256": list(event_bank),
            "receipt_sha256": sorted(receipts),
            "as_of": "2026-09-01T00:01:00Z",
        }
    )
    return [plan, sha(plan), scope, contract, checkpoint, event_bank, receipts]


def test_empty_inputs_red():
    with pytest.raises(ValueError):
        prepare_journal(b"{}", "a" * 64, b"{}", b"{}", b"{}", {}, {})


@pytest.mark.parametrize("prefix", [0, 1, 2])
def test_complete_journal(data, prefix):
    values = args(data, prefix)
    report = prepare_journal(*values)
    assert report["events"] == data[1]
    assert list(report["artifacts"]) == [data[0][0]["artifact_id"]]
    assert report["event_file_sha256"] == list(values[5])
    assert report["inventory_report"]["receipt_count"] == 6
    assert report["inventory_report"]["event_bytes"] == sum(map(len, values[5].values()))
    assert report["inventory_report"]["receipt_bytes"] == sum(map(len, values[6].values()))
    assert prepare_journal(*values) == report


@pytest.mark.parametrize(
    "field,value",
    [
        ("previous_event_id", "f" * 64),
        ("operation_id", "op-0"),
        ("recorded_at", "2026-09-01T00:00:00Z"),
        ("recorded_at", "2026-09-01T00:02:00Z"),
        ("new_state", "published"),
        ("operation", "execute"),
        ("reason_code", "free narrative"),
        ("artifact_id", "f" * 64),
        ("predecessor_artifact_id", "f" * 64),
        ("extra", "unsafe"),
    ],
)
def test_event_constraints(data, field, value):
    data[1][-1][field] = value
    identity(data[1][-1], "event_id")
    with pytest.raises(ValueError):
        prepare_journal(*args(data))


def replace_receipt(data, digest, record):
    raw = canonical(record)
    data[2].pop(digest)
    data[2][sha(raw)] = raw
    for event in data[1]:
        if event["disposition_sha256"] == digest:
            event["disposition_sha256"] = sha(raw)
        event["receipt_sha256"] = [
            sha(raw) if value == digest else value for value in event["receipt_sha256"]
        ]
    previous = None
    for event in data[1]:
        event["previous_event_id"] = previous
        identity(event, "event_id")
        previous = event["event_id"]


@pytest.mark.parametrize(
    "field,value",
    [
        ("provider", "other"),
        ("operation_id", "other"),
        ("artifact_id", "f" * 64),
        ("recorded_at", "2026-09-01T00:00:59Z"),
        ("declared_status", "verified_public"),
        ("locator", "https://example.invalid"),
    ],
)
def test_receipt_binding(data, field, value):
    digest = data[1][-1]["receipt_sha256"][0]
    receipt = json.loads(data[2][digest])
    receipt[field] = value
    replace_receipt(data, digest, receipt)
    with pytest.raises(ValueError):
        prepare_journal(*args(data))


def test_provider_order(data):
    data[1][-1]["receipt_sha256"].reverse()
    identity(data[1][-1], "event_id")
    with pytest.raises(ValueError):
        prepare_journal(*args(data))


@pytest.mark.parametrize(
    "field,value",
    [("state", "accepted"), ("reason_code", "rights"), ("operation_id", "other"), ("extra", "x")],
)
def test_disposition_not_owner_approval(data, field, value):
    digest = data[1][-1]["disposition_sha256"]
    record = json.loads(data[2][digest])
    record[field] = value
    replace_receipt(data, digest, record)
    with pytest.raises(ValueError):
        prepare_journal(*args(data))


@pytest.mark.parametrize(
    "kind", ["changed_source", "b0_content", "shared_b3", "bool_size", "extra_inventory"]
)
def test_artifact_identity_constraints(data, kind):
    extra = copy.deepcopy(data[0][0])
    if kind == "changed_source":
        extra.update(layer="b1", source_sha256="c" * 64, content_sha256="d" * 64)
    elif kind == "b0_content":
        extra["content_sha256"] = "c" * 64
    elif kind == "shared_b3":
        extra.update(layer="b1", content_blake3="c" * 64)
    elif kind == "bool_size":
        extra["size_bytes"] = True
    else:
        extra.update(layer="b1", content_sha256="d" * 64)
    identity(extra, "artifact_id")
    data[0].append(extra)
    with pytest.raises(ValueError):
        prepare_journal(*args(data))


def test_full_predecessor_union_even_before_state_machine(data):
    extra = copy.deepcopy(data[0][0])
    extra.update(layer="b1", content_sha256="c" * 64)
    identity(extra, "artifact_id")
    data[0].append(extra)
    data[1][-1]["predecessor_artifact_id"] = extra["artifact_id"]
    identity(data[1][-1], "event_id")
    # Input helper covers inventory; invalid observe predecessor is a state-machine rule.
    assert prepare_journal(*args(data))["inventory_report"]["artifact_count"] == 2


def test_changed_checkpoint_prefix(data):
    values = args(data)
    checkpoint = json.loads(values[4])
    checkpoint["event_sha256"] = list(values[5])[1:]
    values[4] = canonical(checkpoint)
    plan = json.loads(values[0])
    plan["checkpoint_sha256"] = sha(values[4])
    values[0] = canonical(plan)
    values[1] = sha(values[0])
    with pytest.raises(ValueError):
        prepare_journal(*values)


@pytest.mark.parametrize("bank_index", [5, 6])
@pytest.mark.parametrize("change", ["missing", "extra", "wrongbytes"])
def test_exact_bank(data, bank_index, change):
    values = args(data)
    bank = values[bank_index]
    if change == "missing":
        bank.popitem()
    elif change == "extra":
        bank[sha(b"{}")] = b"{}"
    else:
        bank[next(iter(bank))] = b"{}"
    with pytest.raises(ValueError):
        prepare_journal(*values)


def test_unused_historical_receipt(data):
    data[2][sha(b"{}")] = b"{}"
    with pytest.raises(ValueError):
        prepare_journal(*args(data))


def test_bank_budget_before_hash(data, monkeypatch):
    values = args(data)
    oversized = {f"{i:064x}": b" " * module.MIB for i in range(9)}
    plan = json.loads(values[0])
    plan["receipt_sha256"] = list(oversized)
    values[0] = canonical(plan)
    values[1] = sha(values[0])
    values[6] = oversized

    def forbidden(*args, **kwargs):
        pytest.fail("hash before bank budget check")

    monkeypatch.setattr(module, "_sha", forbidden)
    with pytest.raises(ValueError):
        prepare_journal(*values)


@pytest.mark.parametrize(
    "raw",
    [
        b'{"x":1,"x":2}',
        b'{"x":NaN}',
        b'"\\u0000"',
        b'"\\ud800"',
        b"[" * 17 + b"0" + b"]" * 17,
        b"\xff",
    ],
)
def test_structured_preflight(data, raw):
    values = args(data)
    values[2] = raw
    plan = json.loads(values[0])
    plan["scope_sha256"] = sha(raw)
    values[0] = canonical(plan)
    values[1] = sha(values[0])
    with pytest.raises(ValueError):
        prepare_journal(*values)


def test_no_network_and_fixed_diagnostics(data, monkeypatch, capsys):
    def denied(*args, **kwargs):
        pytest.fail("network attempted")

    monkeypatch.setattr(socket, "create_connection", denied)
    prepare_journal(*args(data))
    data[1][-1]["operation_id"] = "PRIVATE_SENTINEL/invalid"
    identity(data[1][-1], "event_id")
    try:
        prepare_journal(*args(data))
    except ValueError:
        assert "PRIVATE_SENTINEL" not in traceback.format_exc()
    else:
        pytest.fail("invalid identifier accepted")
    assert capsys.readouterr() == ("", "")


@pytest.mark.parametrize("operation", ["register", "correct", "supersede"])
def test_required_operation_reason_fully_rebound(data, operation):
    event = data[1][-1]
    event["operation"] = operation
    event["reason_code"] = "policy"
    digest = event["disposition_sha256"]
    disposition = json.loads(data[2][digest])
    disposition["reason_code"] = "policy"
    replace_receipt(data, digest, disposition)
    # Event IDs, receipt file digests, checkpoint and plan hashes all match.
    with pytest.raises(ValueError):
        prepare_journal(*args(data))
