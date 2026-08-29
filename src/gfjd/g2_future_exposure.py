"""Deterministic exposure snapshots for prospective G2 calibration lineages."""

from __future__ import annotations

import hashlib
import ipaddress
import json
import posixpath
import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, quote, unquote, urlencode, urlsplit, urlunsplit


class FutureExposureError(ValueError):
    """Raised when exposure evidence cannot be verified fail-closed."""


_SHA256 = re.compile(r"^[a-f0-9]{64}$")
_URL_FIELDS = frozenset(
    {
        "candidate_url",
        "canonical_url",
        "direct_pdf_url",
        "download_url",
        "final_url",
        "landing_page_url",
        "proposed_url",
        "requested_entrypoint",
        "request_url",
        "result_url",
        "retrieval_entrypoint",
        "source_url",
        "url",
    }
)
_URL_LIST_FIELDS = frozenset({"denied_urls", "observed_urls", "urls"})
_EDITION_FIELDS = frozenset({"edition_alias", "edition_id", "source_edition_id"})
_SERIES_FIELDS = frozenset({"source_series_id"})
_SOURCE_FIELDS = frozenset({"source_id"})
_CONTENT_DIGEST_FIELDS = frozenset({"source_sha256"})
_KINDS = frozenset({"exposure_ledger", "g2_artifact", "registrar_observations"})


def sha256_file(path: Path) -> str:
    """Return the SHA-256 digest of exact file bytes."""

    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_url(value: str) -> str:
    """Canonicalize a public HTTP locator conservatively for deny matching.

    HTTP and HTTPS intentionally collapse to HTTPS: a scheme upgrade must not
    make an exposed resource appear unseen. Query pairs are sorted while
    duplicates and blank values are retained.
    """

    if not isinstance(value, str) or not value:
        raise FutureExposureError("exposure URL must be a nonempty string")
    try:
        parsed = urlsplit(value)
        port = parsed.port
    except ValueError as error:
        raise FutureExposureError(f"invalid exposure URL: {value}") from error
    scheme = parsed.scheme.lower()
    if scheme == "file":
        if parsed.query or parsed.fragment or parsed.username is not None:
            raise FutureExposureError(f"invalid file exposure URL: {value}")
        decoded_path = unquote(parsed.path)
        normalized_path = posixpath.normpath(decoded_path)
        if decoded_path.startswith("/") and not normalized_path.startswith("/"):
            normalized_path = "/" + normalized_path
        path = quote(normalized_path, safe="/%:@!$&'()*+,;=-._~")
        return urlunsplit(("file", parsed.netloc.lower(), path, "", ""))
    if scheme not in {"http", "https"} or not parsed.hostname:
        raise FutureExposureError(f"unsupported exposure URL: {value}")
    if parsed.username is not None or parsed.password is not None:
        raise FutureExposureError("exposure URL must not contain user information")
    host = parsed.hostname.rstrip(".").lower()
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        try:
            host = host.encode("idna").decode("ascii")
        except UnicodeError as error:
            raise FutureExposureError(f"invalid exposure URL host: {value}") from error
        netloc_host = host
    else:
        netloc_host = f"[{address.compressed}]" if address.version == 6 else address.compressed
    if not host:
        raise FutureExposureError("exposure URL host is empty")
    netloc = netloc_host if port in (None, 80, 443) else f"{netloc_host}:{port}"
    decoded_path = unquote(parsed.path or "/")
    normalized_path = posixpath.normpath(decoded_path)
    if not normalized_path.startswith("/"):
        normalized_path = "/" + normalized_path
    if decoded_path.endswith("/") and not normalized_path.endswith("/"):
        normalized_path += "/"
    path = quote(normalized_path, safe="/%:@!$&'()*+,;=-._~")
    query = urlencode(sorted(parse_qsl(parsed.query, keep_blank_values=True)), doseq=True)
    return urlunsplit(("https", netloc, path, query, ""))


def canonical_request_identity(*, method: str, url: str, body_sha256: str | None = None) -> str:
    """Return a canonical request identity including an optional body digest."""

    normalized_method = method.strip().upper() if isinstance(method, str) else ""
    if not normalized_method or not re.fullmatch(r"[A-Z]+", normalized_method):
        raise FutureExposureError("request method is invalid")
    if body_sha256 is not None and not _SHA256.fullmatch(body_sha256):
        raise FutureExposureError("request body_sha256 is invalid")
    return "\0".join((normalized_method, canonical_url(url), body_sha256 or "-"))


def build_exposure_snapshot(root: Path, input_manifest: Mapping[str, Any]) -> dict[str, Any]:
    """Build a deterministic snapshot from digest-bound exposure artifacts."""

    resolved_root = root.resolve()
    lineage_id, descriptors = _validate_manifest(input_manifest)
    collected = _empty_collected()
    verified: list[dict[str, str]] = []
    visited: set[tuple[str, str]] = set()
    active: set[tuple[str, str]] = set()
    for descriptor in descriptors:
        _consume_descriptor(
            resolved_root,
            descriptor,
            collected=collected,
            verified=verified,
            visited=visited,
            active=active,
        )
    values = {key: sorted(items) for key, items in collected.items()}
    counts = {key: len(items) for key, items in values.items()}
    digests = {key: _canonical_digest(items) for key, items in values.items()}
    return {
        "schema_version": "1.0",
        "lineage_id": lineage_id,
        "canonicalization": "gfjd_future_exposure_v1",
        "inputs": sorted(verified, key=lambda item: (item["path"], item["sha256"])),
        "exposure": values,
        "counts": counts,
        "digests": digests,
    }


def verify_exposure_snapshot(
    root: Path, input_manifest: Mapping[str, Any], snapshot: Mapping[str, Any]
) -> list[str]:
    """Rebuild and byte-semantically compare a claimed exposure snapshot."""

    try:
        expected = build_exposure_snapshot(root, input_manifest)
    except (FutureExposureError, OSError, UnicodeError, json.JSONDecodeError) as error:
        return [str(error)]
    if dict(snapshot) != expected:
        return ["exposure snapshot does not reproduce from its bound inputs"]
    return []


def _validate_manifest(value: Mapping[str, Any]) -> tuple[str, list[dict[str, str]]]:
    if not isinstance(value, Mapping) or set(value) != {"schema_version", "lineage_id", "inputs"}:
        raise FutureExposureError("exposure input manifest has unexpected fields")
    if value["schema_version"] != "1.0":
        raise FutureExposureError("unsupported exposure input manifest schema_version")
    lineage_id = value["lineage_id"]
    if not isinstance(lineage_id, str) or not re.fullmatch(
        r"[A-Z0-9][A-Z0-9_-]{2,127}", lineage_id
    ):
        raise FutureExposureError("exposure lineage_id is invalid")
    inputs = value["inputs"]
    if not isinstance(inputs, list) or not inputs:
        raise FutureExposureError("exposure input manifest requires inputs")
    descriptors = [_validate_descriptor(item) for item in inputs]
    identities = {(item["path"], item["sha256"]) for item in descriptors}
    paths = {item["path"] for item in descriptors}
    if len(identities) != len(descriptors) or len(paths) != len(descriptors):
        raise FutureExposureError("exposure input manifest contains duplicate inputs")
    return lineage_id, descriptors


def _validate_descriptor(value: Any) -> dict[str, str]:
    if not isinstance(value, Mapping) or set(value) != {"path", "sha256", "kind"}:
        raise FutureExposureError("exposure descriptor is malformed")
    if value["kind"] not in _KINDS:
        raise FutureExposureError("exposure descriptor kind is unsupported")
    if not isinstance(value["path"], str) or not value["path"]:
        raise FutureExposureError("exposure descriptor path is invalid")
    if not isinstance(value["sha256"], str) or not _SHA256.fullmatch(value["sha256"]):
        raise FutureExposureError("exposure descriptor sha256 is invalid")
    return {key: str(value[key]) for key in ("path", "sha256", "kind")}


def _consume_descriptor(
    root: Path,
    descriptor: Mapping[str, str],
    *,
    collected: dict[str, set[str]],
    verified: list[dict[str, str]],
    visited: set[tuple[str, str]],
    active: set[tuple[str, str]],
) -> None:
    identity = (descriptor["path"], descriptor["sha256"])
    if identity in active:
        raise FutureExposureError("exposure predecessor chain contains a cycle")
    if identity in visited:
        return
    path = _safe_file(root, descriptor["path"])
    if sha256_file(path) != descriptor["sha256"]:
        raise FutureExposureError(f"exposure binding mismatch: {descriptor['path']}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise FutureExposureError(
            f"exposure input is invalid JSON: {descriptor['path']}"
        ) from error
    if not isinstance(payload, Mapping):
        raise FutureExposureError(f"exposure input must be an object: {descriptor['path']}")
    _validate_kind_payload(payload, descriptor["kind"])
    active.add(identity)
    if descriptor["kind"] == "exposure_ledger" and payload.get("predecessor") is not None:
        predecessor = payload["predecessor"]
        if not isinstance(predecessor, Mapping):
            raise FutureExposureError("exposure predecessor descriptor is malformed")
        predecessor_descriptor = _validate_descriptor({**predecessor, "kind": "exposure_ledger"})
        _consume_descriptor(
            root,
            predecessor_descriptor,
            collected=collected,
            verified=verified,
            visited=visited,
            active=active,
        )
    _collect(payload, collected)
    active.remove(identity)
    visited.add(identity)
    verified.append(dict(descriptor))


def _validate_kind_payload(payload: Mapping[str, Any], kind: str) -> None:
    if kind == "exposure_ledger":
        if not any(key in payload for key in ("denied_urls", "entries")):
            raise FutureExposureError("exposure ledger contains no exposure collection")
        if "entries" in payload and not isinstance(payload["entries"], list):
            raise FutureExposureError("exposure ledger entries must be an array")
        if "denied_urls" in payload and not isinstance(payload["denied_urls"], list):
            raise FutureExposureError("exposure ledger denied_urls must be an array")
    elif kind == "registrar_observations":
        fields = ("observations", "exposure_events", "candidate_hypotheses")
        present = [payload[key] for key in fields if key in payload]
        if not present or not all(isinstance(value, list) for value in present):
            raise FutureExposureError(
                "registrar observations require an observations or exposure-events array"
            )


def _collect(value: Any, output: dict[str, set[str]], *, parent_key: str | None = None) -> None:
    if isinstance(value, Mapping):
        request = _request_from_mapping(value)
        if request is not None:
            output["request_identities"].add(request)
        for key, child in value.items():
            if key in _URL_FIELDS and child is not None:
                output["urls"].add(canonical_url(_string(child, key)))
            elif key in _URL_LIST_FIELDS:
                for item in _string_sequence(child, key):
                    output["urls"].add(canonical_url(item))
            elif key in _EDITION_FIELDS and child is not None:
                output["edition_ids"].add(_identity(child, key))
            elif key in _SERIES_FIELDS and child is not None:
                output["source_series_ids"].add(_identity(child, key))
            elif key in _SOURCE_FIELDS and child is not None:
                output["source_ids"].add(_identity(child, key))
            elif key in _CONTENT_DIGEST_FIELDS and child is not None:
                values = [child] if isinstance(child, str) else child
                for item in _string_sequence(values, key):
                    if not _SHA256.fullmatch(item):
                        raise FutureExposureError(f"invalid content digest in {key}")
                    output["content_sha256"].add(item)
            elif key.endswith("_url") and child is not None:
                output["urls"].add(canonical_url(_string(child, key)))
            _collect(child, output, parent_key=key)
    elif isinstance(value, list):
        for child in value:
            _collect(child, output, parent_key=parent_key)


def _request_from_mapping(value: Mapping[str, Any]) -> str | None:
    method = value.get("method", value.get("request_method"))
    url = value.get("url", value.get("request_url"))
    if method is None and url is None:
        return None
    if method is None or url is None:
        return None
    body_digest = value.get("body_sha256", value.get("request_body_sha256"))
    if body_digest is not None and not isinstance(body_digest, str):
        raise FutureExposureError("request body digest must be a string")
    return canonical_request_identity(
        method=_string(method, "method"), url=_string(url, "url"), body_sha256=body_digest
    )


def _safe_file(root: Path, relative: str) -> Path:
    candidate = Path(relative)
    if candidate.is_absolute() or ".." in candidate.parts or candidate.as_posix() != relative:
        raise FutureExposureError(f"exposure path escapes repository: {relative}")
    current = root
    for part in candidate.parts:
        current /= part
        if current.is_symlink():
            raise FutureExposureError(f"exposure path contains symlink: {relative}")
    try:
        current.resolve(strict=False).relative_to(root)
    except ValueError as error:
        raise FutureExposureError(f"exposure path escapes repository: {relative}") from error
    if not current.is_file():
        raise FutureExposureError(f"exposure input is missing: {relative}")
    return current


def _empty_collected() -> dict[str, set[str]]:
    return {
        "urls": set(),
        "request_identities": set(),
        "edition_ids": set(),
        "source_series_ids": set(),
        "source_ids": set(),
        "content_sha256": set(),
    }


def _string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise FutureExposureError(f"{field} must be a nonempty string")
    return value


def _string_sequence(value: Any, field: str) -> Sequence[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
        raise FutureExposureError(f"{field} must contain nonempty strings")
    return value


def _identity(value: Any, field: str) -> str:
    text = _string(value, field).strip()
    if not text:
        raise FutureExposureError(f"{field} must be nonblank")
    return text.casefold()


def _canonical_digest(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()
