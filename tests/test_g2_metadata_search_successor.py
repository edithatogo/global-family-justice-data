from __future__ import annotations

import hashlib
import json
import shutil
from copy import deepcopy
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest

import gfjd.g2_metadata_search_successor as successor

DESIGN = Path("data/methods/g2/G2HOLDOUT-METADATA-EXPANSION-20260816-02/design")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


NOW = datetime(2026, 8, 18, tzinfo=UTC)


def _bundle(root: Path, *, execution_date: str = "2026-08-16") -> dict[str, Any]:
    manifest_path = root / DESIGN / "successor-query-manifest.json"
    manifest = json.loads(manifest_path.read_text())
    plan = json.loads((root / DESIGN / "successor-plan.json").read_text())
    events = []
    initial = datetime(2026, 8, 16, tzinfo=UTC)
    for index, query in enumerate(manifest["queries"]):
        results: list[object] = []
        started = initial + timedelta(seconds=index * 2)
        finished = started + timedelta(seconds=1)
        events.append(
            {
                "provider_call_order": query["query_order"],
                "provider_call_started_at": started.isoformat(),
                "provider_call_finished_at": finished.isoformat(),
                "query_order": query["query_order"],
                "query_id": query["query_id"],
                "query_text": query["query_text"],
                "language": query["language"],
                "searched_on": execution_date,
                "result_count": 0,
                "results": results,
                "query_sha256": query["query_sha256"],
                "result_sha256": hashlib.sha256(_canonical(results)).hexdigest(),
                "access_issue": None,
            }
        )
    provider = dict(manifest["provider_config"])
    provider["execution_date"] = execution_date
    failed = plan["failed_predecessor"]
    return {
        "schema_version": "1.0",
        "bundle_id": "G2-SUCCESSOR-TEST",
        "generated_at": "2026-08-16T01:00:00+00:00",
        "execution_date": execution_date,
        "authorized_interval": {
            "valid_from": "2026-08-15T04:00:00+00:00",
            "valid_until": "2026-08-17T00:00:00+00:00",
        },
        "query_manifest": {
            "path": manifest_path.relative_to(root).as_posix(),
            "sha256": _sha(manifest_path),
        },
        "design_manifest": {
            "path": (DESIGN / "SUCCESSOR_DESIGN_MANIFEST.sha256").as_posix(),
            "sha256": _sha(root / DESIGN / "SUCCESSOR_DESIGN_MANIFEST.sha256"),
        },
        "authority_receipt": {
            "path": (
                "data/methods/g2/G2HOLDOUT-METADATA-EXPANSION-20260816-02/"
                "authority/execution-authority-receipt.json"
            ),
            "sha256": "0" * 64,
        },
        "lineage_bindings": {
            key: failed[key]
            for key in (
                "execution_stop",
                "stop_receipt",
                "passive_exposure_annex",
                "stop_panel",
                "lineage_index",
                "prior_exposure_ledger",
            )
        },
        "tool_name": "web__run.search_query",
        "tool_version": "test",
        "provider_config": provider,
        "query_events": events,
        "candidate_hypotheses": [],
        "exposure_events": [],
        "non_overlap_receipt": {
            "checked_known_urls": [],
            "known_overlaps": [],
            "prior_aggregate_reconstruction_complete": False,
            "unknown_prior_urls_captured": False,
            "claim": (
                "no overlap found against reconstructable known URLs; non-overlap "
                "with unknown prior aggregate URLs cannot be established"
            ),
        },
        "proposed_official_html_allowlist": [],
        "successor_logical_query_submissions": 208,
        "successor_provider_calls": 208,
        "successor_retries": 0,
        "prior_lineage_submissions": 4,
        "cumulative_lineage_submissions": 212,
        "violations": [],
        "result_url_requests": 0,
        "landing_page_requests": 0,
        "source_file_requests": 0,
        "head_requests": 0,
        "redirects_followed": 0,
        "persisted_snippets": 0,
        "persisted_source_excerpts": 0,
        "persisted_target_facts": 0,
    }


def _verify(monkeypatch: pytest.MonkeyPatch, root: Path, bundle: dict[str, Any]) -> list[str]:
    monkeypatch.setattr(successor, "_verify_authority", lambda *_args, **_kwargs: [])
    return successor.verify_successor_bundle(root, bundle, now=NOW)


def _add_first_result(bundle: dict[str, Any], result: dict[str, Any]) -> None:
    event = bundle["query_events"][0]
    event["results"] = [result]
    event["result_count"] = 1
    event["result_sha256"] = hashlib.sha256(_canonical([result])).hexdigest()
    passive = {
        "url": result["url"],
        "url_kind": result["url_kind"],
        "requested": False,
    }
    bundle["candidate_hypotheses"] = [passive]
    bundle["exposure_events"] = [passive]
    bundle["non_overlap_receipt"]["checked_known_urls"] = [result["url"]]


def test_successor_accepts_captured_iso_execution_date(
    project_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert _verify(monkeypatch, project_root, _bundle(project_root)) == []


def test_successor_accepts_passive_file_candidate_but_not_html_allowlist(
    project_root: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    bundle = _bundle(project_root)
    _add_first_result(
        bundle,
        {
            "rank": 1,
            "title": "Annual report",
            "url": "https://www.fcfcoa.gov.au/sites/default/files/report.pdf",
            "domain": "www.fcfcoa.gov.au",
            "url_kind": "file",
            "requested": False,
            "official_host_candidate": False,
        },
    )
    assert _verify(monkeypatch, project_root, bundle) == []


def test_successor_projects_only_canonical_official_https_html(
    project_root: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    bundle = _bundle(project_root)
    _add_first_result(
        bundle,
        {
            "rank": 1,
            "title": "Annual reports",
            "url": "https://WWW.FCFCOA.GOV.AU/annual-reports#top",
            "domain": "www.fcfcoa.gov.au",
            "url_kind": "html",
            "requested": False,
            "official_host_candidate": True,
        },
    )
    canonical = "https://www.fcfcoa.gov.au/annual-reports"
    bundle["candidate_hypotheses"][0]["url"] = canonical
    bundle["exposure_events"][0]["url"] = canonical
    bundle["non_overlap_receipt"]["checked_known_urls"] = [canonical]
    bundle["proposed_official_html_allowlist"] = [canonical]
    assert _verify(monkeypatch, project_root, bundle) == []


def test_successor_rejects_adversarial_contract_mutations(
    project_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    valid = _bundle(project_root)
    mutations = []
    batched = deepcopy(valid)
    batched["query_events"][1]["provider_call_order"] = 1
    mutations.append(batched)
    retry = deepcopy(valid)
    retry["successor_retries"] = 1
    mutations.append(retry)
    wrong_date = deepcopy(valid)
    wrong_date["query_events"][0]["searched_on"] = "2026-08-15"
    mutations.append(wrong_date)
    false_reconstruction = deepcopy(valid)
    false_reconstruction["non_overlap_receipt"]["prior_aggregate_reconstruction_complete"] = True
    mutations.append(false_reconstruction)
    false_capture = deepcopy(valid)
    false_capture["non_overlap_receipt"]["unknown_prior_urls_captured"] = True
    mutations.append(false_capture)
    wrong_lineage = deepcopy(valid)
    wrong_lineage["cumulative_lineage_submissions"] = 208
    mutations.append(wrong_lineage)
    future = deepcopy(valid)
    future["generated_at"] = "2026-08-19T00:00:00+00:00"
    mutations.append(future)
    nonmonotonic = deepcopy(valid)
    nonmonotonic["query_events"][1]["provider_call_started_at"] = nonmonotonic["query_events"][0][
        "provider_call_started_at"
    ]
    mutations.append(nonmonotonic)
    requested = deepcopy(valid)
    _add_first_result(
        requested,
        {
            "rank": 1,
            "title": "Report",
            "url": "https://www.fcfcoa.gov.au/report.pdf",
            "domain": "www.fcfcoa.gov.au",
            "url_kind": "file",
            "requested": True,
            "official_host_candidate": False,
        },
    )
    mutations.append(requested)
    bad_kind = deepcopy(valid)
    _add_first_result(
        bad_kind,
        {
            "rank": 1,
            "title": "Report",
            "url": "https://www.fcfcoa.gov.au/report.pdf",
            "domain": "www.fcfcoa.gov.au",
            "url_kind": "html",
            "requested": False,
            "official_host_candidate": True,
        },
    )
    bad_kind["proposed_official_html_allowlist"] = [bad_kind["candidate_hypotheses"][0]["url"]]
    mutations.append(bad_kind)
    wrong_domain = deepcopy(valid)
    _add_first_result(
        wrong_domain,
        {
            "rank": 1,
            "title": "Report",
            "url": "https://www.fcfcoa.gov.au/report",
            "domain": "example.org",
            "url_kind": "html",
            "requested": False,
            "official_host_candidate": True,
        },
    )
    wrong_domain["proposed_official_html_allowlist"] = [
        wrong_domain["candidate_hypotheses"][0]["url"]
    ]
    mutations.append(wrong_domain)
    for mutation in mutations:
        assert _verify(monkeypatch, project_root, mutation)


@pytest.mark.parametrize(
    "attacker_path",
    [
        "/tmp/attacker.json",
        "../../attacker.json",
        "data/methods/g2/attacker-successor-query-manifest.json",
    ],
)
def test_successor_rejects_nonexact_query_manifest_paths(
    project_root: Path, attacker_path: str
) -> None:
    bundle = _bundle(project_root)
    bundle["query_manifest"]["path"] = attacker_path
    assert successor.verify_successor_bundle(project_root, bundle, now=NOW)


def test_successor_rejects_design_manifest_swap(project_root: Path) -> None:
    bundle = _bundle(project_root)
    bundle["design_manifest"] = bundle["query_manifest"]
    assert successor.verify_successor_bundle(project_root, bundle, now=NOW)


def test_safe_path_rejects_symlink_escape(tmp_path: Path) -> None:
    outside = tmp_path.parent / f"{tmp_path.name}-outside-successor-manifest.json"
    outside.write_text("{}\n")
    try:
        link = tmp_path / "data/methods/link.json"
        link.parent.mkdir(parents=True)
        link.symlink_to(outside)
        assert successor._safe_path(tmp_path, "data/methods/link.json") is None
    finally:
        outside.unlink(missing_ok=True)


def _authority_fixture(
    project_root: Path, tmp_path: Path
) -> tuple[dict[str, Any], dict[str, Any], Path, Path]:
    design_target = tmp_path / DESIGN
    design_target.mkdir(parents=True)
    for schema in (
        "successor-authority-receipt.schema.json",
        "successor-owner-decision.schema.json",
    ):
        shutil.copyfile(project_root / DESIGN / schema, design_target / schema)
    decision_path = tmp_path / "docs/governance/g2-metadata-search-successor-owner-decision.json"
    decision_path.parent.mkdir(parents=True)
    design_descriptor = {
        "path": (DESIGN / "SUCCESSOR_DESIGN_MANIFEST.sha256").as_posix(),
        "sha256": "1" * 64,
    }
    query_descriptor = {
        "path": (DESIGN / "successor-query-manifest.json").as_posix(),
        "sha256": "2" * 64,
    }
    freeze_commit = "a" * 40
    decision = {
        "schema_version": "1.0",
        "decision_id": "D-G2-METADATA-SEARCH-SUCCESSOR-20260816-01",
        "decision": "authorize_exact_successor_search_index_execution",
        "owner_identity": "test-owner",
        "owner_role": "sole_repository_owner_and_accountable_authority",
        "decided_at": "2026-08-15T01:00:00+00:00",
        "valid_from": "2026-08-15T04:00:00+00:00",
        "valid_until": "2026-08-17T00:00:00+00:00",
        "design_manifest": design_descriptor,
        "freeze_commit": freeze_commit,
        "query_manifest": query_descriptor,
        "authorization": {
            "successor_logical_queries": 208,
            "successor_provider_calls": 208,
            "logical_queries_per_call": 1,
            "successor_retries": 0,
            "prior_lineage_submissions": 4,
            "cumulative_lineage_submissions": 212,
            "passive_metadata_only": True,
            "result_url_requests": 0,
            "landing_page_requests": 0,
            "source_file_requests": 0,
            "head_requests": 0,
            "redirects_followed": 0,
        },
        "acknowledgements": {
            "prior_query_ids_denied": ["G2Q-001", "G2Q-002", "G2Q-003", "G2Q-004"],
            "prior_aggregate_reconstruction_complete": False,
            "unknown_prior_urls_captured": False,
            "source_access_authorized": False,
            "outbound_contact_authorized": False,
            "publication_authorized": False,
            "release_authorized": False,
            "g2_passage_authorized": False,
        },
    }
    decision_path.write_text(json.dumps(decision) + "\n")
    decision_descriptor = {
        "path": decision_path.relative_to(tmp_path).as_posix(),
        "sha256": _sha(decision_path),
    }
    receipt_path = (
        tmp_path / "data/methods/g2/G2HOLDOUT-METADATA-EXPANSION-20260816-02/authority/"
        "execution-authority-receipt.json"
    )
    receipt_path.parent.mkdir(parents=True)
    receipt = {
        "schema_version": "1.0",
        "receipt_id": "G2-METADATA-SEARCH-SUCCESSOR-AUTHORITY-20260816-01",
        "generated_at": "2026-08-15T03:00:00+00:00",
        "design_manifest": design_descriptor,
        "freeze_commit": freeze_commit,
        "freeze_commit_object_type": "commit",
        "freeze_signature": {
            "command": ["git", "verify-commit"],
            "status": "good",
            "verified_at": "2026-08-15T00:30:00+00:00",
        },
        "owner_decision": decision_descriptor,
        "owner_decision_commit": "b" * 40,
        "owner_decision_commit_object_type": "commit",
        "owner_decision_signature": {
            "command": ["git", "verify-commit"],
            "status": "good",
            "verified_at": "2026-08-15T02:00:00+00:00",
        },
        "tree_bindings": {
            "freeze_commit_contains_design_manifest": True,
            "owner_decision_commit_contains_owner_decision": True,
        },
    }
    receipt_path.write_text(json.dumps(receipt) + "\n")
    bundle = {
        "authority_receipt": {
            "path": receipt_path.relative_to(tmp_path).as_posix(),
            "sha256": _sha(receipt_path),
        },
        "design_manifest": design_descriptor,
        "query_manifest": query_descriptor,
        "authorized_interval": {
            "valid_from": decision["valid_from"],
            "valid_until": decision["valid_until"],
        },
    }
    return bundle, receipt, receipt_path, decision_path


def test_authority_receipt_binds_decision_commits_and_interval(
    project_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    bundle, _, _, _ = _authority_fixture(project_root, tmp_path)
    monkeypatch.setattr(successor, "_git_commit_binds", lambda *_args: True)
    assert successor._verify_authority(tmp_path, bundle, now=NOW) == []


def test_authority_receipt_rejects_swaps_and_future_evidence(
    project_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    bundle, receipt, receipt_path, decision_path = _authority_fixture(project_root, tmp_path)
    monkeypatch.setattr(successor, "_git_commit_binds", lambda *_args: True)
    mutations: list[tuple[dict[str, Any], dict[str, Any], dict[str, Any]]] = []
    decision = json.loads(decision_path.read_text())
    swapped_query = deepcopy(decision)
    swapped_query["query_manifest"]["sha256"] = "f" * 64
    mutations.append((deepcopy(bundle), deepcopy(receipt), swapped_query))
    swapped_commit = deepcopy(decision)
    swapped_commit["freeze_commit"] = "c" * 40
    mutations.append((deepcopy(bundle), deepcopy(receipt), swapped_commit))
    future_receipt = deepcopy(receipt)
    future_receipt["owner_decision_signature"]["verified_at"] = "2026-08-19T00:00:00+00:00"
    mutations.append((deepcopy(bundle), future_receipt, deepcopy(decision)))
    retrospective = deepcopy(decision)
    retrospective["valid_from"] = "2026-08-15T02:30:00+00:00"
    mutations.append((deepcopy(bundle), deepcopy(receipt), retrospective))
    decision_before_freeze = deepcopy(decision)
    decision_before_freeze["decided_at"] = "2026-08-14T23:00:00+00:00"
    mutations.append((deepcopy(bundle), deepcopy(receipt), decision_before_freeze))
    for mutated_bundle, mutated_receipt, mutated_decision in mutations:
        decision_path.write_text(json.dumps(mutated_decision) + "\n")
        mutated_receipt["owner_decision"]["sha256"] = _sha(decision_path)
        receipt_path.write_text(json.dumps(mutated_receipt) + "\n")
        mutated_bundle["authority_receipt"]["sha256"] = _sha(receipt_path)
        assert successor._verify_authority(tmp_path, mutated_bundle, now=NOW)


def test_successor_rejects_missing_stop_lineage_link(
    project_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    bundle = _bundle(project_root)
    del bundle["lineage_bindings"]["execution_stop"]
    assert _verify(monkeypatch, project_root, bundle)


def test_successor_rejects_provider_call_before_authorized_interval(
    project_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    bundle = _bundle(project_root)
    bundle["query_events"][0]["provider_call_started_at"] = "2026-08-15T03:59:59+00:00"
    bundle["query_events"][0]["provider_call_finished_at"] = "2026-08-15T04:00:00+00:00"
    assert _verify(monkeypatch, project_root, bundle)
