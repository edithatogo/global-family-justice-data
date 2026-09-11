"""Fail-closed qualification report over the checked-in real B0 cohort."""

import importlib.util
import json
from pathlib import Path

import pytest

_MODULE_PATH = Path(__file__).parents[1] / "scripts" / "qualify_real_b0_cohort.py"
_SPEC = importlib.util.spec_from_file_location("qualify_real_b0_cohort", _MODULE_PATH)
assert _SPEC and _SPEC.loader
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)
DEFAULT_INTAKE = _MODULE.DEFAULT_INTAKE
qualify = _MODULE.qualify


def test_real_b0_report_keeps_unsupported_routes_pending() -> None:
    intake = json.loads(DEFAULT_INTAKE.read_bytes())
    if any(
        not (Path(__file__).parents[1] / row["payload_path"]).is_file() for row in intake["rows"]
    ):
        pytest.skip("local-private B0 payloads are unavailable in this checkout")
    report = qualify(intake, as_of="2026-09-11T12:15:00Z")

    assert report["status"] == "b0_fixity_verified_replay_pending"
    assert report["network_requests"] == 0
    assert len(report["rows"]) == 6
    by_id = {row["inventory_id"]: row for row in report["rows"]}
    assert all(row["b0_fixity"] == "verified" for row in report["rows"])
    assert by_id["ARC-SWE-DOMSTOLSVERKET-2026"]["b0_mechanical"]["status"] == "verified"
    assert (
        by_id["ARC-SWE-DOMSTOLSVERKET-2026"]["b1_replay"]["status"] == "verified_supporting_receipt"
    )
    for inventory_id in (
        "ARC-GBR-EAW-2026Q1",
        "ARC-AUS-FCFCOA-202425",
        "ARC-BRA-CNJ-2026",
        "ARC-ZAF-JUD-202425",
        "ARC-USA-MN-MJB-PERF-2024",
    ):
        row = by_id[inventory_id]
        assert row["b0_mechanical"]["status"] == "not_evaluated"
        assert row["b1_replay"]["status"] == "pending"
        assert row["promotion_authorized"] is False
