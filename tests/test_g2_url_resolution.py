from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

PLAN_ID = "G2HOLDOUT-STRUCTURAL-PREFLIGHT-20260815-01"
RELATIVE_ROOT = Path("data/methods/g2") / PLAN_ID / "url-resolution"


def _read(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _validate(project_root: Path, schema_name: str, value: dict[str, Any]) -> None:
    schema = _read(project_root / RELATIVE_ROOT / "schemas" / schema_name)
    errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(value))
    assert errors == []


def test_url_resolution_outputs_are_schema_valid_and_fail_closed(project_root: Path) -> None:
    output = project_root / RELATIVE_ROOT
    receipt = _read(output / "corrected-resolution-receipt.json")
    network = _read(output / "network-access-receipt.json")
    exposure = _read(output / "exposure-ledger.json")
    proposal = _read(output / "refreshed-pdf-locator-proposal.json")
    for schema, value in (
        ("g2_url_resolution_receipt.schema.json", receipt),
        ("g2_url_resolution_network_access_receipt.schema.json", network),
        ("g2_url_resolution_exposure_ledger.schema.json", exposure),
        ("g2_refreshed_pdf_locator_proposal.schema.json", proposal),
    ):
        _validate(project_root, schema, value)

    assert receipt["status"] == "failed_scope_corrected_metadata_only"
    assert receipt["counts"] == {
        "entries": 33,
        "rejected_urls": 203,
        "source_requests": 0,
        "strong_hypotheses": 15,
        "unresolved": 18,
    }
    assert all(row["source_file_requested"] is False for row in receipt["entries"])
    assert network["method_allowlist"] == ["GET"]
    assert network["counts"]["forbidden_requests"] == 0
    assert all(row["method"] == "GET" for row in network["access_events"])
    assert all(row["forbidden_access"] is False for row in network["access_events"])
    assert exposure["source_content_accessed"] is False
    assert exposure["resolver_role_contaminated_for_extraction"] is True
    assert proposal["status"] == "insufficient_scope_not_authorized"
    assert proposal["counts"]["locator_candidates"] == 26
    assert proposal["counts"]["unique_locator_urls"] == 26
    assert proposal["required_scope"] == 30
    assert all(row["source_request_authorized"] is False for row in proposal["entries"])
    assert all(row["source_request_performed"] is False for row in proposal["entries"])


def test_url_resolution_bindings_and_order_recompute(project_root: Path) -> None:
    output = project_root / RELATIVE_ROOT
    receipt = _read(output / "corrected-resolution-receipt.json")
    network = _read(output / "network-access-receipt.json")
    exposure = _read(output / "exposure-ledger.json")
    proposal = _read(output / "refreshed-pdf-locator-proposal.json")
    manifest = _read(
        project_root / "data/methods/g2" / PLAN_ID / "design/proposed-url-resolution-manifest.json"
    )
    frame = _read(
        project_root / "data/methods/g2" / PLAN_ID / "design/oversampled-metadata-frame.json"
    )
    expected_identities = [
        (row["frame_rank"], row["candidate_id"], row["edition_id"], row["landing_page_url"])
        for row in manifest["entries"]
    ]
    observed_identities = [
        (row["frame_rank"], row["candidate_id"], row["edition_id"], row["landing_page_url"])
        for row in receipt["entries"]
    ]
    assert observed_identities == expected_identities
    expected_urls = sorted({row["landing_page_url"] for row in manifest["entries"]})
    assert network["network_url_allowlist"] == expected_urls
    assert [row["requested_url"] for row in network["access_events"]] == [
        row["landing_page_url"] for row in manifest["entries"]
    ]
    assert [row["frame_rank"] for row in proposal["entries"]] == [
        row["frame_rank"] for row in frame["candidates"]
    ]
    assert [row["frame_rank"] for row in exposure["entries"]] == [
        row["frame_rank"] for row in manifest["entries"]
    ]

    for descriptor in (
        receipt["raw_resolution"],
        receipt["identity_review"],
        receipt["access_review"],
        receipt["owner_authorization"],
        receipt["manifest"],
        network["raw_access_draft"],
        network["owner_authorization"],
        network["manifest"],
        network["role_bundle"],
        exposure["predecessor"],
        exposure["resolution_receipt"],
        proposal["frame"],
        proposal["resolution_receipt"],
    ):
        path = project_root / descriptor["path"]
        assert _sha(path) == descriptor["sha256"]


def test_url_resolution_corrections_are_panel_bound(project_root: Path) -> None:
    output = project_root / RELATIVE_ROOT
    receipt = _read(output / "corrected-resolution-receipt.json")
    corrections = _read(project_root / "config/g2_url_resolution_corrections.json")
    expected = {int(rank): url for rank, url in corrections["strong_hypotheses"].items()}
    observed = {
        int(row["frame_rank"]): row["corrected_pdf_url"]
        for row in receipt["entries"]
        if row["corrected_pdf_url"] is not None
    }
    assert observed == expected
    raw_path = output / "raw-resolution-draft.json"
    identity_path = output / "panels/identity-review.json"
    assert _sha(raw_path) == corrections["raw_resolution_sha256"]
    assert _sha(identity_path) == corrections["identity_panel_sha256"]
    assert corrections["source_request_authorized"] is False


def test_url_resolution_detached_manifest_is_exact(project_root: Path) -> None:
    output = project_root / RELATIVE_ROOT
    manifest_path = output / "URL_RESOLUTION_MANIFEST.sha256"
    lines = manifest_path.read_text(encoding="utf-8").splitlines()
    entries = [line.split("  ", 1) for line in lines]
    observed_paths = [path for _, path in entries]
    expected_paths = sorted(
        [
            "config/g2_url_resolution_corrections.json",
            "docs/governance/g2-structural-preflight-url-resolution-owner-decision-2026-08-15.md",
            f"{RELATIVE_ROOT.as_posix()}/schemas/g2_refreshed_pdf_locator_proposal.schema.json",
            f"{RELATIVE_ROOT.as_posix()}/schemas/g2_url_resolution_exposure_ledger.schema.json",
            f"{RELATIVE_ROOT.as_posix()}/schemas/g2_url_resolution_network_access_receipt.schema.json",
            f"{RELATIVE_ROOT.as_posix()}/schemas/g2_url_resolution_receipt.schema.json",
            "scripts/assemble_g2_url_resolution.py",
            "tests/test_g2_url_resolution.py",
            f"{RELATIVE_ROOT.as_posix()}/corrected-resolution-receipt.json",
            f"{RELATIVE_ROOT.as_posix()}/exposure-ledger.json",
            f"{RELATIVE_ROOT.as_posix()}/network-access-receipt.json",
            f"{RELATIVE_ROOT.as_posix()}/panels/access-review.json",
            f"{RELATIVE_ROOT.as_posix()}/panels/identity-review.json",
            f"{RELATIVE_ROOT.as_posix()}/raw-access-events-draft.json",
            f"{RELATIVE_ROOT.as_posix()}/raw-resolution-draft.json",
            f"{RELATIVE_ROOT.as_posix()}/refreshed-pdf-locator-proposal.json",
        ]
    )
    assert observed_paths == expected_paths
    for expected_sha, relative_path in entries:
        assert _sha(project_root / relative_path) == expected_sha


def test_url_resolution_panels_are_clean_clone_self_contained(project_root: Path) -> None:
    panel_root = project_root / RELATIVE_ROOT / "panels"
    for panel_path in panel_root.glob("*.json"):
        panel_text = panel_path.read_text(encoding="utf-8")
        assert "build/g2-structural-preflight-url-resolution" not in panel_text
        panel = _read(panel_path)
        for artifact in panel["evidence_inputs"]:
            path = project_root / artifact["path"]
            assert path.is_file()
            assert _sha(path) == artifact["sha256"]
