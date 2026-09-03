#!/usr/bin/env python3
"""Build or independently verify the shared medallion compatibility receipt."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from gfjd.shared_medallion_contracts import (
    SharedMedallionError,
    build_compatibility_report,
    verify_compatibility_report,
)


def _encode(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--output", type=Path)
    group.add_argument("--verify", type=Path)
    args = parser.parse_args()
    try:
        if args.output is not None:
            report = build_compatibility_report()
            target = args.output
            target.parent.mkdir(parents=True, exist_ok=True)
            temporary = target.with_name(f".{target.name}.tmp")
            temporary.write_bytes(_encode(report))
            temporary.replace(target)
            print(f"shared medallion compatibility receipt written: {target}")
        else:
            raw = args.verify.read_bytes()
            report = json.loads(raw)
            verify_compatibility_report(report)
            if raw != _encode(report):
                raise SharedMedallionError("receipt is not canonical JSON")
            print("shared medallion compatibility receipt verified")
    except (OSError, ValueError, TypeError, SharedMedallionError) as exc:
        print(f"shared medallion compatibility verification failed: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
