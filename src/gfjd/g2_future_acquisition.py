"""Fail-closed transport for an explicitly bound future G2 campaign."""

from __future__ import annotations

import hashlib
import ipaddress
import os
import socket
import tempfile
from collections.abc import Callable, Iterable, Mapping
from pathlib import Path
from typing import BinaryIO, Protocol
from urllib.parse import urljoin, urlsplit, urlunsplit

from .io import canonical_json_bytes, write_json


class G2FutureAcquisitionError(RuntimeError):
    """Raised before unsafe I/O or when a bounded acquisition cannot complete."""


class Response(Protocol):
    status: int
    headers: Mapping[str, str]

    def read(self, size: int = -1) -> bytes: ...

    def __enter__(self) -> Response: ...

    def __exit__(self, *args: object) -> object: ...


Transport = Callable[..., Response]
Resolver = Callable[[str, int], Iterable[str]]


def acquire_exact_url(
    *,
    url: str,
    exact_url_allowlist: Iterable[str],
    destination_root: Path,
    output_name: str,
    transport: Transport,
    resolver: Resolver | None = None,
    max_redirects: int = 3,
    max_bytes: int = 25 * 1024 * 1024,
    timeout_seconds: float = 30.0,
    allowed_content_types: Iterable[str] = (
        "application/json",
        "application/pdf",
        "application/vnd.oasis.opendocument.spreadsheet",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "text/csv",
        "text/html",
    ),
) -> tuple[dict[str, object], Path, Path]:
    """GET one allowlisted public URL with manually validated redirects.

    ``transport`` is injected so the campaign can bind a concrete HTTP client and
    tests can prove the policy without network access. Redirect following must be
    disabled in that client; every response is handled here.
    """
    if max_redirects < 0 or max_redirects > 10:
        raise G2FutureAcquisitionError("max_redirects must be between 0 and 10")
    if max_bytes < 1:
        raise G2FutureAcquisitionError("max_bytes must be positive")
    if not 0 < timeout_seconds <= 120:
        raise G2FutureAcquisitionError("timeout_seconds must be in (0, 120]")

    resolve = resolver or _resolve_public_addresses
    allowlist = tuple(exact_url_allowlist)
    if not allowlist or len(set(allowlist)) != len(allowlist):
        raise G2FutureAcquisitionError("exact URL allowlist must be nonempty and unique")
    for allowed in allowlist:
        _validate_exact_public_https_url(allowed, resolve)
    if url not in allowlist:
        raise G2FutureAcquisitionError("initial URL is outside the exact allowlist")

    root = destination_root.expanduser().resolve()
    payload_path = _confined_child(root, output_name)
    receipt_path = _confined_child(root, f"{output_name}.receipt.json")
    if payload_path.exists() or receipt_path.exists():
        raise G2FutureAcquisitionError("acquisition output or receipt already exists")
    content_types = frozenset(item.lower() for item in allowed_content_types)
    if not content_types:
        raise G2FutureAcquisitionError("allowed content types must be nonempty")

    # Validate every configuration value before creating a directory or request.
    root.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{payload_path.name}.", suffix=".tmp", dir=root)
    temp_path = Path(temp_name)
    os.close(fd)
    hops: list[dict[str, object]] = []
    current = url
    completed = False
    try:
        for redirect_count in range(max_redirects + 1):
            # Revalidate immediately before every request, including DNS, so a
            # redirect cannot bypass the original preflight or exploit rebinding.
            _validate_exact_public_https_url(current, resolve)
            if current not in allowlist:
                raise G2FutureAcquisitionError("redirect destination is outside exact allowlist")
            request_digest = _digest_json({"method": "GET", "url": current})
            try:
                response_context = transport(
                    current,
                    method="GET",
                    timeout=timeout_seconds,
                    follow_redirects=False,
                )
            except Exception as exc:
                raise G2FutureAcquisitionError(f"GET failed for allowlisted URL: {exc}") from exc
            with response_context as response:
                status = int(response.status)
                headers = {key.lower(): value.strip() for key, value in response.headers.items()}
                header_digest = _digest_json(headers)
                if status in {301, 302, 303, 307, 308}:
                    location = headers.get("location")
                    if not location:
                        raise G2FutureAcquisitionError("redirect response has no Location header")
                    target = urljoin(current, location)
                    _validate_exact_public_https_url(target, resolve)
                    if target not in allowlist:
                        raise G2FutureAcquisitionError(
                            "redirect destination is outside exact allowlist"
                        )
                    hops.append(
                        {
                            "index": redirect_count,
                            "request_url": current,
                            "method": "GET",
                            "request_sha256": request_digest,
                            "status": status,
                            "response_headers_sha256": header_digest,
                            "redirect_url": target,
                            "body_requested": False,
                        }
                    )
                    current = target
                    continue
                if status != 200:
                    raise G2FutureAcquisitionError(f"unexpected HTTP status {status}")
                media_type = headers.get("content-type", "").split(";", 1)[0].strip().lower()
                if media_type not in content_types:
                    raise G2FutureAcquisitionError(
                        f"content type {media_type or '<missing>'} is not allowed"
                    )
                declared_length = headers.get("content-length")
                if declared_length is not None:
                    try:
                        if int(declared_length) > max_bytes:
                            raise G2FutureAcquisitionError("declared content length exceeds limit")
                    except ValueError as exc:
                        raise G2FutureAcquisitionError("invalid Content-Length header") from exc
                digest, byte_count = _stream_bounded(response, temp_path, max_bytes)
                hops.append(
                    {
                        "index": redirect_count,
                        "request_url": current,
                        "method": "GET",
                        "request_sha256": request_digest,
                        "status": status,
                        "response_headers_sha256": header_digest,
                        "content_type": media_type,
                        "body_requested": True,
                        "byte_count": byte_count,
                        "body_sha256": digest,
                    }
                )
                receipt: dict[str, object] = {
                    "schema_version": "1.0",
                    "requested_url": url,
                    "exact_url_allowlist": sorted(allowlist),
                    "allowlist_sha256": _digest_json(sorted(allowlist)),
                    "method": "GET",
                    "redirect_policy": "manual_exact_allowlist",
                    "hops": hops,
                    "final": {
                        "url": current,
                        "content_type": media_type,
                        "byte_count": byte_count,
                        "sha256": digest,
                    },
                }
                os.replace(temp_path, payload_path)
                write_json(receipt_path, receipt)
                completed = True
                return receipt, payload_path, receipt_path
        raise G2FutureAcquisitionError("redirect limit exceeded")
    finally:
        temp_path.unlink(missing_ok=True)
        if not completed:
            payload_path.unlink(missing_ok=True)
            receipt_path.unlink(missing_ok=True)


def _canonical_url(url: str) -> str:
    parts = urlsplit(url)
    host = parts.hostname or ""
    port = f":{parts.port}" if parts.port is not None else ""
    return urlunsplit((parts.scheme.lower(), f"{host.lower()}{port}", parts.path, parts.query, ""))


def _validate_exact_public_https_url(url: str, resolver: Resolver) -> None:
    try:
        parts = urlsplit(url)
        port = parts.port
    except ValueError as exc:
        raise G2FutureAcquisitionError(f"invalid URL: {exc}") from exc
    if parts.scheme != "https":
        raise G2FutureAcquisitionError("only canonical HTTPS URLs are allowed")
    if not parts.hostname:
        raise G2FutureAcquisitionError("URL has no hostname")
    if parts.username is not None or parts.password is not None:
        raise G2FutureAcquisitionError("URL userinfo or credentials are prohibited")
    if parts.fragment:
        raise G2FutureAcquisitionError("URL fragments are prohibited")
    if _canonical_url(url) != url:
        raise G2FutureAcquisitionError("URL is not in canonical exact form")
    addresses = tuple(resolver(parts.hostname, port or 443))
    if not addresses:
        raise G2FutureAcquisitionError("hostname resolved to no address")
    for address in addresses:
        try:
            ip = ipaddress.ip_address(address)
        except ValueError as exc:
            raise G2FutureAcquisitionError("resolver returned an invalid IP address") from exc
        if not ip.is_global:
            raise G2FutureAcquisitionError(f"destination address {ip} is not public")


def _resolve_public_addresses(host: str, port: int) -> Iterable[str]:
    try:
        answers = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise G2FutureAcquisitionError(f"could not resolve hostname {host}: {exc}") from exc
    return (answer[4][0] for answer in answers)


def _confined_child(root: Path, name: str) -> Path:
    if not name or Path(name).name != name or name in {".", ".."}:
        raise G2FutureAcquisitionError("output name must be one plain filename")
    candidate = (root / name).resolve()
    if candidate.parent != root:
        raise G2FutureAcquisitionError("output path escapes controlled root")
    return candidate


def _stream_bounded(response: BinaryIO, path: Path, max_bytes: int) -> tuple[str, int]:
    digest = hashlib.sha256()
    total = 0
    with path.open("wb") as handle:
        while True:
            chunk = response.read(min(1024 * 1024, max_bytes + 1 - total))
            if not chunk:
                break
            total += len(chunk)
            if total > max_bytes:
                raise G2FutureAcquisitionError("response body exceeds byte limit")
            digest.update(chunk)
            handle.write(chunk)
        handle.flush()
        os.fsync(handle.fileno())
    return digest.hexdigest(), total


def _digest_json(value: object) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()
