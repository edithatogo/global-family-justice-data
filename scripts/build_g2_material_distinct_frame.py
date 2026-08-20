"""Build the approved no-network G2 materially distinct candidate-frame result."""

from __future__ import annotations

from pathlib import Path

from gfjd.g2_material_distinct import write_material_distinct_artifacts


def main() -> int:
    write_material_distinct_artifacts(Path(__file__).resolve().parents[1])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
