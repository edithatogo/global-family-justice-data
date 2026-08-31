"""One exact, replayed provenance attachment to a reference-only draft bundle."""

import hashlib
import re
from typing import Any

from gfjd.federation_bundle import prepare_bundle
from gfjd.federation_metadata import MetadataError, parse_json, require
from gfjd.federation_prov import _canonical, prepare_pipeline_prov, prepare_projection_prov

VERSION = "gfjd-federation-replay-attachment-v1"


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _digest(value: Any) -> str:
    require(type(value) is str and re.fullmatch(r"[a-f0-9]{64}", value) is not None)
    return str(value)


def _keys(value: Any, fields: str) -> dict[str, Any]:
    require(type(value) is dict and set(value) == set(fields.split()))
    return value  # type: ignore[no-any-return]


def _replay(
    raw: bytes, expected: str, bank: dict[str, bytes]
) -> tuple[dict[str, bytes], dict[str, Any]]:
    require(type(raw) is bytes and 0 < len(raw) <= 1024 * 1024)
    require(_digest(expected) == _sha(raw))
    envelope = _keys(parse_json(raw), "contract_version mode selection inputs")
    require(envelope["contract_version"] == VERSION)
    selection = _keys(envelope["selection"], "object_id entity_role event_id entity_sha256")
    require(type(selection["object_id"]) is str)
    _digest(selection["entity_sha256"])
    require(type(bank) is dict and 0 < len(bank) <= 401)
    total = 0
    for digest, payload in bank.items():
        _digest(digest)
        require(type(payload) is bytes and 0 < len(payload) <= 1024 * 1024)
        total += len(payload)
        require(total <= 8 * 1024 * 1024 and _sha(payload) == digest)
    mode = envelope["mode"]
    if mode == "projection":
        refs = _keys(envelope["inputs"], "source_sha256 contract_sha256 receipt_sha256")
        require(set(bank) == {_digest(value) for value in refs.values()})
        require(selection["event_id"] is None)
        require(selection["entity_role"] in {"source", "projection_rows"})
        source = bank[refs["source_sha256"]]
        contract = parse_json(bank[refs["contract_sha256"]])
        receipt = parse_json(bank[refs["receipt_sha256"]])
        provenance = prepare_projection_prov(source, contract, receipt)
        selected = source if selection["entity_role"] == "source" else _canonical(receipt["rows"])
    else:
        require(mode == "pipeline_history")
        refs = _keys(
            envelope["inputs"], "entries_sha256 sources safety_receipts custody_receipts contracts"
        )
        used = {_digest(refs["entries_sha256"])}
        banks: dict[str, dict[str, bytes]] = {}
        for name in ("sources", "safety_receipts", "custody_receipts", "contracts"):
            values = refs[name]
            require(type(values) is list and len(values) <= 100)
            digests = [_digest(value) for value in values]
            require(len(set(digests)) == len(digests))
            used.update(digests)
            banks[name] = {digest: bank[digest] for digest in digests}
        require(set(bank) == used)
        entries = parse_json(bank[refs["entries_sha256"]])
        # The attachment bank addresses supplied bytes; pipeline receipts address
        # canonical parsed contracts. Preserve raw bindings outside this adapter
        # and reject ambiguity rather than silently collapsing serializations.
        contracts: dict[str, dict[str, Any]] = {}
        for payload in banks["contracts"].values():
            contract = parse_json(payload)
            require(type(contract) is dict)
            digest = _sha(_canonical(contract))
            require(digest not in contracts)
            contracts[digest] = contract
        provenance = prepare_pipeline_prov(
            entries,
            banks["sources"],
            banks["safety_receipts"],
            banks["custody_receipts"],
            contracts,
        )
        event_id = _digest(selection["event_id"])
        matches = [entry for entry in entries if entry["history_event"]["event_id"] == event_id]
        require(len(matches) == 1)
        pipeline = matches[0]["pipeline"]
        role = selection["entity_role"]
        require(role in {"source", "bronze", "silver"})
        if role == "source":
            selected = banks["sources"][pipeline["source_sha256"]]
        else:
            selected = _canonical(pipeline["b1" if role == "bronze" else "silver"]["rows"])
    require(_sha(selected) == selection["entity_sha256"])
    uri = "urn:gfjd:sha256:" + _sha(selected)
    entity = (
        f"<{uri}> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> "
        "<http://www.w3.org/ns/prov#Entity> ."
    )
    require(entity.encode() in provenance["provenance.nt"].splitlines())
    return provenance, {**selection, "entity_uri": uri, "mode": mode}


def prepare_replayed_bundle(
    scope_raw: bytes,
    expected_scope_sha256: str,
    metadata_bank: dict[str, bytes],
    estate_inputs: dict[str, bytes],
    standards: dict[str, bytes],
    replay_raw: bytes,
    expected_replay_sha256: str,
    replay_bank: dict[str, bytes],
) -> dict[str, bytes]:
    """Recompute one attachment and its exact scoped byte identity, not ownership.

    Existing estate/bundle/replay helpers fingerprint implementation files.
    No source loader, remote lookup, or prebuilt provenance input is accepted.
    """
    try:
        provenance, binding = _replay(replay_raw, expected_replay_sha256, replay_bank)
        outputs = prepare_bundle(
            scope_raw, expected_scope_sha256, metadata_bank, estate_inputs, standards
        )
        scope = parse_json(scope_raw)
        matches = [obj for obj in scope["objects"] if obj["object_id"] == binding["object_id"]]
        require(len(matches) == 1)
        obj = matches[0]
        require(
            obj["content_sha256"] is not None and obj["content_sha256"] == binding["entity_sha256"]
        )
        binding["canonical_id"] = obj["canonical_id"]
        manifest = parse_json(outputs.pop("bundle-manifest.json"))
        outputs.update({"provenance/" + name: value for name, value in provenance.items()})
        outputs["README.md"] = (
            b"# Offline federation draft with one replay attachment\n\n"
            b"Only the selected scoped object's byte identity is bound to recomputed provenance. "
            b"Other objects remain pending. This does not establish semantic identity, ownership, "
            b"factual provenance, custody, rights, standards conformance, "
            b"publication or acceptance. "
            b"No source payload or input metadata is copied. Existing helper implementation "
            b"fingerprint reads occur; no source loader or network request occurs.\n"
        )
        manifest.update(
            {
                "contract_version": "gfjd-federation-replayed-bundle-v1",
                "provenance_integration": "selected_entity_replayed",
                "replay_sha256": _sha(replay_raw),
                "replay_bank_sha256": sorted(replay_bank),
                "replay_binding": binding,
                "provenance_pending_object_ids": sorted(
                    item["object_id"]
                    for item in scope["objects"]
                    if item["object_id"] != binding["object_id"]
                ),
                "artifact_sha256": {name: _sha(value) for name, value in sorted(outputs.items())},
            }
        )
        manifest["base_bundle_implementation_sha256"] = manifest.pop("implementation_sha256")
        outputs["bundle-manifest.json"] = _canonical(manifest) + b"\n"
        return dict(sorted(outputs.items()))
    except Exception:
        raise MetadataError("Replayed federation bundle contract violation") from None


def verify_replayed_bundle(
    scope_raw: bytes,
    expected_scope_sha256: str,
    metadata_bank: dict[str, bytes],
    estate_inputs: dict[str, bytes],
    standards: dict[str, bytes],
    replay_raw: bytes,
    expected_replay_sha256: str,
    replay_bank: dict[str, bytes],
    artifacts: dict[str, bytes],
) -> None:
    """Regenerate every artifact from replay inputs and compare exact set and bytes."""
    try:
        expected = prepare_replayed_bundle(
            scope_raw,
            expected_scope_sha256,
            metadata_bank,
            estate_inputs,
            standards,
            replay_raw,
            expected_replay_sha256,
            replay_bank,
        )
        require(type(artifacts) is dict and set(artifacts) == set(expected))
        require(
            all(
                type(value) is bytes and value == expected[name]
                for name, value in artifacts.items()
            )
        )
    except Exception:
        raise MetadataError("Replayed federation bundle contract violation") from None
