from __future__ import annotations

import json
import shutil
from pathlib import Path

from gfjd.conductor import Conductor


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


def test_conductor_configuration_is_valid(project_root: Path) -> None:
    conductor = Conductor.load(project_root)
    report = conductor.validate()
    assert report.errors == [], "\n".join(str(issue) for issue in report.errors)
    assert len(conductor.tracks) == 10
    assert len(conductor.work_items) >= 55
    assert len(conductor.gates) == 6
    assert len(conductor.evidence) >= len(conductor.work_items)


def test_conductor_reports_honest_current_state(project_root: Path) -> None:
    conductor = Conductor.load(project_root)
    summary = conductor.summary()
    assert summary["current_release"] == "0.6.0-alpha.2"
    assert summary["target_release"] == "1.0.0"
    assert summary["current_gate"] == "G1"
    assert summary["programme_maturity"] == 0
    assert summary["self_assessed_maturity"] >= 1
    assert conductor.gate_result("G6").ready is False
    assert conductor.gate_result("G1").passed is False


def test_next_actions_have_satisfied_dependencies(project_root: Path) -> None:
    conductor = Conductor.load(project_root)
    actions = conductor.next_actions(limit=20)
    assert actions
    assert all(conductor.dependencies_satisfied(item) for item in actions)


def test_topological_order_respects_dependencies(project_root: Path) -> None:
    conductor = Conductor.load(project_root)
    order = conductor.topological_work_items()
    positions = {work_id: index for index, work_id in enumerate(order)}
    for work_id, item in conductor.work_items.items():
        for dependency in item.dependency_ids:
            assert positions[dependency] < positions[work_id]


def test_generated_status_contains_gate_and_track_tables(project_root: Path) -> None:
    output = Conductor.load(project_root).render_status_markdown()
    assert "## Gate readiness" in output
    assert "## Track maturity" in output
    assert "## Evidence-assured maturity" in output
    assert "G6" in output
    assert "T9" in output


def test_controlled_mutation_is_audited(project_root: Path, tmp_path: Path) -> None:
    root = _copy_project(project_root, tmp_path / "repo")
    conductor = Conductor.load(root)
    updated = conductor.update_risk(
        "R01",
        actor="test assurance lead",
        status="mitigating",
        notes="Test review event",
    )
    assert updated.notes == "Test review event"
    lines = (root / "programme/audit-log.jsonl").read_text(encoding="utf-8").splitlines()
    event = json.loads(lines[-1])
    assert event["event_type"] == "risk_updated"
    assert event["actor"] == "test assurance lead"
    assert event["record_key"] == {"risk_id": "R01"}


def test_accountably_accepted_risk_no_longer_blocks_gate(
    project_root: Path, tmp_path: Path
) -> None:
    root = _copy_project(project_root, tmp_path / "repo")
    conductor = Conductor.load(root)
    assert "R02" in conductor.gate_result("G1").risk_failures

    conductor.update_risk(
        "R02",
        actor="accountable risk authority",
        status="accepted",
        notes="Fixed review record supplied for test",
    )

    assert "R02" not in conductor.gate_result("G1").risk_failures
    assert "R02" in conductor.gate_result("G5").risk_failures


def test_evidence_review_enforces_independence_and_unlocks_work_acceptance(
    project_root: Path, tmp_path: Path
) -> None:
    import pytest

    root = _copy_project(project_root, tmp_path / "repo")
    conductor = Conductor.load(root)
    with pytest.raises(ValueError, match="independent"):
        conductor.review_evidence(
            "E-CONDUCTOR-BASELINE",
            "accepted",
            reviewer_role="technical lead",
        )
    accepted = conductor.review_evidence(
        "E-CONDUCTOR-BASELINE",
        "accepted",
        reviewer_role="independent engineering reviewer",
    )
    assert accepted.status == "accepted"
    assert len(accepted.sha256) == 64
    conductor.set_work_status(
        "WI-G1-07",
        "in_review",
        actor="technical lead",
        note="Submitted for acceptance",
    )
    item = conductor.set_work_status(
        "WI-G1-07",
        "accepted",
        actor="independent engineering reviewer",
    )
    assert item.status == "accepted"


def test_invalid_work_transition_is_rejected(project_root: Path, tmp_path: Path) -> None:
    import pytest

    root = _copy_project(project_root, tmp_path / "repo")
    conductor = Conductor.load(root)
    with pytest.raises(ValueError, match="Invalid work transition"):
        conductor.set_work_status("WI-G2-02", "accepted", actor="reviewer")
