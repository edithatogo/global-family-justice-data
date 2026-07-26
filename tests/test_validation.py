from __future__ import annotations

import csv
import shutil
from datetime import date
from pathlib import Path

from jsonschema import Draft202012Validator

from gfjd.io import read_json
from gfjd.validation import validate_repository


def _copy_project(project_root: Path, destination: Path) -> Path:
    return Path(
        shutil.copytree(
            project_root,
            destination,
            ignore=shutil.ignore_patterns(
                ".git", ".pytest_cache", "__pycache__", "build", "dist"
            ),
        )
    )


def test_all_json_schemas_are_valid(project_root: Path) -> None:
    for path in sorted((project_root / "schemas").glob("*.schema.json")):
        Draft202012Validator.check_schema(read_json(path))


def test_repository_has_no_validation_errors(project_root: Path) -> None:
    report = validate_repository(project_root, today=date(2026, 7, 19))
    assert report.errors == [], "\n".join(str(issue) for issue in report.errors)
    assert report.checks_run >= 15


def test_unknown_source_jurisdiction_is_detected(project_root: Path, tmp_path: Path) -> None:
    root = _copy_project(project_root, tmp_path / "repo")
    path = root / "data/seed/source_register.csv"
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
        headers = list(rows[0])
    rows[0]["jurisdiction_id"] = "ZZZ"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    report = validate_repository(root, today=date(2026, 7, 19))
    assert any(issue.code == "SOURCE_JURISDICTION_UNKNOWN" for issue in report.errors)


def test_future_source_verification_is_detected(project_root: Path) -> None:
    report = validate_repository(project_root, today=date(2026, 7, 18))
    assert any(issue.code == "SOURCE_VERIFIED_IN_FUTURE" for issue in report.errors)
