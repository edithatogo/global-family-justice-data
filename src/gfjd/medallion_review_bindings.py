"""Bind supplied review claims to a scope and time, without authenticating them.

There is no identity lookup, signature verification, rights decision or source
access. Only this module's implementation fingerprint reads a local file.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

VERSION = "gfjd-review-binding-v1"
MAX_BYTES = 1024 * 1024
MAX_CODE_ITEMS = 100
MAX_ID_CHARS = 128
LAYERS = frozenset({"b0", "b1", "silver", "gold", "platinum"})
KINDS = frozenset({"rights", "semantic", "disclosure", "owner", "restore"})
STATUSES = frozenset({"accepted", "rejected", "pending"})
FIELDS = frozenset(
    {
        "contract_version",
        "object_id",
        "edition_id",
        "layer",
        "content_sha256",
        "review_kind",
        "decision_reference",
        "reviewer_reference",
        "issued_at",
        "expires_at",
        "status",
        "conditions",
        "conflicts",
    }
)


class ReviewBindingError(ValueError):
    """Malformed or mismatched review record, with fixed public error text."""


def _require(condition: bool) -> None:
    if not condition:
        raise ReviewBindingError("review binding contract violation")


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _identifier(value: Any) -> None:
    _require(isinstance(value, str) and 1 <= len(value) <= MAX_ID_CHARS)
    _require(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]*", value) is not None)


def _digest(value: Any) -> None:
    _require(isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None)


def _timestamp(value: Any) -> datetime:
    _require(isinstance(value, str) and len(value) <= 32)
    _require(
        re.fullmatch(
            r"[0-9]{4}-[0-9]{2}-[0-9]{2}T(?:[01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]"
            r"(?:\.[0-9]{1,6})?(?:Z|[+-](?:[01][0-9]|2[0-3]):[0-5][0-9])",
            value,
        )
        is not None
    )
    # Negative-zero may denote an unknown offset; never infer UTC from it.
    _require(not value.endswith("-00:00"))
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    _require(parsed.tzinfo is not None and parsed.utcoffset() is not None)
    return parsed


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    _require(len(pairs) <= len(FIELDS))
    result = {}
    for key, value in pairs:
        _require(key not in result)
        result[key] = value
    return result


def _nonfinite(_value: str) -> None:
    raise ReviewBindingError("invalid JSON constant")


def _codes(value: Any) -> None:
    _require(isinstance(value, list) and len(value) <= MAX_CODE_ITEMS)
    for item in value:
        _identifier(item)
    _require(len(value) == len(set(value)))


def _assess(raw: bytes, scope: dict[str, str]) -> dict[str, Any]:
    _require(isinstance(raw, bytes) and 0 < len(raw) <= MAX_BYTES)
    _identifier(scope["object_id"])
    _identifier(scope["edition_id"])
    _require(isinstance(scope["layer"], str) and scope["layer"] in LAYERS)
    _digest(scope["content_sha256"])
    clock = _timestamp(scope["as_of"])
    record = json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs, parse_constant=_nonfinite)
    _require(isinstance(record, dict) and set(record) == FIELDS)
    _require(record["contract_version"] == VERSION)
    for field in ("object_id", "edition_id", "layer", "content_sha256"):
        _require(record[field] == scope[field])
    _require(isinstance(record["review_kind"], str) and record["review_kind"] in KINDS)
    _require(isinstance(record["status"], str) and record["status"] in STATUSES)
    _identifier(record["decision_reference"])
    _identifier(record["reviewer_reference"])
    issued, expires = _timestamp(record["issued_at"]), _timestamp(record["expires_at"])
    _require(issued < expires)
    _codes(record["conditions"])
    _codes(record["conflicts"])
    temporal = "future" if clock < issued else "expired" if clock >= expires else "current"
    report = {
        "contract_version": VERSION,
        "record_sha256": _sha(raw),
        "scope_sha256": _sha(_canonical(scope)),
        "implementation_sha256": _sha(Path(__file__).read_bytes()),
        "scope": dict(scope),
        "scope_status": "scoped_record_bound",
        "temporal_status": temporal,
        "issued_at": record["issued_at"],
        "expires_at": record["expires_at"],
        "review_kind": record["review_kind"],
        "decision_reference": record["decision_reference"],
        "reviewer_reference": record["reviewer_reference"],
        "declared_status": record["status"],
        "conditions": list(record["conditions"]),
        "conflicts": list(record["conflicts"]),
        "conditions_present": bool(record["conditions"]),
        "conflicts_present": bool(record["conflicts"]),
        "authenticity_verified": False,
        "substantive_acceptance": False,
        "promotion_authorized": False,
        "limitations": [
            "identity_and_record_authenticity_not_verified",
            "declared_status_is_not_accountable_acceptance",
            "conditions_not_adjudicated_or_assumed_satisfied",
            "conflicts_not_adjudicated_or_assumed_resolved",
            "temporal_currentness_does_not_establish_factual_currency",
            "no_rights_source_access_publication_or_release_authority",
        ],
    }
    report["report_sha256"] = _sha(_canonical(report))
    return report


def assess_review(
    raw: bytes,
    *,
    object_id: str,
    edition_id: str,
    layer: str,
    content_sha256: str,
    as_of: str,
) -> dict[str, Any]:
    """Bind a declared record, never authenticate its signer or adjudicate status."""
    try:
        return _assess(
            raw,
            {
                "object_id": object_id,
                "edition_id": edition_id,
                "layer": layer,
                "content_sha256": content_sha256,
                "as_of": as_of,
            },
        )
    except (ValueError, TypeError, KeyError, RecursionError, OverflowError, OSError):
        raise ReviewBindingError("review binding input invalid") from None


def verify_review(
    raw: bytes,
    report: dict[str, Any],
    *,
    object_id: str,
    edition_id: str,
    layer: str,
    content_sha256: str,
    as_of: str,
) -> None:
    """Recompute scope, time and all false authority flags from supplied inputs."""
    try:
        expected = assess_review(
            raw,
            object_id=object_id,
            edition_id=edition_id,
            layer=layer,
            content_sha256=content_sha256,
            as_of=as_of,
        )
        _require(_canonical(report) == _canonical(expected))
    except (ValueError, TypeError, RecursionError, OverflowError):
        raise ReviewBindingError("review binding report mismatch") from None
