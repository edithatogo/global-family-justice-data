"""Fictional rehearsal exactness and rejection, never programme acceptance."""

import json
import runpy
from pathlib import Path


def test_rehearsal_recomputes_full_chain_and_failure(project_root: Path, tmp_path: Path) -> None:
    script = runpy.run_path(str(project_root / "scripts/rehearse_medallion_qualification.py"))
    report = script["build_report"]()
    assert report == script["build_report"]()
    assert report["synthetic"] is True
    assert all(value is False for value in report["authority"].values())
    positive = report["positive_mechanics_with_pending_authority"]
    assert (
        positive["coverage"][2]["mechanical_checks"]["history"]["full_replay"]["event_count"] == 2
    )
    assert positive["coverage"][4]["mechanical_checks"]["composition"]["object_count"] == 1
    negative = report["substitution_rejected_with_upstream_fixity_preserved"]
    assert negative["coverage"][0]["dimensions"]["fixity"] == "verified"
    assert negative["coverage"][3]["dimensions"]["reproducibility"] == "failed"
    output = tmp_path / "fictional.json"
    assert script["main"](["--output", str(output)]) == 0
    assert script["main"](["--verify", str(output)]) == 0
    recorded = json.loads(output.read_bytes())
    recorded["authority"]["gate_acceptance"] = True
    output.write_text(json.dumps(recorded))
    assert script["main"](["--verify", str(output)]) == 1


def test_rehearsal_missing_report_fails(project_root: Path, tmp_path: Path) -> None:
    script = runpy.run_path(str(project_root / "scripts/rehearse_medallion_qualification.py"))
    assert script["main"](["--verify", str(tmp_path / "absent.json")]) == 1
