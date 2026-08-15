"""Assemble and verify the metadata-only G2 URL-resolution evidence bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

PLAN_ID = "G2HOLDOUT-STRUCTURAL-PREFLIGHT-20260815-01"
DEFAULT_OUTPUT = Path("data/methods/g2") / PLAN_ID / "url-resolution"
MANIFEST_NAME = "URL_RESOLUTION_MANIFEST.sha256"


def _read(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def _remap_panel_paths(value: Any, replacements: dict[str, str]) -> Any:
    if isinstance(value, dict):
        return {key: _remap_panel_paths(item, replacements) for key, item in value.items()}
    if isinstance(value, list):
        return [_remap_panel_paths(item, replacements) for item in value]
    if isinstance(value, str):
        return replacements.get(value, value)
    return value


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _artifact(root: Path, path: Path) -> dict[str, str]:
    resolved = path.resolve()
    return {"path": resolved.relative_to(root.resolve()).as_posix(), "sha256": _sha(resolved)}


def _write_manifest(root: Path, output_dir: Path, artifact_paths: list[Path]) -> None:
    relative_paths = sorted(
        {path.resolve().relative_to(root.resolve()).as_posix() for path in artifact_paths}
    )
    lines = [f"{_sha(root / path)}  {path}" for path in relative_paths]
    (output_dir / MANIFEST_NAME).write_text("\n".join(lines) + "\n", encoding="utf-8")


def _validate(root: Path, schema_path: Path, value: dict[str, Any]) -> None:
    schema = _read(root / schema_path)
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(value),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        rendered = "; ".join(f"{list(error.absolute_path)}: {error.message}" for error in errors)
        raise ValueError(f"{schema_path}: {rendered}")


def assemble(root: Path, agent_dir: Path, panel_dir: Path, output_dir: Path) -> None:
    root = root.resolve()
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "panels").mkdir(exist_ok=True)
    schema_root = output_dir.relative_to(root) / "schemas"

    copies = {
        agent_dir / "resolution-draft.json": output_dir / "raw-resolution-draft.json",
        agent_dir / "access-events-draft.json": output_dir / "raw-access-events-draft.json",
        panel_dir / "identity-review.json": output_dir / "panels/identity-review.json",
        panel_dir / "access-review.json": output_dir / "panels/access-review.json",
    }
    for source, destination in copies.items():
        shutil.copyfile(source, destination)

    raw_resolution_path = output_dir / "raw-resolution-draft.json"
    raw_access_path = output_dir / "raw-access-events-draft.json"
    identity_path = output_dir / "panels/identity-review.json"
    access_review_path = output_dir / "panels/access-review.json"
    tracked_raw_resolution = raw_resolution_path.relative_to(root).as_posix()
    tracked_raw_access = raw_access_path.relative_to(root).as_posix()
    path_replacements = {
        "build/g2-structural-preflight-url-resolution/agent/"
        "resolution-draft.json": tracked_raw_resolution,
        "build/g2-structural-preflight-url-resolution/agent/"
        "access-events-draft.json": tracked_raw_access,
    }
    _write(identity_path, _remap_panel_paths(_read(identity_path), path_replacements))
    _write(access_review_path, _remap_panel_paths(_read(access_review_path), path_replacements))
    raw = _read(raw_resolution_path)
    access = _read(raw_access_path)
    corrections = _read(root / "config/g2_url_resolution_corrections.json")
    if _sha(raw_resolution_path) != corrections["raw_resolution_sha256"]:
        raise ValueError("raw resolution digest differs from correction contract")
    if _sha(identity_path) != corrections["identity_panel_sha256"]:
        raise ValueError("identity panel digest differs from correction contract")
    manifest_path = (
        root / "data/methods/g2" / PLAN_ID / "design/proposed-url-resolution-manifest.json"
    )
    manifest = _read(manifest_path)
    manifest_rows = manifest["entries"]
    if len(raw["records"]) != 33 or len(access["access_events"]) != 33:
        raise ValueError("resolution drafts must contain exactly 33 ordered records")

    strong = {int(rank): str(url) for rank, url in corrections["strong_hypotheses"].items()}
    corrected_entries: list[dict[str, Any]] = []
    rejected_count = 0
    for expected, record in zip(manifest_rows, raw["records"], strict=True):
        identity = (record["frame_rank"], record["candidate_id"], record["edition_id"])
        expected_identity = (
            expected["frame_rank"],
            expected["candidate_id"],
            expected["edition_id"],
        )
        if (
            identity != expected_identity
            or record["requested_landing_url"] != expected["landing_page_url"]
        ):
            raise ValueError("raw resolution order or identity differs from frozen manifest")
        discovered = list(
            dict.fromkeys(
                url
                for url in [record["resolved_exact_pdf_url"], *record["alternate_pdf_urls"]]
                if url is not None
            )
        )
        selected = strong.get(int(record["frame_rank"]))
        if selected is not None and selected not in discovered:
            raise ValueError(
                f"strong hypothesis absent from raw metadata: rank {record['frame_rank']}"
            )
        rejected = [url for url in discovered if url != selected]
        rejected_count += len(rejected)
        links = record["metadata_link_urls"]
        corrected_entries.append(
            {
                "frame_rank": record["frame_rank"],
                "candidate_id": record["candidate_id"],
                "edition_id": record["edition_id"],
                "landing_page_url": record["requested_landing_url"],
                "landing_status": record["status"],
                "identity_disposition": "strong_metadata_hypothesis" if selected else "unresolved",
                "corrected_pdf_url": selected,
                "rejected_pdf_urls": rejected,
                "rights_metadata_links": links["rights"],
                "privacy_metadata_links": links["privacy"],
                "security_metadata_links": links["security"],
                "terms_metadata_links": links["terms"],
                "source_file_requested": False,
                "limitations": record["limitations"],
            }
        )
    if len(strong) != 15 or rejected_count != 203:
        raise ValueError("corrected identity counts differ from reviewed panel result")

    owner_path = (
        root / "docs/governance/g2-structural-preflight-url-resolution-owner-decision-2026-08-15.md"
    )
    corrected = {
        "schema_version": "1.0",
        "receipt_id": "G2URL-CORRECTION-20260815-01",
        "plan_id": PLAN_ID,
        "status": "failed_scope_corrected_metadata_only",
        "raw_resolution": _artifact(root, raw_resolution_path),
        "identity_review": _artifact(root, identity_path),
        "access_review": _artifact(root, access_review_path),
        "owner_authorization": _artifact(root, owner_path),
        "manifest": _artifact(root, manifest_path),
        "counts": {
            "entries": 33,
            "strong_hypotheses": 15,
            "unresolved": 18,
            "rejected_urls": 203,
            "source_requests": 0,
        },
        "entries": corrected_entries,
        "limitations": [
            "Every proposed PDF URL remains an unrequested metadata hypothesis, "
            "not an exact-edition verification.",
            "Rights, privacy, security and terms URLs are unvisited landing-page "
            "link locators only.",
            "No source-file request, structural inspection, extraction, rights "
            "acceptance or G2 decision is represented.",
        ],
    }
    corrected_path = output_dir / "corrected-resolution-receipt.json"
    _validate(root, schema_root / "g2_url_resolution_receipt.schema.json", corrected)
    _write(corrected_path, corrected)

    network = {
        "schema_version": "1.0",
        "receipt_id": "G2URL-NETWORK-ACCESS-20260815-01",
        "plan_id": PLAN_ID,
        "status": "completed_with_unresolved_and_self_attested_enforcement",
        "raw_access_draft": _artifact(root, raw_access_path),
        "owner_authorization": _artifact(root, owner_path),
        "manifest": _artifact(root, manifest_path),
        "role_bundle": _artifact(root, root / "config/g2_structural_role_bundles.json"),
        "role": "metadata_url_resolver",
        "session_id": access["session_id"],
        "fresh_session_attested": True,
        "network_mode": "exact_allowlist_only",
        "method_allowlist": ["GET"],
        "network_url_allowlist": access["network_url_allowlist"],
        "counts": {
            "manifest_entries": 33,
            "recorded_get_attempts": 33,
            "unique_allowlisted_urls": 31,
            "html_bodies_inspected": 22,
            "redirects_blocked": 1,
            "request_or_http_errors": 10,
            "forbidden_requests": 0,
        },
        "access_events": access["access_events"],
        "attestation": access["attestation"],
        "limitations": [
            "Recorded GET attempts are resolver-produced events and are not "
            "independent connection telemetry.",
            "Role isolation and no-forbidden-access claims are digest-bound "
            "attestations, not OS-enforced proof.",
            "The original draft did not conform to the generic artifact-access "
            "schema; this receipt preserves its facts under the dedicated "
            "network-access schema.",
        ],
    }
    network_path = output_dir / "network-access-receipt.json"
    _validate(root, schema_root / "g2_url_resolution_network_access_receipt.schema.json", network)
    _write(network_path, network)

    frame_path = root / "data/methods/g2" / PLAN_ID / "design/oversampled-metadata-frame.json"
    frame = _read(frame_path)
    frame_by_rank = {int(row["frame_rank"]): row for row in frame["candidates"]}
    predecessor_path = (
        root / "data/methods/g2/G2HOLDOUT-PROSPECTIVE-20260815-01/intake/exposure-ledger.json"
    )
    resolution_artifact = _artifact(root, corrected_path)
    exposure_entries = []
    for record in raw["records"]:
        source = frame_by_rank[int(record["frame_rank"])]
        exposure_class = {
            "html_metadata_resolved": "landing_page_metadata_seen",
            "html_metadata_inspected_no_exact_candidate_pdf": "landing_page_metadata_seen",
            "redirect_blocked": "landing_page_redirect_blocked",
            "http_error": "landing_page_http_error",
            "request_error": "landing_page_request_error",
        }[record["status"]]
        exposure_entries.append(
            {
                "frame_rank": record["frame_rank"],
                "candidate_id": record["candidate_id"],
                "edition_id": record["edition_id"],
                "source_series_id": source["source_series_id"],
                "landing_page_url": record["requested_landing_url"],
                "exposure_class": exposure_class,
                "resolver_session_id": raw["session_id"],
                "source_content_accessed": False,
                "extractor_eligible_role": False,
                "evidence": _artifact(root, raw_access_path),
            }
        )
    exposure = {
        "schema_version": "1.0",
        "ledger_id": "G2URL-EXPOSURE-20260815-01",
        "plan_id": PLAN_ID,
        "predecessor": _artifact(root, predecessor_path),
        "resolution_receipt": resolution_artifact,
        "metadata_only": True,
        "source_content_accessed": False,
        "resolver_role_contaminated_for_extraction": True,
        "entry_count": 33,
        "entries": exposure_entries,
        "limitations": [
            "This ledger extends, but does not rewrite, the predecessor "
            "project-wide exposure ledger.",
            "Landing-page metadata exposure does not verify any linked source "
            "edition or authorize a source request.",
        ],
    }
    exposure_path = output_dir / "exposure-ledger.json"
    _validate(root, schema_root / "g2_url_resolution_exposure_ledger.schema.json", exposure)
    _write(exposure_path, exposure)

    direct_path = root / "data/methods/g2" / PLAN_ID / "design/proposed-acquisition-manifest.json"
    direct = _read(direct_path)
    direct_by_rank = {int(row["frame_rank"]): row for row in direct["entries"]}
    proposal_entries = []
    locator_urls: list[str] = []
    for source in frame["candidates"]:
        rank = int(source["frame_rank"])
        if rank in direct_by_rank:
            url = direct_by_rank[rank]["requested_entrypoint"]
            locator_status = "preexisting_direct_proposal"
        elif rank in strong:
            url = strong[rank]
            locator_status = "strong_metadata_hypothesis"
        else:
            url = None
            locator_status = "unresolved"
        if url is not None:
            locator_urls.append(url)
        proposal_entries.append(
            {
                "frame_rank": rank,
                "candidate_id": source["candidate_id"],
                "edition_id": source["edition_id"],
                "jurisdiction_id": source["jurisdiction_id"],
                "source_series_id": source["source_series_id"],
                "locator_status": locator_status,
                "proposed_pdf_url": url,
                "source_request_authorized": False,
                "source_request_performed": False,
                "redistribution_boundary": "metadata_and_citation_only",
            }
        )
    if len(locator_urls) != 26 or len(set(locator_urls)) != 26:
        raise ValueError("refreshed locator counts differ from reviewed result")
    proposal = {
        "schema_version": "1.0",
        "proposal_id": "G2HOLDOUT-REFRESHED-PDF-LOCATOR-PROPOSAL-20260815-01",
        "plan_id": PLAN_ID,
        "frame": _artifact(root, frame_path),
        "resolution_receipt": resolution_artifact,
        "status": "insufficient_scope_not_authorized",
        "source_request_performed": False,
        "required_scope": 30,
        "counts": {
            "candidates": 44,
            "preexisting_direct_locators": 11,
            "resolver_hypotheses": 15,
            "locator_candidates": 26,
            "unique_locator_urls": 26,
            "unresolved_candidates": 18,
        },
        "entries": proposal_entries,
        "limitations": [
            "The 26 unique locator URLs cannot satisfy the frozen 30-edition "
            "primary-plus-reserve scope.",
            "All locators remain unrequested proposals or metadata hypotheses "
            "and require a later owner decision.",
            "The HTTP locator at rank 19 requires a separate secure-transport "
            "disposition before any request.",
        ],
    }
    proposal_path = output_dir / "refreshed-pdf-locator-proposal.json"
    _validate(root, schema_root / "g2_refreshed_pdf_locator_proposal.schema.json", proposal)
    _write(proposal_path, proposal)

    _write_manifest(
        root,
        output_dir,
        [
            root / "config/g2_url_resolution_corrections.json",
            root / "docs/governance/"
            "g2-structural-preflight-url-resolution-owner-decision-2026-08-15.md",
            root / schema_root / "g2_refreshed_pdf_locator_proposal.schema.json",
            root / schema_root / "g2_url_resolution_exposure_ledger.schema.json",
            root / schema_root / "g2_url_resolution_network_access_receipt.schema.json",
            root / schema_root / "g2_url_resolution_receipt.schema.json",
            root / "scripts/assemble_g2_url_resolution.py",
            root / "tests/test_g2_url_resolution.py",
            raw_resolution_path,
            raw_access_path,
            identity_path,
            access_review_path,
            corrected_path,
            network_path,
            exposure_path,
            proposal_path,
        ],
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--agent-dir", type=Path, default=Path("build/g2-structural-preflight-url-resolution/agent")
    )
    parser.add_argument(
        "--panel-dir",
        type=Path,
        default=Path("build/g2-structural-preflight-url-resolution/panels"),
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    assemble(args.root, args.agent_dir, args.panel_dir, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
