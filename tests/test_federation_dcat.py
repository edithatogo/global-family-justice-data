"""Conspicuously fictional metadata; no retrieval or factual clearance."""

import hashlib
import json
import traceback
from pathlib import Path

import pytest

from gfjd.federation_dcat import DCATError, validate_catalogue

RDF = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
DCAT = "http://www.w3.org/ns/dcat#"
DCT = "http://purl.org/dc/terms/"
FOAF = "http://xmlns.com/foaf/0.1/"


@pytest.fixture
def shapes() -> dict[str, bytes]:
    root = Path(__file__).parents[1] / "src/gfjd/federation_specs"
    return {
        name + ".ttl": (root / f"dcat-ap-3.0.1-{name}.ttl").read_bytes()
        for name in ("shapes", "range")
    }


@pytest.fixture
def data() -> bytes:
    return "\n".join(
        [
            f"<urn:fictional:catalogue> <{RDF}type> <{DCAT}Catalog> .",
            f"<urn:fictional:catalogue> <{DCAT}dataset> <urn:fictional:dataset> .",
            f'<urn:fictional:catalogue> <{DCT}title> "Fictional catalogue" .',
            f'<urn:fictional:catalogue> <{DCT}description> "Synthetic machinery test" .',
            f"<urn:fictional:catalogue> <{DCT}publisher> <urn:fictional:publisher> .",
            f"<urn:fictional:publisher> <{RDF}type> <{FOAF}Agent> .",
            f'<urn:fictional:publisher> <{FOAF}name> "Fictional publisher" .',
            f"<urn:fictional:dataset> <{RDF}type> <{DCAT}Dataset> .",
            f'<urn:fictional:dataset> <{DCT}title> "Fictional dataset" .',
            f'<urn:fictional:dataset> <{DCT}description> "No actual source facts" .',
        ]
    ).encode()


def test_shape_binding_rejects_tampering(data: bytes, shapes: dict[str, bytes]) -> None:
    shapes["range.ttl"] += b"\n"
    with pytest.raises(DCATError):
        validate_catalogue(data, shapes)


def test_fictional_positive(data: bytes, shapes: dict[str, bytes]) -> None:
    report = validate_catalogue(data, shapes)
    assert report["status"] == "shape_checks_passed"
    assert report["result_count"] == 0
    assert report["statement_count"] == 10
    assert report["data_sha256"] == hashlib.sha256(data).hexdigest()
    assert report["shape_sha256"] == {
        key: hashlib.sha256(raw).hexdigest() for key, raw in shapes.items()
    }
    assert report["full_conformance"] == report["factual_evidence"] == "unverified"
    assert report["controlled_vocabularies"] == "unverified"
    assert not any(report["authority"].values())
    assert report == validate_catalogue(data, dict(reversed(list(shapes.items()))))


@pytest.mark.parametrize("missing", ["shapes.ttl", "range.ttl"])
def test_missing_shape(data: bytes, shapes: dict[str, bytes], missing: str) -> None:
    del shapes[missing]
    with pytest.raises(DCATError):
        validate_catalogue(data, shapes)


def test_extra_shape(data: bytes, shapes: dict[str, bytes]) -> None:
    shapes["imports.ttl"] = b""
    with pytest.raises(DCATError):
        validate_catalogue(data, shapes)


@pytest.mark.parametrize("payload", [b"", b"not RDF", b"\xff", b" " * (1024 * 1024 + 1)])
def test_invalid_input(payload: bytes, shapes: dict[str, bytes]) -> None:
    with pytest.raises(DCATError):
        validate_catalogue(payload, shapes)


@pytest.mark.parametrize("change", ["catalogue", "dataset", "link", "second_catalogue"])
def test_target_guard(data: bytes, shapes: dict[str, bytes], change: str) -> None:
    if change == "second_catalogue":
        data += f"\n<urn:fictional:second> <{RDF}type> <{DCAT}Catalog> .".encode()
    else:
        marker = {
            "catalogue": f"<{DCAT}Catalog>",
            "dataset": f"<{DCAT}Dataset>",
            "link": f"<{DCAT}dataset>",
        }[change].encode()
        data = b"\n".join(line for line in data.splitlines() if marker not in line)
    with pytest.raises(DCATError):
        validate_catalogue(data, shapes)


def test_normative_cardinality(data: bytes, shapes: dict[str, bytes]) -> None:
    data = b"\n".join(line for line in data.splitlines() if b'"Fictional dataset"' not in line)
    report = validate_catalogue(data, shapes)
    assert report["status"] == "shape_checks_failed"
    assert report["constraint_counts"]["MinCountConstraintComponent"] >= 1
    assert report["severity_counts"]["Violation"] >= 1


def test_normative_range(data: bytes, shapes: dict[str, bytes]) -> None:
    data = b"\n".join(line for line in data.splitlines() if f"<{FOAF}Agent>".encode() not in line)
    report = validate_catalogue(data, shapes)
    assert report["status"] == "shape_checks_failed"
    assert report["constraint_counts"]["ClassConstraintComponent"] >= 1


def test_all_targets_are_validated(data: bytes, shapes: dict[str, bytes]) -> None:
    data += f"\n<urn:fictional:unlinked> <{RDF}type> <{DCAT}Dataset> .".encode()
    report = validate_catalogue(data, shapes)
    assert report["status"] == "shape_checks_failed"
    assert report["constraint_counts"]["MinCountConstraintComponent"] >= 2


def test_order_and_duplicate_statement_counts(data: bytes, shapes: dict[str, bytes]) -> None:
    original = validate_catalogue(data, shapes)
    changed = validate_catalogue(b"\n".join(reversed(data.splitlines())), shapes)
    assert original.pop("data_sha256") != changed.pop("data_sha256")
    assert original == changed
    duplicated = validate_catalogue(data + b"\n" + data.splitlines()[0], shapes)
    assert duplicated["statement_count"] == 11
    assert duplicated["triple_count"] == 10
    assert duplicated["status"] == "shape_checks_passed"


@pytest.mark.parametrize("value", [None, "not bytes", b"", b"x" * (1024 * 1024 + 1)])
def test_invalid_shape_value(data: bytes, shapes: dict, value: object) -> None:
    shapes["shapes.ttl"] = value
    with pytest.raises(DCATError):
        validate_catalogue(data, shapes)


def test_unknown_engine_stops(
    data: bytes, shapes: dict[str, bytes], monkeypatch: pytest.MonkeyPatch
) -> None:
    import pyshacl

    monkeypatch.setattr(pyshacl, "__version__", "fictional-unqualified-version")
    with pytest.raises(DCATError):
        validate_catalogue(data, shapes)


@pytest.mark.parametrize(
    "suffix",
    [
        "<urn:fictional:s> <http://www.w3.org/2002/07/owl#imports> "
        "<https://example.invalid/import> .",
        '<urn:fictional:s> <http://www.w3.org/ns/shacl#deactivated> "true" .',
    ],
)
def test_imports_and_embedded_shapes_stop(
    data: bytes, shapes: dict[str, bytes], suffix: str
) -> None:
    with pytest.raises(DCATError):
        validate_catalogue(data + b"\n" + suffix.encode(), shapes)


def test_no_io(data: bytes, shapes: dict[str, bytes], monkeypatch: pytest.MonkeyPatch) -> None:
    import builtins
    import socket
    import urllib.request

    def forbidden(*args: object, **kwargs: object) -> None:
        raise AssertionError("unexpected I/O")

    monkeypatch.setattr(builtins, "open", forbidden)
    monkeypatch.setattr(Path, "open", forbidden)
    monkeypatch.setattr(socket, "socket", forbidden)
    monkeypatch.setattr(urllib.request, "urlopen", forbidden)
    assert validate_catalogue(data, shapes)["status"] == "shape_checks_passed"


@pytest.mark.parametrize("invalid", [False, True])
def test_diagnostics_are_silent(
    data: bytes,
    shapes: dict[str, bytes],
    capsys: pytest.CaptureFixture,
    caplog: pytest.LogCaptureFixture,
    invalid: bool,
) -> None:
    marker = "FICTIONAL_" + "PRIVATE_MARKER"
    if invalid:
        data += (
            f'\n<urn:fictional:item> <urn:fictional:p> "{marker}"'
            "^^<http://www.w3.org/2001/XMLSchema#integer> ."
        ).encode()
        with pytest.raises(DCATError) as error:
            validate_catalogue(data, shapes)
        assert marker not in "".join(traceback.format_exception(error.value))
    else:
        data = data.replace(b"<urn:fictional:publisher> .", f'"{marker}" .'.encode())
        report = validate_catalogue(data, shapes)
        assert report["status"] == "shape_checks_failed"
        assert marker not in json.dumps(report)
    captured = capsys.readouterr()
    assert captured.out == captured.err == caplog.text == ""
