#!/usr/bin/env python3
"""Monitor one frozen official publication-index endpoint without opening results."""

from __future__ import annotations

import argparse
import hashlib
import json
import urllib.error
import urllib.request
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast
from urllib.parse import urlparse

from gfjd.g2_official_publication_feed import evaluate_response, write_exposure_ledger


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(  # noqa: PLR0913
        self,
        req: urllib.request.Request,
        fp: Any,
        code: int,
        msg: str,
        headers: Any,
        newurl: str,
    ) -> None:
        return None


def _read_bounded(response: Any, limit: int) -> bytes:
    body = cast(bytes, response.read(limit + 1))
    if len(body) > limit:
        raise ValueError("response byte budget exceeded")
    return body


def _known_urls(paths: list[str]) -> set[str]:
    known: set[str] = set()
    for raw_path in paths:
        path = Path(raw_path)
        if path.suffix == ".jsonl":
            for line in path.read_text(encoding="utf-8").splitlines():
                if line:
                    row = json.loads(line)
                    url = row.get("url")
                    if isinstance(url, str):
                        known.add(url)
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        urls = payload.get("exposure", {}).get("urls")
        if not isinstance(urls, list) or not all(isinstance(url, str) for url in urls):
            raise ValueError(f"unsupported exposure source: {path}")
        known.update(urls)
    return known


def _write_receipt(
    output: Path,
    *,
    contract: dict[str, Any],
    checked_at: datetime,
    source_commit: str,
    run_id: str,
    request_record: dict[str, object] | None,
    summary: Mapping[str, object],
    ledger_digest: str,
    status: str,
    error: str | None = None,
) -> None:
    receipt = {
        "schema_version": "1.0",
        "campaign_id": contract["campaign_id"],
        "status": status,
        "checked_at": checked_at.astimezone(UTC).isoformat().replace("+00:00", "Z"),
        "source_commit": source_commit,
        "run_id": run_id,
        "cutoff": contract["exposure_cutoff"],
        "request": request_record,
        "summary": summary,
        "exposure_ledger_sha256": ledger_digest,
        "boundary": {
            "result_url_access": False,
            "candidate_document_access": False,
            "extraction": False,
            "rights_clearance": False,
            "g2_acceptance": False,
            "publication": False,
            "release": False,
        },
    }
    if error is not None:
        receipt["error"] = error
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
    checked_at = datetime.fromisoformat(args.checked_at.replace("Z", "+00:00"))
    if checked_at.tzinfo is None:
        raise ValueError("checked-at must include a timezone")
    cutoff = datetime.fromisoformat(contract["exposure_cutoff"].replace("Z", "+00:00"))
    endpoint = contract["endpoint"]
    endpoint_parts = urlparse(endpoint)
    if (
        endpoint_parts.scheme != "https"
        or endpoint_parts.hostname != contract["allowed_endpoint_host"]
        or endpoint_parts.path != contract["allowed_endpoint_path"]
        or endpoint_parts.username is not None
        or endpoint_parts.password is not None
        or endpoint_parts.fragment
    ):
        raise ValueError("prohibited endpoint binding")

    args.output.mkdir(parents=True, exist_ok=True)
    ledger = args.output / "exposure-ledger.jsonl"
    known_urls = _known_urls(contract["cumulative_exposure_sources"])
    request_record: dict[str, object] | None = None
    try:
        request = urllib.request.Request(
            endpoint,
            headers={"Accept": "application/json", "User-Agent": "GFJD-G2-feed-monitor/1.0"},
        )
        opener = urllib.request.build_opener(_NoRedirect)
        with opener.open(request, timeout=int(contract["request_timeout_seconds"])) as response:
            if response.status != 200:
                raise ValueError(f"non-success HTTP status {response.status}")
            body = _read_bounded(response, int(contract["maximum_response_bytes"]))
            if response.geturl() != endpoint:
                raise ValueError("redirect or effective URL mismatch")
            content_type = response.headers.get_content_type()
            if content_type != "application/json":
                raise ValueError(f"unexpected content type {content_type}")
        request_record = {
            "url": endpoint,
            "http_status": 200,
            "content_type": content_type,
            "response_bytes": len(body),
            "response_sha256": hashlib.sha256(body).hexdigest(),
        }
        payload = json.loads(body)
        if not isinstance(payload, dict):
            raise ValueError("response root must be an object")
        observations, summary = evaluate_response(
            payload,
            cutoff=cutoff,
            endpoint_count=int(contract["endpoint_count"]),
            allowed_locator_hosts=set(contract["allowed_locator_hosts"]),
            allowed_link_prefixes=set(contract["allowed_link_prefixes"]),
            eligible_formats=set(contract["eligible_formats"]),
            minimum_candidate_count=int(contract["minimum_candidate_count"]),
        )
        ledger_digest = write_exposure_ledger(observations, ledger)
    except (json.JSONDecodeError, OSError, TypeError, ValueError, urllib.error.HTTPError) as exc:
        partial_digest = hashlib.sha256(ledger.read_bytes() if ledger.exists() else b"").hexdigest()
        _write_receipt(
            args.output,
            contract=contract,
            checked_at=checked_at,
            source_commit=args.source_commit,
            run_id=args.run_id,
            request_record=request_record,
            summary={"outcome": "terminal_failure"},
            ledger_digest=partial_digest,
            status="terminal_failure",
            error=str(exc),
        )
        return 2

    novel = [observation for observation in observations if observation.url not in known_urls]
    novel_digest = write_exposure_ledger(novel, args.output / "novel-exposure-ledger.jsonl")
    outcome = str(summary["outcome"])
    if novel and outcome != "candidate_threshold_met":
        outcome = "unconsolidated_exposure"
    final_summary = {
        **summary,
        "outcome": outcome,
        "novel_exposure_count": len(novel),
        "novel_exposure_ledger_sha256": novel_digest,
    }
    _write_receipt(
        args.output,
        contract=contract,
        checked_at=checked_at,
        source_commit=args.source_commit,
        run_id=args.run_id,
        request_record=request_record,
        summary=final_summary,
        ledger_digest=ledger_digest,
        status="complete" if outcome == "monitor_no_candidates" else "action_required",
    )
    print(json.dumps(final_summary, indent=2, sort_keys=True))
    if outcome == "candidate_threshold_met":
        return 3
    if outcome == "unconsolidated_exposure":
        return 4
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
