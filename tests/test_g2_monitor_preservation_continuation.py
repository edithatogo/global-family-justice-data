"""Fixity and truthful provenance for the eight named historical monitor artifacts."""

import hashlib
import json
from pathlib import Path

import pytest

from gfjd.monitor_metadata import validate_monitor_metadata

RUNS = (
    "33240200746-1",
    "33240510062-1",
    "33241287646-1",
    "33297404761-1",
    "33301440152-1",
    "33303832206-1",
    "33304063733-1",
    "33305171731-1",
)


def index(root: Path) -> dict:
    return json.loads((root / "data/methods/g2/monitor-preservation-2026-08-31.json").read_bytes())


def bound_files(root: Path, entry: dict) -> dict[str, bytes]:
    files = {}
    for name, binding in entry["files"].items():
        path = root / binding["path"]
        assert path.resolve().is_relative_to(root.resolve())
        raw = path.read_bytes()
        assert len(raw) == binding["bytes"]
        assert hashlib.sha256(raw).hexdigest() == binding["sha256"]
        files[name] = raw
    return files


@pytest.mark.parametrize("run_id", RUNS)
def test_continuation_file_fixity_and_artifact_binding(project_root: Path, run_id: str) -> None:
    payload = index(project_root)
    assert tuple(row["run_id"] for row in payload["runs"]) == RUNS
    inventory = json.loads((project_root / payload["inventory_path"]).read_bytes())
    entry = next(row for row in payload["runs"] if row["run_id"] == run_id)
    artifact = next(row for row in inventory["artifacts"] if row["id"] == entry["artifact_id"])
    assert str(artifact["workflow_run"]["id"]) + "-1" == run_id
    assert artifact["workflow_run"]["head_sha"] == entry["source_commit"]
    assert artifact["workflow_run"]["repository_id"] == 1313678863
    assert artifact["workflow_run"]["head_repository_id"] == 1313678863
    assert artifact["workflow_run"]["head_branch"] == "main"
    assert artifact["name"] == entry["artifact_name"]
    assert artifact["expires_at"] == entry["artifact_expires_at"]
    assert artifact["size_in_bytes"] == entry["verified_archive_bytes"]
    assert entry["provider_reported_archive_bytes"] == entry["verified_archive_bytes"]
    assert artifact["digest"] == "sha256:" + entry["provider_reported_archive_sha256"]
    assert entry["verified_archive_sha256"] == entry["provider_reported_archive_sha256"]
    assert entry["source_contract"]["source_commit"] == entry["source_commit"]
    assert entry["gate_evidence_eligible"] is False
    assert entry["original_receipt_modified"] is False
    files = bound_files(project_root, entry)
    receipt = json.loads(files["receipt.json"])
    assert receipt["status"] == entry["original_status"]
    assert receipt["summary"]["outcome"] == entry["original_outcome"]
    options = {key: entry[key] for key in ("run_id", "source_commit", "campaign_id", "route")}
    options["endpoints"] = tuple(entry["expected_endpoints"])
    if run_id == RUNS[0]:
        assert entry["preservation_class"] == "legacy_artifact_bound_only"
        assert entry["modern_receipt_identity_validation"] == "failed_missing_fields"
        assert entry["identity_basis"] == "github_artifact_metadata"
        assert entry["original_receipt_run_id_present"] is False
        assert entry["original_receipt_source_commit_present"] is False
        assert "run_id" not in receipt and "source_commit" not in receipt
        assert hashlib.sha256(files["receipt.json"]).hexdigest() == (
            "868c452c184584d95811c58da6454fbba72b835d27a2ccb0c489811b8144e30d"
        )
        with pytest.raises(ValueError, match="monitor metadata validation failed"):
            validate_monitor_metadata(files, **options)
        # Compare actual metadata, not a repaired/synthesized identity-bearing receipt.
        reference = payload["runs"][1]
        modern = json.loads(bound_files(project_root, reference)["receipt.json"])
        assert set(receipt) == set(modern) - {"run_id", "source_commit"}
        for key in receipt:
            if key != "checked_at":
                assert receipt[key] == modern[key]
    else:
        assert entry["preservation_class"] == "receipt_and_artifact_bound"
        assert entry["modern_receipt_identity_validation"] == "passed"
        assert entry["original_receipt_run_id_present"] is True
        assert entry["original_receipt_source_commit_present"] is True
        result = validate_monitor_metadata(files, **options)
        assert result["receipt_status"] == receipt["status"]


def test_partial_failure_is_not_completed_or_filled(project_root: Path) -> None:
    entry = next(row for row in index(project_root)["runs"] if row["run_id"] == RUNS[6])
    files = bound_files(project_root, entry)
    receipt = json.loads(files["receipt.json"])
    assert receipt["status"] == receipt["summary"]["outcome"] == "terminal_failure"
    assert receipt["summary"]["completed_endpoint_count"] == 1
    assert len(files["exposure-ledger.jsonl"].splitlines()) == 711
    assert "novel-exposure-ledger.jsonl" not in files
    assert entry["novelty_recomputation"] == "not_available_partial_failure"


@pytest.mark.parametrize("run_id", (RUNS[0], RUNS[1], RUNS[2], RUNS[5]))
def test_complete_novelty_is_recomputed_from_bound_baselines(
    project_root: Path, run_id: str
) -> None:
    entry = next(row for row in index(project_root)["runs"] if row["run_id"] == run_id)
    files = bound_files(project_root, entry)
    known = set()
    for binding in entry["baseline_bindings"]:
        raw = (project_root / binding["path"]).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == binding["sha256"]
        known.update((row["url"], row.get("lastmod")) for row in map(json.loads, raw.splitlines()))
    rows = [json.loads(line) for line in files["exposure-ledger.jsonl"].splitlines()]
    assert [row for row in rows if (row["url"], row["lastmod"]) not in known] == [
        json.loads(line) for line in files["novel-exposure-ledger.jsonl"].splitlines()
    ]
