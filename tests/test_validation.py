from __future__ import annotations

import csv
import shutil
from datetime import date
from pathlib import Path

from jsonschema import Draft202012Validator

from gfjd.io import read_json, write_csv
from gfjd.validation import validate_repository

from .helpers import eligible_observation, observation_headers


def _copy_project(project_root: Path, destination: Path) -> Path:
    return Path(
        shutil.copytree(
            project_root,
            destination,
            ignore=shutil.ignore_patterns(
                ".git",
                ".mypy_cache",
                ".pytest_cache",
                ".ruff_cache",
                ".tox",
                ".venv",
                "__pycache__",
                "build",
                "dist",
            ),
        )
    )


def test_all_json_schemas_are_valid(project_root: Path) -> None:
    for path in sorted((project_root / "schemas").glob("*.schema.json")):
        Draft202012Validator.check_schema(read_json(path))


def test_repository_has_no_validation_errors(project_root: Path) -> None:
    report = validate_repository(project_root, today=date(2026, 8, 15))
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


def test_timeliness_observation_requires_complete_clock_and_denominator(
    project_root: Path, tmp_path: Path
) -> None:
    root = _copy_project(project_root, tmp_path / "repo")
    rows = [
        eligible_observation({"stage_start": "", "observation_id": "OBS_TEST_0002"}),
        eligible_observation({"stage_end": "", "observation_id": "OBS_TEST_0003"}),
        eligible_observation({"denominator_definition": "", "observation_id": "OBS_TEST_0004"}),
    ]
    write_csv(root / "data/gold/timeliness.csv", observation_headers(root), rows)

    report = validate_repository(root, today=date(2026, 7, 19))

    assert (
        sum(issue.code == "OBSERVATION_TIMELINESS_SEMANTICS_INCOMPLETE" for issue in report.errors)
        == 3
    )


def test_methods_contract_manifest_detects_dictionary_drift(
    project_root: Path, tmp_path: Path
) -> None:
    root = _copy_project(project_root, tmp_path / "repo")
    dictionary = root / "data/seed/indicator_dictionary.csv"
    dictionary.write_text(dictionary.read_text(encoding="utf-8") + "\n", encoding="utf-8")

    report = validate_repository(root, today=date(2026, 7, 19))

    assert any(issue.code == "METHODS_CONTRACT_ARTIFACT_DRIFT" for issue in report.errors)


def test_archive_inventory_rejects_malformed_sha256(project_root: Path, tmp_path: Path) -> None:
    root = _copy_project(project_root, tmp_path / "repo")
    inventory = root / "data/raw/archive_inventory.csv"
    with inventory.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
        headers = list(rows[0])
    rows[0]["sha256"] += "0"
    with inventory.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    report = validate_repository(root, today=date(2026, 8, 15))

    assert any(issue.code == "ARCHIVE_INVENTORY_SHA256_INVALID" for issue in report.errors)


def test_archive_inventory_accepts_verified_public_remote_custody(
    project_root: Path, tmp_path: Path
) -> None:
    root = _copy_project(project_root, tmp_path / "repo")
    shutil.rmtree(root / "data/raw/files", ignore_errors=True)

    report = validate_repository(root, today=date(2026, 8, 15))

    assert report.errors == []
    assert any(issue.code == "ARCHIVE_INVENTORY_PAYLOAD_PUBLIC_REMOTE" for issue in report.infos)
