"""Historical actual-config drafts are metadata preparation, never source facts."""

import csv
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "data/federation/config-drafts-2026-09-01"


def test_preserved_actual_configuration_snapshot_is_exact_and_not_acceptance() -> None:
    raw = (SNAPSHOT / "receipt.json").read_bytes()
    receipt = json.loads(raw)
    assert receipt["contract_version"] == "gfjd-config-draft-snapshot-v1"
    assert receipt["evidence_kind"] == "repository_configuration_only"
    assert receipt["factual_evidence"] == "unverified"
    assert not any(receipt["authority"].values())
    assert re.fullmatch(r"[0-9a-f]{40}", receipt["source_commit"])
    bundle = SNAPSHOT / "bundle"
    actual = {
        item.relative_to(bundle).as_posix(): item.read_bytes()
        for item in bundle.rglob("*")
        if item.is_file()
    }
    assert len(actual) == 22
    assert {key: hashlib.sha256(value).hexdigest() for key, value in actual.items()} == receipt[
        "artifact_sha256"
    ]
    manifest = json.loads(actual["draft-manifest.json"])
    assert manifest["input_sha256"] == receipt["input_sha256"]
    assert manifest["artifact_sha256"] == {
        key: hashlib.sha256(value).hexdigest()
        for key, value in actual.items()
        if key != "draft-manifest.json"
    }
    with (ROOT / "programme/evidence_register.csv").open(newline="") as stream:
        evidence = {row["evidence_id"]: row for row in csv.DictReader(stream)}
    support = evidence["E-FEDERATION-CONFIG-DRAFTS-20260901"]
    assert support["status"] == "in_review"
    assert support["sha256"] == hashlib.sha256(raw).hexdigest()
    assert ROOT / support["path"] == SNAPSHOT / "receipt.json"
    assert support["path"] != evidence["E-FEDERATED-MEDALLION-REGISTRY"]["path"]
    with (ROOT / "programme/work_items.csv").open(newline="") as stream:
        items = {row["work_item_id"]: row for row in csv.DictReader(stream)}
    assert support["evidence_id"] not in items["WI-G4-MED-05"]["evidence_ids"].split(";")


def test_snapshot_has_ten_incomplete_dataset_drafts_and_no_explorer_dataset() -> None:
    bundle = SNAPSHOT / "bundle"
    documents = sorted((bundle / "metadata").rglob("*.json"))
    assert len(documents) == 10
    assert {path.parent.name for path in documents} == {
        "source-archive",
        "source-catalogue",
        "observations",
        "outcomes-evidence",
        "extraction-benchmark",
    }
    for path in documents:
        document = json.loads(path.read_bytes())
        root = (
            next(node for node in document["@graph"] if node["@id"] == "./")
            if "@graph" in document
            else document
        )
        assert root["name"].startswith("Draft: edithatogo/gfjd-")
        assert "prospective" in root["description"].lower()
        assert not (
            {
                "datePublished",
                "license",
                "creator",
                "publisher",
                "distribution",
                "recordSet",
                "hasPart",
                "url",
            }
            & set(root)
        )
    assessments = json.loads((bundle / "metadata-assessments.json").read_bytes())
    assert len(assessments) == 10
    for assessment in assessments.values():
        assert assessment["status"] == "profile_incomplete"
        assert assessment["factual_evidence"] == "unverified"
        assert assessment["full_conformance"] == "unverified"
        assert not any(assessment["authority"].values())
