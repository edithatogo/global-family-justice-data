"""Fictional Parquet declarations, not actual Parquet or publication evidence."""

import json

import pytest

from gfjd.federation_metadata import MetadataError
from gfjd.federation_parquet_references import assess_parquet_references, verify_parquet_references
from tests.test_federation_references import encode, sha
from tests.test_federation_references import inputs as inputs


@pytest.fixture
def arguments(inputs: tuple) -> list:
    scope, bank, estate = inputs
    obj = scope["objects"][0]
    obj["content_sha256"] = "a" * 64
    scope_raw = encode(scope)
    declaration = {
        "contract_version": "gfjd-parquet-reference-declarations-v1",
        "scope_sha256": sha(scope_raw),
        "state": "preparation",
        "objects": [
            {
                "object_id": obj["object_id"],
                "canonical_id": obj["canonical_id"],
                "content_format": "parquet",
                "content_sha256": "a" * 64,
                "blake3": "b" * 64,
                "byte_count": 123,
                "locations": [
                    {
                        "url": "https://example.invalid/fictional.parquet",
                        "revision": {"kind": "content_sha256", "value": "a" * 64},
                    }
                ],
            }
        ],
    }
    raw = encode(declaration)
    return [raw, sha(raw), scope_raw, sha(scope_raw), bank, estate]


def test_digest_red(arguments: list) -> None:
    arguments[1] = "0" * 64
    with pytest.raises(MetadataError):
        assess_parquet_references(*arguments)


def test_complete_no_authority(arguments: list) -> None:
    report = assess_parquet_references(*arguments)
    assert report["status"] == "declarations_complete"
    assert report["parquet_format_verified"] is False
    assert report["payload_digest_verified"] is False
    assert not any(report["authority"].values())
    verify_parquet_references(*arguments, report)
    report["authority"]["publication"] = True
    with pytest.raises(MetadataError):
        verify_parquet_references(*arguments, report)


def changed(arguments: list, document: dict) -> list:
    arguments[0] = encode(document)
    arguments[1] = sha(arguments[0])
    return arguments


@pytest.mark.parametrize("field", ["blake3", "byte_count", "locations", "revision"])
def test_missing_declaration(arguments: list, field: str) -> None:
    doc = json.loads(arguments[0])
    obj = doc["objects"][0]
    if field == "revision":
        obj["locations"][0]["revision"] = None
    else:
        obj[field] = [] if field == "locations" else None
    result = assess_parquet_references(*changed(arguments, doc))
    assert result["status"] == "declarations_incomplete"
    assert result["issues"]


@pytest.mark.parametrize(
    "change",
    [
        "format",
        "identity",
        "hash",
        "bool-size",
        "negative-size",
        "big-size",
        "bad-blake3",
        "duplicate",
        "unsafe-url",
        "revision-kind",
        "revision-hash",
        "extra",
    ],
)
def test_negative(arguments: list, change: str) -> None:
    doc = json.loads(arguments[0])
    obj = doc["objects"][0]
    if change == "format":
        obj["content_format"] = "json"
    elif change == "identity":
        obj["canonical_id"] = "urn:gfjd:edition:other"
    elif change == "hash":
        obj["content_sha256"] = "c" * 64
    elif change == "bool-size":
        obj["byte_count"] = True
    elif change == "negative-size":
        obj["byte_count"] = -1
    elif change == "big-size":
        obj["byte_count"] = 2**63
    elif change == "bad-blake3":
        obj["blake3"] = "bad"
    elif change == "duplicate":
        doc["objects"] *= 2
    elif change == "unsafe-url":
        obj["locations"][0]["url"] = "file:///secret"
    elif change == "revision-kind":
        obj["locations"][0]["revision"]["kind"] = "branch"
    elif change == "revision-hash":
        obj["locations"][0]["revision"]["value"] = "c" * 64
    else:
        obj["verified"] = True
    with pytest.raises(MetadataError):
        assess_parquet_references(*changed(arguments, doc))


def test_known_metadata_contradiction(arguments: list) -> None:
    scope = json.loads(arguments[2])
    digest = scope["objects"][0]["metadata_sha256"]
    scope["objects"][0]["content_sha256"] = digest
    arguments[2] = encode(scope)
    arguments[3] = sha(arguments[2])
    doc = json.loads(arguments[0])
    doc["scope_sha256"] = arguments[3]
    doc["objects"][0]["content_sha256"] = digest
    doc["objects"][0]["locations"][0]["revision"]["value"] = digest
    with pytest.raises(MetadataError):
        assess_parquet_references(*changed(arguments, doc))


def test_missing_content_hash_remains_null(arguments: list) -> None:
    scope = json.loads(arguments[2])
    scope["objects"][0]["content_sha256"] = None
    arguments[2] = encode(scope)
    arguments[3] = sha(arguments[2])
    doc = json.loads(arguments[0])
    doc["scope_sha256"] = arguments[3]
    obj = doc["objects"][0]
    obj["content_sha256"] = None
    obj["locations"][0]["revision"] = None
    result = assess_parquet_references(*changed(arguments, doc))
    assert result["status"] == "declarations_incomplete"
    assert result["objects"][0]["content_sha256"] is None


@pytest.mark.parametrize(
    "revision",
    [
        {"kind": "git_commit", "value": "c" * 40},
        {"kind": "persistent_id", "value": "https://example.invalid/persistent-object"},
        {"kind": "content_sha256", "value": "a" * 64},
    ],
)
def test_revision_forms(arguments: list, revision: dict) -> None:
    doc = json.loads(arguments[0])
    doc["objects"][0]["locations"][0]["revision"] = revision
    result = assess_parquet_references(*changed(arguments, doc))
    assert result["status"] == "declarations_complete"
    assert result["immutable_location_verified"] is False


def test_unattached_scope_objects_pending(arguments: list) -> None:
    doc = json.loads(arguments[0])
    doc["objects"] = []
    result = assess_parquet_references(*changed(arguments, doc))
    assert result["pending_object_ids"] == ["fictional-edition"]
    assert result["status"] == "declarations_incomplete"


@pytest.mark.parametrize(
    "change", ["objects", "locations", "duplicate-url", "extra-bank", "scope-hash"]
)
def test_limits_and_exact_membership(arguments: list, change: str) -> None:
    doc = json.loads(arguments[0])
    obj = doc["objects"][0]
    if change == "objects":
        doc["objects"] *= 101
    elif change == "locations":
        obj["locations"] *= 21
    elif change == "duplicate-url":
        obj["locations"] *= 2
    elif change == "extra-bank":
        arguments[4][sha(b"{}")] = b"{}"
    else:
        arguments[3] = "0" * 64
    with pytest.raises(MetadataError):
        assess_parquet_references(*changed(arguments, doc))


def test_no_network_and_unknown_hash_not_format_proof(
    arguments: list, monkeypatch: pytest.MonkeyPatch
) -> None:
    import socket
    import urllib.request

    def forbidden(*args: object, **kwargs: object) -> None:
        raise AssertionError("network attempted")

    monkeypatch.setattr(socket, "socket", forbidden)
    monkeypatch.setattr(urllib.request, "urlopen", forbidden)
    # The digest of an unsupplied JSON value cannot be recognized by this API.
    digest = sha(b'[{"value":"fictional"}]')
    scope = json.loads(arguments[2])
    scope["objects"][0]["content_sha256"] = digest
    arguments[2] = encode(scope)
    arguments[3] = sha(arguments[2])
    doc = json.loads(arguments[0])
    doc["scope_sha256"] = arguments[3]
    doc["objects"][0]["content_sha256"] = digest
    doc["objects"][0]["locations"][0]["revision"]["value"] = digest
    result = assess_parquet_references(*changed(arguments, doc))
    assert result["parquet_format_verified"] is result["payload_digest_verified"] is False


def test_forgery_and_fixed_errors(
    arguments: list, caplog: pytest.LogCaptureFixture, capsys: pytest.CaptureFixture[str]
) -> None:
    report = assess_parquet_references(*arguments)
    report["parquet_format_verified"] = 0
    with pytest.raises(MetadataError) as error:
        verify_parquet_references(*arguments, report)
    assert str(error.value) == "Parquet reference contract violation"
    assert error.value.__suppress_context__
    assert not caplog.records and capsys.readouterr() == ("", "")
