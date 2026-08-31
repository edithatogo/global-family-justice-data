"""Fictional reference-only scope; estate inputs are configuration metadata."""

import hashlib
import json
from pathlib import Path

import pytest

from gfjd.federation_metadata import MetadataError
from gfjd.federation_references import reconcile_references, verify_references
from gfjd.medallion_estate import POLICY_REFERENCE, SOURCEFILES, prepare_estate


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def encode(value: dict) -> bytes:
    return json.dumps(value).encode()


@pytest.fixture
def inputs() -> tuple[dict, dict[str, bytes], dict[str, bytes]]:
    root = Path(__file__).parents[1]
    estate = {p: (root / p).read_bytes() for p in (*SOURCEFILES, POLICY_REFERENCE)}
    metadata = b'{"description":"Fictional metadata only"}'
    scope = {
        "contract_version": "gfjd-federation-reference-scope-v1",
        "state": "preparation",
        "estate_manifest_sha256": sha(prepare_estate(estate)["estate-manifest.json"]),
        "partners": ["archive-govt-nz"],
        "objects": [
            {
                "object_id": "fictional-edition",
                "canonical_id": "urn:gfjd:edition:fictional",
                "kind": "edition",
                "role": "source-archive",
                "content_sha256": None,
                "metadata_sha256": sha(metadata),
                "media_type": "application/json",
                "references": ["https://example.invalid/metadata"],
            }
        ],
    }
    return scope, {sha(metadata): metadata}, estate


def test_wrong_scope_digest(inputs: tuple) -> None:
    scope, bank, estate = inputs
    with pytest.raises(MetadataError):
        reconcile_references(encode(scope), "0" * 64, bank, estate)


def test_positive_and_verify(inputs: tuple) -> None:
    scope, bank, estate = inputs
    raw = encode(scope)
    result = reconcile_references(raw, sha(raw), bank, estate)
    assert result["pending_content_count"] == 1
    assert result["factual_evidence"] == "unverified"
    assert not any(result["authority"].values())
    verify_references(raw, sha(raw), bank, estate, result)
    result["authority"]["publication"] = True
    with pytest.raises(MetadataError):
        verify_references(raw, sha(raw), bank, estate, result)


@pytest.mark.parametrize(
    "change",
    [
        "estate",
        "extra-bank",
        "missing-bank",
        "bank-digest",
        "canonical",
        "role",
        "partner",
        "duplicate",
        "unsafe-ref",
        "content",
        "extra-field",
    ],
)
def test_negative(inputs: tuple, change: str) -> None:
    scope, bank, estate = inputs
    obj = scope["objects"][0]
    if change == "estate":
        scope["estate_manifest_sha256"] = "0" * 64
    elif change == "extra-bank":
        bank[sha(b"{}")] = b"{}"
    elif change == "missing-bank":
        bank.clear()
    elif change == "bank-digest":
        bank[obj["metadata_sha256"]] = b"{}"
    elif change == "canonical":
        obj["canonical_id"] = "urn:gfjd:source:fictional"
    elif change == "role":
        obj["role"] = "other"
    elif change == "partner":
        scope["partners"] = ["unapproved"]
    elif change == "duplicate":
        scope["objects"] *= 2
    elif change == "unsafe-ref":
        obj["references"] = ["file:///secret"]
    elif change == "content":
        obj["content_sha256"] = "invented"
    else:
        obj["authority"] = True
    raw = encode(scope)
    with pytest.raises(MetadataError):
        reconcile_references(raw, sha(raw), bank, estate)


@pytest.mark.parametrize(
    "media,payload",
    [
        ("application/json", b"[]"),
        ("application/json", b'{"x":1,"x":2}'),
        ("text/csv", b"a,b"),
        ("application/n-triples", b'<file:///secret> <urn:x:p> "x" .'),
    ],
)
def test_invalid_metadata(inputs: tuple, media: str, payload: bytes) -> None:
    scope, _, estate = inputs
    scope["objects"][0].update(metadata_sha256=sha(payload), media_type=media)
    raw = encode(scope)
    with pytest.raises(MetadataError):
        reconcile_references(raw, sha(raw), {sha(payload): payload}, estate)


def test_repeated_bytes_are_not_logical_equivalence(inputs: tuple) -> None:
    scope, bank, estate = inputs
    other = dict(scope["objects"][0], object_id="other", canonical_id="urn:gfjd:edition:other")
    scope["objects"].append(other)
    raw = encode(scope)
    result = reconcile_references(raw, sha(raw), bank, estate)
    assert result["object_count"] == 2 and len(result["metadata_sha256"]) == 1
    assert result["semantic_equivalence"] == "unverified"
    other["canonical_id"] = scope["objects"][0]["canonical_id"]
    raw = encode(scope)
    with pytest.raises(MetadataError):
        reconcile_references(raw, sha(raw), bank, estate)


@pytest.mark.parametrize(
    "media,payload",
    [
        ("application/n-triples", b'<urn:x:s> <urn:x:p> "Fictional" .'),
        ("application/ld+json", b'{"@context":"https://example.invalid/not-requested"}'),
    ],
)
def test_metadata_formats_no_loading(
    inputs: tuple, media: str, payload: bytes, monkeypatch: pytest.MonkeyPatch
) -> None:
    import socket
    import urllib.request

    def forbidden(*args: object, **kwargs: object) -> None:
        raise AssertionError("network attempted")

    monkeypatch.setattr(socket, "socket", forbidden)
    monkeypatch.setattr(urllib.request, "urlopen", forbidden)
    scope, _, estate = inputs
    scope["objects"][0].update(
        metadata_sha256=sha(payload), media_type=media, content_sha256="a" * 64
    )
    raw = encode(scope)
    result = reconcile_references(raw, sha(raw), {sha(payload): payload}, estate)
    assert result["pending_content_count"] == 0
    assert result["content_custody"] == "unverified"
    assert payload.decode() not in json.dumps(result)


@pytest.mark.parametrize("change", ["objects", "references", "partners", "bank-size", "total"])
def test_bounds(inputs: tuple, change: str) -> None:
    scope, bank, estate = inputs
    if change == "objects":
        scope["objects"] *= 101
    elif change == "references":
        scope["objects"][0]["references"] *= 21
    elif change == "partners":
        scope["partners"] *= 5
    elif change == "bank-size":
        bank["a" * 64] = b" " * (1024 * 1024 + 1)
    else:
        for i in range(9):
            payload = b'{"i":' + str(i).encode() + b"}" + b" " * (1024 * 1024 - 7)
            bank[sha(payload)] = payload
    raw = encode(scope)
    with pytest.raises(MetadataError):
        reconcile_references(raw, sha(raw), bank, estate)


def test_estate_policy_missing(inputs: tuple) -> None:
    scope, bank, estate = inputs
    del estate[POLICY_REFERENCE]
    raw = encode(scope)
    with pytest.raises(MetadataError):
        reconcile_references(raw, sha(raw), bank, estate)


def test_silent_errors(
    inputs: tuple, caplog: pytest.LogCaptureFixture, capsys: pytest.CaptureFixture[str]
) -> None:
    scope, bank, estate = inputs
    scope["objects"][0]["references"] = ["file:///fictional-private-marker"]
    raw = encode(scope)
    with pytest.raises(MetadataError) as error:
        reconcile_references(raw, sha(raw), bank, estate)
    assert str(error.value) == "Metadata profile contract violation"
    assert error.value.__suppress_context__
    assert not caplog.records and capsys.readouterr() == ("", "")


def test_forged_report_hash_and_types(inputs: tuple) -> None:
    scope, bank, estate = inputs
    raw = encode(scope)
    result = reconcile_references(raw, sha(raw), bank, estate)
    result["objects"][0]["references"] = ["https://example.invalid/substituted"]
    with pytest.raises(MetadataError):
        verify_references(raw, sha(raw), bank, estate, result)
    result = reconcile_references(raw, sha(raw), bank, estate)
    result["authority"]["network"] = 0
    with pytest.raises(MetadataError):
        verify_references(raw, sha(raw), bank, estate, result)
