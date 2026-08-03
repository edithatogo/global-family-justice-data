"""Build deterministic source-register health reports without network access."""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--register", type=Path, default=Path("data/seed/source_register.csv"))
    parser.add_argument("--output", type=Path, default=Path("build/source-monitor"))
    parser.add_argument("--as-of", default=dt.date.today().isoformat())
    args = parser.parse_args()
    as_of = dt.date.fromisoformat(args.as_of)
    rows = list(csv.DictReader(args.register.open(encoding="utf-8", newline="")))
    report = []
    for row in rows:
        verified = row.get("last_verified", "")
        age = None
        if verified:
            age = (as_of - dt.date.fromisoformat(verified)).days
        report.append(
            {
                "source_id": row.get("source_id", ""),
                "canonical_url_present": bool(row.get("source_url")),
                "last_verified": verified or None,
                "age_days": age,
                "licence_status": row.get("licence_status", "unknown"),
                "health": "review_required"
                if not row.get("source_url")
                or not verified
                or row.get("licence_status") in {"unknown", "restricted_or_unknown"}
                else "metadata_healthy",
            }
        )
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "source-monitor.json").write_text(
        json.dumps({"as_of": args.as_of, "network_access": False, "sources": report}, indent=2)
        + "\n",
        encoding="utf-8",
    )
    with (args.output / "source-monitor.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=report[0].keys() if report else ["source_id"])
        writer.writeheader()
        writer.writerows(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
