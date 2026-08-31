"""Fictional canonical responsibility, never actual ownership or transfers."""

import copy
import json
import socket
import traceback
import urllib.request

import pytest

from gfjd.federation_metadata import MetadataError
from gfjd.federation_ownership import assess_ownership_references, verify_ownership_references
from tests.test_federation_references import inputs as reference_inputs
from tests.test_federation_references import sha


@pytest.fixture
def inputs():
    return reference_inputs.__wrapped__()


def arguments(inputs, records=None):
    scope, bank, estate = inputs
    scope_raw = json.dumps(scope).encode()
    if records is None:
        records = [
            {
                **{key: obj[key] for key in ("object_id", "canonical_id", "content_sha256")},
                "relationship": "unresolved",
                "target": None,
            }
            for obj in scope["objects"]
        ]
    raw = json.dumps(
        {
            "contract_version": "gfjd-canonical-ownership-declarations-v1",
            "state": "preparation",
            "scope_sha256": sha(scope_raw),
            "objects": records,
        }
    ).encode()
    return raw, sha(raw), scope_raw, sha(scope_raw), bank, estate


def test_missing_coverage_red(inputs):
    with pytest.raises(MetadataError):
        assess_ownership_references(*arguments(inputs, []))


def records(inputs, relation="reference"):
    return [
        {
            **{key: obj[key] for key in ("object_id", "canonical_id", "content_sha256")},
            "relationship": relation,
            "target": None
            if relation == "unresolved"
            else {
                "owner_id": "gfjd" if relation == "canonical" else "archive-govt-nz",
                "native_object_id": obj["canonical_id"]
                if relation == "canonical"
                else " native identity ",
            },
        }
        for obj in inputs[0]["objects"]
    ]


@pytest.mark.parametrize("relationship", ["canonical", "reference", "unresolved"])
def test_positive_reports(inputs, relationship):
    args = arguments(inputs, records(inputs, relationship))
    report = assess_ownership_references(*args)
    assert report["declaration_consistency"] == "verified"
    assert report["missing_content_ids"] == ["fictional-edition"]
    assert report["unresolved_ids"] == (
        ["fictional-edition"] if relationship == "unresolved" else []
    )
    assert not any(report["authority"].values())
    assert set(report["factual_states"].values()) == {"unverified"}
    if relationship == "reference":
        assert report["objects"][0]["target"]["native_object_id"] == " native identity "
    verify_ownership_references(*args, report)


def expand(inputs, hashes):
    scope = inputs[0]
    template = scope["objects"][0]
    scope["objects"] = [
        {
            **template,
            "object_id": f"object-{i}",
            "canonical_id": f"urn:gfjd:edition:fictional-{i}",
            "content_sha256": digest,
        }
        for i, digest in enumerate(hashes)
    ]


def test_shared_target_null_retained(inputs):
    expand(inputs, [None, "a" * 64, "a" * 64])
    report = assess_ownership_references(*arguments(inputs, records(inputs)))
    assert report["objects"][0]["content_sha256"] is None
    assert report["missing_content_ids"] == ["object-0"]
    assert report["shared_target_groups"] == [
        {
            "owner_id": "archive-govt-nz",
            "native_object_id": " native identity ",
            "object_ids": ["object-0", "object-1", "object-2"],
            "declared_nonnull_content_sha256": ["a" * 64],
            "missing_content_ids": ["object-0"],
        }
    ]


def test_shared_target_conflict(inputs):
    expand(inputs, ["a" * 64, "b" * 64])
    with pytest.raises(MetadataError):
        assess_ownership_references(*arguments(inputs, records(inputs)))


@pytest.mark.parametrize("different_partner", [False, True])
def test_distinct_identity_equal_bytes_not_merged(inputs, different_partner):
    expand(inputs, ["a" * 64, "a" * 64])
    rows = records(inputs)
    if different_partner:
        inputs[0]["partners"].append("global-medicines-atlas")
        rows[1]["target"]["owner_id"] = "global-medicines-atlas"
    else:
        rows[1]["target"]["native_object_id"] = "other"
    report = assess_ownership_references(*arguments(inputs, rows))
    assert len(report["objects"]) == 2
    assert report["shared_target_groups"] == []


@pytest.mark.parametrize(
    "field,value",
    [
        ("object_id", "extra"),
        ("canonical_id", "urn:gfjd:edition:other"),
        ("content_sha256", "a" * 64),
        ("relationship", "transfer"),
        ("relationship", []),
        ("target", {}),
        ("unexpected", True),
    ],
)
def test_object_mismatch(inputs, field, value):
    rows = records(inputs)
    rows[0][field] = value
    with pytest.raises(MetadataError):
        assess_ownership_references(*arguments(inputs, rows))


@pytest.mark.parametrize(
    "field,value",
    [
        ("owner_id", "gfjd"),
        ("owner_id", "unselected"),
        ("owner_id", []),
        ("native_object_id", " "),
        ("native_object_id", "x" * 513),
        ("native_object_id", "private\x00value"),
        ("native_object_id", True),
        ("extra", "x"),
    ],
)
def test_target_mismatch(inputs, field, value):
    rows = records(inputs)
    rows[0]["target"][field] = value
    with pytest.raises(MetadataError):
        assess_ownership_references(*arguments(inputs, rows))


def test_canonical_and_unresolved_requirements(inputs):
    rows = records(inputs, "canonical")
    rows[0]["target"]["native_object_id"] = "other"
    with pytest.raises(MetadataError):
        assess_ownership_references(*arguments(inputs, rows))
    rows = records(inputs)
    rows[0]["relationship"] = "unresolved"
    with pytest.raises(MetadataError):
        assess_ownership_references(*arguments(inputs, rows))


def test_duplicates_and_extra_scope_records(inputs):
    rows = records(inputs)
    with pytest.raises(MetadataError):
        assess_ownership_references(*arguments(inputs, rows * 2))
    extra = copy.deepcopy(rows[0])
    extra["object_id"] = "extra"
    with pytest.raises(MetadataError):
        assess_ownership_references(*arguments(inputs, rows + [extra]))


def test_order_changes_digest_not_sorted_records(inputs):
    expand(inputs, [None, None])
    rows = records(inputs)
    first = assess_ownership_references(*arguments(inputs, rows))
    second = assess_ownership_references(*arguments(inputs, rows[::-1]))
    assert first["objects"] == second["objects"]
    assert first["shared_target_groups"] == second["shared_target_groups"]
    assert first["declaration_sha256"] != second["declaration_sha256"]


@pytest.mark.parametrize(
    "raw", [b"{}", b'{"x":1,"x":2}', b'{"x":NaN}', b"x" * (1024 * 1024 + 1), b"\xff"]
)
def test_invalid_json(inputs, raw):
    args = list(arguments(inputs))
    args[:2] = [raw, sha(raw)]
    with pytest.raises(MetadataError):
        assess_ownership_references(*args)


def test_wrong_binding_and_bank(inputs):
    args = list(arguments(inputs))
    args[1] = "0" * 64
    with pytest.raises(MetadataError):
        assess_ownership_references(*args)
    args = list(arguments(inputs))
    args[4] = {}
    with pytest.raises(MetadataError):
        assess_ownership_references(*args)


@pytest.mark.parametrize(
    "field,value",
    [
        ("object_count", True),
        ("declaration_consistency", "accepted"),
        ("implementation_sha256", "a" * 64),
        ("unresolved_ids", []),
    ],
)
def test_forgery(inputs, field, value):
    args = arguments(inputs)
    report = assess_ownership_references(*args)
    report[field] = value
    with pytest.raises(MetadataError):
        verify_ownership_references(*args, report)


def test_no_network_fixed_error(inputs, monkeypatch, capsys):
    def denied(*args, **kwargs):
        raise AssertionError("network attempted")

    monkeypatch.setattr(socket, "create_connection", denied)
    monkeypatch.setattr(urllib.request, "urlopen", denied)
    args = arguments(inputs)
    assert assess_ownership_references(*args) == assess_ownership_references(*args)
    rows = records(inputs)
    rows[0]["target"]["owner_id"] = "PRIVATE_SENTINEL"
    try:
        assess_ownership_references(*arguments(inputs, rows))
    except MetadataError:
        assert "PRIVATE_SENTINEL" not in traceback.format_exc()
    else:
        pytest.fail("unknown owner accepted")
    assert capsys.readouterr() == ("", "")


def test_hundred_objects_and_native_limit(inputs):
    expand(inputs, [None] * 100)
    rows = records(inputs)
    for row in rows:
        row["target"]["native_object_id"] = "x" * 512
    report = assess_ownership_references(*arguments(inputs, rows))
    assert report["object_count"] == 100
    assert len(report["missing_content_ids"]) == 100
    assert report["estate_input_sha256"] == {name: sha(raw) for name, raw in inputs[2].items()}
    assert report["metadata_sha256"] == sorted(inputs[1])
    with pytest.raises(MetadataError):
        assess_ownership_references(*arguments(inputs, rows + [rows[0]]))


@pytest.mark.parametrize(
    "field,value",
    [
        ("extra", True),
        ("scope_sha256", "a" * 64),
        ("state", "accepted"),
        ("contract_version", "future"),
    ],
)
def test_envelope_contract(inputs, field, value):
    args = list(arguments(inputs))
    doc = json.loads(args[0])
    doc[field] = value
    args[0] = json.dumps(doc).encode()
    args[1] = sha(args[0])
    with pytest.raises(MetadataError):
        assess_ownership_references(*args)
