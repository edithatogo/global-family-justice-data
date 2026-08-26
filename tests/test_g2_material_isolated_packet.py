from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from gfjd.g2_run_preflight import validate_g2_run_identifiers

RUNS = (
    Path("data/methods/g2/G2PKT-MATERIAL-ISOLATED-20260826-01"),
    Path("data/methods/g2/G2PKT-MATERIAL-ISOLATED-20260826-02"),
    Path("data/methods/g2/G2PKT-MATERIAL-ORCHESTRATED-20260826-01"),
)


def _read(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.mark.parametrize("run", RUNS)
def test_isolated_packet_identifiers_and_bindings(project_root: Path, run: Path) -> None:
    packet = _read(project_root / run / "packet.json")
    validate_g2_run_identifiers(
        project_root,
        packet_id=str(packet["packet_id"]),
        comparison_id=str(packet["comparison_id"]),
    )
    authority_key = "owner_direction" if "owner_direction" in packet else "owner_authorization"
    for key in (authority_key, "predecessor_terminal", "contract", "isolation_plan", "row_schema"):
        binding = packet[key]
        assert isinstance(binding, dict)
        assert _sha256(project_root / str(binding["path"])) == binding["sha256"]
    bundles = packet["role_bundles"]
    assert isinstance(bundles, list)
    for binding in bundles:
        assert _sha256(project_root / str(binding["path"])) == binding["sha256"]


@pytest.mark.parametrize("run", RUNS)
def test_isolation_plan_contains_only_explicit_role_inputs(project_root: Path, run: Path) -> None:
    plan = _read(project_root / run / "isolation-plan.json")
    roles = plan["roles"]
    assert isinstance(roles, list)
    assert [role["role"] for role in roles] == ["extractor_a", "extractor_b"]
    assert plan["policy"] == "explicit_allowlist_only"
    assert plan["shared_source_directory_access_by_extractors"] is False
    assert plan["predecessor_outputs_reused"] is False
    for role in roles:
        assert len(role["inputs"]) == 5
        assert len({item["target_name"] for item in role["inputs"]}) == 5
        assert all(item["source_path"].startswith("build/") for item in role["inputs"])


@pytest.mark.parametrize("run", RUNS)
def test_contract_retains_thresholds_and_owner_checkpoint(project_root: Path, run: Path) -> None:
    contract = _read(project_root / run / "contract.json")
    assert contract["thresholds"] == {
        "critical_concordance": 1.0,
        "overall_populated_field_concordance": 0.99,
        "exact_comparison": True,
        "fuzzy_matching": False,
        "critical_waiver": False,
    }
    assert contract["role_isolation"]["physical_allowlist_workspace"] is True
    assert contract["authority_limits"]["passing_run_requires_owner_adjudication"] is True
    assert contract["authority_limits"]["g2_passage"] is False


def test_cli_isolated_terminal_stop_is_fail_closed(project_root: Path) -> None:
    run = RUNS[1]
    packet = _read(project_root / run / "packet.json")
    terminal = _read(project_root / run / "terminal-stop.json")
    assert terminal["status"] == "terminal_failed_preflight"
    assert terminal["frozen_bindings"]["packet_sha256"] == _sha256(
        project_root / run / "packet.json"
    )
    assert (
        terminal["terminal_trigger"]["frozen_command"]
        != terminal["terminal_trigger"]["executed_command"]
    )
    assert terminal["observed_execution_state"]["comparison_started"] is False
    assert terminal["disposition"]["lineage_terminal"] is True
    assert terminal["disposition"]["g2_accepted_criteria"] == 9
    assert packet["authority_limits"]["g2_passage"] is False


def test_orchestrated_packet_prohibits_agent_preflight_commands(project_root: Path) -> None:
    run = RUNS[2]
    packet = _read(project_root / run / "packet.json")
    contract = _read(project_root / run / "contract.json")
    assert packet["workspace_preflight"]["orchestrator_only"] is True
    assert packet["workspace_preflight"]["agent_command_prohibited"] is True
    assert contract["role_isolation"]["orchestrator_verifies_before_delegation"] is True
    assert contract["role_isolation"]["agent_preflight_command_prohibited"] is True
    for name in ("extractor-a-bundle.json", "extractor-b-bundle.json"):
        assert _read(project_root / run / name)["agent_preflight_command"] is None


def test_orchestrated_terminal_result_preserves_failed_thresholds(project_root: Path) -> None:
    terminal = _read(project_root / RUNS[2] / "terminal-result.json")
    assert terminal["status"] == "terminal_failure_critical_discrepancy"
    assert terminal["metrics"]["critical_matches"] == 58
    assert terminal["metrics"]["critical_comparisons"] == 76
    assert terminal["metrics"]["critical_concordance"] < terminal["metrics"]["critical_threshold"]
    assert (
        terminal["metrics"]["overall_populated_concordance"]
        < terminal["metrics"]["overall_threshold"]
    )
    assert terminal["disposition"]["rerun_allowed"] is False
    assert terminal["disposition"]["g2_passed"] is False
