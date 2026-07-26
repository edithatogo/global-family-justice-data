#!/usr/bin/env python3
"""Run the GFJD bootstrap CLI from an unpacked source tree without installation."""
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gfjd.cli import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main(["--root", str(ROOT), "bootstrap", *sys.argv[1:]]))
