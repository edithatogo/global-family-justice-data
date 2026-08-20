from __future__ import annotations

import json
from pathlib import Path

import pytest

import gfjd.g2_candidate_intake as candidate_intake
from gfjd.g2_candidate_intake import SCHEMA, validate_candidate_intake

ROOT = Path(__file__).resolve().parents[1]


def _write_intake(path: Path, candidates: list[dict[str, str]]) -> None:
    path.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "intake_id": "G2-CANDIDATE-INTAKE-TEST-01",
                "metadata_only": True,
                "network_access_performed": False,
                "source_content_accessed": False,
                "candidates": candidates,
            }
        )
        + "\n",
        encoding="utf-8",
    )


def _write_schema(root: Path) -> None:
    destination = root / SCHEMA
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes((ROOT / SCHEMA).read_bytes())
    ledger = root / candidate_intake.EXPOSURE_LEDGER
    ledger.parent.mkdir(parents=True, exist_ok=True)
    ledger.write_bytes((ROOT / candidate_intake.EXPOSURE_LEDGER).read_bytes())


def _candidate(candidate_id: str, url: str) -> dict[str, str]:
    return {
        "candidate_id": candidate_id,
        "jurisdiction_id": "TST",
        "publisher": "Test Court",
        "title": "Aggregate family justice report",
        "source_series_id": f"SERIES-{candidate_id}",
        "edition_label": "2026",
        "proposed_url": url,
        "official_status_claim": "official",
        "source_format_claim": "PDF",
        "language": "English",
    }


def test_candidate_intake_accepts_only_non_exposed_metadata(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    intake = tmp_path / "intake.json"
    _write_schema(tmp_path)
    _write_intake(intake, [_candidate("CAND-01", "https://example.test/report.pdf")])
    monkeypatch.setattr(
        candidate_intake,
        "_complete_exposure_urls",
        lambda _root: ({"https://known.example/report.pdf"}, []),
    )

    result = validate_candidate_intake(tmp_path, intake)

    assert result["status"] == "prepared_metadata_only"
    assert result["candidate_count"] == 1
    assert result["eligible_for_future_screen_count"] == 1
    assert result["external_activity_authorized"] is False
    assert result["candidates"][0]["proposed_url"] == "https://example.test/report.pdf"


def test_candidate_intake_stops_on_any_exposure_overlap(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    intake = tmp_path / "intake.json"
    _write_schema(tmp_path)
    _write_intake(
        intake,
        [
            _candidate("CAND-01", "https://example.test/report.pdf"),
            _candidate("CAND-02", "https://known.example/report.pdf"),
        ],
    )
    monkeypatch.setattr(
        candidate_intake,
        "_complete_exposure_urls",
        lambda _root: ({"https://known.example/report.pdf"}, []),
    )

    result = validate_candidate_intake(tmp_path, intake)

    assert result["status"] == "stopped_exposure_overlap"
    assert result["eligible_for_future_screen_count"] == 0
    assert result["rejections"] == [
        {
            "candidate_id": "CAND-02",
            "reason_code": "CUMULATIVE_EXPOSURE_OVERLAP",
        }
    ]


def test_candidate_intake_rejects_external_activity_claims(tmp_path: Path) -> None:
    intake = tmp_path / "intake.json"
    _write_schema(tmp_path)
    _write_intake(intake, [_candidate("CAND-01", "https://example.test/report.pdf")])
    payload = json.loads(intake.read_text())
    payload["network_access_performed"] = True
    intake.write_text(json.dumps(payload) + "\n")

    with pytest.raises(ValueError, match="does not validate"):
        validate_candidate_intake(tmp_path, intake)


def test_candidate_intake_rejects_duplicate_canonical_urls(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    intake = tmp_path / "intake.json"
    _write_schema(tmp_path)
    _write_intake(
        intake,
        [
            _candidate("CAND-01", "https://example.test/report.pdf"),
            _candidate("CAND-02", "https://example.test/report.pdf#fragment"),
        ],
    )
    monkeypatch.setattr(candidate_intake, "_complete_exposure_urls", lambda _root: (set(), []))

    with pytest.raises(ValueError, match="duplicate canonical proposed URL"):
        validate_candidate_intake(tmp_path, intake)


def test_candidate_intake_rejects_symlinked_input(tmp_path: Path) -> None:
    _write_schema(tmp_path)
    target = tmp_path / "target.json"
    _write_intake(target, [_candidate("CAND-01", "https://example.test/report.pdf")])
    linked = tmp_path / "linked.json"
    linked.symlink_to(target)

    with pytest.raises(ValueError, match="regular file"):
        validate_candidate_intake(tmp_path, linked)
