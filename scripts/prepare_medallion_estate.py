"""Create/verify a fresh local estate draft from four configuration files only.

No discovery, subprocess, network, source payload or upload operation exists.
Intended identities are configuration metadata, not observed remote availability
or card-standard conformance. Safe descriptor-relative filesystem operations are
required; unsupported platforms fail closed. Output's parent must already exist.
"""

from __future__ import annotations

import argparse
import os
import stat
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from gfjd.medallion_estate import EstateError, prepare_estate, verify_estate

ROOT = Path(__file__).absolute().parents[1]
SOURCEFILES = (
    "config/bootstrap.toml",
    "config/archive_targets.toml",
    "portfolio/products.toml",
    ".gfjd/product.toml",
)
OUTPUT_FILES = frozenset(
    {
        "estate-manifest.json",
        "datasets/gfjd-source-archive/README.md",
        "datasets/gfjd-source-catalogue/README.md",
        "datasets/gfjd-observations/README.md",
        "datasets/gfjd-outcomes-evidence/README.md",
        "datasets/gfjd-extraction-benchmark/README.md",
        "explorer/README.md",
        "explorer/index.html",
    }
)
OUTPUT_DIRS = frozenset(
    str(parent) for name in OUTPUT_FILES for parent in Path(name).parents if str(parent) != "."
)
MAX_FILE_BYTES = 1024 * 1024
MAX_TOTAL_BYTES = 8 * 1024 * 1024
MAX_ENTRIES = len(OUTPUT_FILES) + len(OUTPUT_DIRS)


class EstateCliError(ValueError):
    """Fixed-message failure without exposing untrusted file contents."""


def _require(condition: bool) -> None:
    if not condition:
        raise EstateCliError("estate draft filesystem contract failed")


def _directory_flags() -> int:
    _require(hasattr(os, "O_DIRECTORY") and hasattr(os, "O_NOFOLLOW"))
    return os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW


@contextmanager
def _descend(parent: int, parts: tuple[str, ...]) -> Iterator[int]:
    current = os.dup(parent)
    try:
        for part in parts:
            _require(part not in {"", ".", ".."} and "/" not in part and "\\" not in part)
            child = os.open(part, _directory_flags(), dir_fd=current)
            os.close(current)
            current = child
        yield current
    finally:
        os.close(current)


@contextmanager
def _directory(path: Path) -> Iterator[int]:
    absolute = path.absolute()
    _require(absolute.anchor == "/")
    root = os.open("/", _directory_flags())
    try:
        with _descend(root, absolute.parts[1:]) as descriptor:
            yield descriptor
    finally:
        os.close(root)


def _read_at(parent: int, name: str) -> bytes:
    descriptor = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
    with os.fdopen(descriptor, "rb") as stream:
        before = os.fstat(stream.fileno())
        _require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1)
        _require(0 <= before.st_size <= MAX_FILE_BYTES)
        raw = stream.read(MAX_FILE_BYTES + 1)
        after = os.fstat(stream.fileno())
        _require(len(raw) == before.st_size and len(raw) <= MAX_FILE_BYTES)
        _require(
            (before.st_size, before.st_mtime_ns, before.st_ctime_ns)
            == (after.st_size, after.st_mtime_ns, after.st_ctime_ns)
        )
        return raw


def read_configs() -> dict[str, bytes]:
    result = {}
    with _directory(ROOT) as root:
        for name in SOURCEFILES:
            relative = Path(name)
            with _descend(root, relative.parts[:-1]) as parent:
                result[name] = _read_at(parent, relative.name)
    return result


def _validate_artifacts(artifacts: dict[str, bytes]) -> None:
    _require(isinstance(artifacts, dict) and set(artifacts) == OUTPUT_FILES)
    _require(
        all(isinstance(raw, bytes) and len(raw) <= MAX_FILE_BYTES for raw in artifacts.values())
    )
    _require(sum(len(raw) for raw in artifacts.values()) <= MAX_TOTAL_BYTES)


def _write_bundle(destination: Path, artifacts: dict[str, bytes]) -> None:
    _validate_artifacts(artifacts)
    _require(destination.name not in {"", ".", ".."})
    with _directory(destination.parent) as parent:
        os.mkdir(destination.name, dir_fd=parent)
        with _descend(parent, (destination.name,)) as root:
            for name in sorted(OUTPUT_DIRS, key=lambda value: (len(Path(value).parts), value)):
                relative = Path(name)
                with _descend(root, relative.parts[:-1]) as folder:
                    os.mkdir(relative.name, dir_fd=folder)
            for name, raw in sorted(artifacts.items()):
                relative = Path(name)
                with _descend(root, relative.parts[:-1]) as folder:
                    descriptor = os.open(
                        relative.name,
                        os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                        0o644,
                        dir_fd=folder,
                    )
                    with os.fdopen(descriptor, "wb") as stream:
                        stream.write(raw)
    # Do not delete any partial bundle after an I/O failure. Fresh-only semantics
    # keep existing user work untouched; subsequent verification fails closed.


def read_bundle(directory: Path) -> dict[str, bytes]:
    artifacts: dict[str, bytes] = {}
    seen_dirs: set[str] = set()
    entries = 0
    total = 0

    def visit(folder: int, prefix: str) -> None:
        nonlocal entries, total
        with os.scandir(folder) as iterator:
            for entry in iterator:
                entries += 1
                _require(entries <= MAX_ENTRIES)
                name = f"{prefix}/{entry.name}" if prefix else entry.name
                _require(name in OUTPUT_FILES or name in OUTPUT_DIRS)
                mode = entry.stat(follow_symlinks=False).st_mode
                if name in OUTPUT_DIRS:
                    _require(stat.S_ISDIR(mode))
                    seen_dirs.add(name)
                    with _descend(folder, (entry.name,)) as child:
                        visit(child, name)
                else:
                    _require(stat.S_ISREG(mode))
                    raw = _read_at(folder, entry.name)
                    total += len(raw)
                    _require(total <= MAX_TOTAL_BYTES)
                    artifacts[name] = raw

    with _directory(directory) as root:
        visit(root, "")
    _require(seen_dirs == OUTPUT_DIRS)
    _validate_artifacts(artifacts)
    return artifacts


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument("--output", type=Path)
    actions.add_argument("--verify", type=Path)
    args = parser.parse_args(argv)
    if os.name != "posix" or not hasattr(os, "O_DIRECTORY") or not hasattr(os, "O_NOFOLLOW"):
        print("estate draft unavailable: required POSIX filesystem capability missing")
        return 1
    try:
        configs = read_configs()
        if args.verify is not None:
            artifacts = read_bundle(args.verify)
            verify_estate(configs, artifacts)
            print("estate draft bytes verified; no remote availability or publication claimed")
            return 0
        artifacts = prepare_estate(configs)
        _validate_artifacts(artifacts)
        verify_estate(configs, artifacts)
        _write_bundle(args.output, artifacts)
        verify_estate(configs, read_bundle(args.output))
        print("fresh local estate draft written; no source payload or remote operation")
        return 0
    except (EstateCliError, EstateError, OSError, ValueError, TypeError, NotImplementedError):
        print("estate draft operation failed; any existing or partial bundle was preserved")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
