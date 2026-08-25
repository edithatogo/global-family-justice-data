from __future__ import annotations

import hashlib
import json
from pathlib import Path

from gfjd.g2_run_preflight import validate_g2_run_identifiers

RUN = Path("data/methods/g2/G2PKT-MATERIAL-DISTINCT-20260826-01")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_material_distinct_packet_identifiers_and_bindings(project_root: Path) -> None:
    packet = json.loads((project_root / RUN / "packet.json").read_text(encoding="utf-8"))
    validate_g2_run_identifiers(
        project_root,
        packet_id=packet["packet_id"],
        comparison_id=packet["comparison_id"],
    )

    for binding_name in ("owner_decision", "preparation", "contract", "row_schema"):
        binding = packet[binding_name]
        assert _sha256(project_root / binding["path"]) == binding["sha256"]
    for binding in packet["role_bundles"]:
        assert _sha256(project_root / binding["path"]) == binding["sha256"]


def test_material_distinct_contract_is_exact_and_fail_closed(project_root: Path) -> None:
    contract = json.loads((project_root / RUN / "contract.json").read_text(encoding="utf-8"))
    assert len(contract["scope"]) == 4
    assert {row["source_format"] for row in contract["scope"]} == {
        "api_or_json",
        "spreadsheet",
        "html_or_dashboard",
        "pdf",
    }
    assert contract["thresholds"]["critical_concordance"] == 1.0
    assert contract["thresholds"]["overall_populated_field_concordance"] == 0.99
    assert contract["thresholds"]["fuzzy_matching"] is False
    assert contract["thresholds"]["critical_waiver"] is False
    assert contract["role_isolation"]["answer_bearing_locators_prohibited"] is True
    assert contract["authority_limits"]["g2_passage"] is False


def test_private_only_acquisition_is_not_redistribution_permission(project_root: Path) -> None:
    schema = json.loads(
        (project_root / "schemas/acquisition_manifest.schema.json").read_text(encoding="utf-8")
    )
    statuses = schema["properties"]["redistribution_status"]["enum"]
    assert "private_only" in statuses
    assert "allowed" in statuses
    assert statuses.index("private_only") != statuses.index("allowed")
