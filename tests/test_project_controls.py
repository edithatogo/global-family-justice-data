from __future__ import annotations

import json
import tomllib
from pathlib import Path

import pytest

from gfjd import __version__, manifest
from gfjd.io import read_csv
from gfjd.manifest import iter_manifest_files, verify_manifest

ROOT = Path(__file__).resolve().parents[1]


def test_version_matches_pyproject() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert project["project"]["version"] == __version__


def test_json_schemas_parse() -> None:
    for path in (ROOT / "schemas").glob("*.json"):
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["$schema"] == "https://json-schema.org/draft/2020-12/schema"
        assert payload["title"]


def test_csv_reader_rejects_surplus_fields_without_rewriting(tmp_path: Path) -> None:
    path = tmp_path / "governed.csv"
    original = b"id,notes\nA,unquoted,comma\n"
    path.write_bytes(original)

    with pytest.raises(ValueError, match="more fields than its header"):
        read_csv(path)

    assert path.read_bytes() == original


def test_repository_manifest() -> None:
    assert verify_manifest() == []


def test_repository_manifest_excludes_controlled_raw_evidence() -> None:
    assert all(relative.parts[:3] != ("data", "raw", "files") for relative in iter_manifest_files())


def test_manifest_ignores_editable_install_metadata(tmp_path: Path, monkeypatch: object) -> None:
    source = tmp_path / "src" / "gfjd"
    source.mkdir(parents=True)
    (source / "__init__.py").write_text("", encoding="utf-8")
    metadata = tmp_path / "src" / "example.egg-info"
    metadata.mkdir()
    (metadata / "PKG-INFO").write_text("generated", encoding="utf-8")
    monkeypatch.setattr(manifest, "ROOT", tmp_path)  # type: ignore[attr-defined]

    assert manifest.iter_manifest_files() == [Path("src/gfjd/__init__.py")]
