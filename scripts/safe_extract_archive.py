#!/usr/bin/env python3
"""Safely extract a GFJD source archive and optionally verify a SHA-256 sidecar.

This script uses only the Python standard library.  It rejects traversal paths,
absolute paths, links, duplicate/case-colliding members, excessive expansion,
and unexpected multi-root archives.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import stat
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

MAX_MEMBERS = 20_000
MAX_EXPANDED_BYTES = 2 * 1024 * 1024 * 1024
MAX_MEMBER_BYTES = 512 * 1024 * 1024
MAX_COMPRESSION_RATIO = 1_000


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_sidecar(archive: Path, sidecar: Path | None) -> None:
    if sidecar is None:
        candidate = archive.with_suffix(archive.suffix + ".sha256")
        sidecar = candidate if candidate.is_file() else None
    if sidecar is None:
        return
    text = sidecar.read_text(encoding="utf-8").strip()
    expected = text.split()[0] if text else ""
    if len(expected) != 64:
        raise ValueError(f"Malformed SHA-256 sidecar: {sidecar}")
    actual = sha256_file(archive)
    if actual.lower() != expected.lower():
        raise ValueError(f"Archive checksum mismatch: expected {expected}, observed {actual}")


def validate_members(archive: zipfile.ZipFile) -> tuple[list[zipfile.ZipInfo], str]:
    infos = archive.infolist()
    if not infos:
        raise ValueError("Archive is empty")
    if len(infos) > MAX_MEMBERS:
        raise ValueError(f"Archive has {len(infos)} members; maximum is {MAX_MEMBERS}")
    names: set[str] = set()
    folded: set[str] = set()
    roots: set[str] = set()
    expanded = 0
    for info in infos:
        raw = info.filename
        path = PurePosixPath(raw)
        if not raw or raw.startswith(("/", "\\")) or path.is_absolute():
            raise ValueError(f"Unsafe absolute archive path: {raw!r}")
        if "\\" in raw:
            raise ValueError(f"Backslash archive path is not permitted: {raw!r}")
        if any(part in {"", ".", ".."} for part in path.parts):
            raise ValueError(f"Unsafe archive path: {raw!r}")
        normalized = path.as_posix().rstrip("/")
        if normalized in names:
            raise ValueError(f"Duplicate archive member: {normalized}")
        names.add(normalized)
        casefolded = normalized.casefold()
        if casefolded in folded:
            raise ValueError(f"Case-colliding archive member: {normalized}")
        folded.add(casefolded)
        roots.add(path.parts[0])
        mode = info.external_attr >> 16
        if stat.S_ISLNK(mode):
            raise ValueError(f"Symbolic links are not permitted: {raw}")
        if info.file_size > MAX_MEMBER_BYTES:
            raise ValueError(f"Archive member is too large: {raw}")
        expanded += info.file_size
        if expanded > MAX_EXPANDED_BYTES:
            raise ValueError("Archive expanded size exceeds the safety budget")
        if info.compress_size and info.file_size / info.compress_size > MAX_COMPRESSION_RATIO:
            raise ValueError(f"Archive member has an excessive compression ratio: {raw}")
    if len(roots) != 1:
        raise ValueError(f"Archive must have one top-level directory; found {sorted(roots)}")
    return infos, next(iter(roots))


def extract(
    archive_path: Path, destination: Path, sidecar: Path | None = None
) -> dict[str, str | int]:
    archive_path = archive_path.expanduser().resolve()
    destination = destination.expanduser().resolve()
    if not archive_path.is_file():
        raise FileNotFoundError(archive_path)
    verify_sidecar(archive_path, sidecar)
    if destination.exists() and any(destination.iterdir()):
        raise ValueError(f"Destination is not empty: {destination}")
    destination.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive_path) as archive:
        infos, root_name = validate_members(archive)
        bad_member = archive.testzip()
        if bad_member:
            raise ValueError(f"Archive CRC failure: {bad_member}")
        with tempfile.TemporaryDirectory(dir=destination.parent) as temporary:
            staging = Path(temporary)
            for info in infos:
                member = PurePosixPath(info.filename)
                target = staging.joinpath(*member.parts)
                resolved = target.resolve()
                if not resolved.is_relative_to(staging.resolve()):
                    raise ValueError(f"Archive path escapes extraction root: {info.filename}")
                if info.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(info) as source, target.open("wb") as output:
                    shutil.copyfileobj(source, output, length=1024 * 1024)
            extracted_root = staging / root_name
            final_root = destination / root_name
            if final_root.exists():
                raise ValueError(f"Extraction target already exists: {final_root}")
            shutil.move(str(extracted_root), str(final_root))
    return {
        "archive": str(archive_path),
        "archive_sha256": sha256_file(archive_path),
        "repository_root": str((destination / root_name).resolve()),
        "members": len(infos),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--destination", type=Path, default=Path.cwd())
    parser.add_argument("--sidecar", type=Path)
    args = parser.parse_args()
    try:
        result = extract(args.archive, args.destination, args.sidecar)
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
