from __future__ import annotations

from gfjd.preservation import assess_preservation_readiness


def test_preservation_is_fail_closed_without_authority_evidence() -> None:
    result = assess_preservation_readiness(
        {
            "source_edition_id": "ED-1",
            "sha256": "a" * 64,
            "rights_status": "cleared",
            "redistribution_status": "allowed",
        }
    )
    assert result.ready is False
    assert "preservation_decision_ref_required" in result.issues
    assert "custody_receipt_ref_required" in result.issues


def test_metadata_only_receipt_is_not_preservation_ready() -> None:
    result = assess_preservation_readiness(
        {
            "source_edition_id": "ED-1",
            "sha256": "a" * 64,
            "rights_status": "review_required",
            "redistribution_status": "metadata_only",
            "preservation_decision_ref": "DEC-1",
            "custody_receipt_ref": "LOCAL-1",
        }
    )
    assert result.ready is False
    assert "authoritative_rights_decision_pending" in result.issues


def test_complete_receipt_is_only_evidence_packet_ready() -> None:
    result = assess_preservation_readiness(
        {
            "source_edition_id": "ED-1",
            "sha256": "a" * 64,
            "rights_status": "cleared",
            "redistribution_status": "allowed",
            "preservation_decision_ref": "DEC-1",
            "custody_receipt_ref": "CUST-1",
        }
    )
    assert result.ready is True
