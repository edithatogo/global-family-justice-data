"""Rehearse anonymous two-provider restore of the public B0 custody cohort.

Only digest, size, URL and status metadata are persisted. Restored bytes live in
a temporary directory and are removed before the receipt is written.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlparse


CONTRACT_VERSION = "gfjd-public-b0-restore-rehearsal-v1"
MAX_OBJECT_BYTES = 500_000_000
ALLOWED_PREFIXES = {
    "github": "https://github.com/",
    "huggingface": "https://huggingface.co/",
}
Fetcher = Callable[[str, int], tuple[bytes, int]]


def _fetch(url: str, expected_size: int) -> tuple[bytes, int]:
    request = urllib.request.Request(url, headers={"User-Agent": "gfjd-public-restore/1"})
    with urllib.request.urlopen(request, timeout=120) as response:  # noqa: S310
        data = response.read(expected_size + 1)
        return data, int(response.status)


def rehearse(custody: dict[str, Any], *, fetcher: Fetcher | None = None) -> dict[str, Any]:
    objects = custody.get("objects")
    if not isinstance(objects, list) or not objects:
        raise ValueError("custody manifest has no objects")
    retrieve = fetcher or _fetch
    observations: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="gfjd-public-restore-") as temporary_root:
        root = Path(temporary_root)
        for item in objects:
            inventory_id = str(item.get("inventory_id", ""))
            expected_size = int(item.get("size_bytes", 0))
            expected_sha = str(item.get("sha256", ""))
            if not inventory_id or not expected_sha or not 0 < expected_size <= MAX_OBJECT_BYTES:
                raise ValueError(f"invalid custody object: {inventory_id}")
            for replica in item.get("replicas", []):
                provider = str(replica.get("provider", ""))
                url = str(replica.get("url", ""))
                prefix = ALLOWED_PREFIXES.get(provider)
                if prefix is None or not url.startswith(prefix) or urlparse(url).scheme != "https":
                    raise ValueError(f"{inventory_id}: unapproved restore URL")
                record: dict[str, Any] = {
                    "inventory_id": inventory_id,
                    "provider": provider,
                    "url": url,
                    "expected_sha256": expected_sha,
                    "expected_size_bytes": expected_size,
                }
                try:
                    data, http_status = retrieve(url, expected_size)
                    actual_sha = hashlib.sha256(data).hexdigest()
                    restored_path = root / provider / inventory_id
                    restored_path.parent.mkdir(parents=True, exist_ok=True)
                    restored_path.write_bytes(data)
                    record.update(
                        {
                            "http_status": http_status,
                            "actual_sha256": actual_sha,
                            "actual_size_bytes": len(data),
                            "state": (
                                "restored"
                                if http_status == 200
                                and len(data) == expected_size
                                and actual_sha == expected_sha
                                else "mismatch"
                            ),
                        }
                    )
                except (OSError, ValueError, urllib.error.URLError) as exc:
                    record.update({"state": "unavailable", "error_type": type(exc).__name__})
                observations.append(record)
        restored = [item for item in observations if item["state"] == "restored"]
        tree_material = "\n".join(
            f"{item['provider']}|{item['inventory_id']}|{item['actual_sha256']}|{item['actual_size_bytes']}"
            for item in sorted(restored, key=lambda value: (value["provider"], value["inventory_id"]))
        ).encode()
        tree_sha = hashlib.sha256(tree_material).hexdigest()
    status = "pass" if len(observations) == len(objects) * 2 and len(restored) == len(observations) else "fail"
    return {
        "contract_version": CONTRACT_VERSION,
        "status": status,
        "object_count": len(objects),
        "replica_count": len(observations),
        "provider_count": len({item["provider"] for item in observations}),
        "observations": observations,
        "restore_tree_sha256": tree_sha,
        "temporary_bytes_deleted": True,
        "source_bytes_persisted": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--custody", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--observed-at", required=True)
    args = parser.parse_args()
    datetime.fromisoformat(args.observed_at.replace("Z", "+00:00"))
    custody_bytes = args.custody.read_bytes()
    custody = json.loads(custody_bytes)
    report = rehearse(custody)
    report.update(
        {
            "observed_at": args.observed_at,
            "custody_path": args.custody.as_posix(),
            "custody_sha256": hashlib.sha256(custody_bytes).hexdigest(),
        }
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "replica_count": report["replica_count"]}))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
