"""Fictional candidate inventory binding, never release clearance."""

import hashlib
import json

import pytest
from blake3 import blake3

from gfjd.medallion_candidate_inputs import bundle_fingerprint, prepare_candidate_inputs


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def fixture():
    raw = b"FICTIONAL candidate"
    obj = dict(
        object_id="FICTIONAL",
        logical_object_id="FICTIONAL",
        edition_id="EDITION",
        layer="cross_layer",
        role="metadata",
        lifecycle="active",
        sha256=sha(raw),
        blake3=blake3(raw).hexdigest(),
        size_bytes=len(raw),
        media_type="text/plain",
        edges=[],
        locators={"github": None, "huggingface": None},
    )
    scope = dict(
        contract_version="gfjd-candidate-assurance-scope-v1",
        candidate_id="FICTIONAL",
        objects=[obj],
    )
    plan = dict(
        contract_version="gfjd-candidate-assurance-plan-v1",
        state="preparation",
        candidate_id="FICTIONAL",
        as_of="2026-09-01T00:00:00Z",
        scope_sha256=sha(encoded(scope)),
        evidence_bindings=dict.fromkeys(("qualification", "restore", "lifecycle", "dependencies")),
    )
    return plan, scope, {sha(raw): raw}, {}


def call(data):
    plan, scope, bank, evidence = data
    plan["scope_sha256"] = sha(encoded(scope))
    raw = encoded(plan)
    return prepare_candidate_inputs(raw, sha(raw), encoded(scope), bank, evidence)


def test_wrong_plan_digest_red():
    plan, scope, bank, evidence = fixture()
    with pytest.raises(ValueError):
        prepare_candidate_inputs(encoded(plan), "0" * 64, encoded(scope), bank, evidence)


def test_complete_binding():
    data = fixture()
    result = call(data)
    assert result["scope"] == data[1]
    assert result["candidate_bank"] == data[2]
    assert result["bundle_fingerprints"] == {}


@pytest.mark.parametrize(
    "value", [1.0, object(), {1: "x"}, b"x" * (8 * 1024 * 1024 + 1), "\ud800", "\x00"]
)
def test_invalid_tree(value):
    with pytest.raises(ValueError):
        bundle_fingerprint(value)


def test_descriptor_type_and_order():
    assert bundle_fingerprint({"b": b"x", "a": [None, True]}) == bundle_fingerprint(
        {"a": [None, True], "b": b"x"}
    )
    assert bundle_fingerprint(True) != bundle_fingerprint(1)
    assert bundle_fingerprint([1, 2]) != bundle_fingerprint([2, 1])


@pytest.mark.parametrize("escaped", [False, True])
def test_secret_control_metadata_rejected(escaped):
    plan, scope, bank, evidence = fixture()
    secret = "ghp_" + "a" * 36
    scope["objects"][0]["object_id"] = secret
    scope_raw = encoded(scope)
    if escaped:
        scope_raw = scope_raw.replace(b"ghp_", b"\\u0067hp_")
    plan["scope_sha256"] = sha(scope_raw)
    raw = encoded(plan)
    with pytest.raises(ValueError):
        prepare_candidate_inputs(raw, sha(raw), scope_raw, bank, evidence)


@pytest.mark.parametrize(
    "change",
    [
        "extra_bank",
        "missing_bank",
        "bad_size",
        "bool_size",
        "bad_b3",
        "bad_sha",
        "extra_key",
        "bad_role",
        "bad_media",
        "bad_target",
        "duplicate_edge",
        "bad_locator",
        "wrong_candidate",
    ],
)
def test_inventory_rejections(change):
    data = fixture()
    plan, scope, bank, _ = data
    obj = scope["objects"][0]
    if change == "extra_bank":
        bank[sha(b"extra")] = b"extra"
    elif change == "missing_bank":
        bank.clear()
    elif change == "bad_size":
        obj["size_bytes"] += 1
    elif change == "bool_size":
        obj["size_bytes"] = True
    elif change == "bad_b3":
        obj["blake3"] = "0" * 64
    elif change == "bad_sha":
        obj["sha256"] = "0" * 64
    elif change == "extra_key":
        obj["waiver"] = True
    elif change == "bad_role":
        obj["role"] = "exempt"
    elif change == "bad_media":
        obj["media_type"] = "text/plain; unsafe"
    elif change == "bad_target":
        obj["edges"] = [{"relation": "source", "target_object_id": "absent"}]
    elif change == "duplicate_edge":
        obj["edges"] = [{"relation": "source", "target_object_id": "FICTIONAL"}] * 2
    elif change == "bad_locator":
        obj["locators"]["github"] = "https://github.com/a?x=y"
    else:
        plan["candidate_id"] = "OTHER"
    with pytest.raises(ValueError):
        call(data)


def dependency_bundle():
    return dict(
        lock_raw=b"{}", sbom_raw=b"{}", package_bindings_raw=b"{}", project_name="FICTIONAL"
    )


def test_native_binding_without_semantic_execution():
    data = fixture()
    bundle = dependency_bundle()
    data[3]["dependencies"] = bundle
    data[0]["evidence_bindings"]["dependencies"] = bundle_fingerprint(bundle)
    result = call(data)
    assert result["bundle_fingerprints"]["dependencies"] == bundle_fingerprint(bundle)
    # This helper intentionally does not interpret the native JSON fields.
    assert result["evidence_bundles"]["dependencies"] == bundle


@pytest.mark.parametrize("mutation", ["missing", "extra", "wrongroot", "wrongtype", "fingerprint"])
def test_native_rejections(mutation):
    data = fixture()
    bundle = dependency_bundle()
    data[3]["dependencies"] = bundle
    if mutation == "wrongroot":
        bundle["unknown"] = None
    elif mutation == "wrongtype":
        bundle["lock_raw"] = "{}"
    data[0]["evidence_bindings"]["dependencies"] = bundle_fingerprint(bundle)
    if mutation == "missing":
        data[3].clear()
    elif mutation == "extra":
        data[3]["unbound"] = {}
    elif mutation == "fingerprint":
        data[0]["evidence_bindings"]["dependencies"] = "0" * 64
    with pytest.raises(ValueError):
        call(data)


@pytest.mark.parametrize(
    "value", [[b"x" * (8 * 1024 * 1024)] * 9, ["x" * 4096] * 257, 1 << 4096, [0] * 2001]
)
def test_tree_aggregate_before_hash(value, monkeypatch):
    import gfjd.medallion_candidate_inputs as module

    def forbidden(*args):
        pytest.fail("hashing before budget rejection")

    monkeypatch.setattr(module, "_sha", forbidden)
    with pytest.raises(ValueError):
        bundle_fingerprint(value)


def test_tree_depth_and_subclass():
    value = None
    for _ in range(13):
        value = [value]
    with pytest.raises(ValueError):
        bundle_fingerprint(value)

    class Text(str):
        pass

    with pytest.raises(ValueError):
        bundle_fingerprint(Text("x"))


def test_same_digest_category_charging_and_conflicts():
    import copy

    data = fixture()
    other = copy.deepcopy(data[1]["objects"][0])
    other.update(object_id="SECOND", role="package", lifecycle="withdrawn")
    data[1]["objects"].append(other)
    report = call(data)["inventory_report"]
    assert report["object_count"] == 2 and report["unique_content_count"] == 1
    assert (
        report["category_bytes"]["metadata"]
        == report["category_bytes"]["package"]
        == report["unique_bytes"]
    )
    other["media_type"] = "application/json"
    with pytest.raises(ValueError):
        call(data)


def test_role_budget_before_hash(monkeypatch):
    import copy

    import gfjd.medallion_candidate_inputs as module

    data = fixture()
    bank = {}
    objects = []
    for i in range(2):
        raw = bytes([i]) * (5 * 1024 * 1024)
        obj = copy.deepcopy(data[1]["objects"][0])
        obj.update(
            object_id=f"OBJECT-{i}",
            sha256=sha(raw),
            blake3=blake3(raw).hexdigest(),
            size_bytes=len(raw),
        )
        objects.append(obj)
        bank[sha(raw)] = raw
    data[1]["objects"] = objects
    data = data[0], data[1], bank, data[3]

    def forbidden(*args):
        pytest.fail("hash before candidate category budget")

    monkeypatch.setattr(module, "_sha", forbidden)
    with pytest.raises(ValueError):
        call(data)


def test_no_loader_and_fixed_diagnostic(monkeypatch):
    import socket
    import traceback
    import urllib.request

    def forbidden(*args, **kwargs):
        pytest.fail("unexpected network")

    monkeypatch.setattr(socket, "socket", forbidden)
    monkeypatch.setattr(urllib.request, "urlopen", forbidden)
    assert call(fixture()) == call(fixture())
    data = fixture()
    data[1]["objects"][0]["object_id"] = "PRIVATE_SENTINEL/invalid"
    try:
        call(data)
    except ValueError:
        assert "PRIVATE_SENTINEL" not in traceback.format_exc()
    else:
        pytest.fail("invalid identity accepted")


def test_combined_evidence_budget_before_any_hash(monkeypatch):
    import gfjd.medallion_candidate_inputs as module

    data = fixture()
    leaf = b"x" * (8 * 1024 * 1024)
    data[3]["dependencies"] = dict(
        lock_raw=leaf, sbom_raw=leaf, package_bindings_raw=leaf, project_name="FICTIONAL"
    )
    data[3]["lifecycle"] = dict(
        plan_raw=leaf,
        expected_plan_sha256="0" * 64,
        scope_raw=leaf,
        layer_contract_raw=leaf,
        checkpoint_raw=leaf,
        event_bank={"x": leaf},
        receipt_bank={"x": leaf},
    )
    for name in data[3]:
        data[0]["evidence_bindings"][name] = "0" * 64

    def forbidden(*args):
        pytest.fail("hash before aggregate evidence byte bound")

    monkeypatch.setattr(module, "_sha", forbidden)
    with pytest.raises(ValueError):
        call(data)


@pytest.mark.parametrize(
    "locator",
    [
        "http://github.com/x",
        "https://github.com",
        "https://u@github.com/x",
        "https://github.com:443/x",
        "https://github.com/x#fragment",
        "https://github.com/%xx",
        "https://example.invalid/x",
    ],
)
def test_locator_scope(locator):
    data = fixture()
    data[1]["objects"][0]["locators"]["github"] = locator
    with pytest.raises(ValueError):
        call(data)


def test_valid_locators_are_declarations():
    data = fixture()
    data[1]["objects"][0]["locators"] = {
        "github": "https://github.com/FICTIONAL/object",
        "huggingface": "https://huggingface.co/FICTIONAL/object",
    }
    assert call(data)["scope"]["objects"][0]["locators"] == data[1]["objects"][0]["locators"]
