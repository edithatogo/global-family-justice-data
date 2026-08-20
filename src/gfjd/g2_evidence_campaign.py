"""Fail-closed preparation for a future, bounded G2 evidence campaign.

The protocol is deliberately repository-only.  It turns the current exhausted
material-distinct frame into an explicit stop and defines the exact evidence
that a *single future* campaign authorization must bind.  It neither discovers
sources nor permits any external action.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from gfjd.g2_material_distinct import verify_material_distinct_frame

LINEAGE = "G2EVIDENCE-CAMPAIGN-PROTOCOL-20260820-01"
DESIGN = Path("data/methods/g2") / LINEAGE / "design"
MATERIAL_FRAME = Path("data/methods/g2/G2MATERIAL-DISTINCT-20260820-01/design/candidate-frame.json")
MATERIAL_RECEIPT = Path(
    "data/methods/g2/G2MATERIAL-DISTINCT-20260820-01/design/preparation-receipt.json"
)
STANDING_DIRECTION = Path("docs/governance/standing-owner-direction-policy-2026-08-20.md")
MANIFEST = DESIGN / "EVIDENCE_CAMPAIGN_PROTOCOL_MANIFEST.sha256"
PROTOCOL_SCHEMA = DESIGN.parent / "schemas/g2_evidence_campaign_protocol.schema.json"
RECEIPT_SCHEMA = DESIGN.parent / "schemas/g2_evidence_campaign_preparation_receipt.schema.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _descriptor(root: Path, path: Path) -> dict[str, str]:
    return {"path": path.relative_to(root).as_posix(), "sha256": _sha(path)}


def _read_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _json_bytes(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def build_evidence_campaign_protocol(root: Path) -> dict[str, dict[str, Any]]:
    """Build the deterministic no-external-access campaign protocol."""

    if verify_material_distinct_frame(root):
        raise ValueError("materially distinct frame does not verify")

    frame_path = root / MATERIAL_FRAME
    receipt_path = root / MATERIAL_RECEIPT
    direction_path = root / STANDING_DIRECTION
    frame = _read_object(frame_path)
    receipt = _read_object(receipt_path)
    if (
        frame.get("status") != "stopped_insufficient_repository_metadata"
        or frame.get("candidate_count") != 0
        or frame.get("scope_complete") is not False
        or receipt.get("outcome") != "stopped_insufficient_repository_metadata"
    ):
        raise ValueError("materially distinct frame is not the expected exhausted result")

    protocol = {
        "schema_version": "1.0",
        "campaign_id": LINEAGE,
        "status": "repository_ready_external_input_required",
        "purpose": "prospective_g2_factual_evidence_campaign",
        "material_distinct_frame": _descriptor(root, frame_path),
        "material_distinct_receipt": _descriptor(root, receipt_path),
        "standing_direction": _descriptor(root, direction_path),
        "current_state": {
            "candidate_manifest_available": False,
            "candidate_count": 0,
            "external_activity_authorized": False,
            "source_content_accessed": False,
            "g2_passage_authorized": False,
        },
        "required_before_external_activity": [
            "digest_bound_non_exposed_candidate_manifest",
            "complete_cumulative_exposure_check",
            "bounded_resource_budget",
            "role_bound_access_controls",
            "source_specific_rights_privacy_security_screen",
            "single_grouped_owner_campaign_authorization",
        ],
        "future_authorization_model": {
            "single_grouped_campaign_decision": True,
            "per_artifact_owner_decision_required": False,
            "must_bind": [
                "candidate_manifest",
                "exposure_ledger",
                "access_controls",
                "resource_budget",
                "stopping_rules",
                "role_bundles",
            ],
        },
        "prohibited_until_authorized": {
            "network_requests": False,
            "url_requests": False,
            "source_file_access": False,
            "source_content_inspection": False,
            "outbound_contact": False,
            "rights_acceptance": False,
            "publication": False,
            "release": False,
            "g2_passage": False,
        },
        "stopping_rules": [
            (
                "no eligible non-exposed candidate manifest stops the campaign "
                "before external activity"
            ),
            (
                "any exposure-chain, binding, budget, role-isolation or "
                "access-boundary failure stops the campaign"
            ),
            "no candidate substitution, filtering, reuse, waiver or retry after a terminal stop",
            "all factual source-specific evidence remains quarantined until separately assessed",
        ],
        "g2_criterion_dependencies": [
            "G2-C01",
            "G2-C02",
            "G2-C03",
            "G2-C04",
            "G2-C05",
            "G2-C06",
            "G2-C07",
        ],
        "limitations": [
            (
                "This protocol is not a candidate manifest, execution packet, "
                "rights decision or gate decision."
            ),
            (
                "Existing repository metadata yields zero unexposed candidates "
                "and cannot establish factual pilot evidence."
            ),
            (
                "A passing repository validation cannot substitute for real "
                "source evidence or owner gate acceptance."
            ),
        ],
    }
    receipt_payload = {
        "schema_version": "1.0",
        "receipt_id": f"{LINEAGE}-PREPARATION-RECEIPT",
        "protocol_sha256": hashlib.sha256(_json_bytes(protocol)).hexdigest(),
        "material_distinct_frame": _descriptor(root, frame_path),
        "material_distinct_receipt": _descriptor(root, receipt_path),
        "candidate_manifest_available": False,
        "external_activity_authorized": False,
        "source_content_accessed": False,
        "outcome": "blocked_no_unexposed_candidate_manifest",
    }
    return {"protocol": protocol, "preparation_receipt": receipt_payload}


def write_evidence_campaign_protocol(root: Path) -> None:
    destination = root / DESIGN
    destination.mkdir(parents=True, exist_ok=True)
    for name, payload in build_evidence_campaign_protocol(root).items():
        (destination / f"{name.replace('_', '-')}.json").write_bytes(_json_bytes(payload))
    bound_paths = [
        destination / "protocol.json",
        destination / "preparation-receipt.json",
        root / PROTOCOL_SCHEMA,
        root / RECEIPT_SCHEMA,
    ]
    (root / MANIFEST).write_text(
        "".join(f"{_sha(path)}  {path.relative_to(root).as_posix()}\n" for path in bound_paths),
        encoding="utf-8",
    )


def _safe(root: Path, relative: str) -> Path | None:
    candidate = Path(relative)
    if candidate.is_absolute() or ".." in candidate.parts or candidate.as_posix() != relative:
        return None
    path = root / candidate
    try:
        if not path.resolve().is_relative_to(root.resolve()):
            return None
    except (OSError, RuntimeError):
        return None
    return path if path.is_file() else None


def verify_evidence_campaign_protocol(root: Path) -> list[str]:
    """Recompute protocol semantics and detached-manifest bindings."""

    errors: list[str] = []
    try:
        expected = build_evidence_campaign_protocol(root)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
        return [f"evidence campaign protocol inputs are invalid: {error}"]
    destination = root / DESIGN
    for name, payload in expected.items():
        path = destination / f"{name.replace('_', '-')}.json"
        try:
            actual = _read_object(path)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError):
            errors.append(f"evidence campaign protocol artifact is invalid: {path.name}")
            continue
        if actual != payload:
            errors.append(f"evidence campaign protocol semantic mismatch: {path.name}")

    required = {
        (DESIGN / "protocol.json").as_posix(),
        (DESIGN / "preparation-receipt.json").as_posix(),
        PROTOCOL_SCHEMA.as_posix(),
        RECEIPT_SCHEMA.as_posix(),
    }
    try:
        entries = (root / MANIFEST).read_text(encoding="utf-8").splitlines()
    except OSError:
        return sorted(set(errors + ["evidence campaign detached manifest is missing"]))
    seen: set[str] = set()
    for entry in entries:
        digest, separator, relative = entry.partition("  ")
        safe_path = _safe(root, relative)
        if not separator or len(digest) != 64 or relative in seen or safe_path is None:
            errors.append("evidence campaign detached manifest entry is malformed")
            continue
        seen.add(relative)
        if _sha(safe_path) != digest:
            errors.append(f"evidence campaign detached manifest mismatch: {relative}")
    if seen != required:
        errors.append("evidence campaign detached manifest has an unexpected artifact set")
    return sorted(set(errors))
