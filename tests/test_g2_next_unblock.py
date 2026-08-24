from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

BUNDLE = Path("data/methods/g2/G2NEXT-UNBLOCK-20260824-01")


def _load(project_root: Path, name: str) -> dict[str, Any]:
    return json.loads((project_root / BUNDLE / name).read_text())


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_repository_bindings_are_current(project_root: Path) -> None:
    for name in (
        "cohort-acquisition.json",
        "methods-adjudication.json",
        "rights-security-assessment.json",
        "c03-clean-build-acceptance.json",
    ):
        record = _load(project_root, name)
        bindings = record.get("input_bindings", record.get("bindings", []))
        for binding in bindings:
            path = project_root / binding["path"]
            assert path.is_file(), binding["path"]
            assert _sha256(path) == binding["sha256"], binding["path"]


def test_cohort_and_methods_claims_remain_bounded(project_root: Path) -> None:
    cohort = _load(project_root, "cohort-acquisition.json")
    assert cohort["scope"]["global_representativeness"] is False
    assert cohort["scope"]["route_count"] == 4
    assert {route["route_type"] for route in cohort["routes"]} == {
        "api",
        "spreadsheet",
        "html_dashboard",
        "pdf_manual",
    }

    methods = _load(project_root, "methods-adjudication.json")
    assert len(methods["records"]) == 4
    assert all(record["comparison_eligible"] is False for record in methods["records"])
    assert methods["status"] == "prepared_for_owner_decision"


def test_rights_and_blind_execution_remain_fail_closed(project_root: Path) -> None:
    rights = _load(project_root, "rights-security-assessment.json")
    assert rights["summary"]["unresolved_critical_finding_count"] == 0
    assert rights["summary"]["redistribution_cleared"] is False
    assert rights["common_controls"]["publication_authorized"] is False
    assert all(edition["critical_finding_count"] == 0 for edition in rights["editions"])

    blind = _load(project_root, "blind-execution-proposal.json")
    assert blind["status"] == "pending_owner_policy_decision"
    assert blind["design"]["agent_blinded"] is True
    assert blind["design"]["project_unseen"] is False
    assert blind["resource_estimate"]["network_or_new_source_access"] is False
    assert blind["thresholds"]["critical_fields"] == "100_percent_exact"
