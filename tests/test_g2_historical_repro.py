from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from gfjd import g2_historical_repro as module
from gfjd.g2_historical_controls import HistoricalControlError, audit_repository
from gfjd.g2_historical_repro import CLAIM, evaluate, verify_bundle


def _audit(root: Path, *, extra: dict | None = None) -> dict:
    path = root / "data/methods/g2/synthetic.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "coarse_exposure_quarantine": {"blocks_future_search_based_unseen_claims": True},
                **(extra or {}),
            }
        )
    )
    (root / "MANIFEST.sha256").write_text(
        f"{hashlib.sha256(path.read_bytes()).hexdigest()}  data/methods/g2/synthetic.json\n"
    )
    return audit_repository(root)


def _response() -> dict:
    return {
        "total": 2,
        "start": 0,
        "results": [
            {
                "link": f"/government/statistics/fictional-{i}",
                "title": "FICTIONAL title",
                "public_timestamp": "2025-01-01T00:00:00Z",
                "format": "official_statistics",
            }
            for i in range(2)
        ],
    }


def test_approved_claim_carries_unknown_exposure_without_unseen_claim(tmp_path: Path) -> None:
    result = evaluate(json.dumps(_response()).encode(), _audit(tmp_path), root=tmp_path)
    assert result["status"] == "metadata_hypotheses_only"
    assert result["claim"] == CLAIM
    assert result["historical_limitations"] == ["unenumerated_exposure"]
    assert len(result["hypotheses"]) == 2
    assert not any(result["authority"].values())
    assert "FICTIONAL title" not in json.dumps(result)


@pytest.mark.parametrize(
    "fault", ["count", "extra", "duplicate", "date", "host", "missing", "format"]
)
def test_current_response_failures_are_not_waived(tmp_path: Path, fault: str) -> None:
    payload = _response()
    if fault == "count":
        payload["total"] = 3
    elif fault == "extra":
        payload["results"][0]["unfrozen"] = True
    elif fault == "duplicate":
        payload["results"][1] = payload["results"][0]
    elif fault == "date":
        payload["results"][0]["public_timestamp"] = "2025-01-01"
    elif fault == "host":
        payload["results"][0]["link"] = "https://other.example/unsafe"
    elif fault == "missing":
        payload["results"][0].pop("link")
    else:
        payload["results"][0]["format"] = "unknown"
    result = evaluate(json.dumps(payload).encode(), _audit(tmp_path), root=tmp_path)
    assert result["status"] == "terminal_stop"
    assert result["hypotheses"] == []
    assert not any(result["authority"].values())


def test_known_locator_excluded_conservatively(tmp_path: Path) -> None:
    audit = _audit(tmp_path, extra={"url": "https://www.gov.uk/government/statistics/fictional-0"})
    result = evaluate(json.dumps(_response()).encode(), audit, root=tmp_path)
    assert result["hypotheses"] == []
    assert len(result["observations"]) == 2


def test_audit_mutation_rejected(tmp_path: Path) -> None:
    audit = _audit(tmp_path)
    audit["blockers"] = []
    with pytest.raises(HistoricalControlError, match="reproduce"):
        evaluate(json.dumps(_response()).encode(), audit, root=tmp_path)


@pytest.mark.parametrize("raw", [b"{}", b"{bad", b"x" * 2097153])
def test_invalid_or_over_budget_response(tmp_path: Path, raw: bytes) -> None:
    with pytest.raises(HistoricalControlError):
        evaluate(raw, _audit(tmp_path), root=tmp_path)


def test_rejects_arbitrary_bundle(tmp_path: Path) -> None:
    path = tmp_path / "bundle.json"
    path.write_text("{}")
    with pytest.raises(HistoricalControlError):
        verify_bundle(tmp_path, path)


@pytest.mark.parametrize(
    "failure",
    [
        None,
        "http",
        "content",
        "overflow",
        "socket",
        "list",
        "object",
        "null",
        "surrogate",
        "malformed",
        "timestamp_overflow",
    ],
)
def test_capture_is_one_shot_with_fake_transport(
    tmp_path: Path, monkeypatch, failure: str | None
) -> None:
    audit = _audit(tmp_path)
    audit_path = tmp_path / "audit.json"
    audit_path.write_text(json.dumps(audit))
    bundle_path = tmp_path / "bundle.json"
    bundle_path.write_text("{}")
    authority_path = tmp_path / "authority.json"
    authority_path.write_text(
        json.dumps(
            {
                "metadata_request_authorized": True,
                "bundle_sha256": hashlib.sha256(bundle_path.read_bytes()).hexdigest(),
            }
        )
    )
    monkeypatch.setattr(
        module,
        "verify_bundle",
        lambda *args: {
            "audit_path": "audit.json",
            "endpoint": "https://www.gov.uk/api/search.json?test=synthetic",
        },
    )
    calls = []
    monkeypatch.setattr(
        module.subprocess,
        "run",
        lambda args, **kwargs: SimpleNamespace(
            stdout=authority_path.read_bytes() if args[1] == "show" else b"", returncode=0
        ),
    )
    monkeypatch.setattr(module, "resolve_public_addresses", lambda host: ("93.184.216.34",))

    class Response:
        status = 302 if failure == "http" else 200

        def getheader(self, name, default):
            return "text/html" if failure == "content" else "application/json"

        def read(self, limit):
            payload = _response()
            if failure in {"list", "object", "null"}:
                payload["results"][0]["format"] = {"list": [], "object": {}, "null": None}[failure]
            if failure == "surrogate":
                payload["results"][0]["link"] = "\ud800"
            if failure == "timestamp_overflow":
                payload["results"][0]["public_timestamp"] = "0001-01-01T00:00:00+01:00"
            if failure == "malformed":
                return b"{bad"
            return b"x" * limit if failure == "overflow" else json.dumps(payload).encode()

    class Connection:
        def __init__(self, *args, **kwargs):
            pass

        def request(self, *args, **kwargs):
            calls.append(args)
            if failure == "socket":
                raise OSError("synthetic failure")

        def getresponse(self):
            return Response()

        def close(self):
            pass

    monkeypatch.setattr(module, "PeerBoundHTTPSConnection", Connection)
    result = module.capture(tmp_path, bundle_path, "authority.json", "a" * 40)
    assert len(calls) == 1
    assert result["status"] == ("terminal_stop" if failure else "metadata_hypotheses_only")
    if failure in {"list", "object", "null", "surrogate", "timestamp_overflow"}:
        assert len(result["observations"]) == 2
    if failure == "malformed":
        assert result["response_sha256"] == hashlib.sha256(b"{bad").hexdigest()
    assert (tmp_path / "data/methods/g2" / module.CAMPAIGN / "execution/receipt.json").is_file()
    assert (tmp_path / ".gfjd/g2-attempts" / (module.CAMPAIGN + ".json")).is_file()
    with pytest.raises((ValueError, FileExistsError)):
        module.capture(tmp_path, bundle_path, "authority.json", "a" * 40)
    assert len(calls) == 1


def test_capture_cannot_run_without_signed_authority(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(module, "verify_bundle", lambda *args: {})
    with pytest.raises(HistoricalControlError, match="immutable"):
        module.capture(tmp_path, tmp_path / "bundle.json", "authority.json", "not-a-commit")


def test_confined_attempt_and_output_reject_symlinks(tmp_path: Path) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    (tmp_path / ".gfjd").symlink_to(outside, target_is_directory=True)
    with pytest.raises(HistoricalControlError, match="symlink"):
        module._confined(tmp_path, ".gfjd/g2-attempts/campaign.json")


def test_repository_metadata_bundle_verifies_without_network() -> None:
    root = Path(__file__).resolve().parents[1]
    bundle = verify_bundle(root, root / "data/methods/g2-repro/metadata-bundle-2026-08-30.json")
    assert bundle["network_authorized"] is False
    assert bundle["claim"] == CLAIM
