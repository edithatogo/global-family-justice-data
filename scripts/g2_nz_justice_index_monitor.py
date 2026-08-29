#!/usr/bin/env python3
"""Monitor the exact NZ justice-statistics index without opening file links."""

from __future__ import annotations

import argparse
import hashlib
import json
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast
from urllib.parse import urlparse

from gfjd.g2_nz_justice_index import evaluate_index


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args: Any, **kwargs: Any) -> None:
        return None


def _write(output: Path, payload: dict[str, Any]) -> None:
    output.mkdir(parents=True, exist_ok=True)
    (output / "receipt.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--checked-at", required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    contract = json.loads(args.contract.read_text(encoding="utf-8"))
    checked = datetime.fromisoformat(args.checked_at.replace("Z", "+00:00"))
    checked_text = checked.astimezone(UTC).isoformat().replace("+00:00", "Z")
    endpoint = contract["endpoint"]
    request_record: dict[str, Any] = {"url": endpoint, "method": "GET"}
    base = {
        "schema_version": "1.0",
        "campaign_id": contract["campaign_id"],
        "checked_at": checked_text,
        "source_commit": args.source_commit,
        "run_id": args.run_id,
        "boundary": contract["authority_boundary"],
    }
    try:
        parsed = urlparse(endpoint)
        if (
            parsed.scheme != "https"
            or parsed.hostname != contract["allowed_host"]
            or parsed.path != contract["allowed_path"]
            or parsed.query
            or parsed.fragment
        ):
            raise ValueError("prohibited endpoint binding")
        request = urllib.request.Request(
            endpoint,
            headers={"Accept": "text/html", "User-Agent": "GFJD-G2-NZ-index-monitor/1.0"},
        )
        with urllib.request.build_opener(_NoRedirect).open(
            request, timeout=contract["request_timeout_seconds"]
        ) as response:
            body = cast(bytes, response.read(contract["maximum_response_bytes"] + 1))
            if response.status != 200 or response.geturl() != endpoint:
                raise ValueError("endpoint response contract failed")
            if len(body) > contract["maximum_response_bytes"]:
                raise ValueError("response byte budget exceeded")
            if response.headers.get_content_type() != "text/html":
                raise ValueError("unexpected response content type")
        request_record.update(
            response_bytes=len(body), response_sha256=hashlib.sha256(body).hexdigest()
        )
        observation, outcome = evaluate_index(body.decode("utf-8"), contract)
    except (
        UnicodeDecodeError,
        json.JSONDecodeError,
        OSError,
        TypeError,
        ValueError,
        urllib.error.HTTPError,
    ) as exc:
        _write(
            args.output,
            {
                **base,
                "status": "terminal_failure",
                "request": request_record,
                "summary": {"outcome": "terminal_failure", "candidate_eligibility": False},
                "error": str(exc),
            },
        )
        return 2
    _write(
        args.output,
        {
            **base,
            "status": "complete" if outcome == "baseline_unchanged" else "action_required",
            "request": request_record,
            "observation": observation,
            "summary": {"outcome": outcome, "candidate_eligibility": False},
        },
    )
    print(json.dumps({"outcome": outcome, "candidate_eligibility": False}, sort_keys=True))
    return 3 if outcome == "review_required" else 0


if __name__ == "__main__":
    raise SystemExit(main())
