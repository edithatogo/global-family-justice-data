from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from gfjd.g2_material_distinct import (
    DESIGN,
    MANIFEST,
    build_material_distinct_artifacts,
    verify_material_distinct_frame,
)

ROOT = Path(__file__).resolve().parents[1]


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
