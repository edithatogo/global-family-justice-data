from __future__ import annotations

from pathlib import Path

import pytest

from gfjd.g2_run_preflight import G2RunPreflightError, validate_g2_run_identifiers


def test_preflight_accepts_schema_compatible_run_identifiers(project_root: Path) -> None:
    validate_g2_run_identifiers(
        project_root,
        packet_id="G2PKT-MATERIAL-DISTINCT-20260826-01",
        comparison_id="G2CMP-MATERIAL-DISTINCT-20260826-01",
    )


def test_preflight_rejects_invalid_packet_before_any_run_artifact_is_needed(
    project_root: Path,
) -> None:
    with pytest.raises(G2RunPreflightError, match="invalid packet_id"):
        validate_g2_run_identifiers(
            project_root,
            packet_id="G2BLIND-INVALID",
            comparison_id="G2CMP-MATERIAL-DISTINCT-20260826-01",
        )
