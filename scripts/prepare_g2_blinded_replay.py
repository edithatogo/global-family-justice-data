#!/usr/bin/env python3
"""Prepare two fresh, allowlisted G2 blinded-replay workspaces."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTROLLED = ROOT / "data/raw/files/g2-controlled"
RUN = ROOT / "build/g2-blinded-replay-20260908-01"

SOURCES = {
    "finland-metadata.json": "20621bfd4d339e4f1d724b3e2016da845303938367c92cc1fac5c07e9a74575a",
    "finland-observation.json": "59348fe0b98c016881de8761953983fe402490a6de19094e0acf8fcab3f362f0",
    "estonia-offences.xlsx": "81e350d37f6d402f2570f1a0b71cfe1d3ccf2c9578ed023b8b1f1a49fa02d0ab",
    "estonia-domestic-violence.csv": (
        "f0024a590b3423c8b533f95ed597e6fa6f8672b9bee1450403f09296b7fe45b9"
    ),
    "south-africa-report-2024-25.pdf": (
        "41aee1f16221da483677619fc314060a318a5b2a6d7c4ff615a3af5f6952acee"
    ),
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    if RUN.exists():
        raise SystemExit(f"sealed_workspace_exists:{RUN.relative_to(ROOT)}")
    for name, expected in SOURCES.items():
        source = CONTROLLED / name
        if not source.is_file() or sha(source) != expected:
            raise SystemExit(f"source_digest_mismatch:{name}")
    for role in ("extractor-a", "extractor-b"):
        workspace = RUN / role / "inputs"
        workspace.mkdir(parents=True)
        for name in SOURCES:
            shutil.copyfile(CONTROLLED / name, workspace / name)
        for path in workspace.iterdir():
            if sha(path) != SOURCES[path.name]:
                raise SystemExit(f"workspace_digest_mismatch:{role}:{path.name}")
    manifest = {
        "schema_version": "1.0",
        "run_id": "G2-BLINDED-REPLAY-20260908-01",
        "roles": ["extractor-a", "extractor-b", "comparator", "advisory-review"],
        "network_access": False,
        "expected_values_present": False,
        "prior_outputs_present": False,
        "source_artifacts": SOURCES,
        "workspace_paths": {
            role: f"{RUN.relative_to(ROOT)}/{role}/inputs"
            for role in ("extractor-a", "extractor-b")
        },
        "status": "prepared_not_executed",
        "claim_limit": "bounded reproducibility only; owner adjudication required",
    }
    (RUN / "manifest.json").write_bytes(
        json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
    )
    print(
        json.dumps(
            {
                "status": manifest["status"],
                "manifest": str((RUN / "manifest.json").relative_to(ROOT)),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
