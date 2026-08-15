"""Build the detached exact-artifact manifest for the G2 search successor."""

from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DESIGN = Path("data/methods/g2/G2HOLDOUT-METADATA-EXPANSION-20260816-02/design")
FILES = sorted(
    [
        DESIGN / "successor-plan.json",
        DESIGN / "successor-plan.schema.json",
        DESIGN / "successor-query-manifest.json",
        DESIGN / "successor-query-manifest.schema.json",
        DESIGN / "successor-execution-bundle.schema.json",
        DESIGN / "successor-authority-receipt.schema.json",
        DESIGN / "successor-owner-decision.schema.json",
        Path(
            "data/methods/g2/G2HOLDOUT-METADATA-EXPANSION-20260816-STOP-01/"
            "registrar/execution-stop.json"
        ),
        Path(
            "data/methods/g2/G2HOLDOUT-METADATA-EXPANSION-20260816-STOP-01/"
            "registrar/lineage-index.json"
        ),
        Path(
            "data/methods/g2/G2HOLDOUT-METADATA-EXPANSION-20260816-STOP-01/"
            "registrar/passive-exposure-annex.json"
        ),
        Path(
            "data/methods/g2/G2HOLDOUT-METADATA-EXPANSION-20260816-STOP-01/"
            "registrar/stop-receipt.json"
        ),
        Path(
            "data/methods/g2/G2HOLDOUT-METADATA-EXPANSION-20260816-STOP-01/panels/stop-review.json"
        ),
        Path("docs/methods/g2-metadata-search-successor-design-evidence-2026-08-16.md"),
        Path("docs/governance/g2-metadata-search-successor-owner-decision-packet-2026-08-16.md"),
        Path("scripts/build_g2_metadata_search_successor_manifest.py"),
        Path("scripts/build_g2_metadata_search_successor_design_manifest.py"),
        Path("src/gfjd/g2_metadata_search_successor.py"),
        Path("tests/test_g2_metadata_search_successor.py"),
        Path("tests/test_g2_metadata_search_successor_design.py"),
    ],
    key=lambda path: path.as_posix(),
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> str:
    return "".join(f"{_sha(ROOT / path)}  {path.as_posix()}\n" for path in FILES)


def main() -> int:
    output = ROOT / DESIGN / "SUCCESSOR_DESIGN_MANIFEST.sha256"
    output.write_text(build(), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
