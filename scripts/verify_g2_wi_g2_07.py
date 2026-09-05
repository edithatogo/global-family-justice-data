#!/usr/bin/env python3
"""Verify WI-G2-07 terminal evidence without promoting it."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(root: Path) -> dict[str, object]:
    packet = root / "data/methods/g2/G2PKT-MATERIAL-ORCHESTRATED-20260826-01/packet.json"
    terminal = root / "data/methods/g2/G2PKT-MATERIAL-ORCHESTRATED-20260826-01/terminal-result.json"
    packet_bytes = digest(packet)
    terminal_bytes = digest(terminal)
    result = json.loads(terminal.read_text(encoding="utf-8"))
    metrics = result["metrics"]
    passed = (
        metrics["critical_concordance"] == metrics["critical_threshold"]
        and metrics["overall_populated_concordance"] >= metrics["overall_threshold"]
    )
    return {
        "schema_version": "1.0",
        "work_item": "WI-G2-07",
        "packet_sha256": packet_bytes,
        "terminal_result_sha256": terminal_bytes,
        "metrics": metrics,
        "status": "threshold_pass" if passed else "terminal_failed_below_threshold",
        "promotion_authorized": False,
        "owner_adjudication": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = verify(args.root.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "promotion_authorized": False}))
    return 0 if report["status"] == "threshold_pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
