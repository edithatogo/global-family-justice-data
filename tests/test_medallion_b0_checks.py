"""Fictional supplied-byte B0 checks, never retrieval or rights evidence."""

import hashlib
import json
import runpy
from pathlib import Path

import pytest
from blake3 import blake3

from gfjd.medallion_b0_checks import assess_b0, verify_b0


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def evidence(raw: bytes, media_type: str = "text/csv") -> dict:
    return {
        "content_sha256": sha(raw),
        "content_blake3": blake3(raw).hexdigest(),
        "size_bytes": len(raw),
        "media_type": media_type,
    }


def test_fixity_without_receipts_is_not_custody() -> None:
    raw = b"fictional_measure,count\nfictional,7\n"
    report = assess_b0(raw, evidence(raw), object_id="FICTIONAL")
    assert report["checks"] == {"fixity": "verified", "safety": "missing", "custody": "missing"}
    assert report["scan_status"] == "verified"
    assert report["current_remote_custody_verified"] is False
    assert all(value is False for value in report["authority"].values())
    verify_b0(raw, evidence(raw), report, object_id="FICTIONAL")


def test_supplied_xlsx_is_scanned_and_assertions_only_consistent() -> None:
    script = runpy.run_path(
        str(Path(__file__).resolve().parents[1] / "scripts/rehearse_medallion_lineage.py")
    )
    raw, safety, custody, _ = script["fictional_inputs"]("0007", "2026-08-31T00:00:00Z")
    binding = evidence(raw, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    binding.update(safety_receipt_sha256=sha(safety), custody_receipt_sha256=sha(custody))
    result = assess_b0(
        raw, binding, object_id="FICTIONAL-NOT-RETRIEVED", safety_raw=safety, custody_raw=custody
    )
    assert result["checks"] == {"fixity": "verified", "safety": "verified", "custody": "consistent"}
    assert result["current_remote_custody_verified"] is False


def test_unsupported_pdf_keeps_fixity() -> None:
    raw = b"%PDF-fictional-not-a-document"
    result = assess_b0(raw, evidence(raw, "application/pdf"), object_id="FICTIONAL")
    assert result["checks"]["fixity"] == "verified"
    assert result["checks"]["safety"] == "unsupported"


def test_prohibited_csv_headers_are_codes_only() -> None:
    raw = b"case_number,count\nfictional-only,7\n"
    result = assess_b0(raw, evidence(raw), object_id="FICTIONAL")
    assert result["checks"]["safety"] == "failed"
    assert "PROHIBITED_PERSON_FIELD" in result["finding_codes"]
    assert "case_number" not in json.dumps(result)


@pytest.mark.parametrize(
    "field,value",
    [
        ("content_sha256", "0" * 64),
        ("content_blake3", "0" * 64),
        ("size_bytes", True),
        ("size_bytes", 1),
    ],
)
def test_fixity_mismatch_fails(field: str, value: object) -> None:
    raw = b"fictional"
    binding = evidence(raw)
    binding[field] = value
    with pytest.raises(ValueError, match="^B0 validation failed$"):
        assess_b0(raw, binding, object_id="FICTIONAL")


@pytest.mark.parametrize(
    "raw", [b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":1e999}', b"x" * (1024 * 1024 + 1)]
)
def test_invalid_receipts(raw: bytes) -> None:
    source = b"fictional"
    binding = {**evidence(source), "safety_receipt_sha256": sha(raw)}
    with pytest.raises(ValueError):
        assess_b0(source, binding, object_id="FICTIONAL", safety_raw=raw)


def test_size_checked_before_hash(monkeypatch: pytest.MonkeyPatch) -> None:
    def forbidden(*args: object) -> None:
        raise AssertionError("hashed before byte bound")

    monkeypatch.setattr("gfjd.medallion_b0_checks._sha", forbidden)
    with pytest.raises(ValueError):
        assess_b0(b"x" * (8 * 1024 * 1024 + 1), {}, object_id="FICTIONAL")


def test_forged_report_fails_full_recomputation() -> None:
    raw = b"fictional"
    binding = evidence(raw, "text/plain")
    result = assess_b0(raw, binding, object_id="FICTIONAL")
    result["checks"]["custody"] = "consistent"
    with pytest.raises(ValueError):
        verify_b0(raw, binding, result, object_id="FICTIONAL")


def test_forged_safety_pass_cannot_override_payload_scan() -> None:
    raw = b"case_number,count\nfictional,7\n"
    binding = evidence(raw)
    safety = json.dumps(
        {
            "contract_version": "gfjd-public-archive-safety-v1",
            "status": "pass",
            "objects": [
                {
                    "inventory_id": "FICTIONAL",
                    "sha256": sha(raw),
                    "blake3": blake3(raw).hexdigest(),
                    "size_bytes": len(raw),
                    "disposition": "public_safe",
                    "findings": [],
                }
            ],
        }
    ).encode()
    binding["safety_receipt_sha256"] = sha(safety)
    result = assess_b0(raw, binding, object_id="FICTIONAL", safety_raw=safety)
    assert result["checks"]["safety"] == "failed"
    assert result["checks"]["fixity"] == "verified"


def test_malformed_xlsx_keeps_fixity_and_fixed_scan_code() -> None:
    raw = b"fictional not a zip"
    binding = evidence(raw, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    result = assess_b0(raw, binding, object_id="FICTIONAL")
    assert result["checks"]["fixity"] == "verified"
    assert result["checks"]["safety"] == "failed"
    assert result["finding_codes"] == ["XLSX_CONTAINER_SCAN_FAILED"]


def test_receipt_digest_mismatch() -> None:
    raw = b"fictional"
    binding = {**evidence(raw), "safety_receipt_sha256": "0" * 64}
    with pytest.raises(ValueError):
        assess_b0(raw, binding, object_id="FICTIONAL", safety_raw=b"{}")


@pytest.mark.parametrize("negative", ["status", "disposition", "findings"])
def test_recorded_negative_safety_overrides_unsupported_pdf(negative: str) -> None:
    raw = b"%PDF-fictional-not-a-document"
    binding = evidence(raw, "application/pdf")
    selected = {
        "inventory_id": "FICTIONAL",
        "sha256": sha(raw),
        "blake3": blake3(raw).hexdigest(),
        "size_bytes": len(raw),
        "disposition": "public_safe",
        "findings": [],
    }
    receipt = {
        "contract_version": "gfjd-public-archive-safety-v1",
        "status": "pass",
        "objects": [selected],
    }
    if negative == "status":
        receipt["status"] = "fail"
    elif negative == "disposition":
        selected["disposition"] = "blocked"
    else:
        selected["findings"] = [{"code": "FICTIONAL_BLOCK", "detail": "fictional private text"}]
    safety = json.dumps(receipt).encode()
    binding["safety_receipt_sha256"] = sha(safety)
    result = assess_b0(raw, binding, object_id="FICTIONAL", safety_raw=safety)
    assert result["checks"]["safety"] == "failed"
    assert result["checks"]["fixity"] == "verified"
    assert result["scan_status"] == "unsupported"
    assert "RECORDED_SAFETY_NOT_PASS" in result["finding_codes"]
    assert "fictional private text" not in json.dumps(result)
