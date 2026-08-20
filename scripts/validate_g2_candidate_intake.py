"""Validate an offline proposed G2 candidate-metadata intake.

This command performs no network activity.  It prints a deterministic JSON
screening result and returns non-zero when the intake is exposed or invalid.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from gfjd.g2_candidate_intake import validate_candidate_intake


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    result = validate_candidate_intake(root, args.input)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "prepared_metadata_only" else 2


if __name__ == "__main__":
    raise SystemExit(main())
