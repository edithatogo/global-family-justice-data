from __future__ import annotations

import json
from pathlib import Path

from gfjd.cli import main
from gfjd.contract_lock import verify_contract_lock
from gfjd.project import load_project


def test_public_contract_lock_is_current(project_root: Path) -> None:
    report = verify_contract_lock(load_project(project_root))
    assert report.error_count == 0, report.render_text()


def test_version_cli_reports_synchronised_versions(project_root: Path, capsys) -> None:
    result = main(["--root", str(project_root), "version", "--json"])
    payload = json.loads(capsys.readouterr().out)
    assert result == 0
    assert payload["software_version"] == "0.6.0a2"
    assert payload["project_version"] == "0.6.0-alpha.2"


def test_ci_policy_cli_passes(project_root: Path, capsys) -> None:
    result = main(["--root", str(project_root), "policy", "ci", "--json"])
    payload = json.loads(capsys.readouterr().out)
    assert result == 0
    assert payload["error_count"] == 0
