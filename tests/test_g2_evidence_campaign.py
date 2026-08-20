from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from gfjd.g2_evidence_campaign import (
    DESIGN,
    MANIFEST,
    PROTOCOL_SCHEMA,
    RECEIPT_SCHEMA,
    build_evidence_campaign_protocol,
    verify_evidence_campaign_protocol,
    write_evidence_campaign_protocol,
)

ROOT = Path(__file__).resolve().parents[1]


def test_campaign_protocol_is_reproducible_and_stays_disabled() -> None:
    assert verify_evidence_campaign_protocol(ROOT) == []
    protocol = build_evidence_campaign_protocol(ROOT)["protocol"]
    assert protocol["current_state"]["candidate_manifest_available"] is False
    assert protocol["current_state"]["external_activity_authorized"] is False
    assert protocol["future_authorization_model"]["single_grouped_campaign_decision"] is True
    assert protocol["future_authorization_model"]["per_artifact_owner_decision_required"] is False


def test_campaign_protocol_artifacts_validate_against_schemas() -> None:
    schema_names = {
        "protocol": PROTOCOL_SCHEMA,
        "preparation-receipt": RECEIPT_SCHEMA,
    }
    for name, schema_path in schema_names.items():
        instance = json.loads((ROOT / DESIGN / f"{name}.json").read_text())
        schema = json.loads((ROOT / schema_path).read_text())
        assert list(Draft202012Validator(schema).iter_errors(instance)) == []


def test_campaign_protocol_verifier_rejects_authorization_tampering(tmp_path: Path) -> None:
    for relative in (
        "src/gfjd/g2_evidence_campaign.py",
        "src/gfjd/g2_material_distinct.py",
        "src/gfjd/g2_exposure_chain.py",
        "src/gfjd/g2_metadata_search_successor.py",
        "data/seed/source_register.csv",
        "data/methods/g2/G2HOLDOUT-METADATA-EXPANSION-20260816-03/design/ledger.json",
        "data/methods/g2/G2HOLDOUT-STRUCTURAL-PREFLIGHT-20260815-01/url-resolution/exposure-ledger.json",
        "data/methods/g2/G2HOLDOUT-PROSPECTIVE-20260815-01/intake/exposure-ledger.json",
        "data/methods/g2/G2MATERIAL-DISTINCT-20260820-01/design/plan.json",
        "data/methods/g2/G2MATERIAL-DISTINCT-20260820-01/design/candidate-frame.json",
        "data/methods/g2/G2MATERIAL-DISTINCT-20260820-01/design/preparation-receipt.json",
        "data/methods/g2/G2MATERIAL-DISTINCT-20260820-01/design/MATERIAL_DISTINCT_FRAME_MANIFEST.sha256",
        "data/methods/g2/G2EVIDENCE-CAMPAIGN-PROTOCOL-20260820-01/schemas/g2_evidence_campaign_protocol.schema.json",
        "data/methods/g2/G2EVIDENCE-CAMPAIGN-PROTOCOL-20260820-01/schemas/g2_evidence_campaign_preparation_receipt.schema.json",
        "data/methods/g2/G2EVIDENCE-CAMPAIGN-PROTOCOL-20260820-01/schemas/g2_evidence_campaign_candidate_intake.schema.json",
        "docs/governance/g2-material-distinct-option-a-owner-decision-2026-08-20.md",
        "docs/governance/standing-owner-direction-policy-2026-08-20.md",
    ):
        destination = tmp_path / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes((ROOT / relative).read_bytes())
    write_evidence_campaign_protocol(tmp_path)
    protocol_path = tmp_path / DESIGN / "protocol.json"
    protocol = json.loads(protocol_path.read_text())
    protocol["prohibited_until_authorized"]["source_file_access"] = True
    protocol_path.write_text(json.dumps(protocol) + "\n")
    files = [
        tmp_path / DESIGN / "protocol.json",
        tmp_path / DESIGN / "preparation-receipt.json",
    ]
    (tmp_path / MANIFEST).write_text(
        "".join(
            (
                f"{hashlib.sha256(path.read_bytes()).hexdigest()}  "
                f"{path.relative_to(tmp_path).as_posix()}\n"
            )
            for path in files
        )
    )
    errors = verify_evidence_campaign_protocol(tmp_path)
    assert "evidence campaign protocol semantic mismatch: protocol.json" in errors


def test_campaign_protocol_verifier_rejects_manifest_extra_artifact(tmp_path: Path) -> None:
    for relative in (
        "src/gfjd/g2_evidence_campaign.py",
        "src/gfjd/g2_material_distinct.py",
        "src/gfjd/g2_exposure_chain.py",
        "src/gfjd/g2_metadata_search_successor.py",
        "data/seed/source_register.csv",
        "data/methods/g2/G2HOLDOUT-METADATA-EXPANSION-20260816-03/design/ledger.json",
        "data/methods/g2/G2HOLDOUT-STRUCTURAL-PREFLIGHT-20260815-01/url-resolution/exposure-ledger.json",
        "data/methods/g2/G2HOLDOUT-PROSPECTIVE-20260815-01/intake/exposure-ledger.json",
        "data/methods/g2/G2MATERIAL-DISTINCT-20260820-01/design/plan.json",
        "data/methods/g2/G2MATERIAL-DISTINCT-20260820-01/design/candidate-frame.json",
        "data/methods/g2/G2MATERIAL-DISTINCT-20260820-01/design/preparation-receipt.json",
        "data/methods/g2/G2MATERIAL-DISTINCT-20260820-01/design/MATERIAL_DISTINCT_FRAME_MANIFEST.sha256",
        "data/methods/g2/G2EVIDENCE-CAMPAIGN-PROTOCOL-20260820-01/schemas/g2_evidence_campaign_protocol.schema.json",
        "data/methods/g2/G2EVIDENCE-CAMPAIGN-PROTOCOL-20260820-01/schemas/g2_evidence_campaign_preparation_receipt.schema.json",
        "data/methods/g2/G2EVIDENCE-CAMPAIGN-PROTOCOL-20260820-01/schemas/g2_evidence_campaign_candidate_intake.schema.json",
        "docs/governance/g2-material-distinct-option-a-owner-decision-2026-08-20.md",
        "docs/governance/standing-owner-direction-policy-2026-08-20.md",
    ):
        destination = tmp_path / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes((ROOT / relative).read_bytes())
    write_evidence_campaign_protocol(tmp_path)
    extra = tmp_path / "extra.json"
    extra.write_text("{}\n")
    with (tmp_path / MANIFEST).open("a", encoding="utf-8") as handle:
        handle.write(f"{hashlib.sha256(extra.read_bytes()).hexdigest()}  extra.json\n")
    errors = verify_evidence_campaign_protocol(tmp_path)
    assert "evidence campaign detached manifest has an unexpected artifact set" in errors
