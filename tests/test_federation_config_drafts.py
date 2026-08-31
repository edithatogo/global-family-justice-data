"""Configuration-only draft checks; no source payloads or hosted access."""

import hashlib
import json
import socket
import traceback
import urllib.request
from pathlib import Path

import pytest

from gfjd.federation_config_drafts import (
    prepare_config_metadata_draft,
    verify_config_metadata_draft,
)
from gfjd.federation_metadata import MetadataError
from gfjd.medallion_estate import POLICY_REFERENCE, SOURCEFILES, prepare_estate

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def inputs():
    return {name: (ROOT / name).read_bytes() for name in (*SOURCEFILES, POLICY_REFERENCE)}


@pytest.fixture
def standards():
    return {
        name: (ROOT / "src/gfjd/federation_specs" / name).read_bytes()
        for name in ("ro-crate-1.3-context.jsonld", "gfjd-croissant-profile-v1.json")
    }


def test_missing_profile_red(inputs, standards):
    del standards["ro-crate-1.3-context.jsonld"]
    with pytest.raises(MetadataError):
        prepare_config_metadata_draft(inputs, standards)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def test_actual_draft_coverage_and_missing_facts(inputs, standards):
    outputs = prepare_config_metadata_draft(inputs, standards)
    assert len(outputs) == 22
    estate = prepare_estate(inputs)
    assert {
        name.removeprefix("estate/"): raw
        for name, raw in outputs.items()
        if name.startswith("estate/")
    } == estate
    report = json.loads(outputs["declaration-report.json"])
    assert len(report["roles"]) == 6
    assessment = json.loads(outputs["metadata-assessments.json"])
    assert len(assessment) == 10
    assert {item["status"] for item in assessment.values()} == {"profile_incomplete"}
    for item in report["roles"]:
        role = item["declaration"]
        assert role["repository"].startswith("edithatogo/gfjd-")
        assert role["desired_link"]["requested"] is False
        assert {
            "publication_date",
            "creator",
            "publisher",
            "runtime_lineage",
        } <= set(item["missing_facts"])
        if role["id"] == "explorer":
            assert role["repo_type"] == "space"
            assert item["profile_assessments"] == []
            assert item["field_provenance"] == {}
            assert "space_content_license" in item["missing_facts"]
            assert "dataset_license" not in item["missing_facts"]
            continue
        assert "dataset_license" in item["missing_facts"]
        for path in item["profile_assessments"]:
            doc = json.loads(outputs[path])
            root = doc["@graph"][1] if "@graph" in doc else doc
            assert root["name"] == "Draft: " + role["repository"]
            assert root["description"].startswith("Prospective preparation only.")
            assert not {
                "datePublished",
                "license",
                "creator",
                "publisher",
                "url",
                "distribution",
                "hasPart",
                "sha256",
                "recordSet",
                "version",
            } & set(root)
            assert b"huggingface.co" not in outputs[path]
    assert not any(report["authority"].values())
    assert set(report["factual_states"].values()) == {"unverified"}
    verify_config_metadata_draft(inputs, standards, outputs)


def test_exact_configuration_provenance(inputs, standards):
    outputs = prepare_config_metadata_draft(inputs, standards)
    estate_raw = outputs["estate/estate-manifest.json"]
    estate = json.loads(estate_raw)
    report = json.loads(outputs["declaration-report.json"])
    expected_inputs = {name: sha(raw) for name, raw in inputs.items()}
    for index, item in enumerate(report["roles"]):
        assert item["declaration"] == estate["roles"][index]
        for field, provenance in item["field_provenance"].items():
            assert provenance["estate_manifest_sha256"] == sha(estate_raw)
            assert provenance["input_sha256"] == expected_inputs
            expected = (
                [f"/roles/{index}/repository"]
                if field == "name"
                else [f"/roles/{index}/id", f"/roles/{index}/payload_policy"]
            )
            assert provenance["estate_json_pointers"] == expected
            assert set(provenance["generated_field_pointers"]) == set(item["profile_assessments"])
    assert report["diagnostics"] == estate["diagnostics"]
    manifest = json.loads(outputs["draft-manifest.json"])
    assert manifest["input_sha256"] == expected_inputs
    assert manifest["standard_sha256"] == {name: sha(raw) for name, raw in standards.items()}
    assert manifest["artifact_sha256"] == {
        name: sha(raw) for name, raw in outputs.items() if name != "draft-manifest.json"
    }
    assert manifest["implementation_sha256"] == sha(
        (ROOT / "src/gfjd/federation_config_drafts.py").read_bytes()
    )


@pytest.mark.parametrize("name", [*SOURCEFILES, POLICY_REFERENCE])
def test_missing_input(inputs, standards, name):
    del inputs[name]
    with pytest.raises(MetadataError):
        prepare_config_metadata_draft(inputs, standards)


@pytest.mark.parametrize("mutation", ["extra", "conflict", "policy", "malformed"])
def test_bad_configuration(inputs, standards, mutation):
    if mutation == "extra":
        inputs["unexpected"] = b"x"
    elif mutation == "conflict":
        inputs[SOURCEFILES[1]] = inputs[SOURCEFILES[1]].replace(b"edithatogo", b"different")
    elif mutation == "policy":
        inputs[POLICY_REFERENCE] += b"\n"
    else:
        inputs[SOURCEFILES[0]] = b"invalid"
    with pytest.raises(MetadataError):
        prepare_config_metadata_draft(inputs, standards)


@pytest.mark.parametrize("mutation", ["extra", "tamper", "large", "wrongtype"])
def test_bad_standards(inputs, standards, mutation):
    key = "gfjd-croissant-profile-v1.json"
    if mutation == "extra":
        standards["unused"] = b"{}"
    elif mutation == "tamper":
        standards[key] += b"\n"
    elif mutation == "large":
        standards[key] = b"x" * (256 * 1024 + 1)
    else:
        standards[key] = "not bytes"
    with pytest.raises(MetadataError):
        prepare_config_metadata_draft(inputs, standards)


@pytest.mark.parametrize(
    "target",
    [
        "declaration-report.json",
        "metadata-assessments.json",
        "metadata/observations/croissant.json",
        "draft-manifest.json",
    ],
)
def test_rehashed_forgery(inputs, standards, target):
    outputs = prepare_config_metadata_draft(inputs, standards)
    value = json.loads(outputs[target])
    value["forged"] = True
    outputs[target] = json.dumps(value).encode()
    manifest = json.loads(outputs["draft-manifest.json"])
    if target != "draft-manifest.json":
        manifest["artifact_sha256"][target] = sha(outputs[target])
    outputs["draft-manifest.json"] = json.dumps(manifest).encode()
    with pytest.raises(MetadataError):
        verify_config_metadata_draft(inputs, standards, outputs)


@pytest.mark.parametrize("mutation", ["missing", "extra", "type"])
def test_exact_output_set(inputs, standards, mutation):
    outputs = prepare_config_metadata_draft(inputs, standards)
    if mutation == "missing":
        del outputs["README.md"]
    elif mutation == "extra":
        outputs["extra"] = b""
    else:
        outputs["README.md"] = outputs["README.md"].decode()
    with pytest.raises(MetadataError):
        verify_config_metadata_draft(inputs, standards, outputs)


def test_deterministic_no_network_and_no_input_errors(inputs, standards, monkeypatch, capsys):
    def denied(*args, **kwargs):
        raise AssertionError("unexpected network")

    monkeypatch.setattr(socket, "create_connection", denied)
    monkeypatch.setattr(urllib.request, "urlopen", denied)
    assert prepare_config_metadata_draft(inputs, standards) == prepare_config_metadata_draft(
        inputs, standards
    )
    inputs[SOURCEFILES[0]] = b"PRIVATE_SENTINEL"
    try:
        prepare_config_metadata_draft(inputs, standards)
    except MetadataError:
        assert "PRIVATE_SENTINEL" not in traceback.format_exc()
    else:
        pytest.fail("malformed configuration accepted")
    assert capsys.readouterr() == ("", "")
