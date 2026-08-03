import csv

from gfjd.resilience import _entry_set_sha256, verify_restore_receipt


def test_entry_set_digest_is_independent_of_filesystem_traversal_order() -> None:
    entries = [
        ("b" * 64, "data/seed/source_edition_template.csv"),
        ("a" * 64, "config/project.toml"),
    ]

    assert _entry_set_sha256(entries) == _entry_set_sha256(reversed(entries))


def test_restore_receipt_rejects_unlabelled_external_custody(project_root, tmp_path) -> None:
    receipt = project_root / "build" / "test-unlabelled-restore-receipt.json"
    receipt.parent.mkdir(parents=True, exist_ok=True)
    receipt.write_text(
        '{"archive_path":"build/backup/gfjd-critical-state.zip",'
        '"snapshot_path":"build/restore-rehearsal/snapshot",'
        '"custody_class":"independently-administered",'
        '"signature_status":"signed"}\n',
        encoding="utf-8",
    )

    errors = verify_restore_receipt(project_root, receipt)
    receipt.unlink()

    assert "Restore receipt custody_class must be local-rehearsal-only" in errors
    assert "Restore receipt signature_status must be unsigned" in errors


def test_external_operations_register_is_fail_closed(project_root) -> None:
    path = project_root / "docs/operations/external-operations-approval-register.csv"
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    assert {row["control_id"] for row in rows} == {
        "OPS-HOST",
        "OPS-CUSTODY",
        "OPS-SIGNING",
        "OPS-SUPPORT",
        "OPS-FUNDING",
    }
    assert all(row["status"] == "pending" for row in rows)
    assert all(row["required_evidence"] and row["contingency"] for row in rows)


def test_t6_t8_t9_handoff_templates_preserve_external_boundaries(project_root) -> None:
    """Templates must not be mistaken for accessibility, operations, or participation approval."""
    rehearsal = (project_root / "docs/templates/operations-rehearsal-receipt.md").read_text(
        encoding="utf-8"
    )
    assert "local-rehearsal-only" in rehearsal
    assert "signature status: `unsigned`" in rehearsal
    assert "live host established: **no**" in rehearsal

    operating_plan = (project_root / "docs/templates/operating-plan-12-month.md").read_text(
        encoding="utf-8"
    )
    assert "does not commit funding" in operating_plan
    assert "G5/G6 funding and operations gates remain pending" in operating_plan

    exceptions = project_root / "docs/templates/accessibility-exception-register.csv"
    assert exceptions.read_text(encoding="utf-8").startswith(
        "finding_id,candidate_digest,criterion"
    )
