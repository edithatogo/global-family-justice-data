"""Fictional runtime metadata is an association, never execution or production proof."""

import copy
import json

import pytest

from gfjd.federation_metadata import MetadataError
from gfjd.federation_replayed_run import assess_replayed_run, verify_replayed_run
from tests.test_federation_replayed_bundle import encoded, sha
from tests.test_federation_replayed_bundle import inputs as inputs
from tests.test_federation_replayed_bundle import pipeline_inputs as pipeline_inputs


@pytest.fixture
def run_args(inputs):
    run_id = "11111111-1111-1111-1111-111111111111"
    dataset = {"namespace": "gfjd", "name": "urn:gfjd:source:fictional"}
    base = {
        "eventTime": "2026-09-01T00:00:00Z",
        "producer": "https://example.invalid/fictional-producer",
        "schemaURL": "https://openlineage.io/spec/2-0-2/OpenLineage.json",
        "run": {"runId": run_id},
        "job": {"namespace": "fictional", "name": "replay"},
        "inputs": [dataset],
    }
    events = [
        {**copy.deepcopy(base), "eventType": "START"},
        {**copy.deepcopy(base), "eventType": "COMPLETE", "eventTime": "2026-09-01T00:01:00Z"},
    ]
    sequence = encoded({"contract_version": "gfjd-openlineage-run-sequence-v1", "events": events})
    selected = json.loads(inputs[5])["selection"]
    binding = encoded(
        {
            "contract_version": "gfjd-openlineage-replay-association-v1",
            "run_id": run_id,
            "job_namespace": "fictional",
            "job_name": "replay",
            "producer": base["producer"],
            "terminal_type": "COMPLETE",
            "direction": "input",
            "dataset_namespace": dataset["namespace"],
            "dataset_name": dataset["name"],
            "object_id": selected["object_id"],
            "canonical_id": "urn:gfjd:source:fictional",
            "entity_sha256": selected["entity_sha256"],
        }
    )
    return [*inputs, sequence, sha(sequence), binding, sha(binding)]


def test_wrong_binding_digest_red(run_args):
    run_args[11] = "0" * 64
    with pytest.raises(MetadataError):
        assess_replayed_run(*run_args)


def replace_json(args, index, document):
    args[index] = encoded(document)
    args[index + 1] = sha(args[index])


def test_declared_link_is_not_execution(run_args):
    report = assess_replayed_run(*run_args)
    assert report["association_kind"] == "declared_metadata_only"
    assert report["execution_observed"] is report["production_verified"] is False
    assert report["dataset_association"]["event_indices"] == [0, 1]
    assert report["dataset_association"]["post_terminal_only"] is False
    assert report["unbound_datasets"] == report["unbound_object_ids"] == []
    assert not any(report["authority"].values())
    assert "PRIVATE_FICTIONAL_VALUE" not in json.dumps(report)
    verify_replayed_run(*run_args, report)


@pytest.mark.parametrize(
    "field",
    [
        "run_id",
        "job_namespace",
        "job_name",
        "producer",
        "terminal_type",
        "direction",
        "dataset_namespace",
        "dataset_name",
        "object_id",
        "canonical_id",
        "entity_sha256",
        "contract_version",
        "extra",
    ],
)
def test_binding_mismatch(run_args, field):
    binding = json.loads(run_args[10])
    binding[field] = "wrong"
    replace_json(run_args, 10, binding)
    with pytest.raises(MetadataError):
        assess_replayed_run(*run_args)


@pytest.mark.parametrize("terminal", ["COMPLETE", "FAIL", "ABORT"])
def test_post_terminal_output_does_not_prove_production(run_args, terminal):
    sequence = json.loads(run_args[8])
    dataset = sequence["events"][0].pop("inputs")[0]
    sequence["events"][1].pop("inputs")
    sequence["events"][1]["eventType"] = terminal
    post = copy.deepcopy(sequence["events"][1])
    post.update(eventType="OTHER", eventTime="2026-09-01T00:02:00Z", outputs=[dataset])
    sequence["events"].append(post)
    replace_json(run_args, 8, sequence)
    binding = json.loads(run_args[10])
    binding.update(terminal_type=terminal, direction="output")
    replace_json(run_args, 10, binding)
    report = assess_replayed_run(*run_args)
    assert report["declared_terminal_type"] == terminal
    assert report["dataset_association"]["post_terminal_only"] is True
    assert report["dataset_association"]["event_indices"] == [2]
    assert report["production_verified"] is False
    verify_replayed_run(*run_args, report)


def test_other_datasets_and_objects_unbound(run_args):
    sequence = json.loads(run_args[8])
    dataset = copy.deepcopy(sequence["events"][0]["inputs"][0])
    for event in sequence["events"]:
        event["outputs"] = [dataset]  # Same identity, different direction remains unbound.
    replace_json(run_args, 8, sequence)
    scope = json.loads(run_args[0])
    scope["objects"].append(
        {**scope["objects"][0], "object_id": "other", "canonical_id": "urn:gfjd:source:other"}
    )
    replace_json(run_args, 0, scope)
    report = assess_replayed_run(*run_args)
    assert report["unbound_object_ids"] == ["other"]
    assert [item["direction"] for item in report["unbound_datasets"]] == ["output"]


@pytest.mark.parametrize(
    "field",
    [
        "execution_observed",
        "production_verified",
        "binding_sha256",
        "dataset_association",
        "lifecycle_report",
        "implementation_sha256",
    ],
)
def test_forgery(run_args, field):
    report = assess_replayed_run(*run_args)
    report[field] = True
    with pytest.raises(MetadataError):
        verify_replayed_run(*run_args, report)


def test_bool_alias_and_fixed_error(run_args, caplog, capsys):
    report = assess_replayed_run(*run_args)
    report["execution_observed"] = 0
    with pytest.raises(MetadataError) as error:
        verify_replayed_run(*run_args, report)
    assert str(error.value) == "Run replay association contract violation"
    assert error.value.__suppress_context__
    assert not caplog.records and capsys.readouterr() == ("", "")


@pytest.mark.parametrize(
    "change",
    ["source", "extra_bank", "schema", "sequence_hash", "missing_binding", "binding_limit"],
)
def test_bad_inputs(run_args, change):
    if change == "source":
        digest = json.loads(run_args[5])["inputs"]["source_sha256"]
        run_args[7][digest] += b" "
    elif change == "extra_bank":
        run_args[7][sha(b"{}")] = b"{}"
    elif change == "schema":
        run_args[4]["openlineage-2-0-2.json"] += b" "
    elif change == "sequence_hash":
        run_args[9] = "0" * 64
    elif change == "missing_binding":
        run_args[10] = b""
        run_args[11] = sha(b"")
    else:
        run_args[10] = b" " * (1024 * 1024 + 1)
        run_args[11] = sha(run_args[10])
    with pytest.raises(MetadataError):
        assess_replayed_run(*run_args)


def test_pipeline_association(run_args, pipeline_inputs):
    run_args[:8] = pipeline_inputs
    binding = json.loads(run_args[10])
    binding["entity_sha256"] = json.loads(run_args[5])["selection"]["entity_sha256"]
    replace_json(run_args, 10, binding)
    report = assess_replayed_run(*run_args)
    assert report["selected_replay_binding"]["mode"] == "pipeline_history"
    verify_replayed_run(*run_args, report)


def test_no_network_and_determinism(run_args, monkeypatch):
    import socket
    import urllib.request

    def forbidden(*args, **kwargs):
        raise AssertionError("network requested")

    monkeypatch.setattr(socket, "socket", forbidden)
    monkeypatch.setattr(urllib.request, "urlopen", forbidden)
    report = assess_replayed_run(*run_args)
    assert report == assess_replayed_run(*run_args)
    verify_replayed_run(*run_args, report)
