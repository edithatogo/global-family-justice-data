"""Fictional metadata-only integration; no source or provider access."""

import hashlib
import json
from pathlib import Path

import pytest

from gfjd.federation_bundle import prepare_bundle, verify_bundle
from gfjd.federation_metadata import MetadataError
from gfjd.medallion_estate import prepare_estate
from tests.test_federation_dcat import data as data
from tests.test_federation_openlineage import event as event
from tests.test_federation_rocrate import metadata as metadata
from tests.test_medallion_estate import configs as configs


def encode(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


@pytest.fixture
def standards() -> dict[str, bytes]:
    root = Path(__file__).parents[1] / "src/gfjd/federation_specs"
    return {
        name: (root / name).read_bytes()
        for name in (
            "openlineage-2-0-2.json",
            "dcat-ap-3.0.1-shapes.ttl",
            "dcat-ap-3.0.1-range.ttl",
            "ro-crate-1.3-context.jsonld",
            "gfjd-croissant-profile-v1.json",
        )
    }


@pytest.fixture
def inputs(configs):
    raw = encode({"description": "Fictional metadata; no empirical source"})
    scope = {
        "contract_version": "gfjd-federation-reference-scope-v1",
        "state": "preparation",
        "estate_manifest_sha256": sha(prepare_estate(configs)["estate-manifest.json"]),
        "partners": ["dataset-estate-registry"],
        "objects": [
            {
                "object_id": "fictional-source",
                "canonical_id": "urn:gfjd:source:fictional",
                "kind": "source",
                "role": "source-catalogue",
                "content_sha256": None,
                "metadata_sha256": sha(raw),
                "media_type": "application/json",
                "references": ["https://example.invalid/fictional"],
            }
        ],
    }
    scope_raw = encode(scope)
    return scope_raw, sha(scope_raw), {sha(raw): raw}, configs


def test_normative_binding_precedes_bundle(inputs, standards) -> None:
    standards["ro-crate-1.3-context.jsonld"] += b" "
    with pytest.raises(MetadataError):
        prepare_bundle(*inputs, standards)


def replace_metadata(inputs, raw: bytes, media: str):
    scope = json.loads(inputs[0])
    scope["objects"][0]["metadata_sha256"] = sha(raw)
    scope["objects"][0]["media_type"] = media
    scope_raw = encode(scope)
    return scope_raw, sha(scope_raw), {sha(raw): raw}, inputs[3]


def test_reference_only_deterministic_bundle(inputs, standards) -> None:
    output = prepare_bundle(*inputs, standards)
    assert output == prepare_bundle(*inputs, dict(reversed(list(standards.items()))))
    verify_bundle(*inputs, standards, output)
    manifest = json.loads(output["bundle-manifest.json"])
    assert manifest["incomplete_document_count"] == 1
    assert not any(manifest["authority"].values())
    assert manifest["provenance_integration"] == "pending_exact_replay_binding"
    assert len([name for name in output if name.startswith("estate/")]) == 8
    assert all(raw not in output.values() for raw in inputs[2].values())
    assert all(sha(output[name]) == digest for name, digest in manifest["artifact_sha256"].items())


@pytest.mark.parametrize("change", ["missing", "extra", "forged"])
def test_changed_bundle_rejected(inputs, standards, change: str) -> None:
    output = prepare_bundle(*inputs, standards)
    if change == "missing":
        del output["README.md"]
    elif change == "extra":
        output["unbound.json"] = b"{}"
    else:
        altered = json.loads(output["metadata-assessments.json"])
        next(iter(altered.values()))["status"] = "factual_acceptance"
        output["metadata-assessments.json"] = encode(altered)
        manifest = json.loads(output["bundle-manifest.json"])
        manifest["artifact_sha256"]["metadata-assessments.json"] = sha(
            output["metadata-assessments.json"]
        )
        output["bundle-manifest.json"] = encode(manifest)
    with pytest.raises(MetadataError):
        verify_bundle(*inputs, standards, output)


def test_rocrate_dispatch(inputs, standards, metadata) -> None:
    changed = replace_metadata(inputs, encode(metadata), "application/ld+json")
    output = prepare_bundle(*changed, standards)
    assert json.loads(output["bundle-manifest.json"])["incomplete_document_count"] == 0
    del metadata["@graph"][1]["datePublished"]
    output = prepare_bundle(
        *replace_metadata(inputs, encode(metadata), "application/ld+json"), standards
    )
    assert json.loads(output["bundle-manifest.json"])["incomplete_document_count"] == 1


def test_dcat_dispatch(inputs, standards, data) -> None:
    output = prepare_bundle(*replace_metadata(inputs, data, "application/n-triples"), standards)
    reports = json.loads(output["metadata-assessments.json"])
    assert next(iter(reports.values()))["status"] == "shape_checks_passed"


def test_recognisable_invalid_standard_is_not_skipped(inputs, standards) -> None:
    changed = replace_metadata(
        inputs, encode({"@context": "https://example.invalid/context"}), "application/ld+json"
    )
    with pytest.raises(MetadataError):
        prepare_bundle(*changed, standards)


def test_no_network(inputs, standards, monkeypatch) -> None:
    import socket
    import urllib.request

    def forbidden(*args, **kwargs):
        raise AssertionError("network access")

    monkeypatch.setattr(socket, "socket", forbidden)
    monkeypatch.setattr(urllib.request, "urlopen", forbidden)
    assert prepare_bundle(*inputs, standards)


def test_openlineage_dispatch(inputs, standards, event) -> None:
    changed = replace_metadata(inputs, encode(event), "application/json")
    output = prepare_bundle(*changed, standards)
    report = next(iter(json.loads(output["metadata-assessments.json"]).values()))
    assert report["schema_validated"] is True
    assert report["factual_evidence"] == "unverified"
    event["eventTime"] = "not-a-date"
    with pytest.raises(MetadataError):
        prepare_bundle(*replace_metadata(inputs, encode(event), "application/json"), standards)


def test_croissant_dispatch(inputs, standards) -> None:
    document = {
        "@context": json.loads(standards["gfjd-croissant-profile-v1.json"])["context"],
        "@type": "sc:Dataset",
        "conformsTo": "http://mlcommons.org/croissant/1.1",
        "name": "Fictional dataset",
        "description": "Synthetic declarations, no actual data",
        "creator": {"@type": "sc:Organization", "name": "Fictional organization"},
        "license": "https://example.invalid/license",
        "datePublished": "2026-08-31",
        "url": "https://example.invalid/dataset",
        "distribution": [
            {
                "@type": "cr:FileObject",
                "@id": "fictional.csv",
                "name": "fictional.csv",
                "contentUrl": "https://example.invalid/fictional.csv",
                "encodingFormat": "text/csv",
                "sha256": "a" * 64,
            }
        ],
    }
    output = prepare_bundle(
        *replace_metadata(inputs, encode(document), "application/ld+json"), standards
    )
    assert json.loads(output["bundle-manifest.json"])["incomplete_document_count"] == 0
    del document["distribution"]
    output = prepare_bundle(
        *replace_metadata(inputs, encode(document), "application/ld+json"), standards
    )
    assert json.loads(output["bundle-manifest.json"])["incomplete_document_count"] == 1


@pytest.mark.parametrize("change", ["missing", "extra", "type", "scope", "bank", "estate"])
def test_exact_input_membership(inputs, standards, change) -> None:
    scope_raw, digest, bank, estate = inputs
    if change == "missing":
        standards.pop("openlineage-2-0-2.json")
    elif change == "extra":
        standards["other.json"] = b"{}"
    elif change == "type":
        standards["openlineage-2-0-2.json"] = "not bytes"
    elif change == "scope":
        digest = "0" * 64
    elif change == "bank":
        bank[sha(b"{}")] = b"{}"
    else:
        estate[next(iter(estate))] += b"\n"
    with pytest.raises(MetadataError):
        prepare_bundle(scope_raw, digest, bank, estate, standards)


def test_inconsistent_media_for_shared_metadata(inputs, standards) -> None:
    scope = json.loads(inputs[0])
    other = dict(scope["objects"][0])
    other.update(
        object_id="other", canonical_id="urn:gfjd:source:other", media_type="application/ld+json"
    )
    scope["objects"].append(other)
    raw = encode(scope)
    with pytest.raises(MetadataError):
        prepare_bundle(raw, sha(raw), inputs[2], inputs[3], standards)
