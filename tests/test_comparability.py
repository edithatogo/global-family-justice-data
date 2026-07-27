from __future__ import annotations

import shutil
from pathlib import Path

from gfjd.comparability import build_comparability_audit, verify_comparability_audit
from gfjd.io import read_csv, write_csv

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
                "*.egg-info",
            ),
        )
    )


def test_comparability_audit_surfaces_methods_adjudication_queue(
    project_root: Path, tmp_path: Path
) -> None:
    root = _copy_project(project_root, tmp_path / "repo")
    first = eligible_observation()
    second = eligible_observation(
        {
            "observation_id": "OBS_TEST_0002",
            "jurisdiction_id": "NZL",
            "source_id": "NZL-MOJ-RESEARCH-DATA",
            "source_edition_id": "ED-NZL-MOJ-2025",
            "extraction_id": "EXT-NZL-2025-001",
            "transformation_rule_id": "MAP-NZL-2025-001",
            "review_id": "REV-NZL-2025-001",
        }
    )
    fragmented = eligible_observation(
        {
            "observation_id": "OBS_TEST_0003",
            "jurisdiction_id": "NZL",
            "source_id": "NZL-MOJ-RESEARCH-DATA",
            "source_edition_id": "ED-NZL-MOJ-2025",
            "extraction_id": "EXT-NZL-2025-002",
            "transformation_rule_id": "MAP-NZL-2025-002",
            "review_id": "REV-NZL-2025-002",
            "cohort_basis": "filed matters",
        }
    )
    input_path = root / "data/gold/pilot/observations.csv"
    write_csv(input_path, observation_headers(root), [first, second, fragmented])

    result = build_comparability_audit(
        root,
        root / "build/comparability",
        input_patterns=["data/gold/pilot/observations.csv"],
    )

    assert result.cross_jurisdiction_candidate_count == 1
    _, issues = read_csv(result.issues_path)
    assert {row["code"] for row in issues} >= {
        "CANDIDATE_REQUIRES_METHODS_REVIEW",
        "SERIES_FRAGMENTED_BY_DEFINITION",
    }
    assert verify_comparability_audit(result.output_dir, project_or_root=root) == []


def test_comparability_verifier_rejects_tampered_adjudication_queue(
    project_root: Path, tmp_path: Path
) -> None:
    root = _copy_project(project_root, tmp_path / "repo")
    input_path = root / "data/gold/pilot/observations.csv"
    write_csv(input_path, observation_headers(root), [eligible_observation()])
    result = build_comparability_audit(
        root,
        root / "build/comparability",
        input_patterns=["data/gold/pilot/observations.csv"],
    )

    result.issues_path.write_text("tampered\n", encoding="utf-8")

    assert "Comparability artifact checksum mismatch: comparability-issues.csv" in (
        verify_comparability_audit(result.output_dir, project_or_root=root)
    )
