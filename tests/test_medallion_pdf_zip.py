from __future__ import annotations

import io
import json
import zipfile
from hashlib import sha256
from unittest.mock import patch

import pytest

from gfjd import medallion_pdf, medallion_zip


def canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


class FakePage:
    def extract_text(self) -> str:
        return "Table 4\nFamily 101% 100% 100% 101% 99%\n"


class FakeReader:
    def __init__(self, _: object, strict: bool = True) -> None:
        self.pages = [FakePage()]


def test_pdf_contract_is_digest_bound_and_recomputable() -> None:
    source = b"pdf-bytes"
    contract = {
        "extraction_version": medallion_pdf.VERSION,
        "source_sha256": sha256(source).hexdigest(),
        "page_number": 1,
        "markers": ["Table 4", "Family"],
        "pattern": r"(?m)^Family\s+101%\s+100%\s+100%\s+101%\s+(?P<value>99)%\s*$",
    }
    with patch.object(medallion_pdf, "PdfReader", FakeReader):
        receipt = medallion_pdf.extract_pdf(source, contract)
        medallion_pdf.verify_pdf(source, contract, receipt)
        with pytest.raises(medallion_pdf.MedallionPdfError):
            medallion_pdf.extract_pdf(b"changed", contract)


def zip_source() -> bytes:
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_STORED) as archive:
        archive.writestr(
            "values.csv",
            "kind,year,value\nFamily,2024,99\nOther,2024,1\n",
        )
    return stream.getvalue()


def test_zip_csv_contract_is_digest_bound_and_recomputable() -> None:
    source = zip_source()
    contract = {
        "extraction_version": medallion_zip.VERSION,
        "source_sha256": sha256(source).hexdigest(),
        "member_name": "values.csv",
        "selector": {"kind": "Family", "year": "2024"},
        "value_field": "value",
    }
    receipt = medallion_zip.extract_zip_csv(source, contract)
    assert receipt["value"] == 99
    medallion_zip.verify_zip_csv(source, contract, receipt)
    with pytest.raises(medallion_zip.MedallionZipError):
        medallion_zip.extract_zip_csv(source + b"x", contract)
