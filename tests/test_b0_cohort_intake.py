"""Fail-closed real B0 cohort intake tests."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "assemble_b0_evidence_cohort",
    Path(__file__).parents[1] / "scripts/assemble_b0_evidence_cohort.py",
)
assert _SPEC and _SPEC.loader
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)
assemble = _MODULE.assemble


def _write_inventory(root: Path, payload: str, expected: str) -> Path:
    inventory = root / "inventory.csv"
    with inventory.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["inventory_id", "source_id", "edition", "payload_path", "sha256"],
        )
        writer.writeheader()
        writer.writerow(
            {
                "inventory_id": "I1",
                "source_id": "S1",
                "edition": "2026",
                "payload_path": payload,
                "sha256": expected,
            }
        )
    return inventory


def test_missing_bytes_stop_without_network(tmp_path: Path) -> None:
    inventory = _write_inventory(tmp_path, "data/raw/files/missing.pdf", "a" * 64)
    report = assemble(tmp_path, inventory)
    assert report["status"] == "terminal_stop_missing_bytes"
    assert report["eligible_count"] == 0
    assert report["network_used"] is False


def test_matching_bytes_are_eligible(tmp_path: Path) -> None:
    payload = tmp_path / "payload.bin"
    payload.write_bytes(b"real-byte-canary")
    digest = hashlib.sha256(payload.read_bytes()).hexdigest()
    inventory = _write_inventory(tmp_path, "payload.bin", digest)
    report = assemble(tmp_path, inventory)
    assert report["status"] == "ready_for_replay"
    assert report["eligible_count"] == 1
    assert report["rows"][0]["digest_matches"] is True  # type: ignore[index]


def test_mismatched_bytes_are_blocked(tmp_path: Path) -> None:
    payload = tmp_path / "payload.bin"
    payload.write_bytes(b"unexpected")
    inventory = _write_inventory(tmp_path, "payload.bin", "b" * 64)
    report = assemble(tmp_path, inventory)
    assert report["status"] == "terminal_stop_missing_bytes"
    assert report["rows"][0]["status"] == "blocked_missing_or_mismatched_bytes"  # type: ignore[index]
