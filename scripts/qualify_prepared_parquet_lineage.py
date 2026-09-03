#!/usr/bin/env python3
"""Empirically qualify repository-visible Parquet products and field lineage.

This is deliberately fail-closed: declarations and synthetic fixtures are
reported separately from real Parquet bytes and cannot be promoted by this
tool.  No network or remote locator is accessed.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from gfjd.shared_medallion_contracts import build_compatibility_report

ROOT = Path(__file__).resolve().parents[1]


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def qualify() -> dict[str, object]:
    parquet = sorted(
        p for p in ROOT.rglob("*") if p.is_file() and p.suffix.lower() in {".parquet", ".pq"}
    )
    observed = []
    for path in parquet:
        raw = path.read_bytes()
        observed.append(
            {
                "path": path.relative_to(ROOT).as_posix(),
                "sha256": hashlib.sha256(raw).hexdigest(),
                "bytes": len(raw),
                "parquet_magic": len(raw) >= 8 and raw[:4] == b"PAR1" and raw[-4:] == b"PAR1",
            }
        )
    compatibility = build_compatibility_report()
    lineage = compatibility["positive_canaries"]
    return {
        "contract_version": "gfjd-prepared-parquet-lineage-qualification-v1",
        "scope": "repository-visible prepared products; network disabled",
        "parquet_products": observed,
        "real_parquet_payload_count": sum(bool(x["parquet_magic"]) for x in observed),
        "field_lineage_canary_count": sum(x["version"] == "v2" for x in lineage),
        "field_lineage_canaries_schema_valid": all(x["status"] == "conformant" for x in lineage),
        "status": "qualified_preparation_only"
        if not observed
        else "payloads_require_schema_and_lineage_checks",
        "limitations": (
            [
                "No repository-visible Parquet payload bytes were found; "
                "declarations are not payload evidence."
            ]
            if not observed
            else [
                "Observed Parquet magic bytes require complete schema, digest and "
                "field-lineage qualification before use.",
            ]
        )
        + [
            "Field-lineage qualification is limited to schema/canary "
            "conformance, not factual source lineage.",
            "Remote availability, custody, rights, partner interoperability "
            "and accountable promotion remain unverified.",
        ],
    }


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--output", type=Path)
    group.add_argument("--verify", type=Path)
    args = parser.parse_args()
    report = qualify()
    encoded = (json.dumps(report, indent=2, sort_keys=True) + "\n").encode()
    if args.verify:
        if args.verify.read_bytes() != encoded:
            raise SystemExit("qualification receipt mismatch")
    else:
        assert args.output is not None
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(encoded)
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
