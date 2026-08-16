"""Fail-closed traversal of digest-bound G2 exposure-ledger chains."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from gfjd.g2_metadata_search_successor import canonical_url


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _safe_path(root: Path, relative: str) -> Path | None:
    candidate = Path(relative)
    if candidate.is_absolute() or ".." in candidate.parts or candidate.as_posix() != relative:
        return None
    path = root / candidate
    try:
        if not path.resolve().is_relative_to(root.resolve()):
            return None
    except (OSError, RuntimeError):
        return None
    current = root
    for part in candidate.parts:
        current /= part
        if current.is_symlink():
            return None
    return path


def collect_bound_exposure_chain(
    root: Path, descriptor: dict[str, str], *, max_depth: int = 32
) -> tuple[set[str], list[dict[str, str]], list[str]]:
    """Collect canonical URLs from every verified predecessor ledger."""
    urls: set[str] = set()
    ledgers: list[dict[str, str]] = []
    errors: list[str] = []
    seen: set[tuple[str, str]] = set()
    if max_depth < 1:
        return urls, ledgers, ["exposure predecessor max_depth must be positive"]
    current: Any = descriptor
    for _ in range(max_depth):
        if current is None:
            return urls, ledgers, errors
        if (
            not isinstance(current, dict)
            or set(current) != {"path", "sha256"}
            or not all(isinstance(current.get(key), str) for key in ("path", "sha256"))
        ):
            return urls, ledgers, errors + ["exposure predecessor descriptor is malformed"]
        identity = (current["path"], current["sha256"])
        if identity in seen:
            return urls, ledgers, errors + ["exposure predecessor chain contains a cycle"]
        seen.add(identity)
        path = _safe_path(root, current["path"])
        if path is None or not path.is_file() or _sha(path) != current["sha256"]:
            return urls, ledgers, errors + ["exposure predecessor binding mismatch"]
        ledgers.append(dict(current))
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            return urls, ledgers, errors + ["exposure predecessor ledger is invalid JSON"]
        if not isinstance(payload, dict):
            return urls, ledgers, errors + ["exposure predecessor ledger must be an object"]
        denied_urls = payload.get("denied_urls", [])
        entries = payload.get("entries", [])
        if not isinstance(denied_urls, list) or not all(
            isinstance(value, str) for value in denied_urls
        ):
            return urls, ledgers, errors + ["exposure denied_urls must contain strings"]
        if not isinstance(entries, list) or not all(isinstance(entry, dict) for entry in entries):
            return urls, ledgers, errors + ["exposure entries must contain objects"]
        values = set(denied_urls)
        for entry in entries:
            for key in ("url", "landing_page_url"):
                value = entry.get(key)
                if value is not None and not isinstance(value, str):
                    return urls, ledgers, errors + ["exposure entry URL must be a string"]
                if value:
                    values.add(value)
            entry_urls = entry.get("urls", [])
            if not isinstance(entry_urls, list) or not all(
                isinstance(value, str) for value in entry_urls
            ):
                return urls, ledgers, errors + ["exposure entry urls must contain strings"]
            values.update(entry_urls)
        urls.update(canonical_url(value) for value in values)
        current = payload.get("predecessor")
    return urls, ledgers, errors + ["exposure predecessor chain exceeds maximum depth"]
