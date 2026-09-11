"""Bounded source-faithful CSV-in-ZIP fact extraction for private replay."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import zipfile
from pathlib import Path
from typing import Any

from . import public_archive

VERSION = "gfjd-medallion-zip-csv-v1"
MAX_SOURCE_BYTES = 32 * 1024 * 1024
MAX_ROWS = 100_000
CONTRACT_KEYS = frozenset(
    {
        "extraction_version",
        "source_sha256",
        "member_name",
        "selector",
        "value_field",
    }
)


class MedallionZipError(ValueError):
    """Fail-closed ZIP extraction error."""


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def _require(condition: bool) -> None:
    if not condition:
        raise MedallionZipError("medallion ZIP contract violation")


def extract_zip_csv(source: bytes, contract: dict[str, Any]) -> dict[str, Any]:
    """Extract one exact CSV row from one exact ZIP member."""
    try:
        _require(isinstance(source, bytes) and 0 < len(source) <= MAX_SOURCE_BYTES)
        _require(isinstance(contract, dict) and set(contract) == CONTRACT_KEYS)
        _require(contract["extraction_version"] == VERSION)
        _require(contract["source_sha256"] == _sha(source))
        _require(public_archive.scan_zip(source, "selected.zip") == [])
        member = contract["member_name"]
        _require(isinstance(member, str) and 0 < len(member) <= 512)
        selector = contract["selector"]
        _require(
            isinstance(selector, dict)
            and 0 < len(selector) <= 32
            and all(
                isinstance(key, str) and isinstance(value, str) for key, value in selector.items()
            )
        )
        value_field = contract["value_field"]
        _require(
            isinstance(value_field, str) and re.fullmatch(r"[A-Za-z0-9_]+", value_field) is not None
        )
        with zipfile.ZipFile(io.BytesIO(source), "r") as archive:
            _require(member in archive.namelist())
            raw = archive.read(member)
        text = raw.decode("utf-8-sig")
        rows = list(csv.DictReader(io.StringIO(text)))
        _require(0 < len(rows) <= MAX_ROWS)
        matches = [
            row for row in rows if all(row.get(key) == value for key, value in selector.items())
        ]
        _require(len(matches) == 1 and value_field in matches[0])
        raw_value = matches[0][value_field].strip()
        _require(re.fullmatch(r"[0-9]+(?:\.[0-9]+)?", raw_value) is not None)
        value: int | float = float(raw_value) if "." in raw_value else int(raw_value)
        result = {
            "extraction_version": VERSION,
            "source_sha256": _sha(source),
            "contract_sha256": _sha(_canonical(contract)),
            "implementation_sha256": _sha(Path(__file__).read_bytes()),
            "member_name": member,
            "row_selector_sha256": _sha(_canonical(selector)),
            "value_field": value_field,
            "value": value,
            "promotion_authorized": False,
        }
        return result
    except MedallionZipError:
        raise
    except Exception as exc:
        raise MedallionZipError("medallion ZIP extraction failed") from exc


def verify_zip_csv(source: bytes, contract: dict[str, Any], receipt: dict[str, Any]) -> None:
    """Require exact recomputation of the bounded ZIP result."""
    if _canonical(receipt) != _canonical(extract_zip_csv(source, contract)):
        raise MedallionZipError("ZIP receipt does not match exact recomputation")
