"""Capture live GitHub control evidence without confusing access errors for absence."""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from gfjd.github_controls import classify_response, verify_capture


def capture(repo: str) -> dict[str, Any]:
    endpoints = {
        "repository": f"repos/{repo}",
        "rulesets": f"repos/{repo}/rulesets",
        "environments": f"repos/{repo}/environments",
        "actions_permissions": f"repos/{repo}/actions/permissions",
        "security": f"repos/{repo}/code-scanning/alerts",
    }
    observations: dict[str, Any] = {}
    for name, endpoint in endpoints.items():
        result = subprocess.run(
            ["gh", "api", endpoint], capture_output=True, text=True, check=False
        )
        try:
            payload: Any = json.loads(result.stdout or result.stderr)
        except json.JSONDecodeError:
            payload = {"raw": (result.stdout or result.stderr).strip()}
        status = (
            result.returncode
            if result.returncode in {403, 404}
            else 200
            if result.returncode == 0
            else 500
        )
        observations[name] = classify_response(status, payload)
    return {
        "schema_version": "1.0",
        "repository": repo,
        "recorded_at": datetime.now(UTC).isoformat(),
        "endpoints": observations,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    payload = json.loads(args.output.read_text()) if args.verify else capture(args.repo)
    if args.verify:
        errors = verify_capture(payload)
        if errors:
            print("\n".join(errors))
            return 1
        print("GitHub control capture verified")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
