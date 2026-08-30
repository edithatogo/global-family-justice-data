from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

from gfjd.autonomy import _classify_actions, build_autonomy_context, verify_autonomy_context
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
        "WI-G4-MED-02",
    }
    assert {item["work_item_id"]: item["status"] for item in payload["autonomous_queue"]} == {
        "WI-G4-MED-02": "in_progress",
    }
    assert payload["external_actions"]
    assert "WI-G4-MED-04" in {item["work_item_id"] for item in payload["external_actions"]}
    assert all(item["execution_scope"] for item in payload["autonomous_queue"])
    required_context = {
        "AUTONOMOUS_IMPLEMENTATION.md",
        "docs/governance/standing-owner-direction-policy-2026-08-20.md",
        "docs/engineering/medallion-autonomous-continuation-2026-08-30.md",
    }
    assert required_context <= {item["path"] for item in payload["files"] if item["content"]}
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


@pytest.mark.parametrize("status", ["planned", "in_progress"])
def test_explicit_repository_scope_can_execute_without_mutating_input(status: str) -> None:
    action = {"work_item_id": "WI-G4-MED-02", "status": status, "title": "Lineage"}
    queued, held = _classify_actions([action])
    assert not held
    assert queued[0]["work_item_id"] == action["work_item_id"]
    assert "No source access" in queued[0]["execution_scope"]
    assert "execution_scope" not in action


@pytest.mark.parametrize("work_id", ["WI-G4-MED-04", "WI-FUTURE-UNKNOWN", None, [], {}])
@pytest.mark.parametrize("status", ["planned", "in_progress"])
def test_publication_and_unclassified_work_fail_closed(work_id: Any, status: str) -> None:
    action = {"work_item_id": work_id, "status": status, "title": "Safe local preparation"}
    queued, held = _classify_actions([action])
    assert queued == []
    assert held == [action]


@pytest.mark.parametrize(
    "status", ["in_review", "review", "done", "accepted", "blocked", "new", None, [], {}]
)
def test_status_cannot_bypass_acceptance_or_scope_review(status: Any) -> None:
    action = {"work_item_id": "WI-G4-MED-02", "status": status}
    queued, held = _classify_actions([action])
    assert queued == []
    assert held == [action]
