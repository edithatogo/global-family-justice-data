"""Pure bounded selection of metadata bytes from existing monitor artifacts.

No transport, extraction, decoding, receipt interpretation, or filesystem access
is provided. The caller supplies the frozen metadata set for its reviewed route.
An optional execution.log is inspected only through ZIP directory metadata: its
contents are never opened, decompressed, CRC-checked, or returned.
"""

from __future__ import annotations

import io
import stat
import zipfile
import zlib

MAX_ARCHIVE_BYTES = 8 * 1024 * 1024
MAX_MEMBERS = 32
MAX_MEMBER_BYTES = 8 * 1024 * 1024
MAX_EXPANDED_BYTES = 16 * 1024 * 1024
MAX_COMPRESSION_RATIO = 1000
METADATA_NAMES = frozenset(
    {"receipt.json", "exposure-ledger.jsonl", "novel-exposure-ledger.jsonl", "observations.json"}
)


class MonitorArtifactError(ValueError):
    """The artifact or caller's route does not satisfy the bounded contract."""


def _validate_members(members: list[zipfile.ZipInfo], required_members: frozenset[str]) -> None:
    if len(members) > MAX_MEMBERS:
        raise MonitorArtifactError("artifact member count exceeds limit")
    seen: set[str] = set()
    total = 0
    for member in members:
        name = member.orig_filename
        if (
            name != member.filename
            or not name
            or name in {".", ".."}
            or "/" in name
            or "\\" in name
            or name.casefold() in seen
        ):
            raise MonitorArtifactError("artifact has unsafe or colliding member names")
        seen.add(name.casefold())
        if name not in required_members and name != "execution.log":
            raise MonitorArtifactError("artifact member is outside the frozen metadata route")
        mode = member.external_attr >> 16
        if (
            member.is_dir()
            or member.external_attr & 0x10
            or stat.S_IFMT(mode) not in {0, stat.S_IFREG}
        ):
            raise MonitorArtifactError("artifact contains a directory, link, or special file")
        if member.flag_bits & (1 | 0x40):
            raise MonitorArtifactError("encrypted artifact members are forbidden")
        if member.compress_type not in {zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED}:
            raise MonitorArtifactError("unsupported artifact compression method")
        if not 0 <= member.file_size <= MAX_MEMBER_BYTES or member.compress_size < 0:
            raise MonitorArtifactError("artifact member byte limit exceeded")
        if member.file_size > member.compress_size * MAX_COMPRESSION_RATIO:
            raise MonitorArtifactError("artifact compression ratio exceeds limit")
        total += member.file_size
        if total > MAX_EXPANDED_BYTES:
            raise MonitorArtifactError("artifact expanded byte limit exceeded")
    if seen - {"execution.log"} != required_members:
        raise MonitorArtifactError("artifact does not contain the exact frozen metadata route")


def read_monitor_artifact(
    archive_bytes: bytes, *, required_members: frozenset[str]
) -> dict[str, bytes]:
    """Return original selected bytes, or fail without exposing partial results.

    All directory entries (including an unread log) pass metadata bounds before
    any member is opened. Selected streams are bounded and read through EOF for
    CRC validation. Content semantics and provenance remain caller obligations.
    Only stored and deflated ZIP members are supported.
    """
    if (
        not isinstance(required_members, frozenset)
        or "receipt.json" not in required_members
        or not required_members <= METADATA_NAMES
    ):
        raise MonitorArtifactError("required members must be a frozen metadata route with receipt")
    if not isinstance(archive_bytes, bytes) or len(archive_bytes) > MAX_ARCHIVE_BYTES:
        raise MonitorArtifactError("artifact archive byte limit or bytes input contract violated")
    try:
        with zipfile.ZipFile(io.BytesIO(archive_bytes), "r") as archive:
            members = archive.infolist()
            _validate_members(members, required_members)
            selected: dict[str, bytes] = {}
            for member in members:
                if member.filename == "execution.log":
                    continue
                with archive.open(member, "r") as stream:
                    payload = stream.read(min(member.file_size, MAX_MEMBER_BYTES) + 1)
                    if len(payload) != member.file_size:
                        raise MonitorArtifactError("artifact member size mismatch")
                selected[member.filename] = payload
            return selected
    except (zipfile.BadZipFile, EOFError, OSError, RuntimeError, zlib.error) as exc:
        raise MonitorArtifactError("malformed or unreadable metadata artifact") from exc
