from __future__ import annotations

import json
import shutil
from pathlib import Path

from gfjd.conductor import Conductor
from gfjd.validation import validate_project


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
    assert summary["current_gate"] == "G2"
    assert summary["programme_maturity"] == 1
    assert summary["self_assessed_maturity"] >= 1
    assert conductor.gate_result("G6").ready is False
    assert conductor.gate_result("G1").passed is True


def test_g1_acceptance_requires_named_roles_and_digest_bound_packet(project_root: Path) -> None:
    """Owner approval cannot bypass role or packet-integrity controls."""
    conductor = Conductor.load(project_root)
    result = conductor.gate_result("G1")
    assert result.passed is True
    assert result.ready is True

    # A synthetic accepted decision with an invalid binding must remain blocked.
    decision = conductor.gate_decisions["G1"]
    object.__setattr__(decision, "status", "accepted")
    object.__setattr__(decision, "decision_reference", "packet.md@not-a-sha")
    conductor._gate_cache.clear()
    blocked = conductor.gate_result("G1")
    assert "G1:decision-reference-invalid-digest" in blocked.work_failures
    assert blocked.passed is False


def test_tracks_cannot_be_archive_ready_while_external_gate_is_pending(
    project_root: Path,
) -> None:
    """Track completion is distinct from archive/publication authority."""
    conductor = Conductor.load(project_root)

    # The programme is deliberately still before final release. A track status
    # may report implementation progress, but no track may be treated as
    # archive eligible while the final release gate is not passed.
    assert conductor.gate_result("G6").passed is False
    statuses = [conductor.track_status(track_id) for track_id in conductor.tracks]
    assert statuses
    assert all(status["completed_work_items"] < status["work_items"] for status in statuses)


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


def test_g4_g5_blocker_plans_are_explicit_and_fail_closed(project_root: Path) -> None:
    """The documented beta/RC plans must retain options and promotion guards."""
    programme = (
        project_root / "docs/governance/programme-gate-resolution-plan-2026-08-02.md"
    ).read_text(encoding="utf-8")
    tracks = (project_root / "docs/governance/track-external-gate-plan-2026-08-02.md").read_text(
        encoding="utf-8"
    )
    for marker in (
        "## G4 beta blocker plan",
        "## G5 release-candidate blocker plan",
        "**Recommended**",
        "Promotion rule:",
        "adjudication_required",
        "evidence_missing",
        "no unresolved P0/P1",
    ):
        assert marker in programme
    for marker in (
        "## G4/G5 implementation sequence and track controls",
        "role-separated agent panels",
        "signed provenance",
        "tested custody/restore",
        "non-archive-eligible",
    ):
        assert marker in tracks


def test_g6_evidence_sourcing_plan_has_redundant_routes_and_fallbacks(
    project_root: Path,
) -> None:
    """G6 sourcing must specify redundancy without manufacturing authority."""
    plan = (project_root / "docs/governance/g6-evidence-sourcing-plan-2026-08-02.md").read_text(
        encoding="utf-8"
    )
    for marker in (
        "## Evidence lanes and redundant routes",
        "## Acquisition sequence",
        "primary and backup receipts",
        "adjudication_required",
        "narrower fallback (private, unsigned, metadata-only",
        "No route authorizes outbound contact",
        "A — staged dual-route sourcing (recommended)",
    ):
        assert marker in plan


def test_external_blocker_register_requires_assignment_and_freeze_metadata(
    project_root: Path, tmp_path: Path
) -> None:
    """Planning rows must be routed and dated without implying acceptance."""
    root = _copy_project(project_root, tmp_path / "repo")
    register = root / "docs/governance/external-evidence-blocker-register.csv"
    text = register.read_text(encoding="utf-8")
    text = text.replace(
        "international partnerships lead,assigned-pending-authority,2026-08-02",
        "international partnerships lead,,2026-08-02",
        1,
    )
    register.write_text(text, encoding="utf-8")
    report = validate_project(root)
    assert any(issue.code == "EXTERNAL_EVIDENCE_REGISTER_ASSIGNMENT" for issue in report.errors)

    # A malformed freeze date is also rejected; this is metadata hygiene only,
    # and never promotes a blocker to accepted.
    text = text.replace(
        "international partnerships lead,,2026-08-02",
        "international partnerships lead,assigned-pending-authority,not-a-date",
        1,
    )
    register.write_text(text, encoding="utf-8")
    report = validate_project(root)
    assert any(issue.code == "EXTERNAL_EVIDENCE_REGISTER_FREEZE_DATE" for issue in report.errors)


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
    object.__setattr__(conductor.risks["R02"], "status", "mitigating")
    conductor._gate_cache.clear()
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
            "E-PILOT-REVIEW",
            "accepted",
            reviewer_role="quality and assurance lead",
        )
    accepted = conductor.review_evidence(
        "E-PILOT-REVIEW",
        "accepted",
        reviewer_role="role-separated quality reviewer",
    )
    assert accepted.status == "accepted"
    assert len(accepted.sha256) == 64
    item = conductor.set_work_status(
        "WI-G2-04",
        "accepted",
        actor="repository owner",
    )
    assert item.status == "accepted"


def test_work_acceptance_requires_accepted_evidence(project_root: Path, tmp_path: Path) -> None:
    import pytest

    root = _copy_project(project_root, tmp_path / "repo")
    conductor = Conductor.load(root)
    with pytest.raises(ValueError, match="evidence not accepted"):
        conductor.set_work_status("WI-G2-04", "accepted", actor="reviewer")
