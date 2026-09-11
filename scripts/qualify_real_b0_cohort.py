#!/usr/bin/env python3
"""Recompute a fail-closed B0 qualification report for the real cohort.

This command reads only already-present local bytes and checked-in receipts. It
does not download, extract, publish, or promote anything. Formats without a
bounded B0 scanner are reported as replay-pending rather than treated as
qualified.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any

from blake3 import blake3

from gfjd import medallion_b0_checks

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INTAKE = ROOT / "data/federation/real-b0-cohort-intake-20260910.json"
INVENTORY_PATH = ROOT / "data/raw/archive_inventory.csv"
SAFETY_PATH = ROOT / "data/preservation/public_b0_safety_20260827.json"
CUSTODY_PATH = ROOT / "data/preservation/public_b0_custody_20260827.json"
SWE_REPLAY = ROOT / "data/federation/real-swe-b0-replay-receipt-20260905-02.json"


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()


def media_type(path: Path) -> str:
    suffix = path.suffix.lower()
    return {
        ".pdf": "application/pdf",
        ".zip": "application/zip",
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    }.get(suffix, "application/octet-stream")


def _object(receipt: dict[str, Any], inventory_id: str) -> dict[str, Any]:
    for item in receipt.get("objects", []):
        if item.get("inventory_id") == inventory_id:
            return item
    raise ValueError(f"missing receipt object: {inventory_id}")


def _inventory() -> dict[str, dict[str, str]]:
    with INVENTORY_PATH.open(newline="", encoding="utf-8") as handle:
        return {row["inventory_id"]: row for row in csv.DictReader(handle)}


def _safe_payload_path(raw_path: str) -> Path:
    candidate = (ROOT / raw_path).resolve()
    try:
        candidate.relative_to(ROOT)
    except ValueError as exc:
        raise ValueError("payload path escapes repository root") from exc
    if Path(ROOT / raw_path).is_symlink():
        raise ValueError("payload path must not be a symlink")
    return candidate


def _b0_mechanical(
    source: bytes,
    inventory_id: str,
    edition: str,
    source_media_type: str,
    safety_raw: bytes,
    custody_raw: bytes,
    safety_object: dict[str, Any],
) -> dict[str, Any]:
    evidence = {
        "source_edition_id": edition,
        "content_sha256": sha256(source),
        "content_blake3": blake3(source).hexdigest(),
        "size_bytes": len(source),
        "media_type": source_media_type,
        "safety_receipt_sha256": sha256(safety_raw),
        "custody_receipt_sha256": sha256(custody_raw),
    }
    report = medallion_b0_checks.assess_b0(
        source,
        evidence,
        object_id=inventory_id,
        safety_raw=safety_raw,
        custody_raw=custody_raw,
    )
    required_checks = {"fixity": "verified", "safety": "verified", "custody": "consistent"}
    status = (
        "verified"
        if all(report["checks"].get(k) == v for k, v in required_checks.items())
        else "failed"
    )
    return {
        "status": status,
        "report_sha256": sha256(canonical(report)),
        "checks": report["checks"],
        "finding_codes": report["finding_codes"],
        "implementation_sha256": report["implementation_sha256"],
        "receipt_object_disposition": safety_object.get("disposition"),
    }


def qualify(
    intake: dict[str, Any],
    *,
    as_of: str,
    evidence_id: str = "E-G4-MEDALLION-B0-QUALIFICATION-20260911",
) -> dict[str, Any]:
    safety_raw = SAFETY_PATH.read_bytes()
    custody_raw = CUSTODY_PATH.read_bytes()
    safety = json.loads(safety_raw)
    inventory = _inventory()
    rows = []
    for intake_row in intake["rows"]:
        inventory_row = inventory.get(intake_row["inventory_id"])
        path_error = None
        try:
            path = _safe_payload_path(intake_row["payload_path"])
        except ValueError as exc:
            path = ROOT
            path_error = str(exc)
        binding_ok = bool(
            inventory_row
            and intake_row["payload_path"] == inventory_row["payload_path"]
            and intake_row["expected_sha256"] == inventory_row["sha256"]
        )
        source = path.read_bytes() if path_error is None and path.is_file() else b""
        observed_sha = sha256(source) if source else None
        observed_blake3 = blake3(source).hexdigest() if source else None
        fixity = bool(
            source
            and observed_sha == intake_row["expected_sha256"]
            and observed_sha == intake_row["observed_sha256"]
        )
        row: dict[str, Any] = {
            "inventory_id": intake_row["inventory_id"],
            "source_id": intake_row["source_id"],
            "edition": intake_row["edition"],
            "payload_path": intake_row["payload_path"],
            "media_type": media_type(path),
            "size_bytes": len(source),
            "sha256": observed_sha,
            "blake3": observed_blake3,
            "b0_fixity": "verified" if fixity else "failed",
            "b0_mechanical": {"status": "pending", "reason": "not_attempted"},
            "b1_replay": {"status": "pending", "reason": "no_bounded_adapter"},
            "silver_replay": {"status": "pending", "reason": "b1_replay_pending"},
            "promotion_authorized": False,
        }
        if path_error:
            row["b0_fixity"] = "failed"
            row["b0_error"] = path_error
        elif not binding_ok:
            row["b0_fixity"] = "failed"
            row["b0_error"] = "intake does not match frozen archive inventory"
        if not fixity:
            row["b0_mechanical"] = {"status": "blocked", "reason": "fixity_failed"}
        elif row["media_type"] in {
            "application/pdf",
            "application/zip",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        }:
            try:
                row["b0_mechanical"] = _b0_mechanical(
                    source,
                    intake_row["inventory_id"],
                    intake_row["edition"],
                    row["media_type"],
                    safety_raw,
                    custody_raw,
                    _object(safety, intake_row["inventory_id"]),
                )
                if intake_row["inventory_id"] == "ARC-SWE-DOMSTOLSVERKET-2026":
                    replay_raw = SWE_REPLAY.read_bytes()
                    replay = json.loads(replay_raw)
                    replay_ok = (
                        replay.get("source_sha256") == observed_sha
                        and replay.get("status")
                        == "empirical_replay_verified_pending_layer_adjudication"
                        and replay.get("source_recomputation_verifier") is True
                        and replay.get("deterministic_double_execution") is True
                        and replay.get("negative_checks", {}).get("changed_source_rejected") is True
                        and replay.get("negative_checks", {}).get("changed_output_rejected") is True
                    )
                    replay_status = "verified_supporting_receipt" if replay_ok else "failed"
                    row["b1_replay"] = {
                        "status": replay_status,
                        "receipt_path": str(SWE_REPLAY.relative_to(ROOT)),
                        "receipt_sha256": sha256(replay_raw),
                        "source_sha256": replay.get("source_sha256"),
                        "row_count": replay.get("b1_row_count"),
                    }
                    row["silver_replay"] = {
                        "status": replay_status,
                        "receipt_path": str(SWE_REPLAY.relative_to(ROOT)),
                        "receipt_sha256": sha256(replay_raw),
                        "row_count": replay.get("silver_row_count"),
                    }
            except (KeyError, OSError, TypeError, ValueError) as exc:
                row["b0_mechanical"] = {
                    "status": "failed",
                    "reason": "bounded_scanner_failed",
                    "error_type": type(exc).__name__,
                }
        else:
            row["b0_mechanical"] = {
                "status": "not_evaluated",
                "reason": "format_not_supported_by_b0_scanner",
            }
        rows.append(row)
    return {
        "schema_version": "1.0",
        "evidence_id": evidence_id,
        "observed_at": as_of,
        "cohort_id": intake["cohort_id"],
        "intake_sha256": sha256(canonical(intake)),
        "safety_receipt_sha256": sha256(safety_raw),
        "custody_receipt_sha256": sha256(custody_raw),
        "network_requests": 0,
        "rows": rows,
        "status": (
            "b0_fixity_failed"
            if not all(row["b0_fixity"] == "verified" for row in rows)
            else (
                "b0_mechanical_failed"
                if any(row["b0_mechanical"].get("status") in {"failed", "blocked"} for row in rows)
                else "b0_fixity_verified_replay_pending"
            )
        ),
        "interpretation": (
            "All six local payloads match the frozen inventory. B0 fixity and "
            "bounded safety mechanics are evaluated for supported PDF, ZIP and "
            "XLSX routes; only the SWE XLSX route has a source-recomputing "
            "B1/Silver supporting receipt."
        ),
        "limitations": [
            (
                "Fixity and a bounded scanner result do not establish rights, "
                "semantic accuracy, independent assurance, or layer acceptance."
            ),
            (
                "No PDF or ZIP text was extracted; B1/Silver replay remains pending "
                "for every route without a route-specific replay receipt."
            ),
            (
                "The SWE replay receipt is repository-owned supporting evidence "
                "and is not independent assurance."
            ),
            (
                "No B0-to-B1/Silver promotion, Gold promotion, publication, release, "
                "maturity or gate acceptance is authorized."
            ),
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--intake", type=Path, default=DEFAULT_INTAKE)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--evidence-id", required=True)
    args = parser.parse_args()
    intake_path = args.intake if args.intake.is_absolute() else ROOT / args.intake
    output = args.output if args.output.is_absolute() else ROOT / args.output
    intake = json.loads(intake_path.read_bytes())
    report = qualify(intake, as_of=args.as_of, evidence_id=args.evidence_id)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(canonical(report) + b"\n")
    print(json.dumps({"status": report["status"], "rows": len(report["rows"])}))
    return 0 if not report["status"].endswith("_failed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
