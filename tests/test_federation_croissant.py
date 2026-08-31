"""Fictional declarations only; checksums and publication are not factual evidence."""

import copy
import json
import traceback
from pathlib import Path

import pytest

from gfjd.federation_croissant import assess_croissant, verify_croissant
from gfjd.federation_metadata import MetadataError


@pytest.fixture
def profile() -> bytes:
    return (
        Path(__file__).parents[1] / "src/gfjd/federation_specs/gfjd-croissant-profile-v1.json"
    ).read_bytes()


@pytest.fixture
def metadata(profile: bytes) -> dict:
    return {
        "@context": json.loads(profile)["context"],
        "@type": "sc:Dataset",
        "conformsTo": "http://mlcommons.org/croissant/1.1",
        "name": "Fictional test",
        "description": "Synthetic declarations only",
        "creator": {"@type": "sc:Organization", "name": "Fictional organization"},
        "license": "https://example.invalid/fictional-license",
        "datePublished": "2026-08-31",
        "url": "https://example.invalid/fictional-dataset",
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
        "recordSet": [
            {
                "@type": "cr:RecordSet",
                "@id": "fictional",
                "field": [
                    {
                        "@type": "cr:Field",
                        "@id": "fictional/value",
                        "name": "value",
                        "dataType": "sc:Text",
                        "source": {
                            "fileObject": {"@id": "fictional.csv"},
                            "extract": {"column": "fictional_column"},
                        },
                    }
                ],
            }
        ],
    }


def raw(value: dict) -> bytes:
    return json.dumps(value).encode()


def test_binding_red(metadata: dict, profile: bytes) -> None:
    with pytest.raises(MetadataError):
        assess_croissant(raw(metadata), profile + b"\n")


def test_complete(metadata: dict, profile: bytes) -> None:
    report = assess_croissant(raw(metadata), profile)
    assert report["status"] == "profile_complete"
    assert report["full_conformance"] == report["factual_evidence"] == "unverified"
    assert not any(report["authority"].values())
    verify_croissant(raw(metadata), profile, report)
    assert report == assess_croissant(raw(metadata), profile)


@pytest.mark.parametrize(
    "field", ["name", "description", "creator", "license", "datePublished", "distribution"]
)
def test_missing_factual(metadata: dict, profile: bytes, field: str) -> None:
    del metadata[field]
    if field == "distribution":
        metadata.pop("recordSet")
    report = assess_croissant(raw(metadata), profile)
    assert report["status"] == "profile_incomplete"
    assert report["issues"]


@pytest.mark.parametrize(
    "change",
    [
        "context",
        "scoped",
        "fileset",
        "transform",
        "join",
        "payload",
        "dangling",
        "duplicate",
        "column",
        "date",
        "hash",
    ],
)
def test_unsupported(metadata: dict, profile: bytes, change: str) -> None:
    field = metadata["recordSet"][0]["field"][0]
    if change == "context":
        metadata["@context"] = "https://example.invalid/context"
    elif change == "scoped":
        field["@context"] = {}
    elif change == "fileset":
        metadata["distribution"][0]["@type"] = "cr:FileSet"
    elif change == "transform":
        field["source"]["transform"] = {"regex": ".*"}
    elif change == "join":
        field["references"] = {"@id": "other"}
    elif change == "payload":
        metadata["recordSet"][0]["data"] = [{"value": "fictional"}]
    elif change == "dangling":
        field["source"]["fileObject"]["@id"] = "other.csv"
    elif change == "duplicate":
        metadata["distribution"].append(copy.deepcopy(metadata["distribution"][0]))
    elif change == "column":
        field["source"]["extract"]["column"] = "*"
    elif change == "date":
        metadata["datePublished"] = "2026-02-30"
    elif change == "hash":
        metadata["distribution"][0]["sha256"] = "not-a-hash"
    with pytest.raises(MetadataError):
        assess_croissant(raw(metadata), profile)


@pytest.mark.parametrize(
    "payload", [b'{"x":1,"x":2}', b'{"x":NaN}', b"\xff", b" " * (1024 * 1024 + 1)]
)
def test_bad_json(payload: bytes, profile: bytes) -> None:
    with pytest.raises(MetadataError):
        assess_croissant(payload, profile)


def test_forged_report(metadata: dict, profile: bytes) -> None:
    report = assess_croissant(raw(metadata), profile)
    report["authority"]["publication"] = True
    with pytest.raises(MetadataError):
        verify_croissant(raw(metadata), profile, report)


@pytest.mark.parametrize("field", ["contentUrl", "encodingFormat", "sha256"])
def test_missing_file_declaration(metadata: dict, profile: bytes, field: str) -> None:
    del metadata["distribution"][0][field]
    report = assess_croissant(raw(metadata), profile)
    assert report["status"] == "profile_incomplete"
    assert "file_missing_" + field in report["issues"]


def test_recordsets_optional(metadata: dict, profile: bytes) -> None:
    del metadata["recordSet"]
    assert assess_croissant(raw(metadata), profile)["status"] == "profile_complete"


@pytest.mark.parametrize("target", ["dataset_url", "file_name", "field_name"])
def test_required_names_and_url(metadata: dict, profile: bytes, target: str) -> None:
    if target == "dataset_url":
        del metadata["url"]
    elif target == "file_name":
        del metadata["distribution"][0]["name"]
    else:
        del metadata["recordSet"][0]["field"][0]["name"]
    assert assess_croissant(raw(metadata), profile)["status"] == "profile_incomplete"


@pytest.mark.parametrize("field", ["dataType", "source"])
def test_missing_field_declaration(metadata: dict, profile: bytes, field: str) -> None:
    del metadata["recordSet"][0]["field"][0][field]
    assert assess_croissant(raw(metadata), profile)["status"] == "profile_incomplete"


def test_duplicate_across_entity_types(metadata: dict, profile: bytes) -> None:
    metadata["recordSet"][0]["@id"] = "fictional.csv"
    with pytest.raises(MetadataError):
        assess_croissant(raw(metadata), profile)


@pytest.mark.parametrize("value", ["https://user:secret@example.invalid/file", "file:///tmp/file"])
def test_unsafe_locator(metadata: dict, profile: bytes, value: str) -> None:
    metadata["distribution"][0]["contentUrl"] = value
    with pytest.raises(MetadataError):
        assess_croissant(raw(metadata), profile)


def test_report_types_exact(metadata: dict, profile: bytes) -> None:
    report = assess_croissant(raw(metadata), profile)
    report["authority"]["network"] = 0
    with pytest.raises(MetadataError):
        verify_croissant(raw(metadata), profile, report)


def test_no_io_and_silent(
    metadata: dict,
    profile: bytes,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
    caplog: pytest.LogCaptureFixture,
) -> None:
    import builtins
    import socket
    import urllib.request

    def forbidden(*args: object, **kwargs: object) -> None:
        raise AssertionError("unexpected I/O")

    monkeypatch.setattr(builtins, "open", forbidden)
    monkeypatch.setattr(Path, "open", forbidden)
    monkeypatch.setattr(socket, "socket", forbidden)
    monkeypatch.setattr(urllib.request, "urlopen", forbidden)
    assess_croissant(raw(metadata), profile)
    marker = "FICTIONAL_" + "PRIVATE_SENTINEL"
    metadata["creator"] = {"unexpected": marker}
    with pytest.raises(MetadataError) as error:
        assess_croissant(raw(metadata), profile)
    assert marker not in "".join(traceback.format_exception(error.value))
    assert capsys.readouterr() == ("", "") and not caplog.records
