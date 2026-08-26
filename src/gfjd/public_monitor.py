"""Anonymous public-custody monitoring and append-only supersession checks."""

from __future__ import annotations

import hashlib
import ipaddress
import json
import socket
import urllib.error
import urllib.request
from collections.abc import Callable
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from blake3 import blake3

from .public_archive import verify_custody_receipt

MONITOR_CONTRACT_VERSION = "gfjd-public-b0-monitor-v1"
SUPERSESSION_CONTRACT_VERSION = "gfjd-public-b0-supersession-v1"
ALLOWED_FINAL_HOST_SUFFIXES = (
    "github.com",
    "githubusercontent.com",
    "cdn.hf.co",
    "huggingface.co",
    "xethub.hf.co",
)


class PublicMonitorError(ValueError):
    """Raised for an invalid monitoring or supersession contract."""


Fetcher = Callable[[str, int], tuple[bytes, int, str]]


def monitor_custody(
    root: Path,
    custody_path: Path,
    *,
    checked_at: str,
    source_commit: str,
    run_id: str,
    fetcher: Fetcher | None = None,
) -> dict[str, Any]:
    """Retrieve every replica without a cache and emit a digest-only receipt."""

    errors = verify_custody_receipt(root, custody_path)
    if errors:
        raise PublicMonitorError("invalid custody receipt: " + "; ".join(errors))
    custody_bytes = custody_path.read_bytes()
    custody = json.loads(custody_bytes)
    retrieve = fetcher or _fetch_public
    observations: list[dict[str, Any]] = []
    for item in custody["objects"]:
        for replica in item["replicas"]:
            observation: dict[str, Any] = {
                "inventory_id": item["inventory_id"],
                "provider": replica["provider"],
                "url": replica["url"],
                "expected_sha256": item["sha256"],
                "expected_blake3": item["blake3"],
                "expected_size_bytes": item["size_bytes"],
            }
            try:
                data, http_status, final_url = retrieve(replica["url"], item["size_bytes"])
                actual_sha = hashlib.sha256(data).hexdigest()
                actual_blake = blake3(data).hexdigest()
                final_host = (urlparse(final_url).hostname or "").lower()
                matches = (
                    http_status == 200
                    and len(data) == item["size_bytes"]
                    and actual_sha == item["sha256"]
                    and actual_blake == item["blake3"]
                    and _allowed_final_host(final_host)
                )
                observation.update(
                    {
                        "http_status": http_status,
                        "final_host": final_host,
                        "actual_sha256": actual_sha,
                        "actual_blake3": actual_blake,
                        "actual_size_bytes": len(data),
                        "state": "available" if matches else "drift",
                    }
                )
            except (OSError, ValueError, urllib.error.URLError) as exc:
                observation.update({"state": "unavailable", "error_type": type(exc).__name__})
            observations.append(observation)
    status = "pass" if all(item["state"] == "available" for item in observations) else "fail"
    return {
        "contract_version": MONITOR_CONTRACT_VERSION,
        "checked_at": checked_at,
        "source_commit": source_commit,
        "run_id": run_id,
        "custody_receipt_path": custody_path.relative_to(root.resolve()).as_posix(),
        "custody_receipt_sha256": hashlib.sha256(custody_bytes).hexdigest(),
        "status": status,
        "observations": observations,
    }


def verify_monitor_receipt(receipt: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if receipt.get("contract_version") != MONITOR_CONTRACT_VERSION:
        errors.append("unsupported monitor contract_version")
    observations = receipt.get("observations")
    if not isinstance(observations, list) or not observations:
        return [*errors, "monitor observations are missing"]
    keys: set[tuple[str, str]] = set()
    for item in observations:
        key = (str(item.get("inventory_id", "")), str(item.get("provider", "")))
        if key in keys or not all(key):
            errors.append("monitor observation identities must be non-empty and unique")
        keys.add(key)
        if item.get("state") == "available":
            if item.get("http_status") != 200:
                errors.append(f"{key}: available observation lacks HTTP 200")
            for algorithm in ("sha256", "blake3"):
                if item.get(f"actual_{algorithm}") != item.get(f"expected_{algorithm}"):
                    errors.append(f"{key}: available observation has {algorithm} drift")
            if item.get("actual_size_bytes") != item.get("expected_size_bytes"):
                errors.append(f"{key}: available observation has size drift")
            if not _allowed_final_host(str(item.get("final_host", ""))):
                errors.append(f"{key}: available observation has unapproved final host")
    expected_status = (
        "pass" if all(item.get("state") == "available" for item in observations) else "fail"
    )
    if receipt.get("status") != expected_status:
        errors.append("monitor status does not match recomputed observations")
    return errors


def verify_supersession(path: Path) -> tuple[list[str], list[str]]:
    """Verify unique nodes, acyclic edges and return deterministic replay order."""

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return [f"invalid supersession record: {exc}"], []
    errors: list[str] = []
    if payload.get("contract_version") != SUPERSESSION_CONTRACT_VERSION:
        errors.append("unsupported supersession contract_version")
    nodes = payload.get("nodes", [])
    node_ids = [str(node.get("snapshot_id", "")) for node in nodes]
    if any(not node_id for node_id in node_ids) or len(node_ids) != len(set(node_ids)):
        errors.append("snapshot IDs must be non-empty and unique")
    adjacency: dict[str, set[str]] = {node_id: set() for node_id in node_ids}
    indegree: dict[str, int] = {node_id: 0 for node_id in node_ids}
    edge_keys: set[tuple[str, str]] = set()
    for edge in payload.get("edges", []):
        before = str(edge.get("supersedes", ""))
        after = str(edge.get("snapshot_id", ""))
        key = (before, after)
        if key in edge_keys:
            errors.append("supersession edges must be unique")
            continue
        edge_keys.add(key)
        if before == after or before not in adjacency or after not in adjacency:
            errors.append(f"invalid supersession edge: {before}->{after}")
            continue
        adjacency[before].add(after)
        indegree[after] += 1
    ready = sorted(node_id for node_id, degree in indegree.items() if degree == 0)
    order: list[str] = []
    while ready:
        node_id = ready.pop(0)
        order.append(node_id)
        for successor in sorted(adjacency[node_id]):
            indegree[successor] -= 1
            if indegree[successor] == 0:
                ready.append(successor)
                ready.sort()
    if len(order) != len(node_ids):
        errors.append("supersession graph contains a cycle")
    return errors, order


def write_monitor_receipt(receipt: dict[str, Any], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _fetch_public(url: str, expected_size: int) -> tuple[bytes, int, str]:
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname:
        raise PublicMonitorError("replica URL must be HTTPS")
    request = urllib.request.Request(url, headers={"User-Agent": "GFJD-public-monitor/1"})
    with urllib.request.urlopen(request, timeout=60) as response:  # noqa: S310
        final_url = response.geturl()
        final_host = (urlparse(final_url).hostname or "").lower()
        if not _allowed_final_host(final_host):
            raise PublicMonitorError("redirected to an unapproved host")
        try:
            for result in socket.getaddrinfo(final_host, 443, type=socket.SOCK_STREAM):
                address = ipaddress.ip_address(str(result[4][0]))
                if not address.is_global:
                    raise PublicMonitorError("public replica resolved to a private address")
        except socket.gaierror as exc:
            raise PublicMonitorError("public replica DNS resolution failed") from exc
        data = response.read(expected_size + 1)
        if len(data) > expected_size:
            raise PublicMonitorError("replica exceeds expected size")
        return data, int(response.status), final_url


def _allowed_final_host(host: str) -> bool:
    return any(
        host == suffix or host.endswith("." + suffix) for suffix in ALLOWED_FINAL_HOST_SUFFIXES
    )
