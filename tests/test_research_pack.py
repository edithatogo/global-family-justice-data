from __future__ import annotations

import shutil

import pytest

from gfjd.project import load_project
from gfjd.research_pack import ResearchPackError, build_research_pack


def _copy(root, destination):
    return shutil.copytree(
        root, destination, ignore=shutil.ignore_patterns(".git", "build", ".venv", "__pycache__")
    )


def test_research_pack_is_non_evidentiary(project_root, tmp_path):
    root = _copy(project_root, tmp_path / "repo")
    destination = build_research_pack(load_project(root), "AUS", root / "build/research-packs")
    assert "non_evidentiary_handoff" in (destination / "research-pack.json").read_text()
    assert (destination / "search-plan.csv").is_file()


def test_research_pack_rejects_unknown_jurisdiction(project_root, tmp_path):
    root = _copy(project_root, tmp_path / "repo")
    with pytest.raises(ResearchPackError, match="Unknown jurisdiction"):
        build_research_pack(load_project(root), "ZZZ", root / "build/research-packs")
