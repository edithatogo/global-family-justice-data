"""Prospective metadata-only preparation for exposure-uncertain reproducibility.

No source access is implemented. Capture requires a separately signed owner
authorization binding the exact bundle, and permanently consumes one attempt.
"""

from __future__ import annotations

import argparse
import hashlib
import http.client
import json
import re
import subprocess
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from .g2_future_exposure import canonical_url
from .g2_historical_controls import (
    AUTHORITY,
    LOWER,
    UPPER,
    HistoricalControlError,
    _load,
    _timestamp,
    verify_audit,
    write_once,
)
from .g2_successor_transport import PeerBoundHTTPSConnection, bounded_read, resolve_public_addresses

CAMPAIGN = "G2HISTORICAL-REPRO-METADATA-20260830-01"
CLAIM = "bounded_reproducibility_exposure_uncertain_not_project_unseen"
AUDIT_PATH = "data/methods/g2-audits/historical-persisted-exposure-2026-08-30.json"
PROPOSAL_PATH = "data/methods/g2/G2HISTORICAL-PROPOSAL-20260830-01/design/proposal.json"
POLICY_PATH = "docs/governance/g2-historical-repro-policy-owner-decision-2026-08-30.md"
REQUIRED_BINDINGS = frozenset(
    {
        AUDIT_PATH,
        PROPOSAL_PATH,
        POLICY_PATH,
        "src/gfjd/g2_historical_repro.py",
        "src/gfjd/g2_historical_controls.py",
        "src/gfjd/g2_future_exposure.py",
        "src/gfjd/g2_successor_transport.py",
        "src/gfjd/g2_successor_controls.py",
        "tests/test_g2_historical_repro.py",
        "docs/methods/g2-historical-repro-metadata-contract-2026-08-30.md",
    }
)
LIMITS = {
    "requests": 1,
    "retries": 0,
    "redirects": 0,
    "pagination": False,
    "response_bytes": 2097152,
    "results": 100,
    "timeout_seconds": 120,
}
LIMITATIONS = frozenset(
    {
        "unenumerated_exposure",
        "incomplete_passive_exposure_reconstruction",
        "incomplete_manifest_enumeration",
    }
)


def evaluate(raw: bytes, audit: dict[str, Any], *, root: Path) -> dict[str, Any]:
    """Evaluate fresh metadata under the new claim; never ingest a failed receipt."""
    if verify_audit(root, audit):
        raise HistoricalControlError("exposure audit does not reproduce")
    if len(raw) > 2097152:
        raise HistoricalControlError("response byte budget exceeded")
    payload = _load(raw)
    if not isinstance(payload, dict) or not isinstance(payload.get("results"), list):
        raise HistoricalControlError("invalid current response; exposure incomplete")
    rows = payload["results"]
    stops = set(audit["blockers"]) - LIMITATIONS
    if (
        set(payload) - {"results", "total", "start"}
        or type(payload.get("total")) is not int
        or payload["total"] != len(rows)
        or len(rows) > 100
        or type(payload.get("start", 0)) is not int
        or payload.get("start", 0) != 0
    ):
        stops.add("current_enumeration_contract_failed")
    observed: list[dict[str, Any]] = []
    candidates: list[dict[str, str]] = []
    seen: set[str] = set()
    denied = set(audit["identity_sha256"]["urls"])
    for ordinal, row in enumerate(rows, 1):
        if not isinstance(row, dict) or not isinstance(row.get("link"), str):
            stops.add("current_locator_missing")
            continue
        link = row["link"]
        # Unexpected locator text is hash-recorded, never blindly published.
        observation: dict[str, Any] = {
            "ordinal": ordinal,
            "requested": False,
            "locator_sha256": hashlib.sha256(link.encode("utf-8", "surrogatepass")).hexdigest(),
        }
        observed.append(observation)
        if not re.fullmatch(r"/government/statistics/[a-z0-9][a-z0-9-]*", link):
            stops.add("unexpected_locator")
            continue
        url = canonical_url("https://www.gov.uk" + link)
        observation["url"] = url
        if url in seen:
            stops.add("duplicate_locator")
        seen.add(url)
        if (
            set(row) != {"link", "public_timestamp", "format", "title"}
            or not isinstance(row.get("format"), str)
            or row.get("format") not in {"official_statistics", "national_statistics"}
            or not isinstance(row.get("title"), str)
            or not row["title"]
        ):
            stops.add("result_schema_failed")
            continue
        try:
            timestamp = _timestamp(row.get("public_timestamp"))
        except (ValueError, OverflowError):
            stops.add("ambiguous_timestamp")
            continue
        if LOWER <= timestamp < UPPER and hashlib.sha256(url.encode()).hexdigest() not in denied:
            candidates.append(
                {
                    "url": url,
                    "public_timestamp": timestamp.isoformat(),
                    "exposure_status": "uncertain_not_project_unseen",
                }
            )
    if len(candidates) < 2:
        stops.add("fewer_than_two_hypotheses")
    candidates.sort(key=lambda item: (item["public_timestamp"], item["url"]))
    return {
        "schema_version": "1.0",
        "campaign_id": CAMPAIGN,
        "claim": CLAIM,
        "response_sha256": hashlib.sha256(raw).hexdigest(),
        "historical_limitations": sorted(set(audit["blockers"]) & LIMITATIONS),
        "status": "terminal_stop" if stops else "metadata_hypotheses_only",
        "observations": observed,
        "stop_reasons": sorted(stops),
        "hypotheses": [] if stops else candidates[:4],
        "authority": dict(AUTHORITY),
    }


def _confined(root: Path, relative: str) -> Path:
    if (
        not isinstance(relative, str)
        or Path(relative).is_absolute()
        or ".." in Path(relative).parts
    ):
        raise HistoricalControlError("unsafe binding path")
    path = root
    for part in Path(relative).parts:
        path /= part
        if path.is_symlink():
            raise HistoricalControlError("symlink binding")
    return path


def verify_bundle(root: Path, bundle_path: Path) -> dict[str, Any]:
    bundle = _load(bundle_path.read_bytes())
    if not isinstance(bundle, dict) or bundle.get("campaign_id") != CAMPAIGN:
        raise HistoricalControlError("unexpected metadata campaign")
    if bundle.get("claim") != CLAIM or bundle.get("network_authorized") is not False:
        raise HistoricalControlError("invalid claim or implicit authorization")
    if bundle.get("limits") != LIMITS or bundle.get("audit_path") != AUDIT_PATH:
        raise HistoricalControlError("changed limits or inventory")
    bindings = bundle.get("bindings")
    if not isinstance(bindings, list) or not all(isinstance(item, dict) for item in bindings):
        raise HistoricalControlError("missing bindings")
    paths = [item.get("path") for item in bindings]
    if not all(isinstance(path, str) for path in paths) or set(paths) != REQUIRED_BINDINGS:
        raise HistoricalControlError("incomplete binding set")
    if len(paths) != len(set(paths)):
        raise HistoricalControlError("duplicate binding")
    for descriptor in bundle["bindings"]:
        path = _confined(root, descriptor["path"])
        if hashlib.sha256(path.read_bytes()).hexdigest() != descriptor["sha256"]:
            raise HistoricalControlError("bundle binding mismatch")
    audit = _load(_confined(root, bundle["audit_path"]).read_bytes())
    if verify_audit(root, audit):
        raise HistoricalControlError("stale exposure audit")
    proposal = _load(_confined(root, PROPOSAL_PATH).read_bytes())
    if bundle.get("endpoint") != proposal["metadata_request_proposal"]["endpoint"]:
        raise HistoricalControlError("changed exact endpoint")
    return bundle


def capture(
    root: Path, bundle_path: Path, authority_path: str, authority_commit: str
) -> dict[str, Any]:
    """One separately authorized official metadata request; never follows results."""
    bundle = verify_bundle(root, bundle_path)
    if not re.fullmatch(r"[0-9a-f]{40}", authority_commit):
        raise HistoricalControlError("immutable authority commit required")
    authority_bytes = _confined(root, authority_path).read_bytes()
    subprocess.run(
        ["git", "verify-commit", authority_commit], cwd=root, check=True, capture_output=True
    )
    committed = subprocess.run(
        ["git", "show", f"{authority_commit}:{authority_path}"],
        cwd=root,
        check=True,
        capture_output=True,
    ).stdout
    authority = _load(authority_bytes)
    if not isinstance(authority, dict):
        raise HistoricalControlError("invalid owner authorization")
    if (
        committed != authority_bytes
        or authority.get("metadata_request_authorized") is not True
        or authority.get("bundle_sha256") != hashlib.sha256(bundle_path.read_bytes()).hexdigest()
    ):
        raise HistoricalControlError("exact signed metadata authority missing")
    audit = _load(_confined(root, bundle["audit_path"]).read_bytes())
    output = _confined(root, "data/methods/g2/" + CAMPAIGN + "/execution")
    marker = _confined(root, ".gfjd/g2-attempts/" + CAMPAIGN + ".json")
    if marker.exists():
        raise HistoricalControlError("campaign attempt already consumed")
    marker.parent.mkdir(parents=True, exist_ok=True)
    output.mkdir(parents=True, exist_ok=False)
    connection = None
    requests_attempted = 0
    raw = None
    try:
        write_once(
            marker,
            {
                "campaign_id": CAMPAIGN,
                "authority_commit": authority_commit,
                "bundle_sha256": authority["bundle_sha256"],
            },
        )
        parsed = urlsplit(bundle["endpoint"])
        if (
            parsed.scheme != "https"
            or parsed.netloc != "www.gov.uk"
            or parsed.path != "/api/search.json"
        ):
            raise HistoricalControlError("unexpected metadata endpoint")
        connection = PeerBoundHTTPSConnection(
            "www.gov.uk", timeout=120, validated_addresses=resolve_public_addresses("www.gov.uk")
        )
        requests_attempted = 1
        connection.request(
            "GET",
            parsed.path + "?" + parsed.query,
            headers={"Accept": "application/json", "User-Agent": "GFJD-metadata/1.0"},
        )
        response = connection.getresponse()
        if (
            response.status != 200
            or response.getheader("Content-Type", "").split(";")[0] != "application/json"
        ):
            raise HistoricalControlError("metadata HTTP contract failed")
        raw = bounded_read(response, maximum_bytes=2097152)
        result = evaluate(raw, audit, root=root)
        result["request"] = {
            "method": "GET",
            "url": bundle["endpoint"],
            "response_bytes": len(raw),
            "requests": 1,
            "authority_commit": authority_commit,
            "bundle_sha256": authority["bundle_sha256"],
        }
    except (OSError, ValueError, http.client.HTTPException) as error:
        result = {
            "campaign_id": CAMPAIGN,
            "status": "terminal_stop",
            "error_type": type(error).__name__,
            "exposure_complete": False,
            "authority": dict(AUTHORITY),
        }
        if raw is not None:
            result["response_sha256"] = hashlib.sha256(raw).hexdigest()
            result["response_bytes"] = len(raw)
    finally:
        if connection is not None:
            connection.close()
    result["request_attempt"] = {
        "url": bundle["endpoint"],
        "count": requests_attempted,
        "authority_commit": authority_commit,
        "bundle_sha256": authority["bundle_sha256"],
    }
    write_once(output / "receipt.json", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--authority-path")
    parser.add_argument("--authority-commit")
    args = parser.parse_args()
    if bool(args.authority_path) != bool(args.authority_commit):
        parser.error("both exact authority fields are required")
    if args.authority_path:
        result = capture(Path.cwd(), args.bundle, args.authority_path, args.authority_commit)
        print(json.dumps(result, sort_keys=True))
        return 0 if result["status"] == "metadata_hypotheses_only" else 2
    verify_bundle(Path.cwd(), args.bundle)
    print("Metadata bundle bindings verify; no network access authorized or performed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
