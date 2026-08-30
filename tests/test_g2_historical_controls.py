"""Synthetic-only checks; no publisher calls or factual extraction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from gfjd.g2_historical_controls import (
    HistoricalControlError,
    audit_repository,
    evaluate_metadata,
    verify_audit,
    write_once,
)


def _input(root: Path, name: str, value: object) -> Path:
    path = root / "data/methods/g2" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def _response(*links: str) -> bytes:
    return json.dumps(
        {
            "total": len(links),
            "start": 0,
            "results": [
                {
                    "link": link,
                    "public_timestamp": "2025-01-01T00:00:00Z",
                    "format": "official_statistics",
                    "title": "FICTIONAL test publication",
                }
                for link in links
            ],
        }
    ).encode()


def test_audit_json_jsonl_arrays_aliases_and_identifiers(tmp_path: Path) -> None:
    _input(tmp_path, "a.json", {"url": "http://Example.org:80/a#x", "edition_id": "ED-1"})
    path = _input(tmp_path, "b.jsonl", {"endpoint": "https://example.org/a"})
    path.write_text(path.read_text() + '\n{"source_series_id":"SERIES-1"}\n')
    _input(tmp_path, "c.json", [{"product_id": "123"}, {"source_sha256": "a" * 64}])
    audit = audit_repository(tmp_path)
    assert audit["counts"]["urls"] == 1
    assert audit["counts"]["edition_ids"] == 1
    assert audit["counts"]["product_ids"] == 1
    assert len(audit["inputs"]) == 3
    assert audit["execution_ready"] is False
    assert verify_audit(tmp_path, audit) == []


@pytest.mark.parametrize("change", ["omit", "edit", "add"])
def test_audit_recomputes_membership_and_digests(tmp_path: Path, change: str) -> None:
    path = _input(tmp_path, "a.json", {"url": "https://example.org/a"})
    audit = audit_repository(tmp_path)
    if change == "omit":
        audit["inputs"] = []
    elif change == "edit":
        path.write_text("{}")
    else:
        _input(tmp_path, "new.json", {})
    assert verify_audit(tmp_path, audit)


@pytest.mark.parametrize("raw", ['{"url":1,"url":2}', '{"url":NaN}', "{bad", "\n{}\n\n{}"])
def test_malformed_inputs_fail_closed(tmp_path: Path, raw: str) -> None:
    path = _input(tmp_path, "a.jsonl", {})
    path.write_text(raw)
    with pytest.raises(HistoricalControlError):
        audit_repository(tmp_path)


def test_symlink_input_rejected(tmp_path: Path) -> None:
    path = _input(tmp_path, "a.json", {})
    try:
        (path.parent / "linked.json").symlink_to(path)
    except OSError:
        pytest.skip("symlink creation unavailable")
    with pytest.raises(HistoricalControlError, match="symlink"):
        audit_repository(tmp_path)


def test_opaque_exposure_blocks_official_index_historical_claim(tmp_path: Path) -> None:
    _input(
        tmp_path,
        "stop.json",
        {
            "facts": {"observed_results": 280, "complete_locator_records": 0},
            "coarse_exposure_quarantine": {"blocks_future_search_based_unseen_claims": True},
        },
    )
    result = evaluate_metadata(
        _response("/government/statistics/fictional-a"), audit_repository(tmp_path), root=tmp_path
    )
    assert result["status"] == "terminal_stop"
    assert "unenumerated_exposure" in result["stop_reasons"]
    assert len(result["observations"]) == 1
    assert result["selected"] == []


def test_all_locators_retained_without_titles_on_enumeration_failure(tmp_path: Path) -> None:
    _input(tmp_path, "empty.json", {})
    payload = json.loads(_response("/government/statistics/fictional-a"))
    payload["total"] = 101
    result = evaluate_metadata(
        json.dumps(payload).encode(), audit_repository(tmp_path), root=tmp_path
    )
    assert result["status"] == "terminal_stop"
    assert len(result["observations"]) == 1
    assert "title" not in json.dumps(result)
    assert result["selected"] == []


def test_window_and_alias_exclusion_precede_deterministic_selection(tmp_path: Path) -> None:
    _input(tmp_path, "old.json", {"url": "http://www.gov.uk/government/statistics/old#alias"})
    payload = json.loads(
        _response(
            "/government/statistics/old",
            "/government/statistics/b",
            "/government/statistics/a",
            "/government/statistics/late",
        )
    )
    payload["results"][-1]["public_timestamp"] = "2026-08-29T05:17:40Z"
    result = evaluate_metadata(
        json.dumps(payload).encode(), audit_repository(tmp_path), root=tmp_path
    )
    assert result["status"] == "metadata_hypotheses_only"
    assert len(result["observations"]) == 4
    assert [row["url"].rsplit("/", 1)[-1] for row in result["selected"]] == ["a", "b"]
    assert result["execution_ready"] is False
    assert not any(result["authority"].values())


@pytest.mark.parametrize("change", ["host", "date", "duplicate", "fields", "pagination", "bool"])
def test_response_contract_failures_keep_locators(tmp_path: Path, change: str) -> None:
    _input(tmp_path, "empty.json", {})
    payload = json.loads(_response("/government/statistics/a", "/government/statistics/b"))
    if change == "host":
        payload["results"][0]["link"] = "https://other.example/a"
    elif change == "date":
        payload["results"][0]["public_timestamp"] = "2025-01-01"
    elif change == "duplicate":
        payload["results"][1] = payload["results"][0]
    elif change == "fields":
        payload["results"][0]["unexpected"] = "ignored?"
    elif change == "pagination":
        payload["start"] = 1
    else:
        payload["total"] = True
    result = evaluate_metadata(
        json.dumps(payload).encode(), audit_repository(tmp_path), root=tmp_path
    )
    assert result["status"] == "terminal_stop"
    assert result["selected"] == []
    assert len(result["observations"]) == 2


def test_immutable_output(tmp_path: Path) -> None:
    path = tmp_path / "receipt.json"
    write_once(path, {"synthetic": True})
    with pytest.raises(FileExistsError):
        write_once(path, {"repaired": True})


def test_repository_opaque_exposure_is_not_promoted(project_root: Path) -> None:
    audit = audit_repository(project_root)
    assert "unenumerated_exposure" in audit["blockers"]
    assert audit["execution_ready"] is False
    assert any(item["path"].endswith(".jsonl") for item in audit["inputs"])


def test_uppercase_scheme_is_exposure(tmp_path: Path) -> None:
    _input(tmp_path, "old.json", {"url": "HTTPS://www.gov.uk/government/statistics/a"})
    result = evaluate_metadata(
        _response("/government/statistics/a", "/government/statistics/b"),
        audit_repository(tmp_path),
        root=tmp_path,
    )
    assert result["status"] == "terminal_stop"
    assert result["selected"] == []


def test_directory_symlink_rejected(tmp_path: Path) -> None:
    path = _input(tmp_path, "ordinary.json", {})
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    try:
        (path.parent / "linked").symlink_to(elsewhere, target_is_directory=True)
    except OSError:
        pytest.skip("symlink creation unavailable")
    with pytest.raises(HistoricalControlError, match="symlink"):
        audit_repository(tmp_path)


def test_missing_and_changed_predecessor_bindings_block(tmp_path: Path) -> None:
    _input(
        tmp_path,
        "current.json",
        {"predecessor": {"path": "data/methods/g2/prior.json", "sha256": "a" * 64}},
    )
    audit = audit_repository(tmp_path)
    assert "missing_or_changed_reference" in audit["blockers"]
    _input(tmp_path, "prior.json", {})
    assert "missing_or_changed_reference" in audit_repository(tmp_path)["blockers"]


def test_audit_tampering_cannot_remove_opaque_stop(tmp_path: Path) -> None:
    _input(
        tmp_path,
        "stop.json",
        {"coarse_exposure_quarantine": {"blocks_future_search_based_unseen_claims": True}},
    )
    audit = audit_repository(tmp_path)
    audit["blockers"] = []
    with pytest.raises(HistoricalControlError, match="verified"):
        evaluate_metadata(_response("/government/statistics/a"), audit, root=tmp_path)


def test_relative_paths_are_resolved_only_against_explicit_request(tmp_path: Path) -> None:
    _input(
        tmp_path,
        "nz.json",
        {
            "request": {"url": "https://example.org/index"},
            "observation": {"locators": ["/fixture.xlsx"]},
        },
    )
    audit = audit_repository(tmp_path)
    assert audit["counts"]["urls"] == 2
    _input(tmp_path, "ambiguous.json", {"locators": ["/other.xlsx"]})
    assert "unresolved_relative_locator" in audit_repository(tmp_path)["blockers"]


def test_incomplete_passive_and_manifest_evidence_remain_gaps(tmp_path: Path) -> None:
    _input(tmp_path, "annex.json", {"status": "reconstruction_incomplete"})
    _input(
        tmp_path, "sitemap.json", {"status": "terminal_stopped_manifest_response_budget_exceeded"}
    )
    assert set(audit_repository(tmp_path)["blockers"]) == {
        "incomplete_passive_exposure_reconstruction",
        "incomplete_manifest_enumeration",
    }


def test_auxiliary_references_are_hash_checked_not_reported_missing(tmp_path: Path) -> None:
    path = _input(tmp_path, "current.json", {})
    auxiliary = path.parent / "reference.sha256"
    auxiliary.write_text("synthetic binding only\n")
    _input(
        tmp_path,
        "current.json",
        {
            "reference": {
                "path": "data/methods/g2/reference.sha256",
                "sha256": hashlib.sha256(auxiliary.read_bytes()).hexdigest(),
            }
        },
    )
    audit = audit_repository(tmp_path)
    assert audit["reference_checks"][0]["status"] == "exact_binding_verified"
    assert audit["blockers"] == []


def test_over_limit_response_records_all_parseable_locators(tmp_path: Path) -> None:
    _input(tmp_path, "empty.json", {})
    raw = _response(*(f"/government/statistics/fictional-{i}" for i in range(101)))
    result = evaluate_metadata(raw, audit_repository(tmp_path), root=tmp_path)
    assert result["status"] == "terminal_stop"
    assert len(result["observations"]) == 101
    assert result["selected"] == []


def test_timezone_equivalent_upper_cutoff_is_excluded(tmp_path: Path) -> None:
    _input(tmp_path, "empty.json", {})
    payload = json.loads(_response("/government/statistics/a", "/government/statistics/b"))
    payload["results"][0]["public_timestamp"] = "2026-08-29T15:17:40+10:00"
    result = evaluate_metadata(
        json.dumps(payload).encode(), audit_repository(tmp_path), root=tmp_path
    )
    assert result["selected"] == []
    assert "fewer_than_two_metadata_hypotheses" in result["stop_reasons"]
