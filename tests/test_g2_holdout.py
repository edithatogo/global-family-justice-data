from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from gfjd.g2_holdout import (
    G2HoldoutError,
    _canonical_public_url,
    select_g2_holdout,
    verify_g2_holdout_selection,
)

STRATA = [
    "english_text_native",
    "non_english_text_native",
    "embedded_raster_or_dashboard_pdf",
    "structurally_complex_mixed_layout_pdf",
]


@pytest.fixture(autouse=True)
def _unit_test_binding(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("gfjd.g2_holdout._verify_frozen_bindings", lambda *args: None)


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
    decision = root / "docs/governance/g2-blind-holdout-design-owner-decision-2026-08-15.md"
    decision.parent.mkdir(parents=True)
    decision.write_text("unit-test owner decision\n")
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
        "supported_strata": [stratum],
        "stratum_support": "supported_by_public_metadata",
        "stratum_basis": "Official landing-page metadata explicitly identifies the format.",
        "exact_edition_identity_established": True,
        "metadata_evidence_urls": [f"https://example.gov/edition/{index}"],
        "terms_url": "https://example.gov/terms",
        "rights_url": "https://example.gov/rights",
        "privacy_url": "https://example.gov/privacy",
        "security_url": "https://example.gov/security",
        "terms_screen": "no_known_metadata_blocker",
        "rights_screen": "no_known_metadata_blocker",
        "rights_screen_rationale": "Public metadata provides a preliminary rights screen only.",
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
    evidence = root / "test-metadata"
    evidence.write_text("metadata-only test evidence\n")
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
        "evidence_artifacts": [
            {
                "path": "test-metadata",
                "sha256": hashlib.sha256(evidence.read_bytes()).hexdigest(),
            }
        ],
        "limitations": ["Synthetic unit-test ledger."],
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
    ledger_payload["entries"] = [
        {
            "edition_id": "ED-000",
            "source_series_id": None,
            "urls": [],
            "exposure_class": "content_inspected",
            "reason": "Previously inspected test edition.",
            "evidence_paths": ["test-metadata"],
        }
    ]
    ledger_payload["denied_edition_ids"] = ["ED-000"]
    ledger_payload["limitations"] = ["Synthetic unit-test ledger."]
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


def test_ledger_entries_cannot_be_omitted_from_summary(project_root: Path, tmp_path: Path) -> None:
    root = _root(project_root, tmp_path)
    universe, ledger = _write_inputs(
        root, [_candidate(index, STRATA[index % 4]) for index in range(40)]
    )
    value = json.loads(ledger.read_text())
    value["entries"] = [
        {
            "edition_id": "ED-000",
            "source_series_id": None,
            "urls": [],
            "exposure_class": "content_inspected",
            "reason": "Previously inspected test edition.",
            "evidence_paths": ["test-metadata"],
        }
    ]
    ledger.write_text(json.dumps(value))
    with pytest.raises(G2HoldoutError, match="summary does not match"):
        select_g2_holdout(
            root,
            candidate_universe_path=universe,
            exposure_ledger_path=ledger,
            output_dir=Path("out"),
            seed="prospective-test-seed-01",
            generated_at="2026-08-15T00:00:00Z",
        )


def test_duplicate_editions_and_reserve_series_cannot_fill_scope(
    project_root: Path, tmp_path: Path
) -> None:
    root = _root(project_root, tmp_path)
    duplicates = [_candidate(index, STRATA[index % 4], edition_id="ED-SAME") for index in range(40)]
    universe, ledger = _write_inputs(root, duplicates)
    with pytest.raises(G2HoldoutError, match="duplicate edition_id"):
        select_g2_holdout(
            root,
            candidate_universe_path=universe,
            exposure_ledger_path=ledger,
            output_dir=Path("duplicate-editions"),
            seed="prospective-test-seed-01",
            generated_at="2026-08-15T00:00:00Z",
        )

    repeated_reserve_series = [
        _candidate(
            index,
            STRATA[index % 4],
            source_series_id=f"SERIES-{index:03d}" if index < 24 else "SERIES-RESERVE-SAME",
        )
        for index in range(40)
    ]
    universe, ledger = _write_inputs(root, repeated_reserve_series)
    with pytest.raises(G2HoldoutError, match="frozen 24\\+6 scope"):
        select_g2_holdout(
            root,
            candidate_universe_path=universe,
            exposure_ledger_path=ledger,
            output_dir=Path("duplicate-reserve-series"),
            seed="prospective-test-seed-01",
            generated_at="2026-08-15T00:00:00Z",
        )


def test_manifest_schema_rejects_empty_complete_state(project_root: Path) -> None:
    schema = json.loads(
        (project_root / "schemas/g2_holdout_candidate_manifest.schema.json").read_text()
    )
    invalid = {
        "schema_version": "1.0",
        "manifest_id": "G2HOLDOUT-MANIFEST-PROSPECTIVE-20260815-01",
        "design_id": "G2HOLDOUT-PROSPECTIVE-20260815-01",
        "design_commit": "42b89486b7d71a60ed01eb7e7b1d862e6a736820",
        "selection_seed": "prospective-test-seed-01",
        "selection_algorithm": "sha256_seed_nul_candidate_id_ascending_backtracking_v2",
        "metadata_only": True,
        "source_content_accessed": False,
        "scope_complete": True,
        "primary": [],
        "reserves": [],
        "reserve_allocation": {},
        "generated_at": "2026-08-15T00:00:00Z",
        "limitations": [],
    }
    assert list(Draft202012Validator(schema).iter_errors(invalid))


def test_url_alias_exposure_and_manifest_mutation_fail_closed(
    project_root: Path, tmp_path: Path
) -> None:
    root = _root(project_root, tmp_path)
    candidates = [_candidate(index, STRATA[index % 4]) for index in range(40)]
    universe, ledger = _write_inputs(root, candidates)
    value = json.loads(ledger.read_text())
    exposed = [f"HTTPS://EXAMPLE.GOV:443/edition/{index}.pdf" for index in range(40)]
    value["entries"] = [
        {
            "edition_id": None,
            "source_series_id": None,
            "urls": [url],
            "exposure_class": "content_inspected",
            "reason": "Upper-case URL alias was previously inspected.",
            "evidence_paths": ["test-metadata"],
        }
        for url in exposed
    ]
    value["denied_urls"] = exposed
    ledger.write_text(json.dumps(value))
    with pytest.raises(G2HoldoutError, match="frozen 24\\+6 scope"):
        select_g2_holdout(
            root,
            candidate_universe_path=universe,
            exposure_ledger_path=ledger,
            output_dir=Path("url-alias"),
            seed="prospective-test-seed-01",
            generated_at="2026-08-15T00:00:00Z",
        )

    universe, ledger = _write_inputs(root, candidates)
    result = select_g2_holdout(
        root,
        candidate_universe_path=universe,
        exposure_ledger_path=ledger,
        output_dir=Path("mutation"),
        seed="prospective-test-seed-01",
        generated_at="2026-08-15T00:00:00Z",
    )
    original_receipt = json.loads(result.receipt_path.read_text())
    timestamp_receipt = dict(original_receipt)
    timestamp_receipt["generated_at"] = "2099-01-01T00:00:00Z"
    result.receipt_path.write_text(json.dumps(timestamp_receipt, indent=2, sort_keys=True) + "\n")
    timestamp_errors = verify_g2_holdout_selection(root, Path("mutation"))
    assert timestamp_errors and "receipt claims" in timestamp_errors[0]
    result.receipt_path.write_text(json.dumps(original_receipt, indent=2, sort_keys=True) + "\n")
    manifest = json.loads(result.manifest_path.read_text())
    manifest["primary"][0]["edition_id"] = "ED-TAMPERED"
    result.manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    receipt_path = result.receipt_path
    receipt = json.loads(receipt_path.read_text())
    receipt["candidate_manifest"]["sha256"] = hashlib.sha256(
        result.manifest_path.read_bytes()
    ).hexdigest()
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    errors = verify_g2_holdout_selection(root, Path("mutation"))
    assert errors and "does not reproduce" in errors[0]

    with pytest.raises(G2HoldoutError, match="not public"):
        _canonical_public_url("https://localhost./candidate")
    assert _canonical_public_url("https://[2606:4700:4700::1111]/x") == (
        "https://[2606:4700:4700::1111]/x"
    )
