"""Fictional design events; no dataset retrieval or execution evidence."""

import json
import traceback
from pathlib import Path

import pytest

from gfjd.federation_openlineage import FederationError, validate_design_event

SCHEMA_URL = "https://openlineage.io/spec/2-0-2/OpenLineage.json"


@pytest.fixture
def schema() -> bytes:
    return (
        Path(__file__).parents[1] / "src/gfjd/federation_specs/openlineage-2-0-2.json"
    ).read_bytes()


@pytest.fixture
def event() -> dict:
    return {
        "eventTime": "2026-08-31T00:00:00Z",
        "producer": "https://example.invalid/fictional-metadata-compiler",
        "schemaURL": SCHEMA_URL,
        "job": {"namespace": "fictional", "name": "design"},
    }


def raw(event: dict) -> bytes:
    return json.dumps(event).encode()


def test_positive_design_events(schema: bytes, event: dict) -> None:
    result = validate_design_event(raw(event), schema)
    assert result["schema_validated"] is True
    assert result["profile"] == "design_event_only"
    assert result["factual_evidence"] == "unverified"
    assert not any(result["authority"].values())
    assert result == validate_design_event(raw(event), schema)
    event["dataset"] = event.pop("job")
    assert validate_design_event(raw(event), schema)["event_kind"] == "DatasetEvent"


@pytest.mark.parametrize("field", ["eventTime", "producer", "schemaURL", "job"])
def test_missing_required(schema: bytes, event: dict, field: str) -> None:
    del event[field]
    with pytest.raises(FederationError):
        validate_design_event(raw(event), schema)


@pytest.mark.parametrize("value", ["2026-02-30T00:00:00Z", "2026-08-31", "not-a-date"])
def test_bad_date(schema: bytes, event: dict, value: str) -> None:
    event["eventTime"] = value
    with pytest.raises(FederationError):
        validate_design_event(raw(event), schema)


@pytest.mark.parametrize(
    "extra",
    [
        {"run": {"runId": "c0db1629-20dc-4150-a03e-89ed193fbad0"}},
        {"eventType": "COMPLETE"},
        {"dataset": {"namespace": "fictional", "name": "other"}},
        {"facets": {"spoof": {}}},
    ],
)
def test_unsupported_profile(schema: bytes, event: dict, extra: dict) -> None:
    event.update(extra)
    with pytest.raises(FederationError):
        validate_design_event(raw(event), schema)


@pytest.mark.parametrize(
    "payload",
    [
        b"{}",
        b'{"x":1,"x":2}',
        b'{"x":NaN}',
        b'{"x":1e999}',
        b'{"x":"\\u0000"}',
        b'{"x":"\\ud800"}',
        b"[" * 100 + b"0" + b"]" * 100,
        b" " * (1024 * 1024 + 1),
    ],
    ids=["empty-object", "duplicate", "nan", "overflow", "control", "surrogate", "depth", "size"],
)
def test_bad_json(schema: bytes, payload: bytes) -> None:
    with pytest.raises(FederationError):
        validate_design_event(payload, schema)


@pytest.mark.parametrize(
    "bad", [b"", b"{}", b" " * (1024 * 1024 + 1)], ids=["empty", "arbitrary", "oversized"]
)
def test_schema_binding(event: dict, bad: bytes) -> None:
    with pytest.raises(FederationError):
        validate_design_event(raw(event), bad)


def test_schema_tamper(schema: bytes, event: dict) -> None:
    with pytest.raises(FederationError):
        validate_design_event(raw(event), schema + b"\n")


def test_no_network(schema: bytes, event: dict, monkeypatch: pytest.MonkeyPatch) -> None:
    import socket

    def forbidden(*args: object, **kwargs: object) -> None:
        raise AssertionError("network attempted")

    monkeypatch.setattr(socket, "socket", forbidden)
    validate_design_event(raw(event), schema)


def test_nested_facets_and_identifiers(schema: bytes, event: dict) -> None:
    event["job"]["facets"] = {}
    event["inputs"] = [{"namespace": "fictional", "name": "input", "facets": {}}]
    validate_design_event(raw(event), schema)
    event["inputs"][0]["inputFacets"] = {"unvalidated": {}}
    with pytest.raises(FederationError):
        validate_design_event(raw(event), schema)


@pytest.mark.parametrize(
    "producer",
    [
        "relative",
        "https://",
        "https://host/%xx",
        "https://user:password@host/a",
        "https://host:99999/a",
        "https://bad..host/a",
        "https://host/space here",
        "https://host/{bad}",
    ],
)
def test_invalid_producers(schema: bytes, event: dict, producer: str) -> None:
    event["producer"] = producer
    with pytest.raises(FederationError):
        validate_design_event(raw(event), schema)


@pytest.mark.parametrize(
    "payload",
    [
        {"job": {"namespace": "", "name": "x"}},
        {"job": {"namespace": "x", "name": 3}},
        {"outputs": [{"namespace": "x"}]},
        {"inputs": [{}] * 1001},
        {"extra": "x" * 4097},
        {"extra": [[0] * 1000] * 11},
        {"eventTime": "2026-08-31T00:00:00-00:00"},
        {"schemaURL": SCHEMA_URL + "#/$defs/JobEvent"},
    ],
)
def test_bounds_and_profile(schema: bytes, event: dict, payload: dict) -> None:
    event.update(payload)
    with pytest.raises(FederationError):
        validate_design_event(raw(event), schema)


def test_local_registry_denies_unknown_resource() -> None:
    from referencing.exceptions import NoSuchResource

    from gfjd.federation_openlineage import _deny_resource

    with pytest.raises(NoSuchResource):
        _deny_resource("https://example.invalid/unbound-schema")


@pytest.mark.parametrize("invalid_utf8", [False, True])
def test_rejected_input_is_not_rendered_in_traceback(
    schema: bytes, event: dict, invalid_utf8: bool
) -> None:
    marker = "FICTIONAL_" + "REJECTED_INPUT_MARKER"
    event["eventTime"] = "not-a-date"
    event["job"]["name"] = marker
    payload = raw(event) + (b"\xff" if invalid_utf8 else b"")
    with pytest.raises(FederationError) as caught:
        validate_design_event(payload, schema)
    rendered = "".join(traceback.format_exception(caught.value))
    assert marker not in rendered
    assert "jsonschema.exceptions.ValidationError" not in rendered
    assert "UnicodeDecodeError" not in rendered
