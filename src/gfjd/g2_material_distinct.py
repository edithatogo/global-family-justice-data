"""Fail-closed preparation for the G2 materially distinct method route.

This module deliberately uses only checked-in source-register metadata and the
digest-bound cumulative exposure ledger.  It cannot request a URL or turn an
already exposed source into a candidate.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

from gfjd.g2_exposure_chain import collect_bound_exposure_chain
from gfjd.g2_metadata_search_successor import canonical_url

LINEAGE = "G2MATERIAL-DISTINCT-20260820-01"
DESIGN = Path("data/methods/g2") / LINEAGE / "design"
SOURCE_REGISTER = Path("data/seed/source_register.csv")
EXPOSURE_LEDGER = Path(
    "data/methods/g2/G2HOLDOUT-METADATA-EXPANSION-20260816-03/design/ledger.json"
)
OWNER_DECISION = Path("docs/governance/g2-material-distinct-option-a-owner-decision-2026-08-20.md")
MANIFEST = DESIGN / "MATERIAL_DISTINCT_FRAME_MANIFEST.sha256"
TARGET_CANDIDATE_COUNT = 96


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


def build_material_distinct_artifacts(root: Path) -> dict[str, dict[str, Any]]:
    """Build a deterministic, no-network candidate-frame result."""

    source_register = root / SOURCE_REGISTER
    exposure_path = root / EXPOSURE_LEDGER
    owner_decision = root / OWNER_DECISION
    ledger = _read_object(exposure_path)
    predecessor = ledger.get("predecessor")
    if not isinstance(predecessor, dict):
        raise ValueError("materially distinct exposure ledger predecessor is missing")
    prior_urls, prior_chain, chain_errors = collect_bound_exposure_chain(root, predecessor)
    if chain_errors:
        raise ValueError("; ".join(chain_errors))
    current_urls = ledger.get("denied_urls")
    if not isinstance(current_urls, list) or not all(isinstance(url, str) for url in current_urls):
        raise ValueError("materially distinct exposure ledger denied_urls are invalid")
    current = {canonical_url(url) for url in current_urls}
    denied = prior_urls | current

    with source_register.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows or any(not row.get("source_id") or not row.get("source_url") for row in rows):
        raise ValueError("source register lacks required candidate metadata")

    candidates: list[dict[str, str]] = []
    rejected: list[dict[str, str]] = []
    for row in sorted(rows, key=lambda item: str(item["source_id"])):
        source_url = canonical_url(str(row["source_url"]))
        base = {
            "source_id": str(row["source_id"]),
            "jurisdiction_id": str(row["jurisdiction_id"]),
            "publisher": str(row["publisher"]),
            "source_url": source_url,
        }
        if source_url in denied:
            rejected.append({**base, "reason_code": "CUMULATIVE_EXPOSURE_OVERLAP"})
        elif row.get("official_status") != "official":
            rejected.append({**base, "reason_code": "OFFICIAL_STATUS_NOT_CONFIRMED"})
        else:
            candidates.append(base)

    plan = {
        "schema_version": "1.0",
        "plan_id": LINEAGE,
        "status": "prepared_no_network",
        "method": "official_publication_manifest_route",
        "target_candidate_count": TARGET_CANDIDATE_COUNT,
        "source_register": _descriptor(root, source_register),
        "exposure_ledger": _descriptor(root, exposure_path),
        "owner_decision": _descriptor(root, owner_decision),
        "complete_predecessor_chain": prior_chain,
        "controls": {
            "complete_exposure_chain_required": True,
            "candidate_url_must_not_overlap": True,
            "network_access_authorized": False,
            "url_access_authorized": False,
            "source_content_accessed": False,
            "extraction_authorized": False,
            "rights_acceptance_authorized": False,
            "publication_authorized": False,
            "release_authorized": False,
            "g2_passage_authorized": False,
        },
        "stopping_rules": [
            "any digest-bound exposure-chain failure",
            "any candidate URL overlap with cumulative exposure",
            "fewer than 96 repository-metadata candidates",
            "any external request or source-content access",
        ],
        "resource_estimate": {
            "repository_metadata_rows": len(rows),
            "network_requests": 0,
            "source_content_accesses": 0,
            "external_contacts": 0,
        },
    }
    frame = {
        "schema_version": "1.0",
        "frame_id": f"{LINEAGE}-OFFICIAL-PUBLICATION-MANIFEST-FRAME",
        "plan_id": LINEAGE,
        "status": "stopped_insufficient_repository_metadata",
        "target_candidate_count": TARGET_CANDIDATE_COUNT,
        "candidate_count": len(candidates),
        "rejected_count": len(rejected),
        "scope_complete": len(candidates) >= TARGET_CANDIDATE_COUNT,
        "metadata_only": True,
        "source_content_accessed": False,
        "network_access_performed": False,
        "cumulative_exposure_url_count": len(denied),
        "candidates": candidates,
        "rejections": rejected,
        "limitations": [
            "All checked-in source-register URLs overlap the complete cumulative exposure chain.",
            (
                "The checked-in source register contains fewer rows than the fixed "
                "96-candidate target."
            ),
            "No external publication-manifest enumeration was authorized or performed.",
        ],
        "next_owner_checkpoint": (
            "Authorize only after an exact new candidate manifest, controls, stopping rules, "
            "resource estimate, and execution packet are presented."
        ),
    }
    receipt = {
        "schema_version": "1.0",
        "receipt_id": f"{LINEAGE}-PREPARATION-RECEIPT",
        "plan_sha256": hashlib.sha256(_json_bytes(plan)).hexdigest(),
        "frame_sha256": hashlib.sha256(_json_bytes(frame)).hexdigest(),
        "source_register": _descriptor(root, source_register),
        "exposure_ledger": _descriptor(root, exposure_path),
        "owner_decision": _descriptor(root, owner_decision),
        "candidate_count": len(candidates),
        "rejected_count": len(rejected),
        "scope_complete": False,
        "network_access_performed": False,
        "source_content_accessed": False,
        "external_contact_performed": False,
        "outcome": "stopped_insufficient_repository_metadata",
    }
    return {"plan": plan, "candidate_frame": frame, "preparation_receipt": receipt}


def write_material_distinct_artifacts(root: Path) -> None:
    destination = root / DESIGN
    destination.mkdir(parents=True, exist_ok=True)
    for name, payload in build_material_distinct_artifacts(root).items():
        (destination / f"{name.replace('_', '-')}.json").write_bytes(_json_bytes(payload))
    bound_paths = [
        root / DESIGN / name
        for name in ("plan.json", "candidate-frame.json", "preparation-receipt.json")
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


def verify_material_distinct_frame(root: Path) -> list[str]:
    """Recompute the preparation result and every detached manifest binding."""

    errors: list[str] = []
    destination = root / DESIGN
    expected = build_material_distinct_artifacts(root)
    for name, payload in expected.items():
        path = destination / f"{name.replace('_', '-')}.json"
        try:
            actual = _read_object(path)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError):
            errors.append(f"materially distinct artifact is invalid: {path.name}")
            continue
        if actual != payload:
            errors.append(f"materially distinct artifact semantic mismatch: {path.name}")
    frame = expected["candidate_frame"]
    if frame["candidate_count"] or frame["scope_complete"]:
        errors.append("materially distinct frame incorrectly treats exposed metadata as eligible")

    required = {
        (DESIGN / name).as_posix()
        for name in ("plan.json", "candidate-frame.json", "preparation-receipt.json")
    }
    try:
        entries = (root / MANIFEST).read_text(encoding="utf-8").splitlines()
    except OSError:
        return sorted(set(errors + ["materially distinct detached manifest is missing"]))
    seen: set[str] = set()
    for entry in entries:
        digest, separator, relative = entry.partition("  ")
        safe_path = _safe(root, relative)
        if not separator or len(digest) != 64 or relative in seen or safe_path is None:
            errors.append("materially distinct detached manifest entry is malformed")
            continue
        seen.add(relative)
        if _sha(safe_path) != digest:
            errors.append(f"materially distinct detached manifest mismatch: {relative}")
    if not required.issubset(seen):
        errors.append("materially distinct detached manifest omits a design artifact")
    return sorted(set(errors))
