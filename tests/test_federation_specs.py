"""Pinned technical assets remain intact and available as package resources."""

from __future__ import annotations

import hashlib
import json
from importlib.resources import files

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
