"""Bounded supplied candidate scanning; not public safety clearance.

Only compiler fingerprints read files. No extraction, loader, executor or network
is used. Limited pattern/header checks never establish comprehensive privacy.
"""

import csv
import hashlib
import io
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path, PurePosixPath
from typing import Any, cast

from blake3 import blake3

from gfjd import medallion_restore_inputs, medallion_xlsx, security

XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
TEXT_MEMBERS = {".txt", ".md", ".py", ".toml", ".yaml", ".yml", ".cff"}


class CandidateScanError(ValueError):
    """Invalid API input or report; errors never include supplied values."""


def _require(condition: bool) -> None:
    if not condition:
        raise CandidateScanError("Candidate scan contract violation")


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def _binary(raw: bytes) -> bool:
    stripped = raw.removeprefix(b"\xef\xbb\xbf").lstrip()
    return (
        stripped.startswith(
            (b"PK", b"%PDF", b"PAR1", b"PARE", b"\x1f\x8b", b"SQLite format 3", b"DUCK")
        )
        or raw[8:12] == b"DUCK"
    )


class _Scan:
    def __init__(self) -> None:
        self.findings: dict[str, str] = {}
        self.unsupported: set[str] = set()
        self.namespace_count = 0
        self.checks = {"secrets": "checked_no_findings", "prohibited_data": "checked_no_findings"}

    def unsupported_check(self, key: str, code: str) -> None:
        if self.checks[key] != "failed":
            self.checks[key] = "unsupported"
        self.unsupported.add(code)

    def invalid(self, code: str) -> None:
        self.findings[code] = "high"
        for key in self.checks:
            self.unsupported_check(key, "INCOMPLETE_FORMAT_COVERAGE")

    def secret(self, text: str) -> None:
        for code, pattern in security.SECRET_PATTERNS:
            if pattern.search(text):
                self.findings["SECRET_" + code] = "critical"
                self.checks["secrets"] = "failed"

    def field(self, text: str, *, tokens: bool = False) -> None:
        values = (
            re.findall(r"[A-Za-z_][A-Za-z0-9_]*", text.lower())
            if tokens
            else [text.strip().lower()]
        )
        if set(values) & security.PROHIBITED_PUBLIC_DATA_HEADERS:
            self.findings["PROHIBITED_FIELD"] = "critical"
            self.checks["prohibited_data"] = "failed"

    def text(self, raw: bytes, kind: str) -> None:
        try:
            if _binary(raw):
                self.invalid("DISGUISED_CONTAINER")
                return
            text = raw.decode("utf-8-sig")
            if "\x00" in text:
                self.invalid("INVALID_TEXT")
                return
        except UnicodeError:
            self.invalid("INVALID_TEXT")
            return
        self.secret(text)
        if kind == "text":
            self.unsupported_check("prohibited_data", "PLAINTEXT_PROHIBITED_DATA_UNASSESSED")
        elif kind == "json":
            try:
                _require(len(raw) <= 1024 * 1024)
                # Strip only the optional UTF-8 BOM; preserve all other parser limits.
                value = medallion_restore_inputs.preflight(raw.removeprefix(b"\xef\xbb\xbf"))
                pending = [value]
                while pending:
                    item = pending.pop()
                    if isinstance(item, str):
                        self.secret(item)
                    elif isinstance(item, dict):
                        for key in item:
                            self.field(key)
                            self.secret(key)
                        pending.extend(item.values())
                    elif isinstance(item, list):
                        pending.extend(item)
            except ValueError:
                self.invalid("INVALID_JSON")
        elif kind == "csv":
            try:
                reader = csv.reader(io.StringIO(text, newline=""), strict=True)
                rows, cells, width = 0, 0, None
                for row in reader:
                    rows += 1
                    cells += len(row)
                    if rows > 1000 or not 1 <= len(row) <= 64 or cells > 10000:
                        raise ValueError
                    if width is None:
                        width = len(row)
                        if not all(cell.strip() for cell in row):
                            raise ValueError
                        for cell in row:
                            self.field(cell)
                    if len(row) != width or any(len(cell) > 4096 for cell in row):
                        raise ValueError
                    for cell in row:
                        self.secret(cell)
                if not rows:
                    raise ValueError
            except (ValueError, csv.Error):
                self.invalid("INVALID_CSV")

    def xml(self, tree: Any) -> None:
        for element in tree.iter():
            self.secret(str(element.tag))
            self.field(str(element.tag).rsplit("}", 1)[-1], tokens=True)
            for value in (element.text, element.tail):
                if value is not None:
                    self.secret(value)
                    self.field(value, tokens=True)
            for key, value in element.attrib.items():
                self.secret(key)
                self.secret(value)
                self.field(key.rsplit("}", 1)[-1], tokens=True)
                self.field(value, tokens=True)

    def xml_namespaces(self, text: str) -> None:
        """Inspect declarations discarded by ElementTree, only after XML preflight.

        This second in-memory pass never decompresses or resolves a member. End
        events clear elements; namespace declarations have a package-wide cap.
        """
        for event, value in ET.iterparse(io.StringIO(text), events=("start-ns", "end")):
            if event == "start-ns":
                self.namespace_count += 1
                _require(self.namespace_count <= medallion_xlsx.MAX_XML_NODES)
                prefix, uri = cast(tuple[str, str], value)
                _require(len(prefix) <= 4096 and len(uri) <= 4096)
                self.secret(prefix)
                self.secret(uri)
                self.field(prefix, tokens=True)
                self.field(uri, tokens=True)
            else:
                value.clear()


def _scan(raw: bytes, media_type: str) -> dict[str, Any]:
    _require(type(raw) is bytes and 0 < len(raw) <= 8 * 1024 * 1024)
    _require(
        type(media_type) is str
        and len(media_type) <= 128
        and re.fullmatch(r"[a-z][a-z0-9.+-]*/[a-z][a-z0-9.+-]*", media_type) is not None
    )
    scan = _Scan()
    member_hashes: list[str] = []
    member_count = 0
    if media_type in {"text/plain", "text/csv", "application/json"}:
        scan.text(
            raw, {"text/plain": "text", "text/csv": "csv", "application/json": "json"}[media_type]
        )
    elif media_type in {"application/zip", XLSX}:
        try:
            members = medallion_xlsx._package(raw)
        except Exception:
            scan.invalid("UNSAFE_OR_INVALID_CONTAINER")
        else:
            member_count = len(members)
            member_hashes = sorted(_sha(value) for value in members.values())
            if media_type == XLSX and not {"[Content_Types].xml", "xl/workbook.xml"} <= set(
                members
            ):
                scan.invalid("MISSING_XLSX_CORE")
            xml_members = {
                name.lower(): value
                for name, value in members.items()
                if name.lower().endswith((".xml", ".rels"))
            }
            try:
                trees = medallion_xlsx._xmls(xml_members)
            except Exception:
                trees = {}
                scan.invalid("INVALID_XML")
            for name, value in members.items():
                path = PurePosixPath(name.lower())
                suffix = ".rels" if path.name.endswith(".rels") else path.suffix
                if (
                    path.name in security.FORBIDDEN_FILENAMES
                    or suffix in security.FORBIDDEN_SUFFIXES
                ):
                    scan.findings["FORBIDDEN_CREDENTIAL_MEMBER"] = "critical"
                    scan.checks["secrets"] = "failed"
                if _binary(value):
                    for key in scan.checks:
                        scan.unsupported_check(key, "NESTED_OR_BINARY_MEMBER")
                elif suffix in TEXT_MEMBERS:
                    scan.text(value, "text")
                elif suffix in {".json", ".csv"}:
                    scan.text(value, suffix[1:])
                elif suffix in {".xml", ".rels"}:
                    if name.lower() in trees:
                        text = value.decode("utf-8-sig")
                        scan.secret(text)
                        scan.xml(trees[name.lower()])
                        try:
                            scan.xml_namespaces(text)
                        except Exception:
                            scan.invalid("INVALID_XML")
                else:
                    for key in scan.checks:
                        scan.unsupported_check(key, "UNSUPPORTED_MEMBER_EXTENSION")
    else:
        for key in scan.checks:
            scan.unsupported_check(key, "UNSUPPORTED_MEDIA_TYPE")
    components = (security, medallion_xlsx, medallion_restore_inputs)
    return {
        "contract_version": "gfjd-candidate-scan-v1",
        "input_sha256": _sha(raw),
        "input_blake3": blake3(raw).hexdigest(),
        "size_bytes": len(raw),
        "media_type": media_type,
        "status": "failed"
        if scan.findings
        else "unsupported"
        if scan.unsupported
        else "checked_no_findings",
        "checks": scan.checks,
        "findings": [
            {"code": code, "severity": severity} for code, severity in sorted(scan.findings.items())
        ],
        "unsupported_codes": sorted(scan.unsupported),
        "member_count": member_count,
        "member_sha256": member_hashes,
        "check_scope": {
            "secrets": "fixed-literal-patterns-and-supported-decoded-values",
            "prohibited_data": "fixed-CSV-header-JSON-key-XML-token-set",
        },
        "implementation_sha256": _sha(Path(__file__).read_bytes()),
        "component_implementation_sha256": {
            component.__name__: _sha(Path(cast(str, component.__file__)).read_bytes())
            for component in components
        },
        "limitations": [
            "no-comprehensive-privacy-or-disclosure-assessment",
            "no-code-or-config-semantic-certification",
            "no-source-extraction-or-workbook-semantic-validation",
            "unknown-and-nested-formats-block-coverage",
        ],
        "factual_requirements": dict.fromkeys(
            ("rights", "privacy", "disclosure", "external_assurance", "publication", "release"),
            "pending",
        ),
        "authority": dict.fromkeys(
            (
                "network",
                "source_access",
                "rights_clearance",
                "publication",
                "release",
                "promotion",
                "gate_acceptance",
                "execution",
            ),
            False,
        ),
        "filesystem_access": "compiler-fingerprints-only",
    }


def scan_candidate_bytes(raw: bytes, media_type: str) -> dict[str, Any]:
    """Check bounded supplied bytes, retaining unsupported coverage as a blocker."""
    try:
        return _scan(raw, media_type)
    except Exception:
        raise CandidateScanError("Candidate scan contract violation") from None


def verify_candidate_scan(raw: bytes, media_type: str, report: dict[str, Any]) -> None:
    """Recompute the entire report with type-sensitive canonical comparison."""
    try:
        expected = scan_candidate_bytes(raw, media_type)
        _require(type(report) is dict and _canonical(report) == _canonical(expected))
    except Exception:
        raise CandidateScanError("Candidate scan contract violation") from None
