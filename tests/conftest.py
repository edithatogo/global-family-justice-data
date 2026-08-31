from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

import pytest


@pytest.fixture(scope="session")
def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Assign stable tiers without requiring every test file to repeat markers."""

    property_terms = {
        "reject",
        "mismatch",
        "tamper",
        "invalid",
        "private_address",
        "credentials",
        "unreviewed",
        "unknown",
    }
    integration_files = {
        "test_acquisition.py",
        "test_bootstrap.py",
        "test_pipeline.py",
        "test_release.py",
        "test_federation_rehearsal.py",
    }
    for item in items:
        lowered = item.nodeid.lower()
        if any(term in lowered for term in property_terms):
            item.add_marker(pytest.mark.property)
        elif Path(str(item.fspath)).name in integration_files:
            item.add_marker(pytest.mark.integration)
        else:
            item.add_marker(pytest.mark.unit)


_TEST_TIMINGS: dict[str, dict[str, Any]] = {}
_SESSION_STARTED = 0.0


def pytest_sessionstart(session: pytest.Session) -> None:  # noqa: ARG001
    global _SESSION_STARTED
    _SESSION_STARTED = time.monotonic()


def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    if report.when != "call":
        return
    _TEST_TIMINGS[report.nodeid] = {
        "nodeid": report.nodeid,
        "duration_seconds": round(float(report.duration), 9),
        "outcome": report.outcome,
    }


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:  # noqa: ARG001
    destination = os.getenv("GFJD_TEST_TIMINGS", "").strip()
    if not destination:
        return
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "1.0",
        "exitstatus": exitstatus,
        "suite_duration_seconds": round(time.monotonic() - _SESSION_STARTED, 9),
        "test_count": len(_TEST_TIMINGS),
        "tests": {
            nodeid: value["duration_seconds"] for nodeid, value in sorted(_TEST_TIMINGS.items())
        },
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
