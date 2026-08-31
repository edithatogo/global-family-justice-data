"""Fictional supplied-event lifecycle tests; no producer is contacted."""

import copy
import hashlib
import json
import socket
import traceback
import urllib.request
from datetime import UTC, datetime, timedelta
from importlib.resources import files

import pytest

from gfjd.federation_metadata import MetadataError
from gfjd.federation_openlineage import SCHEMA_URL
from gfjd.federation_run_sequence import assess_run_sequence, verify_run_sequence


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


@pytest.fixture
def schema():
    return files("gfjd").joinpath("federation_specs/openlineage-2-0-2.json").read_bytes()


@pytest.fixture
def sequence():
    events = []
    for index, kind in enumerate(["START", "RUNNING", "COMPLETE", "OTHER"]):
        events.append(
            {
                "eventTime": f"2026-09-01T00:00:0{index}Z",
                "eventType": kind,
                "producer": "https://example.invalid/fictional-producer",
                "schemaURL": SCHEMA_URL,
                "run": {"runId": "01234567-89ab-cdef-0123-456789abcdef"},
                "job": {"namespace": "fictional", "name": "job"},
                "inputs": [{"namespace": "fictional", "name": "source"}],
            }
        )
    events[-1]["outputs"] = [{"namespace": "fictional", "name": "late"}]
    return {"contract_version": "gfjd-openlineage-run-sequence-v1", "events": events}


def assess(sequence, schema):
    raw = encoded(sequence)
    return assess_run_sequence(raw, sha(raw), schema)


def test_missing_terminal_red(sequence, schema):
    sequence["events"][2]["eventType"] = "OTHER"
    with pytest.raises(MetadataError):
        assess(sequence, schema)


@pytest.mark.parametrize("terminal", ["COMPLETE", "FAIL", "ABORT"])
def test_declared_lifecycle(sequence, schema, terminal):
    sequence["events"][2]["eventType"] = terminal
    report = assess(sequence, schema)
    assert report["declared_terminal_type"] == terminal
    assert report["terminal_index"] == 2
    assert report["sequence_profile_validated"] is True
    assert report["datasets"] == [
        {
            "direction": "input",
            "namespace": "fictional",
            "name": "source",
            "event_indices": [0, 1, 2, 3],
            "event_types": ["START", "RUNNING", terminal, "OTHER"],
            "post_terminal_only": False,
        },
        {
            "direction": "output",
            "namespace": "fictional",
            "name": "late",
            "event_indices": [3],
            "event_types": ["OTHER"],
            "post_terminal_only": True,
        },
    ]
    assert not any(report["authority"].values())
    assert report["execution_observed"] is False
    assert report["production_verified"] is False
    assert report["full_conformance"] == "unverified"
    raw = encoded(sequence)
    verify_run_sequence(raw, sha(raw), schema, report)


def test_equal_instants_empty_facets_both_directions(sequence, schema):
    for event in sequence["events"]:
        event["eventTime"] = "2026-09-01T01:00:00.000000+01:00"
        event["schemaURL"] += "#/$defs/RunEvent"
        event["job"]["facets"] = {}
        event["run"]["facets"] = {}
        event["outputs"] = [{"namespace": "fictional", "name": "source", "outputFacets": {}}]
        event["inputs"][0].update({"facets": {}, "inputFacets": {}})
    sequence["events"][0]["eventTime"] = "2026-09-01T00:00:00Z"
    assert len(assess(sequence, schema)["datasets"]) == 2


@pytest.mark.parametrize(
    "index,kind",
    [
        (0, "OTHER"),
        (1, "START"),
        (2, "RUNNING"),
        (3, "RUNNING"),
        (3, "ABORT"),
        (1, "invalid"),
        (1, True),
    ],
)
def test_invalid_transitions(sequence, schema, index, kind):
    sequence["events"][index]["eventType"] = kind
    with pytest.raises(MetadataError):
        assess(sequence, schema)


@pytest.mark.parametrize(
    "value",
    [
        "2026-09-01",
        "2026-09-01T00:00:01",
        "2026-09-01T00:00:01-00:00",
        "2026-02-30T00:00:00Z",
        "2026-09-01T00:00:60Z",
        "2026-09-01T00:00:01.1234567Z",
        "2026-09-01T00:00:01+24:00",
        "2026-09-01T00:00:01+00:60",
        "0001-01-01T00:00:00+01:00",
        "9999-12-31T23:59:59-01:00",
        "2026-09-01T00:00:01+01:00",
        123,
        None,
    ],
)
def test_invalid_or_reversed_time(sequence, schema, value):
    sequence["events"][1]["eventTime"] = value
    with pytest.raises(MetadataError):
        assess(sequence, schema)


@pytest.mark.parametrize("field", ["eventTime", "eventType", "producer", "schemaURL", "run", "job"])
def test_missing_event_field(sequence, schema, field):
    del sequence["events"][0][field]
    with pytest.raises(MetadataError):
        assess(sequence, schema)


@pytest.mark.parametrize(
    "path,value",
    [
        (("unexpected",), 1),
        (("run", "unknown"), 1),
        (("run", "facets"), {"x": {}}),
        (("job", "facets"), []),
        (("job", "unknown"), "x"),
        (("job", "name"), " "),
        (("job", "namespace"), "other"),
        (("run", "runId"), "01234567-89AB-cdef-0123-456789abcdef"),
        (("run", "runId"), "11234567-89ab-cdef-0123-456789abcdef"),
        (("producer",), "https://another.invalid"),
        (("producer",), "file:///secret"),
        (("schemaURL",), "https://example.invalid/schema"),
    ],
)
def test_identity_and_nested_keys(sequence, schema, path, value):
    target = sequence["events"][1]
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    with pytest.raises(MetadataError):
        assess(sequence, schema)


@pytest.mark.parametrize(
    "key,value",
    [
        ("outputFacets", {}),
        ("inputFacets", {"x": {}}),
        ("facets", None),
        ("name", ""),
        ("extra", "x"),
    ],
)
def test_dataset_shape(sequence, schema, key, value):
    sequence["events"][0]["inputs"][0][key] = value
    with pytest.raises(MetadataError):
        assess(sequence, schema)


def test_duplicate_events(sequence, schema):
    sequence["events"].insert(2, copy.deepcopy(sequence["events"][1]))
    with pytest.raises(MetadataError):
        assess(sequence, schema)


def test_duplicate_datasets(sequence, schema):
    sequence["events"][0]["inputs"] *= 2
    with pytest.raises(MetadataError):
        assess(sequence, schema)


@pytest.mark.parametrize("count", [0, 1, 257])
def test_event_count(sequence, schema, count):
    sequence["events"] = [sequence["events"][0]] * count
    with pytest.raises(MetadataError):
        assess(sequence, schema)


def test_dataset_count_bound(sequence, schema):
    sequence["events"][0]["inputs"] = [{"namespace": "n", "name": str(i)} for i in range(101)]
    with pytest.raises(MetadataError):
        assess(sequence, schema)


@pytest.mark.parametrize(
    "raw",
    [
        b"{}",
        b'{"events":[],"events":[]}',
        b'{"x":NaN}',
        b"[" * 18 + b"0" + b"]" * 18,
        b"x" * (1024 * 1024 + 1),
        b"\xff",
        None,
    ],
)
def test_raw_bounds_and_json(schema, raw):
    with pytest.raises(MetadataError):
        assess_run_sequence(raw, sha(raw) if isinstance(raw, bytes) else "a" * 64, schema)


def test_schema_and_digest_bindings(sequence, schema):
    raw = encoded(sequence)
    for digest, normative in [
        ("0" * 64, schema),
        (sha(raw).upper(), schema),
        (sha(raw), schema + b" "),
        (sha(raw), b"{}"),
    ]:
        with pytest.raises(MetadataError):
            assess_run_sequence(raw, digest, normative)


@pytest.mark.parametrize(
    "field,value",
    [
        ("execution_observed", True),
        ("terminal_index", True),
        ("implementation_sha256", "a" * 64),
        ("event_count", 4.0),
    ],
)
def test_forged_report(sequence, schema, field, value):
    report = assess(sequence, schema)
    report[field] = value
    raw = encoded(sequence)
    with pytest.raises(MetadataError):
        verify_run_sequence(raw, sha(raw), schema, report)


def test_no_network_and_fixed_diagnostics(sequence, schema, monkeypatch, capsys):
    def denied(*args, **kwargs):
        raise AssertionError("network attempted")

    monkeypatch.setattr(socket, "create_connection", denied)
    monkeypatch.setattr(urllib.request, "urlopen", denied)
    assert assess(sequence, schema) == assess(sequence, schema)
    sequence["events"][0]["producer"] = "PRIVATE_SENTINEL"
    try:
        assess(sequence, schema)
    except MetadataError:
        rendered = traceback.format_exc()
        assert "PRIVATE_SENTINEL" not in rendered
    else:
        pytest.fail("invalid producer accepted")
    assert capsys.readouterr() == ("", "")


def test_max_events_within_shared_node_budget(sequence, schema):
    template = sequence["events"][0]
    template.pop("inputs")
    events = []
    for i in range(256):
        event = copy.deepcopy(template)
        event["eventType"] = "START" if i == 0 else "COMPLETE" if i == 255 else "RUNNING"
        event["eventTime"] = (datetime(2026, 9, 1, tzinfo=UTC) + timedelta(seconds=i)).isoformat()
        events.append(event)
    sequence["events"] = events
    assert assess(sequence, schema)["event_count"] == 256


@pytest.mark.parametrize("value", ["x" * 4097, "private\x00value", "private\ud800value"])
def test_string_limits(sequence, schema, value):
    sequence["events"][0]["job"]["name"] = value
    with pytest.raises(MetadataError):
        assess(sequence, schema)


def test_every_event_uses_normative_validator(sequence, schema, monkeypatch):
    from gfjd import federation_run_sequence as module

    real = module.Draft202012Validator.validate
    visited = []

    def checked(self, instance, *args, **kwargs):
        visited.append(instance["eventType"])
        return real(self, instance, *args, **kwargs)

    monkeypatch.setattr(module.Draft202012Validator, "validate", checked)
    assess(sequence, schema)
    assert visited == ["START", "RUNNING", "COMPLETE", "OTHER"]


def test_unknown_resource_registry_denies_lookup():
    from referencing.exceptions import NoSuchResource

    from gfjd.federation_run_sequence import _deny

    with pytest.raises(NoSuchResource):
        _deny("https://example.invalid/unavailable-schema")
