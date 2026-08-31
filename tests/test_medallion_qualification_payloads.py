"""Fictional byte banks; no acquired source material or acceptance evidence."""

import copy
from pathlib import Path

import pytest

from gfjd.medallion_qualification_inputs import (
    LAYERS,
    VERSION,
    QualificationInputError,
    canonical,
    sha,
)
from gfjd.medallion_qualification_payloads import resolve_payloads, verify_payloads


def fixture(root: Path) -> tuple:
    source = b"FICTIONAL aggregate bytes"
    scope = {
        "contract_version": VERSION,
        "objects": [
            {
                "object_id": "FICTIONAL",
                "edition_id": "FICTIONAL-EDITION",
                "layers": {
                    layer: {"state": "active", "reason_codes": [], "disposition_reference": None}
                    for layer in LAYERS
                },
            }
        ],
    }
    wrapper = {
        "object_id": "FICTIONAL",
        "edition_id": "FICTIONAL-EDITION",
        "record": {
            "contract_version": "gfjd-medallion-layers-v1",
            "object_id": "FICTIONAL",
            "layer": "b0",
            "previous_layer": None,
            "lifecycle_state": "active",
            "evidence": {
                "source_edition_id": "FICTIONAL-EDITION",
                "content_sha256": sha(source),
                "content_blake3": "a" * 64,
                "size_bytes": len(source),
                "media_type": "text/plain",
                "capture_receipt_sha256": "b" * 64,
                "safety_receipt_sha256": "c" * 64,
                "custody_receipt_sha256": "d" * 64,
            },
        },
        "artifacts": {"source": sha(source), "safety": "c" * 64},
    }
    return (
        scope,
        wrapper,
        (root / "config/medallion_layers.json").read_bytes(),
        {sha(source): source},
    )


def args(scope: dict, wrapper: dict, contract: bytes, bank: dict) -> tuple:
    raw, record = canonical(scope), canonical(wrapper)
    return raw, sha(raw), contract, {sha(record): record}, bank


def test_fixity_and_missing_are_visible_without_meaning(project_root: Path) -> None:
    values = args(*fixture(project_root))
    result = resolve_payloads(*values)
    assert len(result["coverage"]) == 5
    assert result["artifact_count"] == 1
    cell = result["coverage"][0]
    assert cell["references"]["source"]["status"] == "fixity_verified"
    assert cell["references"]["safety"]["status"] == "missing"
    assert not cell["evidence_meaning_verified"]
    verify_payloads(*values, result)
    result["promotion_authorized"] = True
    with pytest.raises(QualificationInputError):
        verify_payloads(*values, result)


@pytest.mark.parametrize("state", ["quarantined", "withdrawn", "tombstoned", "invalid"])
def test_ineligible_payloads_cannot_be_processed(project_root: Path, state: str) -> None:
    scope, record, contract, bank = fixture(project_root)
    if state == "invalid":
        del record["record"]["evidence"]["content_sha256"]
    else:
        scope["objects"][0]["layers"]["b0"].update(
            state=state, reason_codes=["FICTIONAL"], disposition_reference="FICTIONAL"
        )
        record["record"]["lifecycle_state"] = state
    with pytest.raises(QualificationInputError):
        resolve_payloads(*args(scope, record, contract, bank))
    result = resolve_payloads(*args(scope, record, contract, {}))
    assert result["coverage"][0]["payload_processing_eligible"] is False
    assert result["coverage"][0]["references"] == {}


@pytest.mark.parametrize("change", ["extra", "altered", "oversized", "nonbytes", "unknown_role"])
def test_bank_and_role_failures(project_root: Path, change: str) -> None:
    scope, record, contract, bank = fixture(project_root)
    key = next(iter(bank))
    if change == "extra":
        bank[sha(b"extra")] = b"extra"
    elif change == "altered":
        bank[key] = b"changed"
    elif change == "oversized":
        bank[key] = b"x" * (8 * 1024 * 1024 + 1)
    elif change == "nonbytes":
        bank[key] = "not-bytes"
    else:
        record["artifacts"]["arbitrary_plugin"] = key
    with pytest.raises(QualificationInputError):
        resolve_payloads(*args(scope, record, contract, bank))


def test_missing_bank_and_no_mutation(project_root: Path) -> None:
    values = args(*fixture(project_root))
    original = copy.deepcopy(values)
    result = resolve_payloads(*values[:-1], {})
    assert all(r["status"] == "missing" for r in result["coverage"][0]["references"].values())
    assert values == original
