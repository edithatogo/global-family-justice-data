from __future__ import annotations

import csv
import hashlib
import json
import zipfile
from pathlib import Path

import pytest
from pypdf import PdfWriter
from pypdf.generic import DictionaryObject, NameObject, TextStringObject

from gfjd.public_archive import (
    PublicArchiveError,
    scan_inventory,
    verify_custody_receipt,
    verify_receipt,
    write_receipt,
)


def _inventory(root: Path, payload: Path, *, digest: str | None = None) -> Path:
    path = root / "inventory.csv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["inventory_id", "payload_path", "sha256"])
        writer.writeheader()
        writer.writerow(
            {
                "inventory_id": "ARC-1",
                "payload_path": payload.relative_to(root).as_posix(),
                "sha256": digest or hashlib.sha256(payload.read_bytes()).hexdigest(),
            }
        )
    return path


def test_safe_pdf_receipt_round_trip(tmp_path: Path) -> None:
    payload = tmp_path / "report.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    with payload.open("wb") as handle:
        writer.write(handle)
    receipt = scan_inventory(tmp_path, _inventory(tmp_path, payload))
    output = tmp_path / "receipt.json"
    write_receipt(receipt, output)
    assert receipt["status"] == "pass"
    assert receipt["objects"][0]["blake3"]
    assert verify_receipt(tmp_path, output) == []


@pytest.mark.parametrize("key", ["/JavaScript", "/JS", "/EmbeddedFiles"])
def test_pdf_active_or_hidden_content_blocks(tmp_path: Path, key: str) -> None:
    payload = tmp_path / "report.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    writer.root_object[NameObject(key)] = DictionaryObject(
        {NameObject("/Value"): TextStringObject("blocked")}
    )
    with payload.open("wb") as handle:
        writer.write(handle)
    receipt = scan_inventory(tmp_path, _inventory(tmp_path, payload))
    assert receipt["status"] == "fail"


def test_zip_path_escape_blocks(tmp_path: Path) -> None:
    payload = tmp_path / "source.zip"
    with zipfile.ZipFile(payload, "w") as archive:
        archive.writestr("../escape.csv", "metric,value\norders,4\n")
    receipt = scan_inventory(tmp_path, _inventory(tmp_path, payload))
    assert receipt["objects"][0]["findings"][0]["code"] == "ARCHIVE_PATH_ESCAPE"


def test_prohibited_person_level_header_blocks(tmp_path: Path) -> None:
    payload = tmp_path / "source.zip"
    with zipfile.ZipFile(payload, "w") as archive:
        archive.writestr("data.csv", "case_number,value\nABC,4\n")
    receipt = scan_inventory(tmp_path, _inventory(tmp_path, payload))
    assert any(
        item["code"] == "PROHIBITED_PERSON_FIELD" for item in receipt["objects"][0]["findings"]
    )


def test_digest_mismatch_and_tampered_receipt_fail(tmp_path: Path) -> None:
    payload = tmp_path / "report.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    with payload.open("wb") as handle:
        writer.write(handle)
    inventory = _inventory(tmp_path, payload, digest="0" * 64)
    receipt = scan_inventory(tmp_path, inventory)
    assert receipt["status"] == "fail"
    output = tmp_path / "receipt.json"
    write_receipt(receipt, output)
    recorded = json.loads(output.read_text(encoding="utf-8"))
    recorded["status"] = "pass"
    output.write_text(json.dumps(recorded), encoding="utf-8")
    assert verify_receipt(tmp_path, output)


def test_inventory_path_escape_fails_closed(tmp_path: Path) -> None:
    outside = tmp_path.parent / "outside.csv"
    outside.write_text("inventory_id,payload_path,sha256\n", encoding="utf-8")
    with pytest.raises(PublicArchiveError, match="escapes"):
        scan_inventory(tmp_path, outside)


def test_repository_public_custody_receipt_is_bound() -> None:
    root = Path(__file__).resolve().parents[1]
    errors = verify_custody_receipt(
        root, root / "data/preservation/public_b0_custody_20260827.json"
    )
    assert errors == []
