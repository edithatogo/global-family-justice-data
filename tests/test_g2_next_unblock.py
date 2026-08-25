from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

BUNDLE = Path("data/methods/g2/G2NEXT-UNBLOCK-20260824-01")
BLIND_RUN = Path("data/methods/g2/G2BLIND-KNOWN-EDITION-20260825-01")


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


def test_authorized_blind_run_is_frozen_and_bounded(project_root: Path) -> None:
    run_dir = project_root / BLIND_RUN
    packet = json.loads((run_dir / "packet.json").read_text())
    contract = json.loads((run_dir / "contract.json").read_text())
    schema = json.loads((run_dir / "row.schema.json").read_text())

    Draft202012Validator.check_schema(schema)
    assert packet["status"] == "frozen_authorized_ready_for_extraction"
    assert packet["source_count"] == 4
    assert packet["authority_limits"]["network_access"] is False
    assert packet["authority_limits"]["publication"] is False
    assert packet["authority_limits"]["g2_passage"] is False
    assert packet["authority_limits"]["passing_run_requires_owner_adjudication"] is True

    assert len(contract["scope"]) == 4
    assert contract["thresholds"]["critical_concordance"] == 1.0
    assert contract["thresholds"]["overall_populated_field_concordance"] == 0.99
    assert contract["thresholds"]["fuzzy_matching"] is False
    assert contract["thresholds"]["critical_waiver"] is False
    assert contract["role_isolation"]["prior_outputs_prohibited"] is True
    assert contract["role_isolation"]["seal_before_compare"] is True

    for binding_name in ("owner_decision", "proposal", "contract", "row_schema"):
        binding = packet[binding_name]
        path = project_root / binding["path"]
        assert path.is_file()
        assert _sha256(path) == binding["sha256"]
    for binding in packet["role_bundles"]:
        path = project_root / binding["path"]
        assert path.is_file()
        assert _sha256(path) == binding["sha256"]

    execution = json.loads((run_dir / "execution-authority.json").read_text())
    manifest = project_root / execution["design_manifest"]["path"]
    assert _sha256(manifest) == execution["design_manifest"]["sha256"]
    assert execution["attestation"]["prior_output_created"] is False
    assert execution["attestation"]["expected_values_added"] is False
    assert execution["attestation"]["answer_bearing_locators_added"] is False


def test_blind_run_source_hashes_match_controlled_local_artifacts(project_root: Path) -> None:
    contract = json.loads((project_root / BLIND_RUN / "contract.json").read_text())
    sources = [(source, project_root / source["source_path"]) for source in contract["scope"]]
    # Content-bearing controlled artifacts are intentionally absent from clean
    # public clones. If the local controlled store is present, require the
    # complete scope and exact bindings rather than accepting a partial copy.
    if not any(path.is_file() for _, path in sources):
        return
    assert all(path.is_file() for _, path in sources)
    for source, path in sources:
        assert _sha256(path) == source["source_sha256"]


def test_terminal_blind_run_stop_is_fail_closed(project_root: Path) -> None:
    stop = json.loads((project_root / BLIND_RUN / "terminal-stop.json").read_text())
    assert stop["status"] == "terminal_failed"
    disposition = stop["comparison_disposition"]
    assert disposition["difference_count"] == 5
    assert disposition["critical_difference_count"] == 5
    assert disposition["threshold_passed"] is None
    assert disposition["critical_concordance"] is None
    assert disposition["overall_populated_field_concordance"] is None
    assert stop["terminal_controls"] == {
        "rerun_authorized": False,
        "repair_authorized": False,
        "normalization_authorized": False,
        "waiver_authorized": False,
        "fuzzy_matching_authorized": False,
        "retrospective_promotion_authorized": False,
    }
    assert stop["conductor_effect"]["g2_c04"] == "in_review"
    assert stop["conductor_effect"]["g2_c07"] == "in_review"
    assert stop["authority_limits"]["publication"] is False
    assert stop["authority_limits"]["g2_passage"] is False
