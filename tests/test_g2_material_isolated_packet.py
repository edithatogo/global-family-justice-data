from __future__ import annotations

import hashlib
import json
from pathlib import Path

from gfjd.g2_run_preflight import validate_g2_run_identifiers

RUN = Path("data/methods/g2/G2PKT-MATERIAL-ISOLATED-20260826-01")


def _read(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_isolated_packet_identifiers_and_bindings(project_root: Path) -> None:
    packet = _read(project_root / RUN / "packet.json")
    validate_g2_run_identifiers(
        project_root,
        packet_id=str(packet["packet_id"]),
        comparison_id=str(packet["comparison_id"]),
    )
    for key in (
        "owner_direction",
        "predecessor_terminal",
        "contract",
        "isolation_plan",
        "row_schema",
    ):
        binding = packet[key]
        assert isinstance(binding, dict)
        assert _sha256(project_root / str(binding["path"])) == binding["sha256"]
    bundles = packet["role_bundles"]
    assert isinstance(bundles, list)
    for binding in bundles:
        assert _sha256(project_root / str(binding["path"])) == binding["sha256"]


def test_isolation_plan_contains_only_explicit_role_inputs(project_root: Path) -> None:
    plan = _read(project_root / RUN / "isolation-plan.json")
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


def test_contract_retains_thresholds_and_owner_checkpoint(project_root: Path) -> None:
    contract = _read(project_root / RUN / "contract.json")
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
