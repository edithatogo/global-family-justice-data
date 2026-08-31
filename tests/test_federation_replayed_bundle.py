"""Fictional exact replay attachments; no actual source or publication evidence."""

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

from gfjd import federation_replayed_bundle as bundle
from gfjd.federation_bundle import ASSETS
from gfjd.federation_metadata import MetadataError
from gfjd.medallion_estate import POLICY_REFERENCE, SOURCEFILES, prepare_estate
from gfjd.medallion_replay import replay_projection


def encoded(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


@pytest.fixture
def inputs() -> list:
    root = Path(__file__).parents[1]
    estate = {name: (root / name).read_bytes() for name in (*SOURCEFILES, POLICY_REFERENCE)}
    standards = {name: (root / "src/gfjd/federation_specs" / name).read_bytes() for name in ASSETS}
    metadata = b'{"description":"Fictional metadata"}'
    source = encoded([{"fictional": "PRIVATE_FICTIONAL_VALUE"}])
    contract = {
        "contract_version": "gfjd-json-projection-v1",
        "source_sha256": sha(source),
        "projection": {"value": "fictional"},
        "valid_from": None,
        "recorded_at": "2026-08-31T00:00:00Z",
    }
    receipt = replay_projection(source, contract)
    contract_raw, receipt_raw = encoded(contract), encoded(receipt)
    obj = {
        "object_id": "fictional",
        "canonical_id": "urn:gfjd:source:fictional",
        "kind": "source",
        "role": "source-archive",
        "content_sha256": sha(source),
        "metadata_sha256": sha(metadata),
        "media_type": "application/json",
        "references": [],
    }
    scope = {
        "contract_version": "gfjd-federation-reference-scope-v1",
        "state": "preparation",
        "estate_manifest_sha256": sha(prepare_estate(estate)["estate-manifest.json"]),
        "partners": [],
        "objects": [obj],
    }
    replay = {
        "contract_version": "gfjd-federation-replay-attachment-v1",
        "mode": "projection",
        "selection": {
            "object_id": "fictional",
            "entity_role": "source",
            "event_id": None,
            "entity_sha256": sha(source),
        },
        "inputs": {
            "source_sha256": sha(source),
            "contract_sha256": sha(contract_raw),
            "receipt_sha256": sha(receipt_raw),
        },
    }
    bank = {sha(value): value for value in (source, contract_raw, receipt_raw)}
    return [
        encoded(scope),
        sha(encoded(scope)),
        {sha(metadata): metadata},
        estate,
        standards,
        encoded(replay),
        sha(encoded(replay)),
        bank,
    ]


def test_replay_binding_red(inputs: list) -> None:
    inputs[6] = "0" * 64
    with pytest.raises(MetadataError):
        bundle.prepare_replayed_bundle(*inputs)


def test_projection_source(inputs: list) -> None:
    output = bundle.prepare_replayed_bundle(*inputs)
    assert "provenance/provenance.nt" in output
    assert "provenance/provenance-report.json" in output
    manifest = json.loads(output["bundle-manifest.json"])
    assert manifest["replay_binding"]["canonical_id"] == "urn:gfjd:source:fictional"
    assert manifest["provenance_pending_object_ids"] == []
    assert b"PRIVATE_FICTIONAL_VALUE" not in b"".join(output.values())
    assert not any(manifest["authority"].values())
    assert output == bundle.prepare_replayed_bundle(*inputs)
    bundle.verify_replayed_bundle(*inputs, output)


@pytest.mark.parametrize(
    "change", ["content", "null", "entity", "role", "event", "extra", "missing", "type"]
)
def test_mismatch(inputs: list, change: str) -> None:
    scope, replay = json.loads(inputs[0]), json.loads(inputs[5])
    if change in {"content", "null"}:
        scope["objects"][0]["content_sha256"] = None if change == "null" else "0" * 64
    elif change == "entity":
        replay["selection"]["entity_sha256"] = "0" * 64
    elif change == "role":
        replay["selection"]["entity_role"] = "silver"
    elif change == "event":
        replay["selection"]["event_id"] = "0" * 64
    elif change == "extra":
        inputs[7][sha(b"extra")] = b"extra"
    elif change == "missing":
        inputs[7].pop(replay["inputs"]["source_sha256"])
    else:
        replay["unexpected"] = True
    inputs[0], inputs[1] = encoded(scope), sha(encoded(scope))
    inputs[5], inputs[6] = encoded(replay), sha(encoded(replay))
    with pytest.raises(MetadataError):
        bundle.prepare_replayed_bundle(*inputs)


def test_output_forgery(inputs: list) -> None:
    output = bundle.prepare_replayed_bundle(*inputs)
    output["provenance/provenance.nt"] += b"# forged\n"
    manifest = json.loads(output["bundle-manifest.json"])
    manifest["artifact_sha256"]["provenance/provenance.nt"] = sha(
        output["provenance/provenance.nt"]
    )
    output["bundle-manifest.json"] = encoded(manifest)
    with pytest.raises(MetadataError):
        bundle.verify_replayed_bundle(*inputs, output)


def test_pending_other_object(inputs: list) -> None:
    scope = json.loads(inputs[0])
    scope["objects"].append(
        dict(
            scope["objects"][0],
            object_id="other",
            canonical_id="urn:gfjd:source:other",
            content_sha256=None,
        )
    )
    inputs[0], inputs[1] = encoded(scope), sha(encoded(scope))
    report = json.loads(bundle.prepare_replayed_bundle(*inputs)["bundle-manifest.json"])
    assert report["provenance_pending_object_ids"] == ["other"]


def test_projection_rows(inputs: list) -> None:
    replay, scope = json.loads(inputs[5]), json.loads(inputs[0])
    receipt = json.loads(inputs[7][replay["inputs"]["receipt_sha256"]])
    digest = sha(encoded(receipt["rows"]))
    replay["selection"].update(entity_role="projection_rows", entity_sha256=digest)
    scope["objects"][0]["content_sha256"] = digest
    inputs[0], inputs[1] = encoded(scope), sha(encoded(scope))
    inputs[5], inputs[6] = encoded(replay), sha(encoded(replay))
    result = bundle.prepare_replayed_bundle(*inputs)
    assert json.loads(result["bundle-manifest.json"])["replay_binding"]["entity_sha256"] == digest


@pytest.fixture
def pipeline_inputs(inputs: list) -> list:
    from gfjd.medallion_pipeline import build_pipeline_event

    path = Path(__file__).parents[1] / "scripts/rehearse_medallion_lineage.py"
    spec = importlib.util.spec_from_file_location("fictional_rehearsal", path)
    assert spec and spec.loader
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    source, safety, custody, contract = helper.fictional_inputs("0007", "2026-08-31T00:00:00Z")
    entry = build_pipeline_event(
        source, safety, custody, contract, partition="fictional", valid_until=None, supersedes=None
    )
    entries = encoded([entry])
    contract_raw = encoded(contract)
    replay = {
        "contract_version": "gfjd-federation-replay-attachment-v1",
        "mode": "pipeline_history",
        "selection": {
            "object_id": "fictional",
            "entity_role": "source",
            "event_id": entry["history_event"]["event_id"],
            "entity_sha256": sha(source),
        },
        "inputs": {
            "entries_sha256": sha(entries),
            "sources": [sha(source)],
            "safety_receipts": [sha(safety)],
            "custody_receipts": [sha(custody)],
            "contracts": [sha(contract_raw)],
        },
    }
    scope = json.loads(inputs[0])
    scope["objects"][0]["content_sha256"] = sha(source)
    inputs[0], inputs[1] = encoded(scope), sha(encoded(scope))
    inputs[5], inputs[6] = encoded(replay), sha(encoded(replay))
    inputs[7] = {sha(value): value for value in (source, safety, custody, contract_raw, entries)}
    return inputs


@pytest.mark.parametrize("role", ["source", "bronze", "silver"])
def test_pipeline_selection(pipeline_inputs: list, role: str) -> None:
    inputs = pipeline_inputs
    replay, scope = json.loads(inputs[5]), json.loads(inputs[0])
    entry = json.loads(inputs[7][replay["inputs"]["entries_sha256"]])[0]
    digest = scope["objects"][0]["content_sha256"]
    if role != "source":
        digest = sha(encoded(entry["pipeline"]["b1" if role == "bronze" else "silver"]["rows"]))
    replay["selection"].update(entity_role=role, entity_sha256=digest)
    scope["objects"][0]["content_sha256"] = digest
    inputs[0], inputs[1] = encoded(scope), sha(encoded(scope))
    inputs[5], inputs[6] = encoded(replay), sha(encoded(replay))
    output = bundle.prepare_replayed_bundle(*inputs)
    bundle.verify_replayed_bundle(*inputs, output)
    assert json.loads(output["bundle-manifest.json"])["replay_binding"]["entity_role"] == role


@pytest.mark.parametrize("change", ["event", "duplicate_list", "parent"])
def test_pipeline_rejection(pipeline_inputs: list, change: str) -> None:
    inputs = pipeline_inputs
    replay = json.loads(inputs[5])
    if change == "event":
        replay["selection"]["event_id"] = "0" * 64
    elif change == "duplicate_list":
        replay["inputs"]["sources"] *= 2
    else:
        old = replay["inputs"]["entries_sha256"]
        entries = json.loads(inputs[7].pop(old))
        entries[0]["history_event"]["supersedes"] = "0" * 64
        payload = encoded(entries)
        replay["inputs"]["entries_sha256"] = sha(payload)
        inputs[7][sha(payload)] = payload
    inputs[5], inputs[6] = encoded(replay), sha(encoded(replay))
    with pytest.raises(MetadataError):
        bundle.prepare_replayed_bundle(*inputs)


def test_no_network(inputs: list, monkeypatch: pytest.MonkeyPatch) -> None:
    import socket
    import urllib.request

    def forbidden(*args: object, **kwargs: object) -> None:
        raise AssertionError("network attempted")

    monkeypatch.setattr(socket, "socket", forbidden)
    monkeypatch.setattr(urllib.request, "urlopen", forbidden)
    bundle.prepare_replayed_bundle(*inputs)


def test_pipeline_contract_serialization(pipeline_inputs: list) -> None:
    inputs = pipeline_inputs
    replay = json.loads(inputs[5])
    old = replay["inputs"]["contracts"][0]
    payload = inputs[7].pop(old) + b"\n"
    inputs[7][sha(payload)] = payload
    replay["inputs"]["contracts"] = [sha(payload)]
    inputs[5], inputs[6] = encoded(replay), sha(encoded(replay))
    output = bundle.prepare_replayed_bundle(*inputs)
    report = json.loads(output["bundle-manifest.json"])
    assert sha(payload) in report["replay_bank_sha256"]
    bundle.verify_replayed_bundle(*inputs, output)


def test_pipeline_canonical_contract_collision(pipeline_inputs: list) -> None:
    inputs = pipeline_inputs
    replay = json.loads(inputs[5])
    old = replay["inputs"]["contracts"][0]
    payload = inputs[7][old] + b"\n"
    inputs[7][sha(payload)] = payload
    replay["inputs"]["contracts"].append(sha(payload))
    inputs[5], inputs[6] = encoded(replay), sha(encoded(replay))
    with pytest.raises(MetadataError):
        bundle.prepare_replayed_bundle(*inputs)


@pytest.mark.parametrize("kind", ["envelope", "member", "count", "total"])
def test_bounds(inputs: list, kind: str) -> None:
    if kind == "envelope":
        inputs[5] = b" " * (1024 * 1024 + 1)
        inputs[6] = sha(inputs[5])
    elif kind == "member":
        value = b" " * (1024 * 1024 + 1)
        inputs[7] = {sha(value): value}
    elif kind == "count":
        inputs[7] = {str(i): b"x" for i in range(402)}
    else:
        inputs[7] = {sha(value): value for value in (bytes([i]) * (1024 * 1024) for i in range(9))}
    with pytest.raises(MetadataError):
        bundle.prepare_replayed_bundle(*inputs)
