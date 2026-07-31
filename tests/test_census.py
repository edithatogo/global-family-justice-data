from __future__ import annotations

import json
import shutil
from pathlib import Path

from gfjd.census import CensusError, build_census_readiness, verify_census_readiness
from gfjd.io import read_csv, write_csv


def _copy(root: Path, destination: Path) -> Path:
    return Path(
        shutil.copytree(
            root,
            destination,
            ignore=shutil.ignore_patterns(".git", ".venv", "build", "__pycache__"),
        )
    )


def test_census_reports_missing_evidence_as_unresolved(project_root: Path, tmp_path: Path) -> None:
    root = _copy(project_root, tmp_path / "repo")
    result = build_census_readiness(root, root / "build/census")
    _, matrix = read_csv(result.matrix_path)
    assert result.ready_count == 0
    assert all(row["readiness_state"] == "unresolved" for row in matrix)
    assert verify_census_readiness(result.output_dir, project_or_root=root) == []


def test_census_resolves_mapping_review_by_institution_subject(
    project_root: Path, tmp_path: Path
) -> None:
    root = _copy(project_root, tmp_path / "repo")
    result = build_census_readiness(root, root / "build/census")
    _, gaps = read_csv(result.gaps_path)
    assert not any(row["gap_code"] == "REVIEW_LEDGER_UNREVIEWED" for row in gaps)


def test_census_rejects_duplicate_current_assessments(project_root: Path, tmp_path: Path) -> None:
    root = _copy(project_root, tmp_path / "repo")
    path = root / "data/seed/coverage_assessment_template.csv"
    headers, _ = read_csv(path)
    row = dict.fromkeys(headers, "")
    row.update(
        {
            "assessment_id": "ASSESS_AUS_01",
            "jurisdiction_id": "AUS",
            "assessed_at": "2026-07-27T00:00:00Z",
            "assessor_role": "analyst",
            "coverage_state": "partial",
            "official_source_state": "found",
            "negative_finding_state": "documented",
            "completeness_basis": "test",
            "next_review_due": "2026-08-01",
            "review_status": "reviewed",
            "evidence_path": "docs/x",
            "notes": "",
        }
    )
    write_csv(path, headers, [row, {**row, "assessment_id": "ASSESS_AUS_02"}])
    try:
        build_census_readiness(root, root / "build/census")
    except CensusError as exc:
        assert "More than one non-superseded" in str(exc)
    else:
        raise AssertionError("expected fail-closed duplicate assessment rejection")


def test_census_verifier_detects_tampering(project_root: Path, tmp_path: Path) -> None:
    root = _copy(project_root, tmp_path / "repo")
    result = build_census_readiness(root, root / "build/census")
    result.gaps_path.write_text("tampered\n", encoding="utf-8")
    assert "Census artifact checksum mismatch: census-gaps.csv" in verify_census_readiness(
        result.output_dir, project_or_root=root
    )


def test_census_verifier_rejects_summary_path_escape(project_root: Path, tmp_path: Path) -> None:
    root = _copy(project_root, tmp_path / "repo")
    result = build_census_readiness(root, root / "build/census")
    summary = json.loads(result.summary_path.read_text(encoding="utf-8"))
    summary["inputs"][0]["path"] = "../outside.csv"
    result.summary_path.write_text(json.dumps(summary), encoding="utf-8")
    assert "Unsafe census input path: ../outside.csv" in verify_census_readiness(
        result.output_dir, project_or_root=root
    )


def test_census_prefers_operational_inputs(project_root: Path, tmp_path: Path) -> None:
    root = _copy(project_root, tmp_path / "repo")
    census_dir = root / "data/census"
    census_dir.mkdir(exist_ok=True)
    universe_headers, _ = read_csv(root / "data/seed/jurisdiction_universe_template.csv")
    write_csv(
        census_dir / "jurisdiction_universe.csv",
        universe_headers,
        [
            {
                "universe_entry_id": "UNIVERSE_AUS",
                "jurisdiction_id": "AUS",
                "inclusion_status": "included",
                "inclusion_reason": "pilot",
                "search_priority": "critical",
                "owner_role": "analyst",
                "review_status": "reviewed",
                "notes": "",
            }
        ],
    )
    result = build_census_readiness(root, root / "build/census")
    _, matrix = read_csv(result.matrix_path)
    australia = next(row for row in matrix if row["jurisdiction_id"] == "AUS")
    assert australia["universe_state"] == "included"
    assert "UNIVERSE_ENTRY_MISSING" not in australia["gap_reason"]


def test_census_rejects_malformed_operational_record(project_root: Path, tmp_path: Path) -> None:
    root = _copy(project_root, tmp_path / "repo")
    path = root / "data/census/jurisdiction_universe.csv"
    headers, _ = read_csv(root / "data/seed/jurisdiction_universe_template.csv")
    write_csv(
        path,
        headers,
        [
            {
                "universe_entry_id": "BAD",
                "jurisdiction_id": "AUS",
                "inclusion_status": "invented",
                "inclusion_reason": "",
                "search_priority": "high",
                "owner_role": "analyst",
                "review_status": "draft",
                "notes": "",
            }
        ],
    )
    try:
        build_census_readiness(root, root / "build/census")
    except CensusError as exc:
        assert "Census input validation failed" in str(exc)
    else:
        raise AssertionError("expected schema validation failure")


def test_census_reports_orphan_operational_record(project_root: Path, tmp_path: Path) -> None:
    root = _copy(project_root, tmp_path / "repo")
    path = root / "data/census/jurisdiction_universe.csv"
    headers, _ = read_csv(root / "data/seed/jurisdiction_universe_template.csv")
    write_csv(
        path,
        headers,
        [
            {
                "universe_entry_id": "UNIVERSE_ORPHAN",
                "jurisdiction_id": "ZZZ",
                "inclusion_status": "included",
                "inclusion_reason": "test",
                "search_priority": "high",
                "owner_role": "analyst",
                "review_status": "reviewed",
                "notes": "",
            }
        ],
    )
    result = build_census_readiness(root, root / "build/census")
    _, gaps = read_csv(result.gaps_path)
    assert any(row["gap_code"] == "ORPHAN_CENSUS_RECORD" for row in gaps)
