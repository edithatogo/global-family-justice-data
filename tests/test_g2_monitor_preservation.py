"""Offline integrity checks for the two immutable three-root observations."""

import hashlib
import json
from pathlib import Path

import pytest

PREDECESSOR = "G2FUTURE-EDITION-THREE-ROOT-20260829-01/execution/run-33288137424-1"
SUCCESSOR = "G2FUTURE-EDITION-THREE-ROOT-20260830-02/execution/run-33288962808-1"
BASELINE = "G2FUTURE-EDITION-MULTIROOT-20260829-01/execution/run-33240864641-1"
LEDGER_SHA256 = "d485519d8332a5e640f08f95b72cd9997d0464eb395c96fe1e5c4b882e556125"


@pytest.mark.parametrize("run", [PREDECESSOR, SUCCESSOR])
def test_full_ledger_is_preserved_for_each_receipt(project_root: Path, run: str) -> None:
    root = project_root / "data/methods/g2"
    payload = (root / PREDECESSOR / "exposure-ledger.jsonl").read_bytes()
    receipt = json.loads((root / run / "receipt.json").read_text(encoding="utf-8"))
    assert hashlib.sha256(payload).hexdigest() == LEDGER_SHA256
    assert receipt["exposure_ledger_sha256"] == LEDGER_SHA256
    rows = [json.loads(line) for line in payload.splitlines()]
    assert len(rows) == receipt["summary"]["observed_locator_count"] == 1212
    assert all(
        set(row) == {"endpoint", "endpoint_ordinal", "lastmod", "ordinal", "url"} for row in rows
    )
    for request in receipt["requests"]:
        group = [row for row in rows if row["endpoint_ordinal"] == request["ordinal"]]
        assert len(group) == request["locator_count"]
        assert [row["ordinal"] for row in group] == list(range(1, len(group) + 1))
        assert all(row["endpoint"] == request["url"] for row in group)
    assert all(value is False for value in receipt["boundary"].values())


def test_preserved_novelty_matches_original_receipt(project_root: Path) -> None:
    root = project_root / "data/methods/g2"
    rows = [
        json.loads(line)
        for line in (root / PREDECESSOR / "exposure-ledger.jsonl").read_bytes().splitlines()
    ]
    baseline = [
        json.loads(line)
        for line in (root / BASELINE / "exposure-ledger.jsonl").read_bytes().splitlines()
    ]
    known = {(row["url"], row["lastmod"]) for row in baseline}
    novel = [row for row in rows if (row["url"], row["lastmod"]) not in known]
    payload = (root / PREDECESSOR / "novel-exposure-ledger.jsonl").read_bytes()
    receipt = json.loads((root / PREDECESSOR / "receipt.json").read_text(encoding="utf-8"))
    assert novel == [json.loads(line) for line in payload.splitlines()]
    assert len(novel) == receipt["summary"]["novel_exposure_count"] == 1
    assert hashlib.sha256(payload).hexdigest() == receipt["summary"]["novel_exposure_ledger_sha256"]
    assert {row["url"] for row in rows} == {row["url"] for row in baseline}
    assert receipt["status"] == "action_required"
    successor = json.loads((root / SUCCESSOR / "receipt.json").read_text(encoding="utf-8"))
    assert successor["status"] == "complete"
    assert successor["summary"]["novel_exposure_count"] == 0


@pytest.mark.parametrize(
    "run_id", ["33288135681-1", "33288139446-1", "33288140850-1", "33288142864-1", "33288144647-1"]
)
def test_additional_monitor_evidence_is_durably_bound(project_root: Path, run_id: str) -> None:
    index = json.loads(
        (project_root / "data/methods/g2/monitor-preservation-2026-08-30.json").read_text()
    )
    assert index["schema_version"] == "1.0"
    assert len(index["runs"]) == 5
    entry = next(row for row in index["runs"] if row["run_id"] == run_id)
    files = {}
    for name, binding in entry["files"].items():
        path = project_root / binding["path"]
        assert path.resolve().is_relative_to(project_root.resolve())
        payload = path.read_bytes()
        assert len(payload) == binding["bytes"]
        assert hashlib.sha256(payload).hexdigest() == binding["sha256"]
        files[name] = payload
    receipt = json.loads(files["receipt.json"])
    assert receipt["run_id"] == run_id
    assert receipt["source_commit"] == "faf520e75c059490690e7b3368b0a2e9f69dc9f2"
    assert receipt["status"] == "complete"
    assert all(value is False for value in receipt["boundary"].values())
    assert receipt["summary"]["outcome"] == entry["outcome"]
    if "exposure-ledger.jsonl" in files:
        ledger = files["exposure-ledger.jsonl"]
        novel = files["novel-exposure-ledger.jsonl"]
        assert hashlib.sha256(ledger).hexdigest() == receipt["exposure_ledger_sha256"]
        assert len(ledger.splitlines()) == receipt["summary"]["observed_locator_count"]
        assert novel == b""
        assert (
            hashlib.sha256(novel).hexdigest() == receipt["summary"]["novel_exposure_ledger_sha256"]
        )
        assert receipt["summary"]["novel_exposure_count"] == 0
    if "observations.json" in files:
        observations = json.loads(files["observations.json"])
        assert len(observations) == receipt["summary"]["observed_product_count"] == 4
        assert all(row["post_cutoff_update"] is False for row in observations)
        assert receipt["summary"]["eligibility_established"] is False
        assert entry["original_receipt_binds_observations_digest"] is False
    if "observation" in receipt:
        assert receipt["summary"]["candidate_eligibility"] is False
