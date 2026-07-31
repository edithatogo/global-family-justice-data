"""Create and verify a deterministic SHA-256 repository manifest."""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "MANIFEST.sha256"
EXCLUDED_PARTS = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".tox",
    "htmlcov",
    "dist",
    "build",
}
EXCLUDED_FILES = {"MANIFEST.sha256", ".DS_Store", ".coverage", "coverage.xml"}
EXCLUDED_PREFIXES = {("data", "raw", "files")}


def _is_excluded_part(part: str) -> bool:
    return part in EXCLUDED_PARTS or part.endswith(".egg-info")


def iter_manifest_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT)
        if any(_is_excluded_part(part) for part in relative.parts):
            continue
        if any(relative.parts[: len(prefix)] == prefix for prefix in EXCLUDED_PREFIXES):
            continue
        if relative.name in EXCLUDED_FILES or relative.suffix == ".zip":
            continue
        files.append(relative)
    return sorted(files, key=lambda item: item.as_posix())


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def compute_entries() -> list[tuple[str, str]]:
    return [(sha256(ROOT / relative), relative.as_posix()) for relative in iter_manifest_files()]


def write_manifest() -> None:
    lines = [f"{digest}  {relative}\n" for digest, relative in compute_entries()]
    MANIFEST.write_text("".join(lines), encoding="utf-8")


def read_manifest() -> list[tuple[str, str]]:
    if not MANIFEST.exists():
        return []
    entries: list[tuple[str, str]] = []
    for line_number, line in enumerate(MANIFEST.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            digest, relative = line.split("  ", 1)
        except ValueError as exc:
            raise ValueError(f"Malformed manifest line {line_number}") from exc
        entries.append((digest, relative))
    return entries


def verify_manifest() -> list[str]:
    errors: list[str] = []
    try:
        expected = read_manifest()
    except ValueError as exc:
        return [str(exc)]
    if not expected:
        return ["MANIFEST.sha256 is missing or empty"]

    actual = compute_entries()
    expected_map = {relative: digest for digest, relative in expected}
    actual_map = {relative: digest for digest, relative in actual}

    for relative in sorted(set(expected_map) - set(actual_map)):
        errors.append(f"Manifest lists missing file: {relative}")
    for relative in sorted(set(actual_map) - set(expected_map)):
        errors.append(f"Manifest omits file: {relative}")
    for relative in sorted(set(expected_map) & set(actual_map)):
        if expected_map[relative] != actual_map[relative]:
            errors.append(f"Checksum mismatch: {relative}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--write", action="store_true", help="write MANIFEST.sha256")
    action.add_argument("--verify", action="store_true", help="verify MANIFEST.sha256")
    args = parser.parse_args(argv)

    if args.write:
        write_manifest()
        print(f"Wrote {MANIFEST.relative_to(ROOT)} with {len(compute_entries())} entries.")
        return 0

    errors = verify_manifest()
    if errors:
        print("Manifest verification failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Manifest verified for {len(read_manifest())} files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
