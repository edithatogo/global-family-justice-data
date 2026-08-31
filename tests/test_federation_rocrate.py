"""Fictional declaration profiles, not publication or payload evidence."""

import json
from pathlib import Path

import pytest

from gfjd.federation_metadata import MetadataError
from gfjd.federation_rocrate import assess_rocrate, verify_rocrate


@pytest.fixture
def context() -> bytes:
    return (
        Path(__file__).parents[1] / "src/gfjd/federation_specs/ro-crate-1.3-context.jsonld"
    ).read_bytes()


@pytest.fixture
def metadata() -> dict:
    return {
        "@context": "https://w3id.org/ro/crate/1.3/context",
        "@graph": [
            {
                "@id": "ro-crate-metadata.json",
                "@type": "CreativeWork",
                "about": {"@id": "./"},
                "conformsTo": {"@id": "https://w3id.org/ro/crate/1.3"},
            },
            {
                "@id": "./",
                "@type": "Dataset",
                "name": "Fictional crate",
                "description": "Fictional declarations only",
                "datePublished": "2026-08-31",
                "license": {"@id": "#license"},
                "creator": {"@id": "#creator"},
                "hasPart": [{"@id": "data/example.csv"}],
            },
            {"@id": "data/example.csv", "@type": "File", "name": "Fictional file"},
            {"@id": "#creator", "@type": "Organization", "name": "Fictional creator"},
            {
                "@id": "#license",
                "@type": "CreativeWork",
                "name": "Fictional licence",
                "description": "Not a grant over real GFJD data",
            },
        ],
    }


def raw(metadata: dict) -> bytes:
    return json.dumps(metadata).encode()


def test_context_binding(metadata: dict) -> None:
    with pytest.raises(MetadataError):
        assess_rocrate(raw(metadata), b"{}")


def test_complete(context: bytes, metadata: dict) -> None:
    report = assess_rocrate(raw(metadata), context)
    assert report["status"] == "profile_complete"
    assert report["factual_evidence"] == report["full_conformance"] == "unverified"
    assert not any(report["authority"].values())
    verify_rocrate(raw(metadata), context, report)
    report["authority"]["publication"] = True
    with pytest.raises(MetadataError):
        verify_rocrate(raw(metadata), context, report)


@pytest.mark.parametrize("field", ["name", "description", "license", "datePublished"])
def test_missing_fact(context: bytes, metadata: dict, field: str) -> None:
    del metadata["@graph"][1][field]
    assert assess_rocrate(raw(metadata), context)["status"] == "profile_incomplete"


@pytest.mark.parametrize("value", ["2026-02-30", "2026-08-31T00:00:00Z", True, "unknown"])
def test_invalid_date(context: bytes, metadata: dict, value: object) -> None:
    metadata["@graph"][1]["datePublished"] = value
    with pytest.raises(MetadataError):
        assess_rocrate(raw(metadata), context)


@pytest.mark.parametrize(
    "value",
    [
        "../secret",
        "/absolute",
        "data/%2e%2e/x",
        "data\\x",
        "data//x",
        "data/./x",
        "https://example.invalid/payload",
        "data/x?query",
    ],
)
def test_bad_file_path(context: bytes, metadata: dict, value: str) -> None:
    metadata["@graph"][2]["@id"] = value
    with pytest.raises(MetadataError):
        assess_rocrate(raw(metadata), context)


def test_bad_structure(context: bytes, metadata: dict) -> None:
    for mutation in [
        lambda m: m.update({"@context": {"@import": "https://example.invalid"}}),
        lambda m: m["@graph"].append(m["@graph"][1]),
        lambda m: m["@graph"][1].update({"@context": {}}),
        lambda m: m["@graph"][1].update({"license": {"@id": "#missing"}}),
        lambda m: m["@graph"][0].update({"about": {"@id": "#wrong"}}),
        lambda m: m["@graph"][2].update({"@type": "Person"}),
    ]:
        cloned = json.loads(raw(metadata))
        mutation(cloned)
        with pytest.raises(MetadataError):
            assess_rocrate(raw(cloned), context)


def test_no_io(context: bytes, metadata: dict, monkeypatch: pytest.MonkeyPatch) -> None:
    import builtins
    import socket

    def forbidden(*args: object, **kwargs: object) -> None:
        raise AssertionError("I/O attempted")

    monkeypatch.setattr(builtins, "open", forbidden)
    monkeypatch.setattr(socket, "socket", forbidden)
    assert assess_rocrate(raw(metadata), context)["status"] == "profile_complete"


@pytest.mark.parametrize(
    "payload",
    [
        b'{"x":1,"x":2}',
        b'{"x":NaN}',
        b"\xff",
        b"[]",
        b'"\\ud800"',
        b'"\\u0000"',
        b"[" * 100 + b"0" + b"]" * 100,
        b" " * (1024 * 1024 + 1),
    ],
    ids=["duplicate", "nan", "utf8", "list", "surrogate", "control", "depth", "size"],
)
def test_bad_metadata(
    context: bytes,
    payload: bytes,
    caplog: pytest.LogCaptureFixture,
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(MetadataError) as exc:
        assess_rocrate(payload, context)
    assert str(exc.value) == "Metadata profile contract violation"
    assert exc.value.__suppress_context__
    assert not caplog.records
    assert capsys.readouterr() == ("", "")


@pytest.mark.parametrize(
    "context",
    [b"", b"{}", None, b" " * (256 * 1024 + 1)],
    ids=["empty", "arbitrary", "wrong-type", "oversize"],
)
def test_bad_context(metadata: dict, context: bytes) -> None:
    with pytest.raises(MetadataError):
        assess_rocrate(raw(metadata), context)


def test_context_drift(context: bytes, metadata: dict) -> None:
    with pytest.raises(MetadataError):
        assess_rocrate(raw(metadata), context + b"\n")


def test_reference_type_and_substitution(context: bytes, metadata: dict) -> None:
    metadata["@graph"][1]["license"] = {"@id": "#creator"}
    with pytest.raises(MetadataError):
        assess_rocrate(raw(metadata), context)


def test_external_reference_is_not_accessed(context: bytes, metadata: dict) -> None:
    metadata["@graph"][1]["license"] = {"@id": "https://example.invalid/fictional-license"}
    assert assess_rocrate(raw(metadata), context)["factual_evidence"] == "unverified"


def test_forged_hash_and_bool_equivalence(context: bytes, metadata: dict) -> None:
    report = assess_rocrate(raw(metadata), context)
    report["authority"]["publication"] = 0
    with pytest.raises(MetadataError):
        verify_rocrate(raw(metadata), context, report)
    report = assess_rocrate(raw(metadata), context)
    metadata["@graph"][1]["name"] = "Other fictional crate"
    with pytest.raises(MetadataError):
        verify_rocrate(raw(metadata), context, report)


def test_orphan_file_and_metadata_only_crate(context: bytes, metadata: dict) -> None:
    del metadata["@graph"][1]["hasPart"]
    with pytest.raises(MetadataError):
        assess_rocrate(raw(metadata), context)
    metadata["@graph"].pop(2)
    assert assess_rocrate(raw(metadata), context)["status"] == "profile_complete"


@pytest.mark.parametrize("field", ["license", "datePublished"])
def test_blank_is_malformed_not_missing(context: bytes, metadata: dict, field: str) -> None:
    metadata["@graph"][1][field] = ""
    with pytest.raises(MetadataError):
        assess_rocrate(raw(metadata), context)
