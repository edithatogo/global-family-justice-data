"""Fictional declarations over real pinned technical contracts; no source access."""

import copy
import hashlib
import json
from pathlib import Path

import pytest

from gfjd.federation_metadata import MetadataError
from gfjd.federation_partner_interfaces import (
    PINNED,
    assess_partner_interfaces,
    verify_partner_interfaces,
)
from gfjd.medallion_estate import prepare_estate
from tests.test_medallion_estate import configs as configs


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


@pytest.fixture
def inputs(configs):
    root = Path(__file__).parents[1] / "src/gfjd/federation_specs"
    bank = {}
    for name in (
        "shared-medallion-v1.schema.json",
        "shared-medallion-v2.schema.json",
        "shared-medallion-v3.schema.json",
        "partner-gma-federation.schema.json",
        "partner-gma-semantics.py.txt",
        "partner-archive-publication.schema.json",
        "partner-archive-ownership.py.txt",
    ):
        raw = (root / name).read_bytes()
        bank[sha(raw)] = raw
    metadata = b'{"description":"Fictional source metadata"}'
    scope = {
        "contract_version": "gfjd-federation-reference-scope-v1",
        "state": "preparation",
        "estate_manifest_sha256": sha(prepare_estate(configs)["estate-manifest.json"]),
        "partners": [
            "archive-govt-nz",
            "global-medicines-atlas",
            "reimbursement-atlas",
            "dataset-estate-registry",
        ],
        "objects": [
            {
                "object_id": "fictional",
                "canonical_id": "urn:gfjd:source:fictional",
                "kind": "source",
                "role": "source-catalogue",
                "content_sha256": None,
                "metadata_sha256": sha(metadata),
                "media_type": "application/json",
                "references": [],
            }
        ],
    }
    raw = encode(scope)
    declaration = {
        "contract_version": "gfjd-partner-interface-references-v1",
        "scope_sha256": sha(raw),
        "state": "preparation",
        "partners": [
            {
                "partner_id": name,
                **copy.deepcopy(PINNED.get(name, {"commit": None, "artifacts": {}})),
            }
            for name in scope["partners"]
        ],
    }
    declared = encode(declaration)
    return [declared, sha(declared), raw, sha(raw), {sha(metadata): metadata}, configs, bank]


def test_wrong_declaration_binding_rejected() -> None:
    with pytest.raises(MetadataError):
        assess_partner_interfaces(b"{}", "0" * 64, b"{}", "0" * 64, {}, {}, {})


def test_pinned_references_not_live_acceptance(inputs) -> None:
    report = assess_partner_interfaces(*inputs)
    assert report["bound_partner_count"] == 2
    assert report["status"] == "partial_reference_binding"
    assert report["pending_partner_ids"] == ["dataset-estate-registry", "reimbursement-atlas"]
    assert report["semantic_code_executed"] is False
    assert not any(report["authority"].values())
    assert report["partners"][0]["qualification"]["ownership_transfer"] == "unsupported_for_gfjd"
    gma = next(p for p in report["partners"] if p["partner_id"] == "global-medicines-atlas")
    assert gma["qualification"]["direct_gfjd_layer_aliasing"] is False
    assert gma["qualification"]["gma_bronze_strata"]["B2"] == "raw"
    assert gma["qualification"]["portable_contracts"] == ["v1", "v2", "v3", "v4"]
    assert gma["qualification"]["record_schema"] == "repository_verified"
    assert all(raw.decode() not in json.dumps(report) for raw in inputs[6].values())
    verify_partner_interfaces(*inputs, report)
    inputs[6] = dict(reversed(list(inputs[6].items())))
    assert report == assess_partner_interfaces(*inputs)


@pytest.mark.parametrize(
    "change",
    [
        "commit",
        "path",
        "missing_partner",
        "duplicate_partner",
        "unknown_contract",
        "extra_field",
        "scope",
        "empty_with_commit",
    ],
)
def test_declaration_contract_rejects_drift(inputs, change) -> None:
    document = json.loads(inputs[0])
    first = document["partners"][0]
    if change == "commit":
        first["commit"] = "0" * 40
    elif change == "path":
        first["artifacts"] = {"../../unbound": "0" * 64}
    elif change == "missing_partner":
        document["partners"].pop()
    elif change == "duplicate_partner":
        document["partners"][1] = first
    elif change == "unknown_contract":
        document["partners"][2]["commit"] = "a" * 40
    elif change == "extra_field":
        first["accepted"] = True
    elif change == "scope":
        document["scope_sha256"] = "0" * 64
    else:
        first["artifacts"] = {}
    inputs[0] = encode(document)
    inputs[1] = sha(inputs[0])
    with pytest.raises(MetadataError):
        assess_partner_interfaces(*inputs)


@pytest.mark.parametrize("change", ["missing", "extra", "changed", "oversized", "wrong_type"])
def test_bank_membership_and_bounds(inputs, change) -> None:
    digest = next(iter(inputs[6]))
    if change == "missing":
        inputs[6].pop(digest)
    elif change == "extra":
        inputs[6][sha(b"extra")] = b"extra"
    elif change == "changed":
        inputs[6][digest] += b" "
    elif change == "oversized":
        raw = b"x" * (1024 * 1024 + 1)
        inputs[6] = {sha(raw): raw}
    else:
        inputs[6][digest] = "not bytes"
    with pytest.raises(MetadataError):
        assess_partner_interfaces(*inputs)


@pytest.mark.parametrize("change", ["authority", "count", "compatibility", "type_alias"])
def test_forged_report_rejected(inputs, change) -> None:
    report = assess_partner_interfaces(*inputs)
    if change == "authority":
        report["authority"]["publication"] = True
    elif change == "count":
        report["bound_partner_count"] = 4
    elif change == "compatibility":
        report["live_interoperability"] = "accepted"
    else:
        report["semantic_code_executed"] = 0
    with pytest.raises(MetadataError):
        verify_partner_interfaces(*inputs, report)


def test_unavailable_contracts_stay_pending(inputs) -> None:
    declaration = json.loads(inputs[0])
    for item in declaration["partners"]:
        item.update(commit=None, artifacts={})
    inputs[0] = encode(declaration)
    inputs[1] = sha(inputs[0])
    inputs[6] = {}
    report = assess_partner_interfaces(*inputs)
    assert report["bound_partner_count"] == 0
    assert len(report["pending_partner_ids"]) == 4


def test_no_network(inputs, monkeypatch) -> None:
    import socket
    import urllib.request

    def forbidden(*args, **kwargs):
        raise AssertionError("network requested")

    monkeypatch.setattr(socket, "socket", forbidden)
    monkeypatch.setattr(urllib.request, "urlopen", forbidden)
    assert assess_partner_interfaces(*inputs)["semantic_code_executed"] is False
