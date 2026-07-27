"""Controlled acquisition with checksums, rights routing and SSRF-safe defaults."""

from __future__ import annotations

import ipaddress
import mimetypes
import os
import shutil
import socket
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from jsonschema import Draft202012Validator, FormatChecker

from . import __version__
from .io import read_json, sha256_file, write_json
from .project import Project


class AcquisitionError(RuntimeError):
    """Raised when a source cannot be acquired safely or reproducibly."""


def acquire_local_file(
    project: Project,
    *,
    source_id: str,
    input_path: Path,
    destination_root: Path,
    source_edition_id: str | None = None,
    rights_status: str = "review_required",
    redistribution_status: str = "metadata_only",
    expected_sha256: str | None = None,
    notes: str = "",
) -> tuple[dict[str, Any], Path]:
    input_path = input_path.expanduser().resolve()
    if not input_path.is_file():
        raise AcquisitionError(f"Input file does not exist: {input_path}")
    checksum = sha256_file(input_path)
    if expected_sha256 and checksum != expected_sha256.lower():
        raise AcquisitionError(
            f"Checksum mismatch for {input_path}: expected {expected_sha256}, found {checksum}"
        )
    retrieved_at = datetime.now(UTC).replace(microsecond=0)
    acquisition_id = _acquisition_id(source_id, retrieved_at, checksum)
    stored_path = _store_if_allowed(
        input_path,
        destination_root,
        source_id=source_id,
        acquisition_id=acquisition_id,
        redistribution_status=redistribution_status,
    )
    content_type = mimetypes.guess_type(input_path.name)[0] or "application/octet-stream"
    manifest = {
        "schema_version": "1.0",
        "acquisition_id": acquisition_id,
        "source_id": source_id,
        "source_edition_id": source_edition_id,
        "retrieved_at": retrieved_at.isoformat(),
        "requested_url": input_path.as_uri(),
        "final_url": input_path.as_uri(),
        "method": "file",
        "status": "success" if stored_path else "metadata_only",
        "http_status": None,
        "content_type": content_type,
        "byte_count": input_path.stat().st_size,
        "sha256": checksum,
        "etag": None,
        "last_modified": datetime.fromtimestamp(input_path.stat().st_mtime, UTC)
        .replace(microsecond=0)
        .isoformat(),
        "rights_status": rights_status,
        "redistribution_status": redistribution_status,
        "stored_path": stored_path,
        "agent_version": __version__,
        "notes": notes,
        "query_or_filter": None,
    }
    _validate_manifest(project, manifest)
    manifest_path = _write_manifest(destination_root, manifest)
    return manifest, manifest_path


def acquire_url(
    project: Project,
    *,
    source_id: str,
    url: str,
    destination_root: Path,
    source_edition_id: str | None = None,
    rights_status: str = "review_required",
    redistribution_status: str = "metadata_only",
    expected_sha256: str | None = None,
    timeout_seconds: int = 30,
    max_bytes: int = 100 * 1024 * 1024,
    allow_http: bool = False,
    allow_private_network: bool = False,
    notes: str = "",
) -> tuple[dict[str, Any], Path]:
    validate_public_url(url, allow_http=allow_http, allow_private_network=allow_private_network)
    destination_root.mkdir(parents=True, exist_ok=True)
    request = Request(
        url,
        headers={
            "User-Agent": f"GFJD-Acquisition/{__version__} (+public research data pipeline)",
            "Accept": "*/*",
        },
        method="GET",
    )
    retrieved_at = datetime.now(UTC).replace(microsecond=0)
    fd, temp_name = tempfile.mkstemp(prefix=".gfjd-download-", dir=destination_root)
    os.close(fd)
    temp_path = Path(temp_name)
    try:
        try:
            with (
                urlopen(request, timeout=timeout_seconds) as response,
                temp_path.open("wb") as handle,
            ):
                final_url = response.geturl()
                validate_public_url(
                    final_url,
                    allow_http=allow_http,
                    allow_private_network=allow_private_network,
                )
                total = 0
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    total += len(chunk)
                    if total > max_bytes:
                        raise AcquisitionError(
                            f"Source exceeds maximum allowed size of {max_bytes} bytes"
                        )
                    handle.write(chunk)
                http_status = getattr(response, "status", None)
                headers = response.headers
        except AcquisitionError:
            raise
        except Exception as exc:
            raise AcquisitionError(f"HTTP acquisition failed for {url}: {exc}") from exc

        checksum = sha256_file(temp_path)
        if expected_sha256 and checksum != expected_sha256.lower():
            raise AcquisitionError(
                f"Checksum mismatch for {url}: expected {expected_sha256}, found {checksum}"
            )
        acquisition_id = _acquisition_id(source_id, retrieved_at, checksum)
        parsed = urlparse(final_url)
        filename = Path(parsed.path).name or f"{source_id}.bin"
        staged_named = temp_path.with_name(filename)
        os.replace(temp_path, staged_named)
        temp_path = staged_named
        stored_path = _store_if_allowed(
            temp_path,
            destination_root,
            source_id=source_id,
            acquisition_id=acquisition_id,
            redistribution_status=redistribution_status,
        )
        manifest = {
            "schema_version": "1.0",
            "acquisition_id": acquisition_id,
            "source_id": source_id,
            "source_edition_id": source_edition_id,
            "retrieved_at": retrieved_at.isoformat(),
            "requested_url": url,
            "final_url": final_url,
            "method": "http_get",
            "status": "success" if stored_path else "metadata_only",
            "http_status": http_status,
            "content_type": headers.get_content_type() if headers else "application/octet-stream",
            "byte_count": temp_path.stat().st_size,
            "sha256": checksum,
            "etag": headers.get("ETag") if headers else None,
            "last_modified": headers.get("Last-Modified") if headers else None,
            "rights_status": rights_status,
            "redistribution_status": redistribution_status,
            "stored_path": stored_path,
            "agent_version": __version__,
            "notes": notes,
            "query_or_filter": urlparse(final_url).query or None,
        }
        _validate_manifest(project, manifest)
        manifest_path = _write_manifest(destination_root, manifest)
        return manifest, manifest_path
    finally:
        temp_path.unlink(missing_ok=True)


def validate_public_url(
    url: str,
    *,
    allow_http: bool = False,
    allow_private_network: bool = False,
) -> None:
    parsed = urlparse(url)
    schemes = {"https", "http"} if allow_http else {"https"}
    if parsed.scheme not in schemes:
        raise AcquisitionError(f"URL scheme must be one of {sorted(schemes)}")
    if not parsed.hostname:
        raise AcquisitionError("URL has no hostname")
    if parsed.username or parsed.password:
        raise AcquisitionError("Credentials in source URLs are prohibited")
    if allow_private_network:
        return
    try:
        addresses = socket.getaddrinfo(parsed.hostname, parsed.port or 443, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise AcquisitionError(f"Could not resolve hostname {parsed.hostname}: {exc}") from exc
    if not addresses:
        raise AcquisitionError(f"Hostname {parsed.hostname} resolved to no address")
    for address in addresses:
        ip_text = address[4][0]
        ip = ipaddress.ip_address(ip_text)
        if not ip.is_global:
            raise AcquisitionError(
                f"Refusing non-public address {ip} for hostname {parsed.hostname}; "
                "use an explicitly controlled environment for private sources"
            )


def read_manifest(path: Path) -> dict[str, Any]:
    """Read an acquisition manifest as a plain JSON object."""

    value = read_json(path)
    if not isinstance(value, dict):
        raise AcquisitionError(f"Acquisition manifest must be a JSON object: {path}")
    return value


def verify_acquisition_manifest(project: Project, manifest_path: Path) -> list[str]:
    manifest = read_json(manifest_path)
    errors: list[str] = []
    try:
        _validate_manifest(project, manifest)
    except AcquisitionError as exc:
        errors.append(str(exc))
    stored = str(manifest.get("stored_path") or "")
    if stored:
        path = (manifest_path.parents[1] / stored).resolve()
        if not path.exists():
            errors.append(f"Stored acquisition file is missing: {path}")
        elif sha256_file(path) != manifest.get("sha256"):
            errors.append(f"Stored acquisition checksum does not match manifest: {path}")
    return errors


def _store_if_allowed(
    input_path: Path,
    destination_root: Path,
    *,
    source_id: str,
    acquisition_id: str,
    redistribution_status: str,
) -> str:
    if redistribution_status != "allowed":
        return ""
    relative = Path("files") / source_id / acquisition_id / input_path.name
    destination = destination_root / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(prefix=f".{destination.name}.", dir=destination.parent)
    os.close(fd)
    temporary = Path(temporary_name)
    try:
        shutil.copyfile(input_path, temporary)
        os.replace(temporary, destination)
    finally:
        temporary.unlink(missing_ok=True)
    return relative.as_posix()


def _write_manifest(destination_root: Path, manifest: dict[str, Any]) -> Path:
    manifest_path = destination_root / "manifests" / f"{manifest['acquisition_id']}.json"
    write_json(manifest_path, manifest)
    return manifest_path


def _validate_manifest(project: Project, manifest: dict[str, Any]) -> None:
    schema = read_json(project.root / "schemas" / "acquisition_manifest.schema.json")
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(manifest),
        key=lambda error: list(error.path),
    )
    if errors:
        raise AcquisitionError(
            "Acquisition manifest is invalid: " + "; ".join(error.message for error in errors)
        )


def _acquisition_id(source_id: str, retrieved_at: datetime, checksum: str) -> str:
    stamp = retrieved_at.strftime("%Y%m%dT%H%M%SZ")
    return f"ACQ-{source_id}-{stamp}-{checksum[:8].upper()}"
