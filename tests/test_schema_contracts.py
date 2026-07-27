from __future__ import annotations

from pathlib import Path

from gfjd.project import load_project
from gfjd.reporting import Report
from gfjd.schema_validation import load_contracts, validate_contracts


def test_all_configured_contracts_and_seed_rows_validate(project_root: Path) -> None:
    project = load_project(project_root)
    report = Report("contracts")
    tables = validate_contracts(project, report)
    assert report.errors == [], "\n".join(str(issue) for issue in report.errors)
    assert len(load_contracts(project)) == 15
    assert len(tables) >= 10
    assert sum(len(table.typed_rows) for table in tables) >= 80
