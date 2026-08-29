#!/usr/bin/env python3
"""Monitor exact official sitemap endpoints without opening returned locators."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlparse

from gfjd.g2_future_monitor import ObservedLocator, evaluate_entries, write_exposure_ledger
from gfjd.g2_sitemap_stream import iter_sitemap_entries


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001, ANN201
        return None


def _read_bounded(response, limit: int) -> bytes:  # noqa: ANN001
    body = response.read(limit + 1)
    if len(body) > limit:
        raise ValueError("response byte budget exceeded")
    return body


def _known_exposures(paths: list[str]) -> set[tuple[str, str | None]]:
    known: set[tuple[str, str | None]] = set()
    for raw_path in paths:
        for line in Path(raw_path).read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            known.add((row["url"], row.get("lastmod")))
    return known


def _write_receipt(
    output: Path,
    *,
    contract: dict,
    checked_at: datetime,
    requests: list[dict[str, object]],
    summary: dict[str, object],
    ledger_digest: str,
    status: str,
    error: str | None = None,
) -> None:
    receipt = {
        "schema_version": "1.0",
        "campaign_id": contract["campaign_id"],
        "status": status,
        "checked_at": checked_at.astimezone(UTC).isoformat().replace("+00:00", "Z"),
        "cutoff": contract["exposure_cutoff"],
        "requests": requests,
        "summary": summary,
        "exposure_ledger_sha256": ledger_digest,
        "boundary": {
            "returned_locator_access": False,
            "candidate_document_access": False,
            "extraction": False,
            "g2_acceptance": False,
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
    args = parser.parse_args()
    contract = json.loads(args.contract.read_text(encoding="utf-8"))
    checked_at = datetime.fromisoformat(args.checked_at.replace("Z", "+00:00"))
    if checked_at.tzinfo is None:
        raise ValueError("checked-at must include a timezone")
    cutoff = datetime.fromisoformat(contract["exposure_cutoff"].replace("Z", "+00:00"))
    rules = contract["execution_rules"]
    endpoints = contract["ordered_endpoints"]
    known_exposures = _known_exposures(contract["cumulative_exposure_ledgers"])
    opener = urllib.request.build_opener(_NoRedirect)
    total_limit = int(rules["maximum_total_uncompressed_bytes"])
    total_bytes = 0
    parsed: list[tuple[str, list]] = []
    requests: list[dict[str, object]] = []
    args.output.mkdir(parents=True, exist_ok=True)
    ledger = args.output / "exposure-ledger.jsonl"
    for ordinal, endpoint in enumerate(endpoints, 1):
        try:
            endpoint_parts = urlparse(endpoint)
            if (
                endpoint_parts.scheme != "https"
                or endpoint_parts.hostname != contract["allowed_locator_host"]
                or endpoint_parts.username is not None
                or endpoint_parts.password is not None
            ):
                raise ValueError(f"prohibited endpoint binding at ordinal {ordinal}")
            request = urllib.request.Request(
                endpoint, headers={"User-Agent": "GFJD-G2-monitor/1.0"}
            )
            with opener.open(request, timeout=120) as response:
                if response.status != 200:
                    raise ValueError(f"non-success HTTP status {response.status}")
                body = _read_bounded(response, total_limit - total_bytes)
                effective = response.geturl()
                if effective != endpoint:
                    raise ValueError("redirect or effective URL mismatch")
                content_type = response.headers.get_content_type()
            total_bytes += len(body)
            entries = list(iter_sitemap_entries(io.BytesIO(body)))
            parsed.append((endpoint, entries))
            requests.append(
                {
                    "ordinal": ordinal,
                    "url": endpoint,
                    "http_status": 200,
                    "content_type": content_type,
                    "response_bytes": len(body),
                    "response_sha256": hashlib.sha256(body).hexdigest(),
                    "locator_count": len(entries),
                }
            )
            raw_observations = [
                ObservedLocator(endpoint_no, endpoint_url, entry_no, entry.url, entry.lastmod)
                for endpoint_no, (endpoint_url, endpoint_entries) in enumerate(parsed, 1)
                for entry_no, entry in enumerate(endpoint_entries, 1)
            ]
            ledger_digest = write_exposure_ledger(raw_observations, ledger)
            observations, summary = evaluate_entries(
                parsed,
                cutoff=cutoff,
                allowed_host=contract["allowed_locator_host"],
                maximum_locator_count=int(rules["maximum_locator_count"]),
            )
            _write_receipt(
                args.output,
                contract=contract,
                checked_at=checked_at,
                requests=requests,
                summary={**summary, "total_response_bytes": total_bytes},
                ledger_digest=ledger_digest,
                status="in_progress",
            )
        except (OSError, ValueError, urllib.error.HTTPError) as exc:
            partial = ledger.read_bytes() if ledger.exists() else b""
            _write_receipt(
                args.output,
                contract=contract,
                checked_at=checked_at,
                requests=requests,
                summary={
                    "outcome": "terminal_failure",
                    "completed_endpoint_count": len(requests),
                    "total_response_bytes": total_bytes,
                },
                ledger_digest=hashlib.sha256(partial).hexdigest(),
                status="terminal_failure",
                error=str(exc),
            )
            return 2
    novel = [
        observation
        for observation in observations
        if (observation.url, observation.lastmod) not in known_exposures
    ]
    novel_digest = write_exposure_ledger(novel, args.output / "novel-exposure-ledger.jsonl")
    outcome = str(summary["outcome"])
    if novel and outcome != "candidate_threshold_met":
        outcome = "unconsolidated_exposure"
    final_summary = {
        **summary,
        "outcome": outcome,
        "novel_exposure_count": len(novel),
        "novel_exposure_ledger_sha256": novel_digest,
        "total_response_bytes": total_bytes,
    }
    _write_receipt(
        args.output,
        contract=contract,
        checked_at=checked_at,
        requests=requests,
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
