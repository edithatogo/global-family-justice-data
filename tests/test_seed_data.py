from __future__ import annotations

from pathlib import Path

from gfjd.validate import validate


def test_compatibility_validator_returns_no_errors(project_root: Path) -> None:
    assert validate(project_root) == []
