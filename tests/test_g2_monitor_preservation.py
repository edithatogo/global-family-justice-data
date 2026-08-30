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
