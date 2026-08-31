"""Shared supplied-byte metadata profile primitives; no JSON-LD resource loader."""

import hashlib
import json
import math
import re
from datetime import date
from typing import Any
from urllib.parse import urlsplit


class MetadataError(ValueError):
    """Rejected preparation input, without raw-data diagnostics."""


def require(condition: bool) -> None:
    if not condition:
        raise MetadataError("Metadata profile contract violation")


def _pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in items:
        require(key not in result)
        result[key] = value
    return result


def parse_json(raw: bytes) -> Any:
    try:
        require(type(raw) is bytes and 0 < len(raw) <= 1024 * 1024)
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs)
        pending = [(value, 0)]
        count = 0
        while pending:
            item, depth = pending.pop()
            count += 1
            require(count <= 10000 and depth <= 16)
            if isinstance(item, str):
                require(len(item) <= 4096)
                require(
                    all(
                        ord(c) >= 32 and not 127 <= ord(c) <= 159 and not 0xD800 <= ord(c) <= 0xDFFF
                        for c in item
                    )
                )
            elif isinstance(item, (dict, list)):
                require(len(item) <= 1000)
                children = list(item.items()) if isinstance(item, dict) else enumerate(item)
                for key, child in children:
                    if isinstance(item, dict):
                        pending.append((key, depth + 1))
                    pending.append((child, depth + 1))
            elif isinstance(item, float):
                require(math.isfinite(item))
        return value
    except Exception:
        raise MetadataError("Metadata profile contract violation") from None


def safe_url(value: Any) -> str:
    """Restricted HTTPS reference syntax only; never access or resolve it."""
    try:
        require(isinstance(value, str) and value.isascii())
        assert isinstance(value, str)
        require(len(value) <= 4096 and all(32 < ord(c) < 127 for c in value))
        require(value.count("#") <= 1)
        require(not re.search(r'[\s<>"{}|^`\\]', value))
        require(re.search(r"%(?![0-9A-Fa-f]{2})", value) is None)
        parsed = urlsplit(value)
        require(parsed.scheme == "https" and bool(parsed.hostname))
        require(parsed.username is None and parsed.password is None)
        require(parsed.port is None or 1 <= parsed.port <= 65535)
        require(
            all(
                re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?", label)
                for label in (parsed.hostname or "").split(".")
            )
        )
        return value
    except Exception:
        raise MetadataError("Metadata profile contract violation") from None


def date_label(value: Any) -> bool:
    """This profile supports explicit calendar dates, not inferred publication time."""
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return False
    try:
        date.fromisoformat(value)
        return True
    except ValueError:
        return False


def make_report(
    profile: str, raw: bytes, bindings: dict[str, str], issues: list[str]
) -> dict[str, Any]:
    return {
        "profile": profile,
        "status": "profile_incomplete" if issues else "profile_complete",
        "metadata_sha256": hashlib.sha256(raw).hexdigest(),
        "bindings": dict(sorted(bindings.items())),
        "issues": sorted(set(issues)),
        "coverage": "restricted-declaration-profile-only",
        "full_conformance": "unverified",
        "factual_evidence": "unverified",
        "authority": dict.fromkeys(
            (
                "network",
                "source_access",
                "publication",
                "release",
                "rights_clearance",
                "custody",
                "gold_promotion",
                "maturity",
                "gate_acceptance",
                "partner_registration",
            ),
            False,
        ),
    }
