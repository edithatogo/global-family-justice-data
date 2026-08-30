"""Pure, bounded structural diagnostics; no transport, values or eligibility.

Unknown-name hashes are fingerprints, not anonymization. This component is
synthetic-tested preparation, not a validated publisher schema or access grant.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections import Counter
from typing import Any

MAX_BYTES = 2 * 1024 * 1024
MAX_DEPTH = 16
MAX_NODES = 10000
MAX_MEMBERS = 128
MAX_ARRAY = 1000
KNOWN = frozenset({"results", "total", "start", "link", "title", "format", "public_timestamp"})
ROW_FIELDS = ("format", "link", "public_timestamp", "title")


class _Invalid(ValueError):
    pass


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise _Invalid("duplicate_key")
        result[key] = value
    return result


def _number(value: str) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise _Invalid("nonfinite_number")
    return number


def _constant(value: str) -> Any:
    raise _Invalid("nonfinite_number")


def _kind(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    return "object" if isinstance(value, dict) else "array"


def inspect_shape(raw: bytes) -> dict[str, Any]:
    """Inspect structure only; never emit scalar contents or authorize a stage."""
    report: dict[str, Any] = {
        "schema_version": "1.0",
        "purpose": "offline_structural_diagnostics",
        "input_bytes": len(raw),
        "input_sha256": None,
        "inspection_complete": False,
        "enumeration_complete": None,
        "eligibility": "not_assessed",
        "authority": dict.fromkeys(
            (
                "network",
                "source_access",
                "extraction",
                "rights_clearance",
                "publication",
                "release",
                "maturity",
                "g2_acceptance",
            ),
            False,
        ),
    }
    if len(raw) > MAX_BYTES:
        return {**report, "status": "limit_stop", "code": "byte_limit"}
    report["input_sha256"] = hashlib.sha256(raw).hexdigest()
    try:
        payload = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_pairs,
            parse_float=_number,
            parse_constant=_constant,
        )
    except _Invalid as error:
        return {**report, "status": "invalid_input", "code": str(error)}
    except (ValueError, UnicodeError, RecursionError):
        return {**report, "status": "invalid_input", "code": "invalid_json_or_encoding"}

    types: Counter[str] = Counter()
    fields: dict[str, Counter[str]] = {}
    stack = [(payload, 0)]
    nodes = 0
    while stack:
        value, depth = stack.pop()
        nodes += 1
        if depth > MAX_DEPTH or nodes > MAX_NODES:
            return {**report, "status": "limit_stop", "code": "depth_or_node_limit"}
        types[_kind(value)] += 1
        if isinstance(value, dict):
            if len(value) > MAX_MEMBERS:
                return {**report, "status": "limit_stop", "code": "object_member_limit"}
            for key, child in value.items():
                identity = (
                    "known:" + key
                    if key in KNOWN
                    else "hash:"
                    + hashlib.sha256(
                        b"gfjd-metadata-field-v1\0" + key.encode("utf-8", "surrogatepass")
                    ).hexdigest()
                )
                fields.setdefault(identity, Counter())[_kind(child)] += 1
                stack.append((child, depth + 1))
        elif isinstance(value, list):
            if len(value) > MAX_ARRAY:
                return {**report, "status": "limit_stop", "code": "array_member_limit"}
            stack.extend((child, depth + 1) for child in value)

    report.update(
        status="structural_diagnostics_only",
        inspection_complete=True,
        types=dict(sorted(types.items())),
        fields=[
            {
                **(
                    {"name": identity[6:]}
                    if identity.startswith("known:")
                    else {"name_sha256": identity[5:]}
                ),
                "types": dict(sorted(counts.items())),
            }
            for identity, counts in sorted(fields.items())
        ],
        field_scope="pooled_all_object_levels_not_semantic_paths",
    )
    if isinstance(payload, dict):
        report["missing_root_fields"] = sorted({"results", "total"} - payload.keys())
        rows = payload.get("results")
        report["results_type"] = _kind(rows) if "results" in payload else "absent"
        if isinstance(rows, list):
            report["result_count"] = len(rows)
            report["nonobject_rows"] = sum(not isinstance(row, dict) for row in rows)
            report["missing_row_fields"] = {
                name: sum(name not in row for row in rows if isinstance(row, dict))
                for name in ROW_FIELDS
            }
    else:
        report["root_type"] = _kind(payload)
    return report
