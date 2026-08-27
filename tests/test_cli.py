from __future__ import annotations

import json
import shutil
from pathlib import Path

from gfjd.cli import main


def test_validate_cli_json(project_root: Path, capsys) -> None:
    result = main(["--root", str(project_root), "validate", "--json"])
    payload = json.loads(capsys.readouterr().out)
    assert result == 0
    assert payload["ok"] is True


def test_gate_cli_reports_not_ready(project_root: Path, capsys) -> None:
    result = main(["--root", str(project_root), "conductor", "gate", "G6", "--json"])
    payload = json.loads(capsys.readouterr().out)
    assert result == 2
    assert payload["ready"] is False


def test_conductor_status_can_be_written(project_root: Path, tmp_path: Path) -> None:
    output = tmp_path / "status.md"
    result = main(
        [
            "--root",
            str(project_root),
            "conductor",
            "status",
            "--write",
            str(output),
        ]
    )
    assert result == 0
    assert "Generated programme status" in output.read_text(encoding="utf-8")


def test_conductor_graph_and_next_commands(project_root: Path, tmp_path: Path, capsys) -> None:
    graph_path = tmp_path / "graph.mmd"
    assert (
        main(
            [
                "--root",
                str(project_root),
                "conductor",
                "graph",
                "--write",
                str(graph_path),
            ]
        )
        == 0
    )
    capsys.readouterr()
    assert graph_path.read_text(encoding="utf-8").startswith("flowchart LR")
    assert main(["--root", str(project_root), "conductor", "next", "--limit", "3", "--json"]) == 0
    actions = json.loads(capsys.readouterr().out)
    assert len(actions) <= 3
    assert all("work_item_id" in action for action in actions)


def test_security_cli_passes(project_root: Path, capsys) -> None:
    result = main(["--root", str(project_root), "security", "--json"])
    payload = json.loads(capsys.readouterr().out)
    assert result == 0
    assert payload["counts"]["errors"] == 0


def test_public_archive_cli_scan_and_verify(project_root: Path, tmp_path: Path, capsys) -> None:
    root = tmp_path / "repo"
    (root / "config").mkdir(parents=True)
    shutil.copyfile(project_root / "config/project.toml", root / "config/project.toml")
    inventory = root / "inventory.csv"
    inventory.write_text(
        "inventory_id,payload_path,sha256\nARC-1,missing.pdf," + "0" * 64 + "\n",
        encoding="utf-8",
    )
    receipt = root / "missing-local-receipt.json"
    result = main(
        [
            "--root",
            str(root),
            "archive",
            "scan",
            "--inventory",
            "inventory.csv",
            "--output",
            str(receipt),
        ]
    )
    assert result == 1
    assert json.loads(capsys.readouterr().out)["status"] == "fail"
    assert main(["--root", str(root), "archive", "verify", str(receipt)]) == 0
    assert "verified" in capsys.readouterr().out


def test_public_archive_cli_verifies_custody(project_root: Path, capsys) -> None:
    result = main(
        [
            "--root",
            str(project_root),
            "archive",
            "verify-custody",
            "data/preservation/public_b0_custody_20260827.json",
        ]
    )
    assert result == 0
    assert "verified" in capsys.readouterr().out


def test_medallion_layer_cli_is_fail_closed(project_root: Path, tmp_path: Path, capsys) -> None:
    record = tmp_path / "b0.json"
    record.write_text(
        json.dumps(
            {
                "contract_version": "gfjd-medallion-layers-v1",
                "object_id": "OBJ-001",
                "layer": "b0",
                "previous_layer": None,
                "lifecycle_state": "active",
                "evidence": {
                    "source_edition_id": "ED-001",
                    "content_sha256": "a" * 64,
                    "content_blake3": "b" * 64,
                    "size_bytes": 1,
                    "media_type": "application/pdf",
                    "capture_receipt_sha256": "c" * 64,
                    "safety_receipt_sha256": "d" * 64,
                    "custody_receipt_sha256": "e" * 64,
                },
            }
        ),
        encoding="utf-8",
    )
    command = [
        "--root",
        str(project_root),
        "pipeline",
        "verify-layer",
        "--record",
        str(record),
    ]
    assert main(command) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "pass"
    payload = json.loads(record.read_text(encoding="utf-8"))
    del payload["evidence"]["safety_receipt_sha256"]
    record.write_text(json.dumps(payload), encoding="utf-8")
    assert main(command) == 1
    assert "missing safety_receipt_sha256" in capsys.readouterr().out
