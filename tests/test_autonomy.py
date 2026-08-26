from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from gfjd.autonomy import build_autonomy_context, verify_autonomy_context
from gfjd.io import read_json
from gfjd.project import load_project


def test_autonomy_context_is_bounded_and_fail_closed(tmp_path: Path) -> None:
    result = build_autonomy_context(
        load_project(),
        tmp_path,
        generated_at=datetime(2026, 7, 27, 12, 0, tzinfo=UTC),
    )

    assert result.next_actions > 0
    assert verify_autonomy_context(tmp_path) == []
    payload = read_json(tmp_path / "autonomy-context.json")
    assert payload["operating_mode"] == "single_maintainer_autonomous"
    assert payload["external_boundaries"]
    assert all(item["kind"] == "governance_decision" for item in payload["external_boundaries"])
    assert {item["work_item_id"] for item in payload["autonomous_queue"]} == {
        "WI-G3-MED-02",
        "WI-G4-MED-01",
    }
    assert all(item["status"] == "planned" for item in payload["autonomous_queue"])
    assert payload["external_actions"]
    assert len(payload["blocker_matrix"]) == 6
    assert payload["blocker_matrix"][0]["gate_id"] == "G1"
    assert {item["track_id"] for item in payload["dependency_sequence"]} == {
        f"T{i}" for i in range(10)
    }
    assert payload["context_bytes"] <= payload["context_byte_limit"]
    assert all(item["content"] for item in payload["files"])
    assert "environment" not in payload
    assert payload["git"]["head"]


def test_autonomy_context_detects_tampering(tmp_path: Path) -> None:
    build_autonomy_context(load_project(), tmp_path)
    (tmp_path / "autonomy-context.md").write_text("tampered\n", encoding="utf-8")

    assert verify_autonomy_context(tmp_path) == ["checksum mismatch: autonomy-context.md"]
