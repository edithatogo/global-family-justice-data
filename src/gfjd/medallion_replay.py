"""Bounded offline string projection; receipts never authorize layer promotion."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

VERSION = "gfjd-json-projection-v1"
MAX_BYTES = 1024 * 1024
MAX_ROWS = 1000
MAX_FIELDS = 64
MAX_CELLS = 10000


class ProjectionReplayError(ValueError):
    """Invalid input, contract or replay evidence; no result may be promoted."""


def _canonical(value: Any) -> bytes:
    try:
        return json.dumps(
            value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode("utf-8")
    except (TypeError, ValueError, UnicodeError, RecursionError) as exc:
        raise ProjectionReplayError("value is not canonical JSON") from exc


def _sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ProjectionReplayError("duplicate JSON key")
        result[key] = value
    return result


def _timestamp(value: Any, *, nullable: bool = False) -> None:
    if nullable and value is None:
        return
    if not isinstance(value, str) or not re.fullmatch(
        r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z", value
    ):
        raise ProjectionReplayError("timestamps must be explicit UTC instants")
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ProjectionReplayError("invalid timestamp") from exc


def _pointer(row: int, field: str) -> str:
    return f"/{row}/{field.replace('~', '~0').replace('/', '~1')}"


def replay_projection(source: bytes, contract: dict[str, Any]) -> dict[str, Any]:
    """Rebuild an unpromoted candidate from exact supplied bytes and explicit mapping.

    Performs no acquisition, source assessment or writes. Callers must enforce
    handling/custody controls. Unknown source-valid time stays null; neither
    clock is inferred. Only this module is hashed as the transformation identity.
    """

    if not isinstance(source, bytes) or not 0 < len(source) <= MAX_BYTES:
        raise ProjectionReplayError("source byte budget exceeded or invalid bytes")
    if not isinstance(contract, dict) or set(contract) != {
        "contract_version",
        "source_sha256",
        "projection",
        "valid_from",
        "recorded_at",
    }:
        raise ProjectionReplayError("contract fields must match the versioned contract")
    if contract["contract_version"] != VERSION:
        raise ProjectionReplayError("unsupported projection contract")
    if contract["source_sha256"] != _sha(source):
        raise ProjectionReplayError("source digest mismatch")
    _timestamp(contract["valid_from"], nullable=True)
    _timestamp(contract["recorded_at"])
    projection = contract["projection"]
    if (
        not isinstance(projection, dict)
        or not 0 < len(projection) <= MAX_FIELDS
        or not all(
            isinstance(target, str)
            and target.strip()
            and isinstance(origin, str)
            and origin.strip()
            for target, origin in projection.items()
        )
        or len(set(projection.values())) != len(projection)
    ):
        raise ProjectionReplayError("projection must contain unique nonempty string fields")
    try:
        source_rows = json.loads(source.decode("utf-8"), object_pairs_hook=_unique_object)
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise ProjectionReplayError("invalid source JSON or duplicate key") from exc
    if not isinstance(source_rows, list) or not 0 < len(source_rows) <= MAX_ROWS:
        raise ProjectionReplayError("source row budget exceeded or invalid row array")
    if len(source_rows) * len(projection) > MAX_CELLS:
        raise ProjectionReplayError("projected cell budget exceeded")
    rows: list[dict[str, str]] = []
    lineage: list[dict[str, Any]] = []
    for ordinal, row in enumerate(source_rows):
        if (
            not isinstance(row, dict)
            or not 0 < len(row) <= MAX_FIELDS
            or not all(isinstance(value, str) for value in row.values())
        ):
            raise ProjectionReplayError("source rows must be bounded string-valued objects")
        output: dict[str, str] = {}
        for target in sorted(projection):
            origin = projection[target]
            if origin not in row:
                raise ProjectionReplayError("mapped source field is missing")
            value = row[origin]
            output[target] = value
            lineage.append(
                {
                    "output_pointer": _pointer(ordinal, target),
                    "source_pointer": _pointer(ordinal, origin),
                    "value_sha256": _sha(_canonical(value)),
                }
            )
        rows.append(output)
    receipt = {
        "contract_version": VERSION,
        "source_sha256": _sha(source),
        "contract_sha256": _sha(_canonical(contract)),
        "implementation_sha256": _sha(Path(__file__).read_bytes()),
        "valid_from": contract["valid_from"],
        "recorded_at": contract["recorded_at"],
        "rows": rows,
        "field_lineage": lineage,
        "promotion_authorized": False,
    }
    receipt["snapshot_sha256"] = _sha(_canonical(receipt))
    return receipt


def verify_projection(source: bytes, contract: dict[str, Any], receipt: dict[str, Any]) -> None:
    """Require an exact full recomputation; never trust self-reported result hashes."""

    expected = replay_projection(source, contract)
    if _canonical(receipt) != _canonical(expected):
        raise ProjectionReplayError("receipt does not match exact recomputed projection")
