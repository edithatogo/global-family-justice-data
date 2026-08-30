"""Synthetic-only exact projection and replay tests; no empirical evidence."""

from __future__ import annotations

import copy
import hashlib
import json
from typing import Any

import pytest

from gfjd.medallion_replay import ProjectionReplayError, replay_projection, verify_projection

SOURCE = b'[{"label":"SYNTHETIC ONLY","count":"001","a/b~c":"fictional"}]'


def contract(source: bytes = SOURCE) -> dict[str, Any]:
    return {
        "contract_version": "gfjd-json-projection-v1",
        "source_sha256": hashlib.sha256(source).hexdigest(),
        "projection": {"matter": "label", "value": "count"},
        "valid_from": None,
        "recorded_at": "2026-08-30T00:00:00Z",
    }


def test_exact_projection_is_deterministic_and_recomputable() -> None:
    specification = contract()
    result = replay_projection(SOURCE, specification)
    assert result == replay_projection(SOURCE, specification)
    specification["projection"] = {"value": "count", "matter": "label"}
    assert result == replay_projection(SOURCE, specification)
    assert result["rows"] == [{"matter": "SYNTHETIC ONLY", "value": "001"}]
    assert result["valid_from"] is None
    assert result["promotion_authorized"] is False
    assert [item["source_pointer"] for item in result["field_lineage"]] == ["/0/label", "/0/count"]
    assert len(result["implementation_sha256"]) == 64
    verify_projection(SOURCE, specification, result)


def test_pointer_escaping_and_value_hash() -> None:
    specification = contract()
    specification["projection"] = {"out/~": "a/b~c"}
    result = replay_projection(SOURCE, specification)
    item = result["field_lineage"][0]
    assert item["source_pointer"] == "/0/a~1b~0c"
    assert item["output_pointer"] == "/0/out~1~0"
    assert item["value_sha256"] == hashlib.sha256(b'"fictional"').hexdigest()


@pytest.mark.parametrize("field", ["valid_from", "recorded_at"])
def test_explicit_clock_changes_snapshot_identity(field: str) -> None:
    original = replay_projection(SOURCE, contract())
    changed = contract()
    changed[field] = "2026-08-31T00:00:00Z"
    result = replay_projection(SOURCE, changed)
    assert result["snapshot_sha256"] != original["snapshot_sha256"]
    assert result["rows"] == original["rows"]


@pytest.mark.parametrize("value", [None, "", "2026-08-30", "2026-13-01T00:00:00Z", True])
def test_invalid_recorded_clock_rejected(value: Any) -> None:
    specification = contract()
    specification["recorded_at"] = value
    with pytest.raises(ProjectionReplayError):
        replay_projection(SOURCE, specification)


@pytest.mark.parametrize(
    "source",
    [
        b"[]",
        b"{}",
        b"[1]",
        b'[{"label":"a","label":"b","count":"1"}]',
        b'[{"label":"fictional","count":1}]',
        b'[{"label":"fictional"}]',
        b"\xff",
    ],
)
def test_invalid_source_fails_without_coercion(source: bytes) -> None:
    with pytest.raises(ProjectionReplayError):
        replay_projection(source, contract(source))


@pytest.mark.parametrize("projection", [{}, {"": "label"}, {"x": []}, {"x": "label", "y": "label"}])
def test_invalid_projection_fails(projection: Any) -> None:
    specification = contract()
    specification["projection"] = projection
    with pytest.raises(ProjectionReplayError):
        replay_projection(SOURCE, specification)


def test_source_digest_and_budget_fail_closed() -> None:
    with pytest.raises(ProjectionReplayError, match="digest"):
        replay_projection(SOURCE + b" ", contract())
    oversized = b" " * (1024 * 1024 + 1)
    with pytest.raises(ProjectionReplayError, match="byte"):
        replay_projection(oversized, contract(oversized))
    too_many = json.dumps([{"label": "SYNTHETIC", "count": "1"}] * 1001).encode()
    with pytest.raises(ProjectionReplayError, match="row"):
        replay_projection(too_many, contract(too_many))


def test_field_and_cell_budgets_fail_closed() -> None:
    row = {str(index): "SYNTHETIC" for index in range(65)}
    source = json.dumps([row]).encode()
    specification = contract(source)
    specification["projection"] = {"value": "0"}
    with pytest.raises(ProjectionReplayError, match="bounded"):
        replay_projection(source, specification)
    specification["projection"] = {key: key for key in row}
    with pytest.raises(ProjectionReplayError, match="projection"):
        replay_projection(source, specification)
    row.pop("64")
    source = json.dumps([row] * 157).encode()
    specification = contract(source)
    specification["projection"] = {key: key for key in row}
    with pytest.raises(ProjectionReplayError, match="cell"):
        replay_projection(source, specification)


@pytest.mark.parametrize(
    "change", [{"contract_version": "other"}, {"extra": True}, {"valid_from": False}]
)
def test_contract_drift_is_rejected(change: dict[str, Any]) -> None:
    specification = contract()
    specification.update(change)
    with pytest.raises(ProjectionReplayError):
        replay_projection(SOURCE, specification)


def test_source_identity_and_row_order_are_preserved() -> None:
    source = b'[{"label":"SYNTHETIC A","count":"2"},{"label":"SYNTHETIC B","count":"1"}]'
    result = replay_projection(source, contract(source))
    assert [row["value"] for row in result["rows"]] == ["2", "1"]
    spaced = source + b" "
    changed = replay_projection(spaced, contract(spaced))
    assert changed["rows"] == result["rows"]
    assert changed["snapshot_sha256"] != result["snapshot_sha256"]


@pytest.mark.parametrize(
    "field", ["rows", "field_lineage", "snapshot_sha256", "promotion_authorized"]
)
def test_self_reported_output_cannot_pass_verification(field: str) -> None:
    result = replay_projection(SOURCE, contract())
    damaged = copy.deepcopy(result)
    damaged[field] = 0 if field == "promotion_authorized" else "tampered"
    with pytest.raises(ProjectionReplayError, match="recompute"):
        verify_projection(SOURCE, contract(), damaged)
