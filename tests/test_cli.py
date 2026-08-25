from __future__ import annotations

import json
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
