"""Deterministic fictional preparation does not establish remote custody."""

import runpy

from gfjd.medallion_qualification_inputs import canonical


def test_rehearsal_recomputes_and_verifies(project_root, tmp_path):
    script = runpy.run_path(str(project_root / "scripts/rehearse_medallion_restore.py"))
    report = script["build_report"]()
    assert report == script["build_report"]()
    assert report["complete_supplied_banks"]["offline_rebuild_verified"]
    assert not report["reproduced_blocked_qualification"]["offline_rebuild_verified"]
    assert report["missing_peer_rejected"]
    assert not any(report["authority"].values())
    path = tmp_path / "fictional.json"
    path.write_bytes(canonical(report) + b"\n")
    assert script["main"](["--verify", str(path)]) == 0
    path.write_bytes(b"{}")
    assert script["main"](["--verify", str(path)]) == 1
    assert script["main"](["--verify", str(tmp_path / "missing")]) == 1
