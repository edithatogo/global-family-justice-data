"""Supplied-byte B0 fixity and bounded scanner mechanics, not public clearance.

Only implementation fingerprinting reads files. PDF/unknown containers remain
unsupported; no temporary files, subprocesses, remote reads, or rights inference.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import zipfile
import zlib
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

from blake3 import blake3

from . import medallion_pipeline, medallion_xlsx, public_archive

MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_RECEIPT_BYTES = 1024 * 1024
XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def _require(condition: bool) -> None:
    if not condition:
        raise ValueError("B0 validation failed")


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    _require(len(pairs) <= 128)
    result = {}
    for key, value in pairs:
        _require(key not in result)
        result[key] = value
    return result


def _nonfinite(value: str) -> None:
    raise ValueError("B0 validation failed")


def _json(raw: bytes, *, limit: int) -> Any:
    _require(isinstance(raw, bytes) and 0 < len(raw) <= limit)
    root = json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs, parse_constant=_nonfinite)
    pending = [(root, 1)]
    nodes = 0
    while pending:
        value, depth = pending.pop()
        nodes += 1
        _require(nodes <= 10000 and depth <= 16)
        if isinstance(value, dict):
            pending.extend((key, depth + 1) for key in value)
            pending.extend((item, depth + 1) for item in value.values())
        elif isinstance(value, list):
            _require(len(value) <= 1000)
            pending.extend((item, depth + 1) for item in value)
        elif isinstance(value, float):
            _require(math.isfinite(value))
        elif isinstance(value, str):
            _require(
                len(value) <= 4096 and not any(0xD800 <= ord(char) <= 0xDFFF for char in value)
            )
    return root


def _receipt(raw: bytes, evidence: dict[str, Any], key: str) -> dict[str, Any]:
    _require(isinstance(raw, bytes) and 0 < len(raw) <= MAX_RECEIPT_BYTES)
    _require(evidence.get(key) == _sha(raw))
    value = _json(raw, limit=MAX_RECEIPT_BYTES)
    _require(isinstance(value, dict))
    return dict(value)


def _scan(source: bytes, media: str) -> tuple[str, list[str]]:
    if media == XLSX:
        try:
            # Every ZIP member passes hard budgets and bounded CRC reads before
            # any broad scanner runs. Never call the unbounded _scan_zip path.
            members = medallion_xlsx._package(source)
            _require({"[Content_Types].xml", "xl/workbook.xml"} <= members.keys())
            medallion_xlsx._xmls(members)
            findings = []
            for name, raw in members.items():
                findings.extend(public_archive._scan_bytes(raw, "supplied-member"))
                if name.lower().endswith(".csv"):
                    findings.extend(public_archive._scan_csv_headers(raw, "supplied-member"))
        except (
            ValueError,
            TypeError,
            KeyError,
            OSError,
            RuntimeError,
            zipfile.BadZipFile,
            zlib.error,
            ElementTree.ParseError,
        ):
            return "failed", ["XLSX_CONTAINER_SCAN_FAILED"]
    elif media in {"text/plain", "text/csv", "application/json"}:
        if source.startswith((b"PK", b"%PDF")):
            return "unsupported", ["UNSUPPORTED_CONTAINER"]
        try:
            text = source.decode("utf-8-sig")
            if "\x00" in text:
                return "unsupported", ["UNSUPPORTED_ENCODING"]
            if media == "application/json":
                _json(source, limit=MAX_SOURCE_BYTES)
        except (ValueError, UnicodeError, RecursionError):
            return "failed", ["SOURCE_TEXT_OR_JSON_INVALID"]
        findings = public_archive._scan_bytes(source, "supplied-source")
        if media == "text/csv":
            findings.extend(public_archive._scan_csv_headers(source, "supplied-source"))
    else:
        return "unsupported", ["UNSUPPORTED_MEDIA_TYPE"]
    codes = sorted({finding.code for finding in findings})
    return ("failed" if codes else "verified"), codes


def _assess(
    source: bytes,
    evidence: dict[str, Any],
    *,
    object_id: str,
    safety_raw: bytes | None,
    custody_raw: bytes | None,
) -> dict[str, Any]:
    _require(isinstance(source, bytes) and 0 < len(source) <= MAX_SOURCE_BYTES)
    _require(isinstance(evidence, dict))
    _require(
        isinstance(object_id, str)
        and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}", object_id) is not None
    )
    digest, b3 = _sha(source), blake3(source).hexdigest()
    _require(evidence.get("content_sha256") == digest and evidence.get("content_blake3") == b3)
    _require(type(evidence.get("size_bytes")) is int and evidence["size_bytes"] == len(source))
    media = evidence.get("media_type")
    _require(isinstance(media, str) and 0 < len(media) <= 128 and "/" in media)
    safety = None
    if safety_raw is not None:
        safety = _receipt(safety_raw, evidence, "safety_receipt_sha256")
        _require(safety.get("contract_version") == public_archive.CONTRACT_VERSION)
        _require(safety.get("status") in {"pass", "fail"})
        objects = medallion_pipeline._objects(safety)
        _require(object_id in objects)
        selected = objects[object_id]
        _require(selected.get("sha256") == digest and selected.get("blake3") == b3)
        _require(type(selected.get("size_bytes")) is int and selected["size_bytes"] == len(source))
        _require(selected.get("disposition") in {"public_safe", "blocked"})
        _require(isinstance(selected.get("findings"), list))
    custody_status = "missing"
    if custody_raw is not None:
        custody = _receipt(custody_raw, evidence, "custody_receipt_sha256")
        _require(safety is not None and safety_raw is not None)
        assert safety is not None and safety_raw is not None
        _require(custody.get("safety_receipt_sha256") == _sha(safety_raw))
        medallion_pipeline._custody(safety, custody, object_id)
        custody_status = "consistent"
    scan_status, codes = _scan(source, str(media))
    safety_status = scan_status
    if safety is not None and (
        safety["status"] != "pass"
        or selected["disposition"] != "public_safe"
        or selected["findings"]
    ):
        safety_status = "failed"
        codes.append("RECORDED_SAFETY_NOT_PASS")
    elif scan_status == "verified" and safety is None:
        safety_status = "missing"
    report = {
        "contract_version": "gfjd-b0-qualification-checks-v1",
        "object_id": object_id,
        "source_sha256": digest,
        "content_blake3": b3,
        "size_bytes": len(source),
        "evidence_sha256": _sha(_canonical(evidence)),
        "safety_receipt_sha256": _sha(safety_raw) if safety_raw is not None else None,
        "custody_receipt_sha256": _sha(custody_raw) if custody_raw is not None else None,
        "checks": {"fixity": "verified", "safety": safety_status, "custody": custody_status},
        "scan_status": scan_status,
        "finding_codes": sorted(codes),
        "scan_scope": "bounded credential patterns and CSV headers; XLSX container/XML bounds",
        "pending_requirements": [
            "capture_authenticity",
            "rights",
            "current_remote_custody",
            "comprehensive_privacy_and_public_safety",
        ],
        "current_remote_custody_verified": False,
        "implementation_sha256": _sha(Path(__file__).read_bytes()),
        "scanner_implementation_sha256": _sha(Path(public_archive.__file__).read_bytes()),
        "container_implementation_sha256": _sha(Path(medallion_xlsx.__file__).read_bytes()),
        "custody_implementation_sha256": _sha(Path(medallion_pipeline.__file__).read_bytes()),
        "authority": dict.fromkeys(
            (
                "network",
                "source_access",
                "rights_clearance",
                "promotion",
                "publication",
                "release",
                "gate_acceptance",
            ),
            False,
        ),
    }
    report["report_sha256"] = _sha(_canonical(report))
    return report


def assess_b0(
    source: bytes,
    evidence: dict[str, Any],
    *,
    object_id: str,
    safety_raw: bytes | None = None,
    custody_raw: bytes | None = None,
) -> dict[str, Any]:
    """Recompute fixity/limited scan and check asserted custody consistency only."""
    try:
        return _assess(
            source, evidence, object_id=object_id, safety_raw=safety_raw, custody_raw=custody_raw
        )
    except (
        ValueError,
        TypeError,
        KeyError,
        AttributeError,
        OSError,
        OverflowError,
        RecursionError,
    ):
        raise ValueError("B0 validation failed") from None


def verify_b0(
    source: bytes,
    evidence: dict[str, Any],
    report: dict[str, Any],
    *,
    object_id: str,
    safety_raw: bytes | None = None,
    custody_raw: bytes | None = None,
) -> None:
    expected = assess_b0(
        source, evidence, object_id=object_id, safety_raw=safety_raw, custody_raw=custody_raw
    )
    try:
        _require(_canonical(expected) == _canonical(report))
    except (ValueError, TypeError, OverflowError, RecursionError):
        raise ValueError("B0 validation failed") from None
