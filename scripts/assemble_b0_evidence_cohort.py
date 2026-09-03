#!/usr/bin/env python3
"""Assemble a fail-closed B0 cohort from the checked-in archive inventory.

This command never downloads or substitutes source bytes.  It only verifies
that inventory-declared payloads exist locally and match their manifest digest.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def assemble(root: Path, inventory: Path) -> dict[str, object]:
    rows: list[dict[str, object]] = []
    with inventory.open(newline="", encoding="utf-8") as handle:
        for record in csv.DictReader(handle):
            payload = root / record["payload_path"]
            exists = payload.is_file()
            observed = sha256(payload) if exists else None
            digest_matches = observed == record["sha256"] if exists else False
            rows.append(
                {
                    "inventory_id": record["inventory_id"],
                    "source_id": record["source_id"],
                    "edition": record["edition"],
                    "payload_path": record["payload_path"],
                    "expected_sha256": record["sha256"],
                    "observed_sha256": observed,
                    "exists": exists,
                    "digest_matches": digest_matches,
                    "status": "eligible_b0" if digest_matches else "blocked_missing_or_mismatched_bytes",
                }
            )
    eligible = [row for row in rows if row["status"] == "eligible_b0"]
    return {
        "schema_version": "1.0",
        "cohort_id": "GFJD-B0-REAL-20260903-01",
        "source_inventory": str(inventory.relative_to(root)),
        "source_access": "local-only-verification",
        "network_used": False,
        "rows": rows,
        "eligible_count": len(eligible),
        "total_count": len(rows),
        "status": "ready_for_replay" if eligible else "terminal_stop_missing_bytes",
        "replay_authorized": bool(eligible),
        "limitations": [
            "No source bytes are downloaded or substituted by this command.",
            "Inventory metadata and acquisition receipts do not establish B0 custody without matching bytes.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--inventory", type=Path, default=Path("data/raw/archive_inventory.csv"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    inventory = (root / args.inventory).resolve() if not args.inventory.is_absolute() else args.inventory
    report = assemble(root, inventory)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "eligible_count": report["eligible_count"], "total_count": report["total_count"]}))
    return 0 if report["status"] == "ready_for_replay" else 2


if __name__ == "__main__":
    raise SystemExit(main())
