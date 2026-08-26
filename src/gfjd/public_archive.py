"""Fail-closed safety and integrity checks for public Bronze source objects."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import stat
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from blake3 import blake3
from pypdf import PdfReader
from pypdf.errors import PdfReadError
from pypdf.generic import ArrayObject, DictionaryObject, IndirectObject

from .security import PROHIBITED_PUBLIC_DATA_HEADERS, SECRET_PATTERNS

CONTRACT_VERSION = "gfjd-public-archive-safety-v1"
CUSTODY_CONTRACT_VERSION = "gfjd-public-b0-custody-v1"
MAX_MEMBERS = 10_000
MAX_EXPANDED_BYTES = 500_000_000
MAX_MEMBER_BYTES = 100_000_000
MAX_RATIO = 200
TEXT_EXTENSIONS = {".csv", ".json", ".txt", ".xml", ".yaml", ".yml"}
PDF_DANGEROUS_KEYS = {"/AA", "/JavaScript", "/JS", "/Launch", "/EmbeddedFiles"}


class PublicArchiveError(ValueError):
    """Raised when the archive contract or its input is invalid."""


@dataclass(frozen=True)
class Finding:
    code: str
    location: str
    detail: str

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "location": self.location, "detail": self.detail}


def scan_inventory(root: Path, inventory_path: Path) -> dict[str, Any]:
    """Scan every inventory object and return a deterministic public-safe receipt."""

    inventory = _inside_root(root, inventory_path)
    raw = inventory.read_bytes()
    objects: list[dict[str, Any]] = []
    with io.StringIO(raw.decode("utf-8-sig"), newline="") as handle:
        rows = list(csv.DictReader(handle))
    required = {"inventory_id", "payload_path", "sha256"}
    if not rows or not required.issubset(rows[0]):
        raise PublicArchiveError("inventory is empty or missing required columns")
    seen: set[str] = set()
    for row in rows:
        inventory_id = row["inventory_id"].strip()
        if not inventory_id or inventory_id in seen:
            raise PublicArchiveError(f"invalid or duplicate inventory_id: {inventory_id!r}")
        seen.add(inventory_id)
        objects.append(_scan_object(root, inventory_id, row["payload_path"], row["sha256"]))
    status = "pass" if all(item["disposition"] == "public_safe" for item in objects) else "fail"
    return {
        "contract_version": CONTRACT_VERSION,
        "inventory_path": inventory.relative_to(root.resolve()).as_posix(),
        "inventory_sha256": hashlib.sha256(raw).hexdigest(),
        "status": status,
        "objects": objects,
    }


def verify_receipt(root: Path, receipt_path: Path) -> list[str]:
    """Recompute a receipt rather than trusting its recorded disposition."""

    receipt_file = _inside_root(root, receipt_path)
    try:
        recorded = json.loads(receipt_file.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return [f"invalid receipt: {exc}"]
    if recorded.get("contract_version") != CONTRACT_VERSION:
        return ["unsupported receipt contract_version"]
    inventory_value = recorded.get("inventory_path")
    if not isinstance(inventory_value, str):
        return ["receipt inventory_path is missing"]
    try:
        current = scan_inventory(root, root / inventory_value)
    except (OSError, UnicodeError, csv.Error, PublicArchiveError, zipfile.BadZipFile) as exc:
        return [f"receipt recomputation failed: {exc}"]
    return [] if current == recorded else ["receipt differs from recomputed source inventory"]


def verify_custody_receipt(root: Path, receipt_path: Path) -> list[str]:
    """Verify that custody evidence binds every safe object to two public providers."""

    try:
        receipt = json.loads(_inside_root(root, receipt_path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError, PublicArchiveError) as exc:
        return [f"invalid custody receipt: {exc}"]
    errors: list[str] = []
    if receipt.get("contract_version") != CUSTODY_CONTRACT_VERSION:
        errors.append("unsupported custody contract_version")
    safety_value = receipt.get("safety_receipt_path")
    if not isinstance(safety_value, str):
        return [*errors, "custody safety_receipt_path is missing"]
    try:
        safety_path = _inside_root(root, root / safety_value)
        safety_bytes = safety_path.read_bytes()
        safety = json.loads(safety_bytes)
    except (OSError, UnicodeError, json.JSONDecodeError, PublicArchiveError) as exc:
        return [*errors, f"invalid bound safety receipt: {exc}"]
    if hashlib.sha256(safety_bytes).hexdigest() != receipt.get("safety_receipt_sha256"):
        errors.append("custody safety receipt digest mismatch")
    safe_objects = {item["inventory_id"]: item for item in safety.get("objects", [])}
    custody_objects = {item.get("inventory_id"): item for item in receipt.get("objects", [])}
    if set(safe_objects) != set(custody_objects):
        errors.append("custody objects do not exactly match safety objects")
        return errors
    allowed_hosts = {
        "huggingface": "https://huggingface.co/",
        "github": "https://github.com/",
    }
    for inventory_id, safe in safe_objects.items():
        item = custody_objects[inventory_id]
        for field in ("sha256", "blake3", "size_bytes"):
            if item.get(field) != safe.get(field):
                errors.append(f"{inventory_id}: custody {field} differs from safety receipt")
        replicas = item.get("replicas", [])
        providers = {replica.get("provider") for replica in replicas}
        if providers != set(allowed_hosts):
            errors.append(f"{inventory_id}: exactly two provider-separated replicas required")
        for replica in replicas:
            provider = replica.get("provider")
            prefix = allowed_hosts.get(provider)
            if prefix is None or not str(replica.get("url", "")).startswith(prefix):
                errors.append(f"{inventory_id}: invalid {provider!r} public locator")
            if not replica.get("anonymous_get_verified"):
                errors.append(f"{inventory_id}: anonymous retrieval is not verified")
            if replica.get("retrieved_sha256") != safe.get("sha256"):
                errors.append(f"{inventory_id}: retrieved SHA-256 mismatch for {provider}")
            if replica.get("retrieved_blake3") != safe.get("blake3"):
                errors.append(f"{inventory_id}: retrieved BLAKE3 mismatch for {provider}")
    return errors


def write_receipt(receipt: dict[str, Any], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _scan_object(
    root: Path, inventory_id: str, payload_value: str, expected_sha: str
) -> dict[str, Any]:
    findings: list[Finding] = []
    try:
        payload = _inside_root(root, root / payload_value)
    except PublicArchiveError as exc:
        return _object_result(inventory_id, payload_value, b"", findings, "blocked", str(exc))
    if not payload.is_file():
        return _object_result(
            inventory_id, payload_value, b"", findings, "missing", "payload missing"
        )
    data = payload.read_bytes()
    sha256 = hashlib.sha256(data).hexdigest()
    if not re.fullmatch(r"[0-9a-f]{64}", expected_sha) or sha256 != expected_sha:
        findings.append(
            Finding("DIGEST_MISMATCH", payload.name, "SHA-256 does not match inventory")
        )
    findings.extend(_scan_bytes(data, payload.name))
    suffix = payload.suffix.lower()
    if suffix == ".pdf":
        findings.extend(_scan_pdf(data, payload.name))
    elif suffix in {".zip", ".xlsx", ".ods"}:
        findings.extend(_scan_zip(data, payload.name))
    else:
        findings.append(
            Finding("UNSUPPORTED_MEDIA_TYPE", payload.name, f"unsupported suffix {suffix}")
        )
    return _object_result(
        inventory_id,
        payload_value,
        data,
        findings,
        "public_safe" if not findings else "blocked",
        "",
    )


def _scan_zip(data: bytes, location: str) -> list[Finding]:
    findings: list[Finding] = []
    try:
        archive = zipfile.ZipFile(io.BytesIO(data))
    except zipfile.BadZipFile:
        return [Finding("INVALID_ZIP", location, "invalid ZIP-compatible container")]
    infos = archive.infolist()
    if len(infos) > MAX_MEMBERS:
        findings.append(Finding("ARCHIVE_MEMBER_LIMIT", location, "too many archive members"))
        return findings
    expanded = sum(info.file_size for info in infos)
    if expanded > MAX_EXPANDED_BYTES:
        findings.append(
            Finding("ARCHIVE_EXPANDED_LIMIT", location, "expanded archive is too large")
        )
    names: set[str] = set()
    for info in infos:
        member = PurePosixPath(info.filename.replace("\\", "/"))
        normalised = member.as_posix().casefold()
        mode = info.external_attr >> 16
        file_type = stat.S_IFMT(mode)
        if member.is_absolute() or ".." in member.parts:
            findings.append(Finding("ARCHIVE_PATH_ESCAPE", info.filename, "unsafe member path"))
            continue
        if normalised in names:
            findings.append(
                Finding("ARCHIVE_CASE_COLLISION", info.filename, "duplicate normalised path")
            )
            continue
        names.add(normalised)
        if stat.S_ISLNK(mode) or (file_type and not (stat.S_ISREG(mode) or stat.S_ISDIR(mode))):
            findings.append(
                Finding(
                    "ARCHIVE_SPECIAL_FILE", info.filename, "links and special files are forbidden"
                )
            )
            continue
        if info.flag_bits & 0x1:
            findings.append(Finding("ARCHIVE_ENCRYPTED_MEMBER", info.filename, "encrypted member"))
            continue
        if info.file_size > MAX_MEMBER_BYTES:
            findings.append(Finding("ARCHIVE_MEMBER_SIZE", info.filename, "member is too large"))
            continue
        if info.compress_size and info.file_size / info.compress_size > MAX_RATIO:
            findings.append(
                Finding(
                    "ARCHIVE_COMPRESSION_RATIO", info.filename, "compression ratio exceeds limit"
                )
            )
            continue
        if info.is_dir():
            continue
        try:
            member_data = archive.read(info)
        except (RuntimeError, NotImplementedError, OSError, zipfile.BadZipFile) as exc:
            findings.append(Finding("ARCHIVE_MEMBER_UNREADABLE", info.filename, type(exc).__name__))
            continue
        findings.extend(_scan_bytes(member_data, f"{location}!/{info.filename}"))
        if member.suffix.lower() == ".csv":
            findings.extend(_scan_csv_headers(member_data, f"{location}!/{info.filename}"))
    archive.close()
    return findings


def _scan_pdf(data: bytes, location: str) -> list[Finding]:
    if not data.startswith(b"%PDF-"):
        return [Finding("MEDIA_TYPE_MISMATCH", location, "expected PDF signature")]
    try:
        reader = PdfReader(io.BytesIO(data), strict=True)
    except (PdfReadError, OSError, ValueError) as exc:
        return [Finding("PDF_UNREADABLE", location, type(exc).__name__)]
    if reader.is_encrypted:
        return [Finding("PDF_ENCRYPTED", location, "encrypted PDF")]
    findings: list[Finding] = []
    root = reader.trailer.get("/Root")
    if root is None:
        return [Finding("PDF_MISSING_CATALOG", location, "PDF catalog is absent")]
    _walk_pdf(root, location, findings)
    return findings


def _walk_pdf(
    value: Any,
    location: str,
    findings: list[Finding],
) -> None:
    pending = [value]
    seen: set[tuple[int, int]] = set()
    while pending:
        current = pending.pop()
        if isinstance(current, IndirectObject):
            identity = (current.idnum, current.generation)
            if identity in seen:
                continue
            seen.add(identity)
            try:
                current = current.get_object()
            except (PdfReadError, OSError, ValueError):
                findings.append(
                    Finding("PDF_OBJECT_UNREADABLE", location, "indirect object unreadable")
                )
                continue
        if isinstance(current, DictionaryObject):
            for key, item in current.items():
                key_text = str(key)
                if key_text in PDF_DANGEROUS_KEYS:
                    findings.append(
                        Finding(
                            "PDF_ACTIVE_OR_EMBEDDED_CONTENT",
                            location,
                            f"dangerous key {key_text}",
                        )
                    )
                if key_text == "/OpenAction":
                    action = item.get_object() if isinstance(item, IndirectObject) else item
                    subtype = (
                        str(action.get("/S", "")) if isinstance(action, DictionaryObject) else ""
                    )
                    if subtype not in {"", "/GoTo"}:
                        findings.append(
                            Finding("PDF_ACTIVE_OPEN_ACTION", location, f"open action {subtype}")
                        )
                pending.append(item)
        elif isinstance(current, ArrayObject):
            pending.extend(current)


def _scan_bytes(data: bytes, location: str) -> list[Finding]:
    text = data.decode("utf-8", errors="ignore")
    return [
        Finding(f"SECRET_{code}", location, "potential credential material")
        for code, pattern in SECRET_PATTERNS
        if pattern.search(text)
    ]


def _scan_csv_headers(data: bytes, location: str) -> list[Finding]:
    try:
        headers = next(csv.reader(io.StringIO(data.decode("utf-8-sig"))), [])
    except (UnicodeError, csv.Error):
        return [Finding("CSV_UNREADABLE", location, "could not parse CSV header")]
    prohibited = sorted(
        {value.strip().lower() for value in headers} & PROHIBITED_PUBLIC_DATA_HEADERS
    )
    return (
        [Finding("PROHIBITED_PERSON_FIELD", location, ", ".join(prohibited))] if prohibited else []
    )


def _inside_root(root: Path, path: Path) -> Path:
    resolved_root = root.resolve()
    resolved = path.resolve()
    if not resolved.is_relative_to(resolved_root):
        raise PublicArchiveError(f"path escapes repository root: {path}")
    return resolved


def _object_result(
    inventory_id: str,
    payload_path: str,
    data: bytes,
    findings: list[Finding],
    disposition: str,
    error: str,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "inventory_id": inventory_id,
        "payload_path": payload_path,
        "size_bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest() if data else None,
        "blake3": blake3(data).hexdigest() if data else None,
        "disposition": disposition,
        "findings": [finding.as_dict() for finding in findings],
    }
    if error:
        result["error"] = error
    return result
