"""Synthetic rehearsal recomputation tests, with no source/provider access."""

import json
import runpy
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/rehearse_medallion_lineage.py"


def test_report_is_deterministic_and_fictional() -> None:
    script = runpy.run_path(str(SCRIPT))
    report = script["build_report"]()
    assert report == script["build_report"]()
    assert report["synthetic"] is True
    assert report["current_remote_custody_verified"] is False
    assert all(value is False for value in report["authority"].values())
    assert report["entries"][0]["pipeline"]["silver"]["rows"][0]["value"] == "0007"
    assert report["entries"][1]["pipeline"]["silver"]["rows"][0]["value"] == "0009"
    assert report["history"]["history"]["event_count"] == 2
    assert (
        report["append_checkpoint"]["previous_entries_sha256"]
        != report["history"]["entries_sha256"]
    )
    assert report["queries"]["before_correction"]["rows"][0]["value"] == "0007"
    assert report["queries"]["after_correction"]["rows"][0]["value"] == "0009"


def test_cli_roundtrip_and_modified_report_rejected(tmp_path: Path) -> None:
    script = runpy.run_path(str(SCRIPT))
    output = tmp_path / "fictional-report.json"
    assert script["main"](["--output", str(output)]) == 0
    assert script["main"](["--verify", str(output)]) == 0
    original = output.read_bytes()
    report = json.loads(original)
    report["entries"][1]["pipeline"]["silver"]["rows"][0]["value"] = "9999"
    output.write_text(json.dumps(report))
    assert script["main"](["--verify", str(output)]) == 1
    output.write_bytes(original)
    assert script["main"](["--verify", str(output)]) == 0


def test_deterministic_workbook_has_real_changed_cell() -> None:
    script = runpy.run_path(str(SCRIPT))
    first = script["fictional_workbook"]("0007")
    assert first == script["fictional_workbook"]("0007")
    assert first != script["fictional_workbook"]("0009")
    with pytest.raises(ValueError):
        script["fictional_workbook"]("unreviewed value")


def test_forged_self_hash_cannot_replace_recomputation(tmp_path: Path) -> None:
    script = runpy.run_path(str(SCRIPT))
    report = script["build_report"]()
    report["synthetic"] = False
    del report["report_sha256"]
    report["report_sha256"] = script["sha"](script["canonical"](report))
    output = tmp_path / "fictional-forgery.json"
    output.write_bytes(script["canonical"](report) + b"\n")
    assert script["main"](["--verify", str(output)]) == 1


@pytest.mark.parametrize(
    "raw",
    [
        b'{"synthetic":true,"synthetic":false}',
        b'{"value":NaN}',
        b'{"value":Infinity}',
        b"x" * (1024 * 1024),
    ],
)
def test_verification_rejects_duplicate_nonfinite_and_excess_bytes(
    tmp_path: Path, raw: bytes
) -> None:
    script = runpy.run_path(str(SCRIPT))
    output = tmp_path / "fictional-invalid-report.json"
    output.write_bytes(raw)
    assert script["main"](["--verify", str(output)]) == 1
