"""Capture live GitHub control evidence without confusing access errors for absence."""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def classify_response(status: int, payload: Any) -> dict[str, Any]:
    """Return a fail-closed observation for a GitHub API response."""
    if status == 200:
        return {"state": "available", "payload": payload}
    if status == 403:
        return {"state": "forbidden", "payload": payload}
    if status == 404:
        return {"state": "not_found_or_unavailable", "payload": payload}
    return {"state": "error", "status": status, "payload": payload}


def verify_capture(capture: dict[str, Any], *, max_age_days: int = 7) -> list[str]:
    errors: list[str] = []
    recorded = capture.get("recorded_at")
    if not isinstance(recorded, str):
        return ["missing recorded_at"]
    try:
        age = datetime.now(UTC) - datetime.fromisoformat(recorded)
    except ValueError:
        return ["invalid recorded_at"]
    if age.days > max_age_days:
        errors.append("capture is stale")
    endpoints = capture.get("endpoints")
    if not isinstance(endpoints, dict) or not endpoints:
        errors.append("missing endpoint observations")
    return errors


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
