"""Generate the repository SHA-256 manifest used by release validation."""
from __future__ import annotations

import argparse
from hashlib import sha256
from pathlib import Path

from gfjd.validate import ROOT, is_ignored_manifest_path


def manifest_files(root: Path = ROOT) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file() or path.name == "MANIFEST.sha256":
            continue
        relative = path.relative_to(root)
        if is_ignored_manifest_path(relative):
            continue
        files.append(path)
    return sorted(files, key=lambda item: str(item.relative_to(root)))


def render_manifest(root: Path = ROOT) -> str:
    lines = []
    for path in manifest_files(root):
        relative = path.relative_to(root)
        digest = sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {relative}")
    return "\n".join(lines) + "\n"


def write_manifest(root: Path = ROOT) -> Path:
    output = root / "MANIFEST.sha256"
    output.write_text(render_manifest(root), encoding="utf-8")
    return output


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate MANIFEST.sha256 for tracked repository artifacts.")
    parser.add_argument("--check", action="store_true", help="check whether the manifest is current without writing")
    args = parser.parse_args(argv)
    expected = render_manifest(ROOT)
    output = ROOT / "MANIFEST.sha256"
    if args.check:
        if not output.exists() or output.read_text(encoding="utf-8") != expected:
            print("MANIFEST.sha256 is out of date.")
            return 1
        print("MANIFEST.sha256 is current.")
        return 0
    write_manifest(ROOT)
    print(f"Updated {output.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
