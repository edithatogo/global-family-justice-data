"""Fail-closed preservation and rights-readiness checks for acquisition receipts.

These checks do not decide rights.  They make the evidence required for a
rights/preservation decision explicit and prevent a receipt from being treated
as an archive or redistribution approval merely because bytes were captured.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class PreservationReadiness:
    ready: bool
    issues: tuple[str, ...]


def assess_preservation_readiness(manifest: dict[str, Any]) -> PreservationReadiness:
    """Assess whether an acquisition receipt is eligible for preservation.

    ``ready`` means only that the receipt contains the minimum evidence packet;
    it is not an approval to publish, redistribute, or claim independent
    custody.  Ambiguous or missing rights evidence remains blocked.
    """

    issues: list[str] = []
    if not str(manifest.get("source_edition_id") or "").strip():
        issues.append("source_edition_id_required_for_preservation")
    if not str(manifest.get("sha256") or "").strip():
        issues.append("content_checksum_required_for_preservation")
    rights = str(manifest.get("rights_status") or "unknown")
    redistribution = str(manifest.get("redistribution_status") or "unknown")
    if rights != "cleared":
        issues.append("authoritative_rights_decision_pending")
    if redistribution != "allowed":
        issues.append("redistribution_not_cleared_metadata_only")
    if not str(manifest.get("preservation_decision_ref") or "").strip():
        issues.append("preservation_decision_ref_required")
    if not str(manifest.get("custody_receipt_ref") or "").strip():
        issues.append("custody_receipt_ref_required")
    return PreservationReadiness(not issues, tuple(issues))
