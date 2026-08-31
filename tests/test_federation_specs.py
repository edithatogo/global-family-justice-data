"""Pinned technical assets remain intact and available as package resources."""

from __future__ import annotations

import hashlib
import json
import tomllib
from importlib.resources import files
from pathlib import Path

import pytest


@pytest.mark.parametrize(
    ("name", "digest"),
    [
        (
            "openlineage-2-0-2.json",
            "69f68bee00b9beac88a87059c0102410e7bb05f3f43c46d02a0409831eceb0d2",
        ),
        (
            "OpenLineage-LICENSE.txt",
            "c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4",
        ),
        (
            "ro-crate-1.3-context.jsonld",
            "5a3df1a43185501db4d45cdde5a478c57eeb1d673eedfe400488fc4c4b21dd91",
        ),
        (
            "dcat-ap-3.0.1-shapes.ttl",
            "7fe9815e0f32b10f5cbce74fa6ccd0290aae3ef9e5080fb84e2d8093eb984d1d",
        ),
        (
            "dcat-ap-3.0.1-range.ttl",
            "24d3bfd0fa17a3d0e877c9ebb91c8174124e5038538e1bf081b2cb679ad0f1b2",
        ),
    ],
)
def test_upstream_asset_is_unchanged(name: str, digest: str) -> None:
    raw = files("gfjd").joinpath("federation_specs", name).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == digest


def test_upstream_schema_identity() -> None:
    raw = files("gfjd").joinpath("federation_specs", "openlineage-2-0-2.json").read_bytes()
    assert len(raw) == 9155
    schema = json.loads(raw)
    assert schema["$id"] == "https://openlineage.io/spec/2-0-2/OpenLineage.json"
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"


def test_distribution_requirements_match_dcat_engine_guards() -> None:
    from gfjd.federation_dcat import ENGINE_VERSIONS

    project = tomllib.loads(
        (Path(__file__).parents[1] / "pyproject.toml").read_text(encoding="utf-8")
    )
    requirements = project["project"]["dependencies"]
    for name, version in ENGINE_VERSIONS.items():
        assert f"{name}=={version}" in requirements
