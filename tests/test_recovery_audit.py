"""Verify recovery evidence was reconciled without claiming an owner decision."""

import csv
import hashlib
import json
from pathlib import Path


def test_recovery_audit_matches_current_registered_receipts(project_root: Path) -> None:
    with (project_root / "programme/evidence_register.csv").open() as handle:
        rows = {row["evidence_id"]: row for row in csv.DictReader(handle)}
    events = [
        json.loads(line)
        for line in (project_root / "programme/audit-log.jsonl").read_text().splitlines()
    ]
    for key in ("E-G2-ODS-EXACT-RECOVERY-20260906", "E-G2-ODS-DURABLE-CUSTODY-20260906"):
        matching = [
            event
            for event in events
            if event.get("event_type") == "evidence_register_reconciled"
            and event["record_key"] == {"evidence_id": key}
        ]
        assert len(matching) == 1
        assert matching[0]["before"] is None
        assert matching[0]["after"]["evidence_id"] == rows[key]["evidence_id"]
        recorded = matching[0]["after"]
        assert (
            hashlib.sha256((project_root / recorded["path"]).read_bytes()).hexdigest()
            == (recorded["sha256"])
        )
        assert matching[0]["after"]["status"] == "in_review"
        assert matching[0]["before_commit"] == "09a4fd9cb053885c9d401663bfd1fd651bdfdc4e"
