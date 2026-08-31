"""Calendar defaults must not depend on the operator's local timezone."""

from dataclasses import replace
from datetime import UTC, date, datetime
from pathlib import Path

import gfjd.conductor as conductor_module
import gfjd.validation as validation_module


class LocalTomorrow(date):
    @classmethod
    def today(cls) -> date:
        raise AssertionError("local calendar must not determine governance dates")


class FrozenUTC(datetime):
    @classmethod
    def now(cls, tz=None):
        assert tz is UTC
        return datetime(2026, 8, 31, 14, 30, tzinfo=UTC)


def test_conductor_default_uses_utc(project_root: Path, monkeypatch) -> None:
    monkeypatch.setattr(conductor_module, "date", LocalTomorrow)
    monkeypatch.setattr(conductor_module, "datetime", FrozenUTC)
    conductor = conductor_module.Conductor.load(project_root)
    assert conductor.validate().to_dict() == conductor.validate(as_of=date(2026, 8, 31)).to_dict()
    conductor.status_payload()


def test_project_default_uses_utc(project_root: Path, monkeypatch) -> None:
    monkeypatch.setattr(validation_module, "date", LocalTomorrow)
    monkeypatch.setattr(validation_module, "datetime", FrozenUTC, raising=False)
    result = validation_module.validate_project(project_root, include_security=False)
    assert result.metrics["as_of"] == "2026-08-31"


def test_explicit_next_day_keeps_overdue_warnings(project_root: Path) -> None:
    conductor = conductor_module.Conductor.load(project_root)
    conductor.risks["R01"] = replace(
        conductor.risks["R01"], status="open", next_review_on=date(2026, 8, 31)
    )
    report = conductor.validate(as_of=date(2026, 9, 1))
    assert any(issue.code == "RISK_REVIEW_OVERDUE" for issue in report.issues)
