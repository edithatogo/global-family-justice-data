from __future__ import annotations

import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse

from blake3 import blake3

from gfjd.public_monitor import (
    _allowed_final_host,
    monitor_custody,
    verify_monitor_receipt,
    verify_supersession,
)


def test_hugging_face_public_cdn_is_approved() -> None:
    assert _allowed_final_host("us.aws.cdn.hf.co")


def test_monitor_recomputes_replica_state(project_root: Path, tmp_path: Path) -> None:
    custody_path = project_root / "data/preservation/public_b0_custody_20260827.json"
    custody = json.loads(custody_path.read_text(encoding="utf-8"))
    custody["objects"] = custody["objects"][:1]
    data = b"safe aggregate fixture"
    item = custody["objects"][0]
    item["size_bytes"] = len(data)
    item["sha256"] = hashlib.sha256(data).hexdigest()
    item["blake3"] = blake3(data).hexdigest()
    for replica in item["replicas"]:
        replica["retrieved_sha256"] = item["sha256"]
        replica["retrieved_blake3"] = item["blake3"]
    safety = json.loads(
        (project_root / "data/preservation/public_b0_safety_20260827.json").read_text(
            encoding="utf-8"
        )
    )
    safety["objects"] = safety["objects"][:1]
    safety["objects"][0]["size_bytes"] = len(data)
    safety["objects"][0]["sha256"] = hashlib.sha256(data).hexdigest()
    safety["objects"][0]["blake3"] = blake3(data).hexdigest()
    root = tmp_path
    safety_path = root / "safety.json"
    safety_path.write_text(json.dumps(safety) + "\n", encoding="utf-8")
    custody["safety_receipt_path"] = "safety.json"
    custody["safety_receipt_sha256"] = hashlib.sha256(safety_path.read_bytes()).hexdigest()
    local_custody = root / "custody.json"
    local_custody.write_text(json.dumps(custody), encoding="utf-8")

    by_url = {replica["url"]: data for replica in item["replicas"]}

    def fetch(url: str, expected: int) -> tuple[bytes, int, str]:
        assert len(by_url[url]) == expected
        return by_url[url], 200, url

    receipt = monitor_custody(
        root,
        local_custody,
        checked_at="2026-08-27T00:00:00Z",
        source_commit="a" * 40,
        run_id="test-1",
        fetcher=fetch,
    )
    assert receipt["status"] == "pass"
    assert verify_monitor_receipt(receipt) == []


def test_monitor_detects_drift_and_unavailability(project_root: Path, tmp_path: Path) -> None:
    custody_path = project_root / "data/preservation/public_b0_custody_20260827.json"

    def fetch(url: str, expected: int) -> tuple[bytes, int, str]:
        if urlparse(url).hostname == "github.com":
            return b"drift", 200, url
        raise OSError("offline")

    receipt = monitor_custody(
        project_root,
        custody_path,
        checked_at="2026-08-27T00:00:00Z",
        source_commit="b" * 40,
        run_id="test-2",
        fetcher=fetch,
    )
    assert receipt["status"] == "fail"
    assert {item["state"] for item in receipt["observations"]} == {"drift", "unavailable"}
    receipt["status"] = "pass"
    assert any(
        "monitor status does not match" in error for error in verify_monitor_receipt(receipt)
    )


def test_supersession_replay_is_deterministic_and_cycles_fail(tmp_path: Path) -> None:
    record = tmp_path / "supersession.json"
    record.write_text(
        json.dumps(
            {
                "contract_version": "gfjd-public-b0-supersession-v1",
                "nodes": [
                    {"snapshot_id": "A"},
                    {"snapshot_id": "B"},
                    {"snapshot_id": "C"},
                ],
                "edges": [
                    {"supersedes": "A", "snapshot_id": "B"},
                    {"supersedes": "B", "snapshot_id": "C"},
                ],
            }
        ),
        encoding="utf-8",
    )
    errors, order = verify_supersession(record)
    assert errors == []
    assert order == ["A", "B", "C"]
    payload = json.loads(record.read_text(encoding="utf-8"))
    payload["edges"].append({"supersedes": "C", "snapshot_id": "A"})
    record.write_text(json.dumps(payload), encoding="utf-8")
    errors, order = verify_supersession(record)
    assert "supersession graph contains a cycle" in errors
    assert order == []
