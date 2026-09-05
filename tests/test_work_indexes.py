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
