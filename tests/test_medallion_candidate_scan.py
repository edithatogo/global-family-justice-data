"""Fictional candidate bytes; no source retrieval or actual credentials."""

import hashlib
import io
import json
import socket
import stat
import zipfile

import pytest

from gfjd import medallion_candidate_scan as module
from gfjd.medallion_candidate_scan import scan_candidate_bytes, verify_candidate_scan
from tests.test_medallion_qualification import fictional_workbook


def package(members, compression=zipfile.ZIP_STORED):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", compression=compression) as archive:
        for name, raw in members:
            archive.writestr(name, raw)
    return stream.getvalue()


def test_escaped_secret_red():
    token = "ghp_" + "a" * 35
    raw = ('{"value":"' + "".join(f"\\u{ord(c):04x}" for c in token) + '"}').encode()
    assert scan_candidate_bytes(raw, "application/json")["status"] == "failed"


@pytest.mark.parametrize(
    "raw,media,status",
    [
        (b"safe text", "text/plain", "unsupported"),
        (b'{"value":"fictional"}', "application/json", "checked_no_findings"),
        (b"value,count\nfictional,10\n", "text/csv", "checked_no_findings"),
        (b"\xef\xbb\xbf{}", "application/json", "checked_no_findings"),
        (b"PAR1example", "application/vnd.apache.parquet", "unsupported"),
        (b"%PDF-example", "application/pdf", "unsupported"),
        (b"unknown", "application/duckdb", "unsupported"),
    ],
)
def test_profiles_and_authority(raw, media, status):
    result = scan_candidate_bytes(raw, media)
    assert result["status"] == status
    assert result["input_sha256"] == hashlib.sha256(raw).hexdigest()
    assert result["size_bytes"] == len(raw)
    assert not any(result["authority"].values())
    assert set(result["factual_requirements"].values()) == {"pending"}
    verify_candidate_scan(raw, media, result)


@pytest.mark.parametrize(
    "raw,media",
    [
        (b'{" Full_Name ":"fictional"}', "application/json"),
        (b'{"nested":[{"case_number":"fictional"}]}', "application/json"),
        (b" EMAIL_ADDRESS ,count\nfictional,1", "text/csv"),
    ],
)
def test_prohibited_headers_and_keys(raw, media):
    report = scan_candidate_bytes(raw, media)
    assert report["checks"]["prohibited_data"] == "failed"
    assert {"code": "PROHIBITED_FIELD", "severity": "critical"} in report["findings"]


@pytest.mark.parametrize(
    "raw",
    [
        b"PKexample",
        b"%PDF-example",
        b"PAR1example",
        b"PAREexample",
        b"\x1f\x8bexample",
        b"SQLite format 3",
        b"12345678DUCKexample",
        b"\xef\xbb\xbf  PAR1test",
    ],
)
def test_disguised_binary(raw):
    report = scan_candidate_bytes(raw, "text/plain")
    assert report["status"] == "failed"
    assert {"code": "DISGUISED_CONTAINER", "severity": "high"} in report["findings"]


@pytest.mark.parametrize("raw", [b"\xff", b"a\x00b"])
def test_invalid_text(raw):
    assert scan_candidate_bytes(raw, "text/plain")["status"] == "failed"


@pytest.mark.parametrize(
    "raw",
    [
        b'{"a":1,"a":2}',
        b'{"x":NaN}',
        b'"\\u0000"',
        b"[" * 17 + b"0" + b"]" * 17,
        json.dumps("x" * 4097).encode(),
        b" " * (1024 * 1024) + b"{}",
    ],
)
def test_json_strict_bounds(raw):
    assert scan_candidate_bytes(raw, "application/json")["status"] == "failed"


@pytest.mark.parametrize(
    "raw",
    [
        b"\n",
        b"a,b\n1\n",
        b'"unterminated',
        b"a\n" + b"x" * 4097,
        b",".join([b"x"] * 65),
        b"a\n" * 1001,
        (b",".join([b"x"] * 64) + b"\n") * 157,
    ],
)
def test_csv_strict_bounds(raw):
    assert scan_candidate_bytes(raw, "text/csv")["status"] == "failed"


def test_csv_boundary():
    raw = b",".join([b"x"] * 10) + b"\n"
    raw *= 1000
    assert scan_candidate_bytes(raw, "text/csv")["status"] == "checked_no_findings"


def test_zip_supported_json_csv_xml_no_names():
    raw = package(
        [
            ("private-member-name.json", b'{"value":1}'),
            ("data.csv", b"value\n1"),
            ("values.xml", b'<root><value name="safe">fictional</value></root>'),
        ]
    )
    report = scan_candidate_bytes(raw, "application/zip")
    assert report["status"] == "checked_no_findings"
    assert report["member_count"] == 3
    assert len(report["member_sha256"]) == 3
    assert "private-member-name" not in json.dumps(report)


def test_xml_decoded_secret_and_prohibited_token():
    token = "ghp_" + "a" * 35
    encoded = "".join(f"&#{ord(c)};" for c in token)
    xml = f'<root><value key="case_number">{encoded}</value></root>'.encode()
    report = scan_candidate_bytes(package([("document.xml", xml)]), "application/zip")
    assert report["status"] == "failed"
    assert report["checks"] == {"secrets": "failed", "prohibited_data": "failed"}
    assert token not in json.dumps(report)


@pytest.mark.parametrize("unused", [False, True])
def test_xml_namespace_decoded_secret(unused):
    token = "ghp_" + "a" * 35
    escaped = "".join(f"&#{ord(c)};" for c in token)
    declaration = "xmlns:unused" if unused else "xmlns"
    xml = f'<root {declaration}="urn:{escaped}"/>'.encode()
    report = scan_candidate_bytes(package([("fixture.xml", xml)]), "application/zip")
    assert report["checks"]["secrets"] == "failed"
    assert {"code": "SECRET_GITHUB_TOKEN", "severity": "critical"} in report["findings"]
    assert token not in json.dumps(report)


def test_xml_namespace_budget_is_package_wide(monkeypatch):
    monkeypatch.setattr(module.medallion_xlsx, "MAX_XML_NODES", 2)
    raw = package(
        [
            ("one.xml", b'<root xmlns:a="urn:a" xmlns:b="urn:b"/>'),
            ("two.xml", b'<root xmlns:c="urn:c"/>'),
        ]
    )
    report = scan_candidate_bytes(raw, "application/zip")
    assert {"code": "INVALID_XML", "severity": "high"} in report["findings"]


def test_xml_namespace_pass_follows_hard_xml_validation(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("namespace pass before XML preflight")

    monkeypatch.setattr(module._Scan, "xml_namespaces", forbidden)
    raw = package([("bad.xml", b'<!DOCTYPE x [<!ENTITY x "a">]><x>&x;</x>')])
    assert scan_candidate_bytes(raw, "application/zip")["status"] == "failed"


@pytest.mark.parametrize(
    "xml",
    [
        b'<!DOCTYPE x [<!ENTITY x "a">]><x>&x;</x>',
        b"<x>",
        b'<?xml version="1.0" encoding="utf-16"?><x/>',
        b"<x>" * 65 + b"</x>" * 65,
    ],
)
def test_xml_unsafe(xml):
    report = scan_candidate_bytes(package([("document.xml", xml)]), "application/zip")
    assert {"code": "INVALID_XML", "severity": "high"} in report["findings"]


@pytest.mark.parametrize(
    "name,raw",
    [
        ("notes.txt", b"safe"),
        ("unknown.dat", b"safe"),
        ("nested.zip", package([("inside.json", b"{}")])),
    ],
)
def test_zip_unsupported_coverage(name, raw):
    report = scan_candidate_bytes(package([(name, raw)]), "application/zip")
    assert report["status"] == "unsupported"
    assert report["unsupported_codes"]


@pytest.mark.parametrize(
    "name", ["../escape.json", "/absolute.json", "directory/", "macro.bin", "vbaProject.xml"]
)
def test_unsafe_member_names(name):
    report = scan_candidate_bytes(package([(name, b"{}")]), "application/zip")
    assert report["status"] == "failed"


def test_case_collision_and_member_bounds():
    for members in (
        [("a.json", b"{}"), ("A.json", b"{}")],
        [(f"{i}.json", b"{}") for i in range(129)],
    ):
        assert scan_candidate_bytes(package(members), "application/zip")["status"] == "failed"


def test_symlink_member():
    entry = zipfile.ZipInfo("link.json")
    entry.external_attr = (stat.S_IFLNK | 0o777) << 16
    assert (
        scan_candidate_bytes(package([(entry, b"target")]), "application/zip")["status"] == "failed"
    )


def test_ratio_rejection_before_member_read(monkeypatch):
    raw = package([("large.json", b" " * 100000)], zipfile.ZIP_DEFLATED)

    def forbidden(*args, **kwargs):
        pytest.fail("read before complete package preflight")

    monkeypatch.setattr(zipfile.ZipFile, "open", forbidden)
    assert scan_candidate_bytes(raw, "application/zip")["status"] == "failed"


def test_credential_filename_critical():
    report = scan_candidate_bytes(package([("credentials.json", b"{}")]), "application/zip")
    assert {"code": "FORBIDDEN_CREDENTIAL_MEMBER", "severity": "critical"} in report["findings"]


def test_xlsx_all_members_no_extraction():
    raw = fictional_workbook({"value": "FICTIONAL"})
    report = scan_candidate_bytes(raw, module.XLSX)
    assert report["status"] == "checked_no_findings"
    assert report["member_count"] == 5
    raw = fictional_workbook({"case_number": "FICTIONAL"})
    assert scan_candidate_bytes(raw, module.XLSX)["checks"]["prohibited_data"] == "failed"
    assert scan_candidate_bytes(package([("test.json", b"{}")]), module.XLSX)["status"] == "failed"


@pytest.mark.parametrize(
    "raw,media",
    [
        (b"", "text/plain"),
        (b"x" * (8 * 1024 * 1024 + 1), "text/plain"),
        ("text", "text/plain"),
        (b"x", "TEXT/plain"),
        (b"x", "text/plain; charset=utf-8"),
        (b"x", "application/1invalid"),
        (b"x", None),
    ],
)
def test_api_bounds_before_hash(raw, media, monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("hash before API bounds")

    monkeypatch.setattr(module, "_sha", forbidden)
    with pytest.raises(ValueError):
        scan_candidate_bytes(raw, media)


@pytest.mark.parametrize(
    "field,value",
    [
        ("status", "accepted"),
        ("size_bytes", True),
        ("implementation_sha256", "a" * 64),
        ("findings", [{"code": "invented", "severity": "low"}]),
    ],
)
def test_forged_report(field, value):
    report = scan_candidate_bytes(b"{}", "application/json")
    report[field] = value
    with pytest.raises(ValueError):
        verify_candidate_scan(b"{}", "application/json", report)


def test_no_network_or_broad_scanner(monkeypatch):
    from gfjd import public_archive

    def forbidden(*args, **kwargs):
        pytest.fail("forbidden scanner capability")

    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(public_archive, "_scan_zip", forbidden)
    raw = package([("fixture.json", b"{}")])
    assert scan_candidate_bytes(raw, "application/zip") == scan_candidate_bytes(
        raw, "application/zip"
    )


def test_json_bom_does_not_extend_input_budget():
    raw = b"\xef\xbb\xbf" + b" " * (1024 * 1024 - 2) + b"{}"
    assert scan_candidate_bytes(raw, "application/json")["status"] == "failed"
