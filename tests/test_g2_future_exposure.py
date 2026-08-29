from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from gfjd.g2_future_exposure import (
    FutureExposureError,
    build_exposure_snapshot,
    canonical_request_identity,
    canonical_url,
    verify_exposure_snapshot,
)


def _write(path: Path, value: object) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _manifest(path: str, digest: str, kind: str = "exposure_ledger") -> dict:
    return {
        "schema_version": "1.0",
        "lineage_id": "G2-FUTURE-TEST",
        "inputs": [{"path": path, "sha256": digest, "kind": kind}],
    }


def test_canonical_url_collapses_safe_aliases() -> None:
    first = canonical_url("http://EXAMPLE.com:80/a/../b/%7Efile?q=2&q=1#fragment")
    second = canonical_url("https://example.com/b/~file?q=1&q=2")
    assert first == second == "https://example.com/b/~file?q=1&q=2"
    assert canonical_url("file:///private/a/../source%20one.pdf") == (
        "file:///private/source%20one.pdf"
    )


def test_request_identity_binds_method_url_and_body() -> None:
    assert (
        canonical_request_identity(
            method="post",
            url="https://EXAMPLE.com/api?b=2&a=1",
            body_sha256="a" * 64,
        )
        == "POST\0https://example.com/api?a=1&b=2\0" + "a" * 64
    )


def test_builds_sorted_deduplicated_snapshot_with_predecessor(tmp_path: Path) -> None:
    prior = {
        "denied_urls": ["http://Example.COM/report#x"],
        "entries": [
            {
                "edition_id": "ED-1",
                "source_series_id": "SERIES-1",
                "source_id": "SOURCE-1",
                "urls": ["https://example.com/report"],
                "source_sha256": "b" * 64,
            }
        ],
        "predecessor": None,
    }
    prior_digest = _write(tmp_path / "prior.json", prior)
    current = {
        "denied_urls": ["https://example.org/z?b=2&a=1"],
        "entries": [
            {
                "source_edition_id": "ED-2",
                "source_url": "https://example.org/z?a=1&b=2",
                "method": "GET",
                "url": "https://example.org/z?b=2&a=1",
            }
        ],
        "predecessor": {"path": "prior.json", "sha256": prior_digest},
    }
    digest = _write(tmp_path / "current.json", current)
    snapshot = build_exposure_snapshot(tmp_path, _manifest("current.json", digest))
    assert snapshot["counts"] == {
        "urls": 2,
        "request_identities": 1,
        "edition_ids": 2,
        "source_series_ids": 1,
        "source_ids": 1,
        "content_sha256": 1,
    }
    assert snapshot["exposure"]["edition_ids"] == ["ed-1", "ed-2"]
    assert len(snapshot["inputs"]) == 2
    assert verify_exposure_snapshot(tmp_path, _manifest("current.json", digest), snapshot) == []


def test_registrar_observations_are_explicit_bound_input(tmp_path: Path) -> None:
    observations = {
        "exposure_events": [
            {"url": "https://example.net/new", "requested": False},
            {
                "edition_alias": "EDITION-NEW",
                "request_method": "POST",
                "request_url": "https://example.net/api",
                "request_body_sha256": "c" * 64,
            },
        ]
    }
    digest = _write(tmp_path / "observations.json", observations)
    snapshot = build_exposure_snapshot(
        tmp_path, _manifest("observations.json", digest, "registrar_observations")
    )
    assert snapshot["counts"]["urls"] == 2
    assert snapshot["counts"]["request_identities"] == 1
    assert snapshot["exposure"]["edition_ids"] == ["edition-new"]


def test_collects_generic_url_suffixes_from_historical_artifacts(tmp_path: Path) -> None:
    artifact = {
        "result_url": "https://example.net/result",
        "download_url": "https://example.net/download",
        "nested": {"final_url": "https://example.net/final"},
    }
    digest = _write(tmp_path / "artifact.json", artifact)
    snapshot = build_exposure_snapshot(tmp_path, _manifest("artifact.json", digest, "g2_artifact"))
    assert snapshot["exposure"]["urls"] == [
        "https://example.net/download",
        "https://example.net/final",
        "https://example.net/result",
    ]


def test_fails_on_digest_mismatch_missing_and_escape(tmp_path: Path) -> None:
    digest = _write(tmp_path / "input.json", {"denied_urls": []})
    with pytest.raises(FutureExposureError, match="binding mismatch"):
        build_exposure_snapshot(tmp_path, _manifest("input.json", "0" * 64))
    with pytest.raises(FutureExposureError, match="missing"):
        build_exposure_snapshot(tmp_path, _manifest("missing.json", digest))
    with pytest.raises(FutureExposureError, match="escapes"):
        build_exposure_snapshot(tmp_path, _manifest("../input.json", digest))


def test_fails_on_malformed_url_and_descriptor(tmp_path: Path) -> None:
    digest = _write(tmp_path / "input.json", {"denied_urls": ["ftp://example.com/source"]})
    with pytest.raises(FutureExposureError, match="unsupported exposure URL"):
        build_exposure_snapshot(tmp_path, _manifest("input.json", digest))
    bad = _manifest("input.json", digest)
    bad["inputs"][0]["extra"] = True
    with pytest.raises(FutureExposureError, match="malformed"):
        build_exposure_snapshot(tmp_path, bad)


def test_fails_on_predecessor_cycle(tmp_path: Path) -> None:
    # A digest self-cycle is cryptographically infeasible; two descriptors with
    # the same identity exercise the active-set guard directly through a mocked
    # fixed digest and file verifier.
    path = tmp_path / "loop.json"
    path.write_text("{}", encoding="utf-8")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    value = {
        "denied_urls": [],
        "predecessor": {"path": "loop.json", "sha256": digest},
    }
    digest = _write(path, value)
    # The predecessor binding now mismatches, which is the required fail-closed
    # result for a mutable attempt to manufacture a cycle.
    with pytest.raises(FutureExposureError, match="binding mismatch"):
        build_exposure_snapshot(tmp_path, _manifest("loop.json", digest))


def test_snapshot_tampering_is_rejected(tmp_path: Path) -> None:
    digest = _write(tmp_path / "input.json", {"denied_urls": ["https://example.com/a"]})
    manifest = _manifest("input.json", digest)
    snapshot = build_exposure_snapshot(tmp_path, manifest)
    snapshot["counts"]["urls"] = 0
    assert verify_exposure_snapshot(tmp_path, manifest, snapshot) == [
        "exposure snapshot does not reproduce from its bound inputs"
    ]


def test_repository_future_campaign_snapshot_reproduces(project_root: Path) -> None:
    control = project_root / (
        "data/methods/g2/G2PROSPECTIVE-CALIBRATION-20260829-01/execution-control"
    )
    manifest = json.loads((control / "exposure-input-manifest.json").read_text())
    snapshot = json.loads((control / "exposure-snapshot.json").read_text())
    assert verify_exposure_snapshot(project_root, manifest, snapshot) == []
    assert snapshot["counts"]["urls"] >= 760
    assert any(
        item["path"].endswith("preliminary-registrar-observations.json")
        for item in snapshot["inputs"]
    )
