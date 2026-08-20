"""Run the bounded, metadata-only G2 official-manifest-root discovery.

The endpoint set is derived solely from official entries in the checked-in
source register. It requests only each host's ``robots.txt`` and ``sitemap.xml``
with redirects disabled. It never requests a registered source URL, follows a
locator, downloads a source file, or persists response bodies.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import ssl
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, HTTPSHandler, Request, build_opener

MAX_BYTES = 131_072
TIMEOUT_SECONDS = 15
PATHS = ("/robots.txt", "/sitemap.xml")


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args: Any, **kwargs: Any) -> None:
        return None


def _endpoints(source_register: Path) -> list[dict[str, str]]:
    with source_register.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    hosts = sorted(
        {
            (urlsplit(row["source_url"]).hostname or "").lower()
            for row in rows
            if row["official_status"] == "official"
        }
    )
    if not hosts or any(not host for host in hosts):
        raise ValueError("source register lacks official HTTPS hosts")
    return [
        {"host": host, "endpoint": f"https://{host}{path}", "kind": path[1:-4]}
        for host in hosts
        for path in PATHS
    ]


def _fetch(endpoint: str) -> dict[str, Any]:
    opener = build_opener(NoRedirect(), HTTPSHandler(context=ssl.create_default_context()))
    request = Request(endpoint, headers={"User-Agent": "GFJD-manifest-root-discovery/1.0"})
    try:
        with opener.open(request, timeout=TIMEOUT_SECONDS) as response:
            payload = response.read(MAX_BYTES + 1)
            return {
                "status": int(response.status),
                "content_type": response.headers.get_content_type(),
                "bytes_read": len(payload),
                "response_sha256": hashlib.sha256(payload[:MAX_BYTES]).hexdigest(),
                "oversize": len(payload) > MAX_BYTES,
                "redirected": False,
            }
    except HTTPError as error:
        return {
            "status": int(error.code),
            "error": "http_error",
            "redirected": 300 <= error.code < 400,
        }
    except (TimeoutError, URLError, OSError, ValueError):
        return {"status": None, "error": "request_error", "redirected": False}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    register = root / "data/seed/source_register.csv"
    endpoints = _endpoints(register)
    records = [{**item, **_fetch(item["endpoint"])} for item in endpoints]
    payload = {
        "schema_version": "1.0",
        "discovery_id": "G2OFFICIAL-MANIFEST-ROOT-DISCOVERY-20260821-01",
        "executed_at": datetime.now(UTC).isoformat(),
        "source_register_sha256": hashlib.sha256(register.read_bytes()).hexdigest(),
        "network_scope": {
            "endpoint_count": len(endpoints),
            "redirects_followed": False,
            "registered_source_urls_requested": False,
            "source_files_requested": False,
            "source_content_persisted": False,
            "outbound_contacts": False,
        },
        "records": records,
        "limitations": [
            "Only standard host metadata endpoints were requested.",
            "Response bodies were not persisted or interpreted as source evidence.",
            "A successful endpoint is a locator hypothesis, not a source-rights or G2 finding.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    failures = [record for record in records if record.get("redirected") or record.get("oversize")]
    return 2 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
