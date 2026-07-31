from __future__ import annotations

from datetime import date
from pathlib import Path

from gfjd.governance import build_governance_pack, verify_governance_pack
from gfjd.io import read_json
from gfjd.project import load_project


def test_governance_pack_is_complete_and_fail_closed(tmp_path: Path) -> None:
    project = load_project()
    result = build_governance_pack(project, tmp_path, as_of=date(2026, 7, 27))

    assert result.gates == 6
    assert verify_governance_pack(tmp_path) == []
    payload = read_json(tmp_path / "governance-pack.json")
    assert payload["governance_state"] == "pending_external_acceptance"
    assert payload["release_decision"]["decision"] == "pending"
    assert all(item["name"] is None for item in payload["release_decision"]["signatories"])
    assert {item["gate_id"] for item in payload["gates"]} == {
        "G1",
        "G2",
        "G3",
        "G4",
        "G5",
        "G6",
    }
    for gate_id in ("G1", "G2", "G3", "G4", "G5", "G6"):
        gate_dir = tmp_path / "gate-packs" / gate_id
        assert {path.name for path in gate_dir.iterdir()} == {
            "MANIFEST.sha256",
            "criterion-matrix.csv",
            "evidence-index.csv",
            "gate-pack.json",
        }


def test_governance_pack_detects_tampering(tmp_path: Path) -> None:
    project = load_project()
    build_governance_pack(project, tmp_path, as_of=date(2026, 7, 27))
    (tmp_path / "release-decision-template.json").write_text("{}\n", encoding="utf-8")

    assert verify_governance_pack(tmp_path) == [
        "checksum mismatch: release-decision-template.json",
        "release decision artifacts disagree",
    ]


def test_governance_pack_rejects_manifest_path_injection(tmp_path: Path) -> None:
    project = load_project()
    build_governance_pack(project, tmp_path, as_of=date(2026, 7, 27))
    (tmp_path / "manifest.json").write_text('{"../../outside":"untrusted"}\n', encoding="utf-8")

    assert verify_governance_pack(tmp_path) == ["manifest artifact set is invalid"]


def test_governance_pack_reports_malformed_json(tmp_path: Path) -> None:
    project = load_project()
    build_governance_pack(project, tmp_path, as_of=date(2026, 7, 27))
    (tmp_path / "manifest.json").write_text("{", encoding="utf-8")

    assert verify_governance_pack(tmp_path)[0].startswith("invalid manifest.json:")


def test_governance_pack_detects_per_gate_tampering(tmp_path: Path) -> None:
    project = load_project()
    build_governance_pack(project, tmp_path, as_of=date(2026, 7, 27))
    path = tmp_path / "gate-packs" / "G1" / "evidence-index.csv"
    path.write_text("tampered\n", encoding="utf-8")

    assert verify_governance_pack(tmp_path) == ["G1: checksum mismatch: evidence-index.csv"]
