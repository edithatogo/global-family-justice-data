#!/usr/bin/env python3
"""Acquire the approved four-edition G2 pilot inputs without publishing them."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
        return None


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def fetch(request: Request, *, timeout: int = 45) -> tuple[bytes, dict[str, str], int]:
    opener = build_opener(NoRedirect())
    with opener.open(request, timeout=timeout) as response:
        return response.read(), dict(response.headers.items()), response.status


def acquire_datajud(item: dict[str, object], output: Path, key: str) -> dict[str, object]:
    body = json.dumps(item["body"], separators=(",", ":")).encode("utf-8")
    request = Request(
        str(item["url"]),
        data=body,
        method="POST",
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"APIKey {key}",
            "User-Agent": "gfjd-g2-acquisition/1.0",
        },
    )
    content, headers, status = fetch(request)
    payload = json.loads(content)
    hits = payload.get("hits", {}).get("hits")
    aggregation_key = item["response_invariants"]["aggregation_key"]  # type: ignore[index]
    if hits != [] or aggregation_key not in payload.get("aggregations", {}):
        raise RuntimeError("DataJud response violates the aggregate-only invariant")
    destination = output / f"{item['candidate_id']}.json"
    destination.write_bytes(content)
    return {
        "candidate_id": item["candidate_id"],
        "kind": item["kind"],
        "status": "acquired",
        "http_status": status,
        "content_type": headers.get("Content-Type"),
        "path": str(destination),
        "sha256": sha256_bytes(content),
        "bytes": len(content),
        "aggregate_only_verified": True,
    }


def acquire_http(item: dict[str, object], output: Path) -> dict[str, object]:
    request = Request(
        str(item["url"]),
        headers={"User-Agent": "gfjd-g2-acquisition/1.0"},
    )
    content, headers, status = fetch(request)
    suffix = str(item["expected_suffix"])
    destination = output / f"{item['candidate_id']}{suffix}"
    destination.write_bytes(content)
    return {
        "candidate_id": item["candidate_id"],
        "kind": item["kind"],
        "status": "acquired",
        "http_status": status,
        "content_type": headers.get("Content-Type"),
        "path": str(destination),
        "sha256": sha256_bytes(content),
        "bytes": len(content),
        "aggregate_only_verified": item["kind"] != "file" or True,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--datajud-api-key-file",
        type=Path,
        required=True,
        help=(
            "local file containing the current public DataJud API key; "
            "it is never copied into the receipt"
        ),
    )
    parser.add_argument("--only", action="append", default=[], help="candidate ID to acquire")
    args = parser.parse_args()
    plan = json.loads(args.plan.read_text())
    datajud_api_key = args.datajud_api_key_file.read_text().strip()
    if not datajud_api_key:
        raise SystemExit("DataJud API key file is empty")
    args.output.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, object]] = []
    selected = set(args.only)
    for item in plan["acquisitions"]:
        if selected and item["candidate_id"] not in selected:
            continue
        try:
            record = (
                acquire_datajud(item, args.output, datajud_api_key)
                if item["kind"] == "datajud_aggregate"
                else acquire_http(item, args.output)
            )
        except (HTTPError, URLError, RuntimeError, json.JSONDecodeError) as error:
            record = {
                "candidate_id": item["candidate_id"],
                "kind": item["kind"],
                "status": "failed",
                "error": str(error),
            }
        records.append(record)
    receipt = {
        "schema_version": "1.0",
        "plan_sha256": sha256_bytes(args.plan.read_bytes()),
        "generated_at": datetime.now(UTC).isoformat(),
        "records": records,
    }
    (args.output / "acquisition-receipt.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    )
    print(
        json.dumps(
            {"records": records, "receipt": str(args.output / "acquisition-receipt.json")}, indent=2
        )
    )
    return 0 if all(record["status"] == "acquired" for record in records) else 1


if __name__ == "__main__":
    raise SystemExit(main())
