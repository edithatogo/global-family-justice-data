"""Bounded source-faithful PDF fact extraction for private replay.

The adapter accepts only a digest-bound page/marker/regular-expression contract.
It returns a hashed match, not source excerpts.  It does not assess rights or
promote a result to any medallion layer.
"""

from __future__ import annotations

import hashlib
import io
import json
import re
from pathlib import Path
from typing import Any

from pypdf import PdfReader

VERSION = "gfjd-medallion-pdf-v1"
MAX_SOURCE_BYTES = 32 * 1024 * 1024
MAX_PAGES = 4000
MAX_TEXT = 4 * 1024 * 1024
CONTRACT_KEYS = frozenset(
    {"extraction_version", "source_sha256", "page_number", "markers", "pattern"}
)


class MedallionPdfError(ValueError):
    """Fail-closed PDF extraction error."""


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def _require(condition: bool) -> None:
    if not condition:
        raise MedallionPdfError("medallion PDF contract violation")


def extract_pdf(source: bytes, contract: dict[str, Any]) -> dict[str, Any]:
    """Extract one explicit numeric fact from one explicit PDF page."""
    try:
        _require(isinstance(source, bytes) and 0 < len(source) <= MAX_SOURCE_BYTES)
        _require(isinstance(contract, dict) and set(contract) == CONTRACT_KEYS)
        _require(contract["extraction_version"] == VERSION)
        _require(contract["source_sha256"] == _sha(source))
        page_number = contract["page_number"]
        _require(type(page_number) is int and 1 <= page_number <= MAX_PAGES)
        markers = contract["markers"]
        _require(
            isinstance(markers, list)
            and 1 <= len(markers) <= 16
            and all(isinstance(marker, str) and 0 < len(marker) <= 512 for marker in markers)
        )
        pattern = contract["pattern"]
        _require(isinstance(pattern, str) and 1 <= len(pattern) <= 1024)
        reader = PdfReader(io.BytesIO(source), strict=True)
        _require(0 < len(reader.pages) <= MAX_PAGES)
        _require(page_number <= len(reader.pages))
        text = reader.pages[page_number - 1].extract_text() or ""
        _require(isinstance(text, str) and len(text) <= MAX_TEXT)
        _require(all(marker in text for marker in markers))
        matches = list(re.finditer(pattern, text, flags=re.MULTILINE))
        _require(len(matches) == 1 and matches[0].groupdict().get("value") is not None)
        raw_value = matches[0].group("value").replace(",", "").strip()
        _require(re.fullmatch(r"[0-9]+(?:\.[0-9]+)?", raw_value) is not None)
        value: int | float = float(raw_value) if "." in raw_value else int(raw_value)
        matched = matches[0].group(0)
        result = {
            "extraction_version": VERSION,
            "source_sha256": _sha(source),
            "contract_sha256": _sha(_canonical(contract)),
            "implementation_sha256": _sha(Path(__file__).read_bytes()),
            "page_number": page_number,
            "matched_text_sha256": _sha(matched.encode()),
            "value": value,
            "promotion_authorized": False,
        }
        return result
    except MedallionPdfError:
        raise
    except Exception as exc:
        raise MedallionPdfError("medallion PDF extraction failed") from exc


def verify_pdf(source: bytes, contract: dict[str, Any], receipt: dict[str, Any]) -> None:
    """Require exact recomputation of the bounded PDF result."""
    if _canonical(receipt) != _canonical(extract_pdf(source, contract)):
        raise MedallionPdfError("PDF receipt does not match exact recomputation")
