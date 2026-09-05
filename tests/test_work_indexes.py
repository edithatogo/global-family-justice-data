import hashlib
import json
import runpy
import sys
from dataclasses import replace
from pathlib import Path

import pytest

from gfjd.conductor import Conductor


def test_work_views_partition_without_mutating_register(project_root: Path) -> None:
    functions = runpy.run_path(str(project_root / "scripts/render_work_indexes.py"))
    conductor = Conductor.load(project_root)
    before = (project_root / "programme/work_items.csv").read_bytes()
    active = functions["render"](conductor, completed=False)
    completed = functions["render"](conductor, completed=True)
    for item in conductor.work_items.values():
        marker = f"| {item.id} |"
        assert (marker in completed) == (item.status == "accepted")
        assert (marker in active) == (item.status != "accepted")
    assert before == (project_root / "programme/work_items.csv").read_bytes()
    assert active == functions["render"](conductor, completed=False)


def test_reopened_work_returns_to_active_view(project_root: Path) -> None:
    functions = runpy.run_path(str(project_root / "scripts/render_work_indexes.py"))
    conductor = Conductor.load(project_root)
    item = next(item for item in conductor.work_items.values() if item.status == "accepted")
    conductor.work_items[item.id] = replace(item, status="in_review", title="A | B\nC")
    active = functions["render"](conductor, completed=False)
    assert f"| {item.id} |" in active
    assert f"| {item.id} |" not in functions["render"](conductor, completed=True)
    assert "A \\| B C" in active


@pytest.mark.parametrize("configured_statuses", [None, ["accepted"], ["waived", "done"]])
def test_work_views_follow_configured_completion_statuses(
    project_root: Path, configured_statuses: list[str] | None
) -> None:
    functions = runpy.run_path(str(project_root / "scripts/render_work_indexes.py"))
    conductor = Conductor.load(project_root)
    config = conductor.project.config.setdefault("conductor", {})
    if configured_statuses is None:
        config.pop("accepted_work_statuses", None)
    else:
        config["accepted_work_statuses"] = configured_statuses
    statuses = {"accepted", "waived"} if configured_statuses is None else set(configured_statuses)
    original_items = list(conductor.work_items.values())[:3]
    for item, status in zip(original_items, ("accepted", "waived", "done"), strict=True):
        conductor.work_items[item.id] = replace(item, status=status)
    active = functions["render"](conductor, completed=False)
    completed = functions["render"](conductor, completed=True)
    for item in conductor.work_items.values():
        marker = f"| {item.id} |"
        assert (marker in completed) == (item.status in statuses)
        assert (marker in active) == (item.status not in statuses)
    waived = conductor.work_items[original_items[1].id]
    view = completed if "waived" in statuses else active
    assert f"| {waived.id} | {waived.track_id}/{waived.gate_id} | waived |" in view
    assert "Recorded complete" in completed


def test_check_rejects_missing_and_stale_views(
    project_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    functions = runpy.run_path(str(project_root / "scripts/render_work_indexes.py"))
    conductor = Conductor.load(project_root)
    monkeypatch.setattr(Conductor, "load", lambda root: conductor)
    monkeypatch.setitem(functions["main"].__globals__, "ROOT", tmp_path)
    monkeypatch.setattr(sys, "argv", ["render_work_indexes.py", "--check"])
    with pytest.raises(ValueError, match="Stale or missing"):
        functions["main"]()
    monkeypatch.setattr(sys, "argv", ["render_work_indexes.py"])
    assert functions["main"]() == 0
    monkeypatch.setattr(sys, "argv", ["render_work_indexes.py", "--check"])
    assert functions["main"]() == 0
    active = tmp_path / "docs/programme/generated/active-work.md"
    active.write_text("stale", encoding="utf-8")
    with pytest.raises(ValueError, match="Stale or missing"):
        functions["main"]()


def test_recovered_custody_metadata_is_bound_outside_build(project_root: Path) -> None:
    receipt_path = project_root / "docs/governance/g2-ods-durable-custody-2026-09-06.json"
    custody = json.loads(receipt_path.read_text())
    recovery = project_root / custody["recovery_receipt"]
    assert hashlib.sha256(recovery.read_bytes()).hexdigest() == custody["recovery_receipt_sha256"]
    recorded = json.loads(recovery.read_text())
    assert custody["sha256"] == recorded["expected_sha256"] == recorded["local_readback_sha256"]
    assert custody["size_bytes"] == recorded["size_bytes"] == 990297
    retained = Path(custody["retained_path"])
    assert Path("data/raw/files") in retained.parents
    assert not retained.is_absolute() and ".." not in retained.parts
    assert "data/raw/files/" in (project_root / ".gitignore").read_text().splitlines()
    assert custody["provider_separated"] is False
    assert custody["source_content_published"] is False
