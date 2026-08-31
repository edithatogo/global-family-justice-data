"""Bounded Gold-preparation diagnostics; no semantic or disclosure acceptance.

Supplied rows remain unchanged. Only implementation fingerprinting reads files.
Counts and issue codes are technical observations, never promotion authority.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from . import quality

VERSION = "gfjd-gold-quality-checks-v1"
MAX_BYTES = 1024 * 1024
MAX_ROWS = 5000
MAX_FIELDS = 100
MAX_STRING_CHARS = 4096
MAX_NUMERIC_CHARS = 256
MAX_COEFFICIENT_DIGITS = 128
MAX_EXPONENT = 1000
SIGNATURE_FIELDS = (
    "statistic_type",
    "unit",
    "cohort_basis",
    "indicator_id",
    "matter_type_original",
    "matter_type_harmonised",
    "stage_start",
    "stage_end",
)
POLICY_KEYS = frozenset({"contract_version", "source_sha256", "small_cell_threshold"})


class QualityChecksError(ValueError):
    """Invalid bounded input or policy; no partial report is returned."""


def _require(condition: bool) -> None:
    if not condition:
        raise QualityChecksError("quality checks input contract violation")


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    _require(len(pairs) <= MAX_FIELDS)
    result = {}
    for key, value in pairs:
        _require(key not in result)
        result[key] = value
    return result


def _nonfinite(_value: str) -> None:
    raise QualityChecksError("nonfinite JSON input")


def _string(value: Any) -> None:
    _require(isinstance(value, str) and len(value) <= MAX_STRING_CHARS)
    _require(not any(0xD800 <= ord(char) <= 0xDFFF for char in value))


def _load(raw: bytes, policy: dict[str, Any]) -> list[dict[str, str]]:
    _require(isinstance(raw, bytes) and 0 < len(raw) <= MAX_BYTES)
    _require(isinstance(policy, dict) and set(policy) == POLICY_KEYS)
    _require(policy["contract_version"] == VERSION and policy["source_sha256"] == _sha(raw))
    threshold = policy["small_cell_threshold"]
    _require(type(threshold) is int and 1 <= threshold <= 100)
    rows = json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs, parse_constant=_nonfinite)
    _require(isinstance(rows, list) and 1 <= len(rows) <= MAX_ROWS)
    result = []
    for row in rows:
        _require(isinstance(row, dict) and len(row) <= MAX_FIELDS)
        for key, value in row.items():
            _string(key)
            _string(value)
        result.append(dict(row))
    return result


def _number(value: str) -> tuple[Decimal | None, str | None]:
    if len(value) > MAX_NUMERIC_CHARS:
        return None, "numeric_budget_exceeded"
    if re.fullmatch(r"[+-]?(?:inf(?:inity)?|s?nan[0-9]*)", value, re.IGNORECASE):
        return None, "nonfinite_value"
    match = re.fullmatch(r"([+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+))(?:[eE]([+-]?[0-9]+))?", value)
    if match is None:
        return None, "invalid_numeric_value"
    exponent = match[2] or "0"
    if (
        sum(char.isdigit() for char in match[1]) > MAX_COEFFICIENT_DIGITS
        or len(exponent) > 5
        or abs(int(exponent)) > MAX_EXPONENT
    ):
        return None, "numeric_budget_exceeded"
    number = Decimal(value)
    if not number.is_finite():
        return None, "nonfinite_value"
    return number, None


def _period(value: str) -> date | None:
    if re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value) is None:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _assess(rows_raw: bytes, policy: dict[str, Any]) -> dict[str, Any]:
    rows = _load(rows_raw, policy)
    required = (*quality.MANDATORY_GOLD_FIELDS, "value")
    identities = Counter(
        row.get("observation_id") for row in rows if row.get("observation_id", "").strip()
    )
    signatures: set[tuple[str, ...]] = set()
    issues = []
    counts = dict.fromkeys(
        [
            "rows_with_issues",
            "missing_required_fields",
            "blank_required_fields",
            "duplicate_observation_rows",
            "numeric_issue_rows",
            "period_issue_rows",
            "small_cell_rows",
            "small_cell_assessed_rows",
            "small_cell_unassessed_unit_rows",
            "small_cell_unassessed_value_rows",
            "incomplete_signature_rows",
        ],
        0,
    )
    for index, row in enumerate(rows):
        codes = []
        for field in required:
            if field not in row:
                codes.append(f"missing_required:{field}")
                counts["missing_required_fields"] += 1
            elif not row[field].strip():
                codes.append(f"blank_required:{field}")
                counts["blank_required_fields"] += 1
        if identities.get(row.get("observation_id"), 0) > 1:
            codes.append("duplicate_observation_id")
            counts["duplicate_observation_rows"] += 1
        number, number_issue = _number(row.get("value", ""))
        numeric_codes = []
        if number_issue:
            numeric_codes.append(number_issue)
        elif number is not None:
            if number < 0:
                numeric_codes.append("negative_value")
            if row.get("unit") == "percent" and not Decimal(0) <= number <= Decimal(100):
                numeric_codes.append("percent_out_of_range")
        codes.extend(numeric_codes)
        counts["numeric_issue_rows"] += bool(numeric_codes)
        if row.get("unit") != "count":
            counts["small_cell_unassessed_unit_rows"] += 1
        elif numeric_codes or number is None:
            counts["small_cell_unassessed_value_rows"] += 1
        else:
            counts["small_cell_assessed_rows"] += 1
            if 0 < number < policy["small_cell_threshold"]:
                counts["small_cell_rows"] += 1
                codes.append("small_cell_diagnostic")
        start, end = _period(row.get("period_start", "")), _period(row.get("period_end", ""))
        period_codes = []
        if start is None:
            period_codes.append("invalid_period_start")
        if end is None:
            period_codes.append("invalid_period_end")
        if start is not None and end is not None and start > end:
            period_codes.append("period_reversed")
        codes.extend(period_codes)
        counts["period_issue_rows"] += bool(period_codes)
        missing_signature = [field for field in SIGNATURE_FIELDS if not row.get(field, "").strip()]
        if missing_signature:
            counts["incomplete_signature_rows"] += 1
            codes.extend(f"missing_signature:{field}" for field in missing_signature)
        else:
            signatures.add(tuple(row[field] for field in SIGNATURE_FIELDS))
        counts["rows_with_issues"] += bool(codes)
        issues.append({"row_index": index, "issue_codes": sorted(set(codes))})
    counts["rows"] = len(rows)
    counts["comparability_signatures"] = len(signatures)
    report = {
        "contract_version": VERSION,
        "source_sha256": _sha(rows_raw),
        "policy_sha256": _sha(_canonical(policy)),
        "implementation_sha256": _sha(Path(__file__).read_bytes()),
        "mandatory_fields_implementation_sha256": _sha(Path(quality.__file__).read_bytes()),
        "required_fields": list(required),
        "signature_fields": list(SIGNATURE_FIELDS),
        "row_issues": issues,
        "counts": counts,
        "technical_checks": {
            "mandatory_fields_complete": counts["missing_required_fields"]
            == counts["blank_required_fields"]
            == 0,
            "observation_ids_unique": counts["duplicate_observation_rows"] == 0,
            "numeric_bounds_valid": counts["numeric_issue_rows"] == 0,
            "calendar_periods_ordered": counts["period_issue_rows"] == 0,
            "signature_components_complete": counts["incomplete_signature_rows"] == 0,
        },
        "comparability": "exact source-defined signature diversity only; equivalence not assessed",
        "numeric_scope": (
            "finite nonnegative exact decimals; upper bound 100 only for exact unit=percent; "
            "no unit inference"
        ),
        "small_cell_scope": (
            "only exact unit=count with a valid nonnegative value; not disclosure clearance"
        ),
        "period_scope": (
            "explicit YYYY-MM-DD calendar dates; equal endpoints allowed; no clock inference"
        ),
        "pending_reviews": ["semantic_review", "disclosure_review", "owner_decision"],
        "authority": dict.fromkeys(
            [
                "network",
                "source_access",
                "selection",
                "rights_clearance",
                "semantic_acceptance",
                "disclosure_acceptance",
                "owner_decision",
                "gold_promotion",
                "publication",
                "release",
                "gate_acceptance",
            ],
            False,
        ),
    }
    report["report_sha256"] = _sha(_canonical(report))
    return report


def assess_quality(rows_raw: bytes, policy: dict[str, Any]) -> dict[str, Any]:
    """Compute diagnostics without filtering, transforming or accepting any row."""
    try:
        return _assess(rows_raw, policy)
    except (
        ValueError,
        TypeError,
        KeyError,
        RecursionError,
        OverflowError,
        InvalidOperation,
        OSError,
    ):
        raise QualityChecksError("quality checks input invalid") from None


def verify_quality(rows_raw: bytes, policy: dict[str, Any], report: dict[str, Any]) -> None:
    """Recompute all diagnostics from the exact supplied source and policy."""
    try:
        _require(_canonical(report) == _canonical(assess_quality(rows_raw, policy)))
    except (ValueError, TypeError, RecursionError, OverflowError):
        raise QualityChecksError("quality checks report mismatch") from None
