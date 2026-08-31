"""Fictional composed references, never actual Parquet or partner acceptance."""

import json

import pytest

from gfjd.federation_interface_bundle import prepare_interface_bundle, verify_interface_bundle
from gfjd.federation_metadata import MetadataError
from tests.test_federation_replayed_bundle import encoded, sha
from tests.test_federation_replayed_bundle import inputs as inputs
from tests.test_federation_replayed_bundle import pipeline_inputs as pipeline_inputs


def sidecars(inputs: list) -> list:
    scope = json.loads(inputs[0])
    scope["objects"].append(
        dict(
            scope["objects"][0],
            object_id="parquet",
            canonical_id="urn:gfjd:observation:parquet",
            kind="observation",
            content_sha256="a" * 64,
        )
    )
    inputs[0] = encoded(scope)
    inputs[1] = sha(inputs[0])
    parquet = encoded(
        {
            "contract_version": "gfjd-parquet-reference-declarations-v1",
            "scope_sha256": inputs[1],
            "state": "preparation",
            "objects": [
                {
                    "object_id": "parquet",
                    "canonical_id": "urn:gfjd:observation:parquet",
                    "content_format": "parquet",
                    "content_sha256": "a" * 64,
                    "blake3": None,
                    "byte_count": None,
                    "locations": [],
                }
            ],
        }
    )
    partner = encoded(
        {
            "contract_version": "gfjd-partner-interface-references-v1",
            "scope_sha256": inputs[1],
            "state": "preparation",
            "partners": [],
        }
    )
    return [*inputs, parquet, sha(parquet), partner, sha(partner), {}]


def test_missing_sidecar_red(inputs: list) -> None:
    args = sidecars(inputs)
    args[8] = b""
    with pytest.raises(MetadataError):
        prepare_interface_bundle(*args)


def test_projection_bundle(inputs: list) -> None:
    args = sidecars(inputs)
    output = prepare_interface_bundle(*args)
    assert "interfaces/parquet-reference-report.json" in output
    assert "interfaces/partner-interface-report.json" in output
    manifest = json.loads(output["bundle-manifest.json"])
    assert manifest["contract_version"] == "gfjd-federation-interface-bundle-v1"
    assert manifest["provenance_pending_object_ids"] == ["parquet"]
    assert not any(manifest["authority"].values())
    assert b"PRIVATE_FICTIONAL_VALUE" not in b"".join(output.values())
    verify_interface_bundle(*args, output)


def replace_parquet_hash(args: list, digest: str) -> None:
    scope = json.loads(args[0])
    scope["objects"][1]["content_sha256"] = digest
    args[0] = encoded(scope)
    args[1] = sha(args[0])
    for index in (8, 10):
        doc = json.loads(args[index])
        doc["scope_sha256"] = args[1]
        if index == 8:
            doc["objects"][0]["content_sha256"] = digest
        args[index] = encoded(doc)
        args[index + 1] = sha(args[index])


@pytest.mark.parametrize("kind", ["source", "contract", "receipt", "rows", "standard"])
def test_known_nonparquet_projection(inputs: list, kind: str) -> None:
    args = sidecars(inputs)
    replay = json.loads(args[5])
    refs = replay["inputs"]
    if kind in {"source", "contract", "receipt"}:
        digest = refs[kind + "_sha256"]
    elif kind == "rows":
        digest = sha(encoded(json.loads(args[7][refs["receipt_sha256"]])["rows"]))
    elif kind == "standard":
        digest = sha(next(iter(args[4].values())))
    replace_parquet_hash(args, digest)
    with pytest.raises(MetadataError):
        prepare_interface_bundle(*args)


def test_pipeline_rows(pipeline_inputs: list) -> None:
    args = sidecars(pipeline_inputs)
    prepare_interface_bundle(*args)
    replay = json.loads(args[5])
    entry = json.loads(args[7][replay["inputs"]["entries_sha256"]])[0]
    replace_parquet_hash(args, sha(encoded(entry["pipeline"]["b1"]["rows"])))
    with pytest.raises(MetadataError):
        prepare_interface_bundle(*args)


def test_rehashed_forgery(inputs: list) -> None:
    args = sidecars(inputs)
    output = prepare_interface_bundle(*args)
    report = json.loads(output["interfaces/parquet-reference-report.json"])
    report["parquet_format_verified"] = True
    output["interfaces/parquet-reference-report.json"] = encoded(report)
    manifest = json.loads(output["bundle-manifest.json"])
    manifest["artifact_sha256"]["interfaces/parquet-reference-report.json"] = sha(
        output["interfaces/parquet-reference-report.json"]
    )
    output["bundle-manifest.json"] = encoded(manifest)
    with pytest.raises(MetadataError):
        verify_interface_bundle(*args, output)


@pytest.mark.parametrize("index", [8, 10])
def test_sidecar_digest_and_scope(inputs: list, index: int) -> None:
    args = sidecars(inputs)
    args[index + 1] = "0" * 64
    with pytest.raises(MetadataError):
        prepare_interface_bundle(*args)


@pytest.mark.parametrize("mode", ["extra", "missing", "compiler"])
def test_exact_artifacts(inputs: list, mode: str) -> None:
    args = sidecars(inputs)
    output = prepare_interface_bundle(*args)
    if mode == "extra":
        output["unbound.json"] = b"{}"
    elif mode == "missing":
        output.pop("interfaces/partner-interface-report.json")
    else:
        manifest = json.loads(output["bundle-manifest.json"])
        manifest["interface_implementation_sha256"] = "0" * 64
        output["bundle-manifest.json"] = encoded(manifest)
    with pytest.raises(MetadataError):
        verify_interface_bundle(*args, output)


def test_scope_substitution(inputs: list) -> None:
    args = sidecars(inputs)
    doc = json.loads(args[10])
    doc["scope_sha256"] = "0" * 64
    args[10] = encoded(doc)
    args[11] = sha(args[10])
    with pytest.raises(MetadataError):
        prepare_interface_bundle(*args)


def test_no_network_deterministic_and_fingerprints(
    inputs: list, monkeypatch: pytest.MonkeyPatch
) -> None:
    import socket
    import urllib.request
    from pathlib import Path

    import gfjd.federation_interface_bundle as module

    def forbidden(*args: object, **kwargs: object) -> None:
        raise AssertionError("network attempted")

    monkeypatch.setattr(socket, "socket", forbidden)
    monkeypatch.setattr(urllib.request, "urlopen", forbidden)
    args = sidecars(inputs)
    output = prepare_interface_bundle(*args)
    assert output == prepare_interface_bundle(*args)
    manifest = json.loads(output["bundle-manifest.json"])
    assert manifest["interface_implementation_sha256"] == sha(Path(module.__file__).read_bytes())
    for name, digest in manifest["artifact_sha256"].items():
        assert sha(output[name]) == digest
    assert manifest["parquet_format_verified"] is manifest["payload_digest_verified"] is False


def test_previous_history_rows_not_just_selected(inputs: list) -> None:
    from tests.test_federation_prov import pipeline

    entries, sources, safety, custody, contracts = pipeline.__wrapped__()
    contract_bytes = {key: encoded(value) for key, value in contracts.items()}
    entries_raw = encoded(entries)
    selected = entries[-1]["pipeline"]["source_sha256"]
    replay = {
        "contract_version": "gfjd-federation-replay-attachment-v1",
        "mode": "pipeline_history",
        "selection": {
            "object_id": "fictional",
            "entity_role": "source",
            "event_id": entries[-1]["history_event"]["event_id"],
            "entity_sha256": selected,
        },
        "inputs": {
            "entries_sha256": sha(entries_raw),
            "sources": list(sources),
            "safety_receipts": list(safety),
            "custody_receipts": list(custody),
            "contracts": list(contracts),
        },
    }
    scope = json.loads(inputs[0])
    scope["objects"][0]["content_sha256"] = selected
    inputs[0] = encoded(scope)
    inputs[1] = sha(inputs[0])
    inputs[5] = encoded(replay)
    inputs[6] = sha(inputs[5])
    inputs[7] = {**sources, **safety, **custody, **contract_bytes, sha(entries_raw): entries_raw}
    args = sidecars(inputs)
    prepare_interface_bundle(*args)
    replace_parquet_hash(args, sha(encoded(entries[0]["pipeline"]["silver"]["rows"])))
    with pytest.raises(MetadataError):
        prepare_interface_bundle(*args)
