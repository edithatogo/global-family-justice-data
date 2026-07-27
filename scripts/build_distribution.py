#!/usr/bin/env python3
"""Build GFJD distributions from an isolated source copy.

This avoids leaking prior build products into a package and avoids depending on
``python -m build`` at runtime.  The project still declares the standard PEP 517
backend; this wrapper invokes that backend in a temporary clean room.
"""

from __future__ import annotations

import argparse
import gzip
import io
import json
import os
import shutil
import tarfile
import tempfile
from pathlib import Path

EXCLUDED_NAMES = {
    ".git",
    ".venv",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "build",
    "dist",
    "__pycache__",
}


def _ignore(directory: str, names: list[str]) -> set[str]:
    del directory
    ignored = {name for name in names if name in EXCLUDED_NAMES}
    ignored.update(name for name in names if name.endswith(".egg-info"))
    ignored.update(name for name in names if name.endswith((".pyc", ".pyo")))
    return ignored


def _normalise_sdist(path: Path, epoch: int) -> None:
    """Rewrite a generated tar.gz with deterministic metadata and ordering."""

    entries: list[tuple[tarfile.TarInfo, bytes | None]] = []
    with tarfile.open(path, mode="r:gz") as source:
        for member in sorted(source.getmembers(), key=lambda item: item.name):
            payload: bytes | None = None
            if member.isfile():
                extracted = source.extractfile(member)
                if extracted is None:
                    raise RuntimeError(f"Could not read sdist member: {member.name}")
                payload = extracted.read()
            entries.append((member, payload))

    temporary = path.with_suffix(path.suffix + ".normalised")
    with (
        temporary.open("wb") as raw,
        gzip.GzipFile(
            filename="", mode="wb", fileobj=raw, mtime=epoch, compresslevel=9
        ) as compressed,
        tarfile.open(fileobj=compressed, mode="w", format=tarfile.PAX_FORMAT) as target,
    ):
        for original, payload in entries:
            info = tarfile.TarInfo(original.name)
            info.type = original.type
            info.mode = original.mode
            info.uid = 0
            info.gid = 0
            info.uname = ""
            info.gname = ""
            info.mtime = epoch
            info.linkname = original.linkname
            info.pax_headers = {}
            if payload is not None:
                info.size = len(payload)
                target.addfile(info, io.BytesIO(payload))
            else:
                info.size = 0
                target.addfile(info)
    os.replace(temporary, path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wheel", action="store_true", help="Build a wheel")
    parser.add_argument("--sdist", action="store_true", help="Build a source distribution")
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()
    build_wheel = args.wheel or not args.sdist
    build_sdist = args.sdist or not args.wheel

    root = Path(__file__).resolve().parents[1]
    outdir = args.outdir.expanduser()
    if not outdir.is_absolute():
        outdir = (root / outdir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="gfjd-dist-build-") as temporary:
        source = Path(temporary) / "source"
        shutil.copytree(root, source, ignore=_ignore, symlinks=False)
        previous = Path.cwd()
        try:
            os.chdir(source)
            from setuptools import build_meta

            built: list[str] = []
            if build_wheel:
                built.append(build_meta.build_wheel(str(outdir)))
            if build_sdist:
                sdist_name = build_meta.build_sdist(str(outdir))
                epoch = int(os.environ.get("SOURCE_DATE_EPOCH", "0") or "0")
                if epoch <= 0:
                    raise RuntimeError("SOURCE_DATE_EPOCH must be set for deterministic sdists")
                _normalise_sdist(outdir / sdist_name, epoch)
                built.append(sdist_name)
        finally:
            os.chdir(previous)

    payload = {
        "schema_version": "1.0",
        "source_root": str(root),
        "output_directory": str(outdir),
        "artifacts": sorted(built),
        "source_date_epoch": os.environ.get("SOURCE_DATE_EPOCH", ""),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
