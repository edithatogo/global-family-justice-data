from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from gfjd.g2_holdout import G2HoldoutError, select_g2_holdout

STRATA = [
    "english_text_native",
    "non_english_text_native",
    "embedded_raster_or_dashboard_pdf",
    "structurally_complex_mixed_layout_pdf",
]


def _root(project_root: Path, tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    (root / "schemas").mkdir(parents=True)
    for name in (
        "g2_blind_holdout_plan.schema.json",
        "g2_holdout_candidate_universe.schema.json",
        "g2_holdout_exposure_ledger.schema.json",
        "g2_holdout_candidate_manifest.schema.json",
        "g2_holdout_selection_receipt.schema.json",
    ):
        shutil.copyfile(project_root / "schemas" / name, root / "schemas" / name)
    (root / "config").mkdir()
    plan = json.loads((project_root / "config/g2_blind_holdout_plan.json").read_text())
    (root / "config/g2_blind_holdout_plan.json").write_text(json.dumps(plan))
    return root


def _candidate(index: int, stratum: str, **changes: object) -> dict[str, object]:
    item: dict[str, object] = {
        "candidate_id": f"G2CAND-{index:03d}",
        "edition_id": f"ED-{index:03d}",
        "edition_title": f"Official edition {index}",
        "jurisdiction_id": f"J{index // 2:02d}",
        "source_series_id": f"SERIES-{index:03d}",
        "publisher": "Official court",
        "official_publisher": True,
        "landing_page_url": f"https://example.gov/edition/{index}",
        "source_url": f"https://example.gov/edition/{index}.pdf",
        "edition_date_or_period": "2025",
        "languages": ["en"],
        "format": "pdf",
        "proposed_stratum": stratum,
        "stratum_support": "supported_by_public_metadata",
        "stratum_basis": "Official landing-page metadata explicitly identifies the format.",
        "exact_edition_identity_established": True,
        "metadata_evidence_urls": [f"https://example.gov/edition/{index}"],
        "terms_url": "https://example.gov/terms",
        "privacy_url": "https://example.gov/privacy",
        "security_url": "https://example.gov/security",
        "terms_screen": "no_known_metadata_blocker",
        "privacy_screen": "no_known_metadata_blocker",
        "security_screen": "no_known_metadata_blocker",
        "prohibited_data_screen": "no_known_metadata_blocker",
        "eligibility": "eligible_metadata_only",
        "checked_at": "2026-08-15T00:00:00Z",
        "source_content_accessed": False,
        "notes": None,
    }
    item.update(changes)
    return item


def _write_inputs(root: Path, candidates: list[dict[str, object]]) -> tuple[Path, Path]:
    universe = {
        "schema_version": "1.0",
        "universe_id": "G2HOLDOUT-UNIVERSE-TEST01",
        "design_id": "G2HOLDOUT-PROSPECTIVE-20260815-01",
        "as_of": "2026-08-15T00:00:00Z",
        "metadata_only": True,
        "source_content_accessed": False,
        "candidates": candidates,
        "limitations": [],
    }
    ledger = {
        "schema_version": "1.0",
        "ledger_id": "G2HOLDOUT-EXPOSURE-TEST01",
        "design_id": "G2HOLDOUT-PROSPECTIVE-20260815-01",
        "as_of": "2026-08-15T00:00:00Z",
        "metadata_only": True,
        "source_content_accessed_during_registration": False,
        "entries": [],
        "denied_edition_ids": [],
        "denied_source_series_ids": [],
        "denied_urls": [],
        "evidence_artifacts": [],
        "limitations": [],
    }
    universe_path = root / "universe.json"
    ledger_path = root / "ledger.json"
    universe_path.write_text(json.dumps(universe))
    ledger_path.write_text(json.dumps(ledger))
    return universe_path, ledger_path


def test_selects_exact_frozen_scope_deterministically(project_root: Path, tmp_path: Path) -> None:
    root = _root(project_root, tmp_path)
    candidates = [_candidate(index, STRATA[index % 4]) for index in range(40)]
    universe, ledger = _write_inputs(root, candidates)
    first = select_g2_holdout(
        root,
        candidate_universe_path=universe,
        exposure_ledger_path=ledger,
        output_dir=Path("out-one"),
        seed="prospective-test-seed-01",
        generated_at="2026-08-15T00:00:00Z",
    )
    second = select_g2_holdout(
        root,
        candidate_universe_path=universe,
        exposure_ledger_path=ledger,
        output_dir=Path("out-two"),
        seed="prospective-test-seed-01",
        generated_at="2026-08-15T00:00:00Z",
    )
    one = json.loads(first.manifest_path.read_text())
    two = json.loads(second.manifest_path.read_text())
    assert len(one["primary"]) == 24
    assert len(one["reserves"]) == 6
    assert one == two
    assert len({item["jurisdiction_id"] for item in one["primary"]}) >= 12
    assert (
        max(
            sum(
                item["jurisdiction_id"] == jurisdiction for item in one["primary"] + one["reserves"]
            )
            for jurisdiction in {
                item["jurisdiction_id"] for item in one["primary"] + one["reserves"]
            }
        )
        <= 2
    )


def test_exposure_or_uncertainty_is_fail_closed(project_root: Path, tmp_path: Path) -> None:
    root = _root(project_root, tmp_path)
    candidates = [_candidate(index, STRATA[index % 4]) for index in range(30)]
    candidates[1]["terms_screen"] = "uncertain"
    universe, ledger = _write_inputs(root, candidates)
    ledger_payload = json.loads(ledger.read_text())
    ledger_payload["denied_edition_ids"] = ["ED-000"]
    ledger.write_text(json.dumps(ledger_payload))
    with pytest.raises(G2HoldoutError, match="frozen .* scope"):
        select_g2_holdout(
            root,
            candidate_universe_path=universe,
            exposure_ledger_path=ledger,
            output_dir=Path("out"),
            seed="prospective-test-seed-01",
            generated_at="2026-08-15T00:00:00Z",
        )


def test_rejects_weak_seed_and_repository_escape(project_root: Path, tmp_path: Path) -> None:
    root = _root(project_root, tmp_path)
    candidates = [_candidate(index, STRATA[index % 4]) for index in range(40)]
    universe, ledger = _write_inputs(root, candidates)
    with pytest.raises(G2HoldoutError, match="at least 16"):
        select_g2_holdout(
            root,
            candidate_universe_path=universe,
            exposure_ledger_path=ledger,
            output_dir=Path("out"),
            seed="short",
            generated_at="2026-08-15T00:00:00Z",
        )
    with pytest.raises(G2HoldoutError, match="escapes repository"):
        select_g2_holdout(
            root,
            candidate_universe_path=universe,
            exposure_ledger_path=ledger,
            output_dir=Path("../escape"),
            seed="prospective-test-seed-01",
            generated_at="2026-08-15T00:00:00Z",
        )
