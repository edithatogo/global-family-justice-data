#!/usr/bin/env python3
"""Verify G2 extractor workspace blindness before delegation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DENY_NAMES = {"output.json", "receipt.json", "concordance.json", "differences.json"}
DENY_TOKENS = ("expected", "gold", "comparator", "prior_output", "semantic_answer")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(run: Path) -> dict[str, object]:
    manifest = json.loads((run / "manifest.json").read_text())
    if manifest.get("expected_values_present") or manifest.get("prior_outputs_present"):
        raise SystemExit("blindness_failed:manifest_contains_prior_or_expected_values")
    results: dict[str, object] = {"run_id": manifest["run_id"], "roles": {}}
    sources = manifest["source_artifacts"]
    for role in ("extractor-a", "extractor-b"):
        workspace = run / role / "inputs"
        files = sorted(p for p in workspace.iterdir() if p.is_file())
        if {p.name for p in files} != set(sources):
            raise SystemExit(f"blindness_failed:{role}:unexpected_inputs")
        for path in files:
            if path.name.lower() in DENY_NAMES or any(t in path.name.lower() for t in DENY_TOKENS):
                raise SystemExit(f"blindness_failed:{role}:prohibited_name:{path.name}")
            if sha(path) != sources[path.name]:
                raise SystemExit(f"blindness_failed:{role}:digest_mismatch:{path.name}")
        results["roles"][role] = {"input_count": len(files), "prohibited_names": 0}
    results["status"] = "verified_blind_inputs"
    return results


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("run", type=Path)
    args = parser.parse_args()
    run = args.run if args.run.is_absolute() else ROOT / args.run
    result = verify(run)
    receipt = run / "blindness-verification.json"
    receipt.write_text(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n")
    print(json.dumps({"status": result["status"], "receipt": str(receipt.relative_to(ROOT))}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
