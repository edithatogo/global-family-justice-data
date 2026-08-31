"""Fictional replica banks, never provider retrieval or acquired source input."""

import copy
import hashlib
import json
import socket
import traceback
from pathlib import Path

import pytest
from blake3 import blake3

from gfjd import medallion_restore_inputs as module
from gfjd.medallion_qualification_inputs import canonical, sha
from gfjd.medallion_restore_inputs import preflight, prepare_replica
from tests.test_medallion_qualification import AS_OF, fixture


def test_empty_bank_red():
    with pytest.raises(ValueError):
        prepare_replica(b"{}", "a" * 64, b"{}", "a" * 64, b"{}", {}, "github")


def build(values, auxiliary=None):
    scope, wrappers, payloads, contract = values
    roots = canonical(scope)
    records = {sha(canonical(record)): canonical(record) for record in wrappers}
    union = {value for wrapper in wrappers for value in wrapper["artifacts"].values()}
    payloads = {digest: payloads[digest] for digest in union}
    aux = auxiliary or {}
    bank = {**records, **payloads, **aux, sha(roots): roots, sha(contract): contract}
    plan = {
        "contract_version": "gfjd-two-replica-restore-plan-v1",
        "state": "preparation",
        "release_id": "FICTIONAL",
        "scope_sha256": sha(roots),
        "layer_contract_sha256": sha(contract),
        "as_of": AS_OF,
        "expected_qualification_sha256": "a" * 64,
        "record_sha256": sorted(records),
        "payload_sha256": sorted(payloads),
        "auxiliary_sha256": sorted(aux),
        "inventory": [
            {"sha256": digest, "blake3": blake3(raw).hexdigest(), "size_bytes": len(raw)}
            for digest, raw in sorted(bank.items())
        ],
        "providers": {
            provider: {
                "locators": {digest: f"https://{host}/fictional/{digest}" for digest in bank}
            }
            for provider, host in module.PROVIDERS.items()
        },
    }
    return plan, roots, contract, bank


def call(parts, provider="github"):
    plan, scope, contract, bank = parts
    raw = canonical(plan)
    return prepare_replica(raw, sha(raw), scope, sha(scope), contract, bank, provider)


@pytest.fixture
def values():
    return fixture(Path(__file__).resolve().parents[1])


def test_complete_five_layer_inventory(values):
    parts = build(values)
    result = call(parts)
    assert set(result) == {
        "scope_raw",
        "layer_contract_raw",
        "record_bank",
        "eligible_payload_bank",
        "plan",
        "inventory_report",
        "preservation_edges",
        "binding",
    }
    assert len(result["binding"]["coverage"]) == 5
    assert len(result["record_bank"]) == 5
    assert result["inventory_report"]["fixity"] == "verified"
    assert result["inventory_report"]["unique_bytes"] == sum(map(len, parts[3].values()))
    assert {edge["payload_sha256"] for edge in result["preservation_edges"]} == set(
        parts[0]["payload_sha256"]
    )
    assert all(edge["processing_eligible"] for edge in result["preservation_edges"])
    assert result["eligible_payload_bank"] == {
        key: parts[3][key] for key in parts[0]["payload_sha256"]
    }
    second = call(parts, "huggingface")
    assert second["binding"] == result["binding"]


def test_inactive_payload_union_preserved_without_decoding(values):
    scope, wrappers, payloads, _ = values
    scope["objects"][0]["layers"]["gold"].update(
        state="quarantined", reason_codes=["FICTIONAL"], disposition_reference="FICTIONAL"
    )
    wrapper = wrappers[3]
    wrapper["record"]["lifecycle_state"] = "quarantined"
    opaque = b"\xff\x00INACTIVE_NOT_JSON"
    payloads[sha(opaque)] = opaque
    wrapper["artifacts"]["quality"] = sha(opaque)
    result = call(build(values))
    edges = [edge for edge in result["preservation_edges"] if edge["layer"] == "gold"]
    assert edges and not any(edge["processing_eligible"] for edge in edges)
    assert sha(opaque) not in result["eligible_payload_bank"]
    assert sha(opaque) in {item["sha256"] for item in result["inventory_report"]["inventory"]}


def test_inactive_shared_digest_only_active_edge_eligible(values):
    scope, wrappers, _, _ = values
    scope["objects"][0]["layers"]["gold"].update(
        state="withdrawn", reason_codes=["FICTIONAL"], disposition_reference="FICTIONAL"
    )
    wrappers[3]["record"]["lifecycle_state"] = "withdrawn"
    result = call(build(values))
    shared = wrappers[3]["artifacts"]["rows"]
    matching = [edge for edge in result["preservation_edges"] if edge["payload_sha256"] == shared]
    assert {edge["processing_eligible"] for edge in matching} == {True, False}


@pytest.mark.parametrize("mutation", ["missing", "extra", "corrupt", "root_missing", "root_wrong"])
def test_bad_bank(values, mutation):
    parts = build(values)
    digest = parts[0]["payload_sha256"][0]
    if mutation == "missing":
        del parts[3][digest]
    elif mutation == "extra":
        parts[3][sha(b"extra")] = b"extra"
    elif mutation == "corrupt":
        parts[3][digest] += b"x"
    elif mutation == "root_missing":
        del parts[3][parts[0]["scope_sha256"]]
    else:
        parts[3][parts[0]["scope_sha256"]] = b"{}"
    with pytest.raises(ValueError):
        call(parts)


@pytest.mark.parametrize(
    "mutation", ["sha", "b3", "size", "bool_size", "duplicate", "union", "extra_field"]
)
def test_inventory_and_union(values, mutation):
    parts = build(values)
    plan = parts[0]
    item = plan["inventory"][0]
    if mutation == "sha":
        item["sha256"] = "0" * 64
    elif mutation == "b3":
        item["blake3"] = "0" * 64
    elif mutation == "size":
        item["size_bytes"] += 1
    elif mutation == "bool_size":
        item["size_bytes"] = True
    elif mutation == "duplicate":
        plan["inventory"].append(copy.deepcopy(item))
    elif mutation == "union":
        plan["payload_sha256"].pop()
    else:
        item["extra"] = "x"
    with pytest.raises(ValueError):
        call(parts)


@pytest.mark.parametrize(
    "url",
    [
        "https://github.com",
        "http://github.com/x",
        "https://github.com:443/x",
        "https://github.com@evil.invalid/x",
        "https://github.com/x?q=1",
        "https://github.com/x#f",
        "https://github.com/\\x",
        "https://github.com/\u0001",
        "https://evil.invalid/x",
    ],
)
def test_locator_restrictions(values, url):
    parts = build(values)
    locators = parts[0]["providers"]["github"]["locators"]
    locators[next(iter(locators))] = url
    with pytest.raises(ValueError):
        call(parts)


@pytest.mark.parametrize(
    "raw",
    [
        b'{"x":1,"x":2}',
        b'{"x":NaN}',
        b'{"x":Infinity}',
        b'"\\ud800"',
        b'"\\u0000"',
        b"[" * 17 + b"0" + b"]" * 17,
        b"\xff",
        b"x" * (1024 * 1024 + 1),
        json.dumps([0] * 2001).encode(),
        json.dumps("x" * 4097).encode(),
        json.dumps([[0] * 1000] * 51).encode(),
    ],
)
def test_preflight_bounds(raw):
    with pytest.raises(ValueError):
        preflight(raw)


def test_overlap_charged_to_each_category(values):
    parts = build(values)
    digest = parts[0]["record_sha256"][0]
    parts[0]["auxiliary_sha256"] = [digest]
    result = call(parts)
    report = result["inventory_report"]
    assert report["category_bytes"]["auxiliary"] == len(parts[3][digest])
    assert report["category_bytes"]["records"] == sum(
        len(parts[3][d]) for d in parts[0]["record_sha256"]
    )


def test_auxiliary_budget_precedes_hashing(values, monkeypatch):
    a, b = b"a" * (4 * module.MIB + 1), b"b" * (4 * module.MIB)
    parts = build(values, {sha(a): a, sha(b): b})
    raw = canonical(parts[0])
    digest, scope_digest = sha(raw), sha(parts[1])

    def forbidden(*args, **kwargs):
        pytest.fail("hash called before budget rejection")

    monkeypatch.setattr(hashlib, "sha256", forbidden)
    with pytest.raises(ValueError):
        prepare_replica(raw, digest, parts[1], scope_digest, parts[2], parts[3], "github")


def test_invalid_active_record_preserves_refs(values):
    values[1][0]["record"]["evidence"]["size_bytes"] = True
    result = call(build(values))
    assert result["binding"]["coverage"][0]["record_status"] == "invalid"
    assert all(
        not edge["processing_eligible"]
        for edge in result["preservation_edges"]
        if edge["layer"] == "b0"
    )


def test_no_network_diagnostics(values, monkeypatch, capsys):
    parts = build(values)

    def denied(*args, **kwargs):
        pytest.fail("network attempted")

    monkeypatch.setattr(socket, "create_connection", denied)
    assert call(parts)["inventory_report"]["fixity"] == "verified"
    parts[0]["release_id"] = "PRIVATE_SENTINEL/invalid"
    try:
        call(parts)
    except ValueError:
        assert "PRIVATE_SENTINEL" not in traceback.format_exc()
    else:
        pytest.fail("bad identity accepted")
    assert capsys.readouterr() == ("", "")


def test_payload_cannot_be_reclassified_auxiliary(values):
    parts = build(values)
    digest = parts[0]["payload_sha256"].pop()
    parts[0]["auxiliary_sha256"].append(digest)
    # Inventory and bank remain exactly complete; only preservation role changed.
    with pytest.raises(ValueError):
        call(parts)


def test_unknown_active_artifact_role_rejected(values):
    wrapper = values[1][0]
    wrapper["artifacts"]["unknown_role"] = wrapper["artifacts"]["source"]
    with pytest.raises(ValueError):
        call(build(values))


def test_wrapper_preflight_before_legacy_parser(values, monkeypatch):
    values[1][0]["record"]["deep"] = json.loads("[" * 18 + "0" + "]" * 18)
    parts = build(values)

    def forbidden(*args, **kwargs):
        pytest.fail("legacy parser called before structured preflight")

    monkeypatch.setattr(module.inputs, "bind_layer_records", forbidden)
    with pytest.raises(ValueError):
        call(parts)


@pytest.mark.parametrize(
    "change", ["missing_provider", "extra_provider", "missing_locator", "count"]
)
def test_provider_and_category_membership(values, change):
    parts = build(values)
    if change == "missing_provider":
        del parts[0]["providers"]["huggingface"]
    elif change == "extra_provider":
        parts[0]["providers"]["other"] = {"locators": {}}
    elif change == "missing_locator":
        parts[0]["providers"]["huggingface"]["locators"].popitem()
    else:
        parts[0]["auxiliary_sha256"] = [f"{i:064x}" for i in range(501)]
    with pytest.raises(ValueError):
        call(parts)
