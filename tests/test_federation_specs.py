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
            "partner-archive-ownership.py.txt",
            "9bdbecd2cd84f1faff7d69b5bdad729f8add68baa98b9345b066ccc1775d031a",
        ),
        (
            "partner-archive-publication.schema.json",
            "6097ba87f4eafa04bcea8f586144cb9129961d085709fe99350e600274137c9d",
        ),
        (
            "partner-archive-LICENSE.txt",
            "a6cba85bc92e0cff7a450b1d873c0eaa2e9fc96bf472df0247a26bec77bf3ff9",
        ),
        (
            "partner-gma-federation.schema.json",
            "ac28485a70e0853266e4c140f9a07cd557eb27816b0b408b9bf2927a4cffacec",
        ),
        (
            "partner-gma-semantics.py.txt",
            "2a21eb2d09a8a9ba1e956c1b0d5c123529c185d79bb31ced2c2a0cb8bebaeb78",
        ),
        (
            "partner-gma-LICENSE.txt",
            "450ea334a0b6b4cfc91760135d029f8182bb20689ba77ae3c1251cc7f4265066",
        ),
        (
            "partner-gma-NOTICE.txt",
            "5e71f55fe41db303f30b5eb4659ecbdfec6e8dc0de8886c2f15ca8bace5a114b",
        ),
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
