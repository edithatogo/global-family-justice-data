from __future__ import annotations

import json
from pathlib import Path

import pytest

from gfjd.g2_quarantine_pipeline import (
    G2QuarantinePipelineError,
    build_g2_quarantine_pipeline,
    verify_g2_quarantine_pipeline,
)


def _packet(tmp_path: Path) -> Path:
    path = tmp_path / "packet.json"
    path.write_text(
        json.dumps({"sources": [{"source_record_key": "a"}, {"source_record_key": "b"}]})
    )
    return path


def _rows(tmp_path: Path, *, quarantine: str = "quarantine") -> Path:
    path = tmp_path / "rows.json"
    row = {
        "source_record_key": "a",
        "candidate_id": "candidate-a",
        "source_id": "source-a",
        "source_edition_id": "edition-a",
        "source_sha256": "a" * 64,
        "source_format": "spreadsheet",
        "source_locator": {"kind": "spreadsheet_cell"},
        "value": 1,
        "period_label_source": "2026 Q1",
        "domain_code": "family_justice",
        "matter_type_code": "family_case",
        "indicator_code": "family_case_filing_or_disposition_count",
        "statistic_type": "count",
        "unit_code": "count",
        "period_start": None,
        "period_end": None,
        "time_basis": "source_defined",
        "counted_entity_code": "orders",
        "population_scope_code": "national",
        "quarantine_status": quarantine,
    }
    path.write_text(
        json.dumps([row, row | {"source_record_key": "b", "candidate_id": "candidate-b"}])
    )
    return path


def test_builds_deterministic_quarantine_only_layers(tmp_path: Path) -> None:
    result = build_g2_quarantine_pipeline(
        packet_path=_packet(tmp_path),
        extraction_path=_rows(tmp_path),
        output_dir=tmp_path / "build",
    )
    assert result.rows == 2
    assert verify_g2_quarantine_pipeline(result.receipt_path) == []
    assert json.loads((result.output_dir / "gold.json").read_text()) == []
    assert len(json.loads((result.output_dir / "quarantine.json").read_text())) == 2


def test_rejects_non_quarantine_input(tmp_path: Path) -> None:
    with pytest.raises(G2QuarantinePipelineError, match="remain quarantined"):
        build_g2_quarantine_pipeline(
            packet_path=_packet(tmp_path),
            extraction_path=_rows(tmp_path, quarantine="accepted"),
            output_dir=tmp_path / "build",
        )
