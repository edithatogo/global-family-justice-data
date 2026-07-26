from __future__ import annotations

import json
import tomllib
from pathlib import Path

from gfjd import __version__
from gfjd.manifest import verify_manifest

ROOT = Path(__file__).resolve().parents[1]


def test_version_matches_pyproject() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert project["project"]["version"] == __version__


def test_json_schemas_parse() -> None:
    for path in (ROOT / "schemas").glob("*.json"):
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["$schema"] == "https://json-schema.org/draft/2020-12/schema"
        assert payload["title"]


def test_repository_manifest() -> None:
    assert verify_manifest() == []
