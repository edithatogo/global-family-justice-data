#!/usr/bin/env python3
"""Observe four exact official family-law metadata records without table data."""

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

from gfjd.g2_statcan_metadata import evaluate_metadata


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args: Any, **kwargs: Any) -> None:
        return None


def _write_receipt(output: Path, receipt: dict[str, Any]) -> None:
    output.mkdir(parents=True, exist_ok=True)
    (output / "receipt.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
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
    args.output.mkdir(parents=True, exist_ok=True)
    checked_at = datetime.fromisoformat(args.checked_at.replace("Z", "+00:00"))
    checked_at_text = checked_at.astimezone(UTC).isoformat().replace("+00:00", "Z")
    endpoint = contract["endpoint"]
    request_body = json.dumps(
        [{"productId": value} for value in contract["product_ids"]],
        separators=(",", ":"),
    ).encode()
    request_record: dict[str, Any] = {
        "url": endpoint,
        "method": "POST",
        "body_sha256": hashlib.sha256(request_body).hexdigest(),
    }
    try:
        parsed = urlparse(endpoint)
        if (
            parsed.scheme != "https"
            or parsed.hostname != contract["allowed_endpoint_host"]
            or parsed.path != contract["allowed_endpoint_path"]
            or parsed.query
            or parsed.fragment
        ):
            raise ValueError("prohibited endpoint binding")
        request = urllib.request.Request(
            endpoint,
            data=request_body,
            method="POST",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "GFJD-G2-StatCan-metadata-monitor/1.0",
            },
        )
        opener = urllib.request.build_opener(_NoRedirect)
        with opener.open(request, timeout=contract["request_timeout_seconds"]) as response:
            body = cast(bytes, response.read(contract["maximum_response_bytes"] + 1))
            if response.status != 200 or response.geturl() != endpoint:
                raise ValueError("endpoint response contract failed")
            if len(body) > contract["maximum_response_bytes"]:
                raise ValueError("response byte budget exceeded")
            if response.headers.get_content_type() != "application/json":
                raise ValueError("unexpected response content type")
        request_record.update(
            response_bytes=len(body), response_sha256=hashlib.sha256(body).hexdigest()
        )
        cutoff = datetime.fromisoformat(contract["exposure_cutoff"].replace("Z", "+00:00"))
        observations, summary = evaluate_metadata(
            json.loads(body),
            product_ids=contract["product_ids"],
            expected_titles=contract["expected_titles"],
            cutoff=cutoff,
        )
    except (json.JSONDecodeError, OSError, TypeError, ValueError, urllib.error.HTTPError) as exc:
        _write_receipt(
            args.output,
            {
                "schema_version": "1.0",
                "campaign_id": contract["campaign_id"],
                "status": "terminal_failure",
                "checked_at": checked_at_text,
                "source_commit": args.source_commit,
                "run_id": args.run_id,
                "request": request_record,
                "summary": {"outcome": "terminal_failure", "eligibility_established": False},
                "error": str(exc),
                "boundary": contract["authority_boundary"],
            },
        )
        return 2
    (args.output / "observations.json").write_text(
        json.dumps(observations, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    receipt = {
        "schema_version": "1.0",
        "campaign_id": contract["campaign_id"],
        "status": "complete" if summary["outcome"] == "monitor_no_update" else "action_required",
        "checked_at": checked_at_text,
        "source_commit": args.source_commit,
        "run_id": args.run_id,
        "request": request_record,
        "summary": summary,
        "boundary": contract["authority_boundary"],
    }
    _write_receipt(args.output, receipt)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 3 if summary["outcome"] == "review_required" else 0


if __name__ == "__main__":
    raise SystemExit(main())
