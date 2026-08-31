"""Immutable fictional replay is not publicly executed lifecycle evidence."""

import runpy

from gfjd.medallion_qualification_inputs import canonical


def test_fictional_lifecycle_rehearsal(project_root, tmp_path):
    script = runpy.run_path(str(project_root / "scripts/rehearse_medallion_lifecycle.py"))
    report = script["build_report"]()
    assert report == script["build_report"]()
    assert len(report["all_operations"]["history"]) == 15
    assert len(report["implicit_withdrawal_backlog"]["declared_provider_backlog"]) == 2
    path = tmp_path / "fictional.json"
    path.write_bytes(canonical(report) + b"\n")
    assert script["main"](["--verify", str(path)]) == 0
    path.write_bytes(b"{}")
    assert script["main"](["--verify", str(path)]) == 1
    assert script["main"](["--verify", str(tmp_path / "missing")]) == 1
