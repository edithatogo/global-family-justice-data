from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

import gfjd.g2_material_distinct as material_distinct
from gfjd.g2_material_distinct import (
    DESIGN,
    EXPOSURE_LEDGER,
    MANIFEST,
    OWNER_DECISION,
    SOURCE_REGISTER,
    build_material_distinct_artifacts,
    verify_material_distinct_frame,
    write_material_distinct_artifacts,
)

ROOT = Path(__file__).resolve().parents[1]


def _write_inputs(root: Path, ledger: object, source_register: str) -> None:
    ledger_path = root / EXPOSURE_LEDGER
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    ledger_path.write_text(json.dumps(ledger), encoding="utf-8")
    register_path = root / SOURCE_REGISTER
    register_path.parent.mkdir(parents=True, exist_ok=True)
    register_path.write_text(source_register, encoding="utf-8")
    decision_path = root / OWNER_DECISION
    decision_path.parent.mkdir(parents=True, exist_ok=True)
    decision_path.write_text("owner decision\n", encoding="utf-8")


def test_materially_distinct_preparation_is_reproducible_and_stopped() -> None:
    assert verify_material_distinct_frame(ROOT) == []
    artifacts = build_material_distinct_artifacts(ROOT)
    assert artifacts["candidate_frame"]["candidate_count"] == 0
    assert artifacts["candidate_frame"]["rejected_count"] == 20
    assert {row["reason_code"] for row in artifacts["candidate_frame"]["rejections"]} == {
        "CUMULATIVE_EXPOSURE_OVERLAP"
    }


def test_materially_distinct_artifacts_validate_against_schemas() -> None:
    artifacts = {
        "plan": "g2_material_distinct_plan.schema.json",
        "candidate-frame": "g2_material_distinct_candidate_frame.schema.json",
        "preparation-receipt": "g2_material_distinct_preparation_receipt.schema.json",
    }
    for name, schema_name in artifacts.items():
        instance = json.loads((ROOT / DESIGN / f"{name}.json").read_text())
        schema = json.loads((ROOT / "schemas" / schema_name).read_text())
        assert list(Draft202012Validator(schema).iter_errors(instance)) == []


def test_materially_distinct_verifier_rejects_tampered_frame(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    for relative in (
        "src/gfjd/g2_material_distinct.py",
        "src/gfjd/g2_exposure_chain.py",
        "src/gfjd/g2_metadata_search_successor.py",
        "data/seed/source_register.csv",
        "data/methods/g2/G2HOLDOUT-METADATA-EXPANSION-20260816-03/design/ledger.json",
        "data/methods/g2/G2HOLDOUT-STRUCTURAL-PREFLIGHT-20260815-01/url-resolution/exposure-ledger.json",
        "data/methods/g2/G2HOLDOUT-PROSPECTIVE-20260815-01/intake/exposure-ledger.json",
        "docs/governance/g2-material-distinct-option-a-owner-decision-2026-08-20.md",
    ):
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes((ROOT / relative).read_bytes())
    design = target / DESIGN
    design.mkdir(parents=True)
    for name in ("plan.json", "candidate-frame.json", "preparation-receipt.json"):
        (design / name).write_bytes((ROOT / DESIGN / name).read_bytes())
    frame_path = design / "candidate-frame.json"
    frame = json.loads(frame_path.read_text())
    frame["candidate_count"] = 1
    frame_path.write_text(json.dumps(frame) + "\n")
    files = [
        design / name for name in ("plan.json", "candidate-frame.json", "preparation-receipt.json")
    ]
    (target / MANIFEST).parent.mkdir(parents=True, exist_ok=True)
    (target / MANIFEST).write_text(
        "".join(
            f"{hashlib.sha256(path.read_bytes()).hexdigest()}  "
            f"{path.relative_to(target).as_posix()}\n"
            for path in files
        )
    )
    assert (
        "materially distinct artifact semantic mismatch: candidate-frame.json"
        in verify_material_distinct_frame(target)
    )


def test_materially_distinct_builder_handles_candidate_and_officiality_branches(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        material_distinct,
        "collect_bound_exposure_chain",
        lambda _root, _predecessor: (set(), [{"path": "prior.json"}], []),
    )
    _write_inputs(
        tmp_path,
        {"predecessor": {}, "denied_urls": []},
        "source_id,jurisdiction_id,publisher,source_url,official_status\n"
        "S-OFFICIAL,J1,Publisher,https://example.test/official,official\n"
        "S-UNCERTAIN,J2,Publisher,https://example.test/uncertain,unknown\n",
    )

    frame = build_material_distinct_artifacts(tmp_path)["candidate_frame"]

    assert [candidate["source_id"] for candidate in frame["candidates"]] == ["S-OFFICIAL"]
    assert frame["rejections"][0]["reason_code"] == "OFFICIAL_STATUS_NOT_CONFIRMED"


def test_materially_distinct_builder_rejects_invalid_inputs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source_rows = (
        "source_id,jurisdiction_id,publisher,source_url,official_status\n"
        "S1,J1,Publisher,https://example.test/source,official\n"
    )
    _write_inputs(tmp_path, [], source_rows)
    with pytest.raises(ValueError, match="expected JSON object"):
        build_material_distinct_artifacts(tmp_path)

    _write_inputs(tmp_path, {}, source_rows)
    with pytest.raises(ValueError, match="predecessor is missing"):
        build_material_distinct_artifacts(tmp_path)

    monkeypatch.setattr(
        material_distinct,
        "collect_bound_exposure_chain",
        lambda _root, _predecessor: (set(), [], ["malformed predecessor chain"]),
    )
    _write_inputs(tmp_path, {"predecessor": {}, "denied_urls": []}, source_rows)
    with pytest.raises(ValueError, match="malformed predecessor chain"):
        build_material_distinct_artifacts(tmp_path)

    monkeypatch.setattr(
        material_distinct,
        "collect_bound_exposure_chain",
        lambda _root, _predecessor: (set(), [], []),
    )
    _write_inputs(tmp_path, {"predecessor": {}, "denied_urls": [1]}, source_rows)
    with pytest.raises(ValueError, match="denied_urls are invalid"):
        build_material_distinct_artifacts(tmp_path)

    _write_inputs(
        tmp_path,
        {"predecessor": {}, "denied_urls": []},
        "source_id,jurisdiction_id,publisher,source_url,official_status\n,J1,Publisher,,official\n",
    )
    with pytest.raises(ValueError, match="lacks required candidate metadata"):
        build_material_distinct_artifacts(tmp_path)


def test_materially_distinct_writer_and_verifier_fail_closed_on_manifest_problems(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        material_distinct,
        "collect_bound_exposure_chain",
        lambda _root, _predecessor: ({"https://example.test/source"}, [], []),
    )
    _write_inputs(
        tmp_path,
        {"predecessor": {}, "denied_urls": []},
        "source_id,jurisdiction_id,publisher,source_url,official_status\n"
        "S1,J1,Publisher,https://example.test/source,official\n",
    )
    write_material_distinct_artifacts(tmp_path)
    assert verify_material_distinct_frame(tmp_path) == []

    (tmp_path / MANIFEST).unlink()
    assert "materially distinct detached manifest is missing" in verify_material_distinct_frame(
        tmp_path
    )

    write_material_distinct_artifacts(tmp_path)
    (tmp_path / MANIFEST).write_text(
        "0" * 64 + "  ../outside.json\n",
        encoding="utf-8",
    )
    errors = verify_material_distinct_frame(tmp_path)
    assert "materially distinct detached manifest entry is malformed" in errors
    assert "materially distinct detached manifest omits a design artifact" in errors
