"""Build the source-disabled G2 overlap-successor preparation bundle."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from gfjd.g2_exposure_chain import collect_bound_exposure_chain
from gfjd.g2_metadata_search_successor import canonical_url

ROOT = Path(__file__).resolve().parents[1]
LINEAGE = "G2HOLDOUT-METADATA-EXPANSION-20260816-03"
DESIGN = ROOT / "data/methods/g2" / LINEAGE / "design"
PREVIOUS = ROOT / "data/methods/g2/G2HOLDOUT-METADATA-EXPANSION-20260816-02"
PREVIOUS_QUERY = PREVIOUS / "design/successor-query-manifest.json"
EXECUTION = PREVIOUS / "registrar/execution-bundle.json"
PREDECESSOR_LEDGER = ROOT / (
    "data/methods/g2/G2HOLDOUT-STRUCTURAL-PREFLIGHT-20260815-01/url-resolution/exposure-ledger.json"
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _descriptor(path: Path) -> dict[str, str]:
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": _sha(path)}


def _read(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def build() -> dict[str, dict[str, Any]]:
    previous_manifest = _read(PREVIOUS_QUERY)
    execution = _read(EXECUTION)
    observed = {
        canonical_url(result["url"])
        for event in execution["query_events"]
        for result in event["results"]
    }
    if len(observed) != 609:
        raise ValueError(f"expected 609 observed URLs, got {len(observed)}")
    predecessor = _descriptor(PREDECESSOR_LEDGER)
    prior_urls, prior_ledgers, errors = collect_bound_exposure_chain(ROOT, predecessor)
    if errors:
        raise ValueError("; ".join(errors))

    ledger = {
        "schema_version": "1.0",
        "ledger_id": f"{LINEAGE}-CUMULATIVE-EXPOSURE",
        "status": "prepared_not_authorized",
        "predecessor": predecessor,
        "predecessor_chain": prior_ledgers,
        "predecessor_url_count": len(prior_urls),
        "current_observed_url_count": len(observed),
        "cumulative_denied_url_count": len(prior_urls | observed),
        "denied_urls": sorted(observed),
        "complete_chain_required": True,
        "network_access_authorized": False,
    }

    rows = []
    for old in previous_manifest["queries"]:
        row = dict(old)
        row["query_id"] = old["query_id"].replace("G2S2Q-", "G2S3Q-")
        row["origin"] = "prospectively_refrozen_definition"
        row["replaces_or_retains_query_id"] = old["query_id"]
        rows.append(row)
    query_manifest = {
        "schema_version": "1.0",
        "manifest_id": f"{LINEAGE}-QUERIES",
        "status": "prepared_not_authorized",
        "predecessor_query_manifest": _descriptor(PREVIOUS_QUERY),
        "query_count": 208,
        "provider_call_count": 208,
        "queries_per_provider_call": 1,
        "retry_count": 0,
        "provider_config": previous_manifest["provider_config"],
        "queries": rows,
        "authorization_flags": {
            "search_index_execution_authorized": False,
            "result_url_access_authorized": False,
            "landing_page_access_authorized": False,
            "source_file_access_authorized": False,
        },
    }
    if len(rows) != 208 or len({row["query_text"] for row in rows}) != 208:
        raise ValueError("successor query scope must contain 208 unique definitions")

    plan = {
        "schema_version": "1.0",
        "plan_id": LINEAGE,
        "status": "prepared_not_authorized",
        "purpose": "Prospective metadata-only successor after cumulative exposure stop.",
        "owner_decision": {
            "path": "docs/governance/g2-successor-overlap-stop-owner-decision-2026-08-16.md",
            "sha256": _sha(
                ROOT / "docs/governance/g2-successor-overlap-stop-owner-decision-2026-08-16.md"
            ),
        },
        "failed_predecessor_execution": _descriptor(EXECUTION),
        "exact_scope": {
            "logical_queries": 208,
            "provider_calls": 208,
            "queries_per_call": 1,
            "retries": 0,
            "result_records_maximum_per_query": 5,
        },
        "exposure_contract": {
            "all_609_current_urls_denied": True,
            "complete_predecessor_chain_required": True,
            "chain_maximum_depth": 32,
            "malformed_or_unbound_ledger_stops": True,
            "any_observed_overlap_stops": True,
            "no_current_result_may_be_promoted": True,
        },
        "access_boundary": {
            "passive_search_metadata_only": True,
            "persist_snippets": False,
            "result_url_requests": 0,
            "landing_page_requests": 0,
            "source_file_requests": 0,
            "head_requests": 0,
            "outbound_contacts": 0,
        },
        "roles": [
            "fresh_metadata_registrar",
            "network_disabled_exposure_auditor",
            "network_disabled_advisory_panel",
        ],
        "stopping_rules": [
            "any query scope order digest or authority mismatch",
            "any retry or more than one query per provider call",
            "any result URL landing page file HEAD redirect source or contact request",
            "any persisted snippet source excerpt or target fact",
            "any malformed unbound cyclic or incomplete exposure chain",
            "any passive result overlapping the complete cumulative denylist",
        ],
        "resource_estimate": {
            "maximum_provider_calls": 208,
            "maximum_persisted_result_records": 1040,
            "minimum_role_sessions": 3,
            "expected_wall_clock_minutes": 90,
        },
        "next_owner_checkpoint": {
            "signed_freeze_commit_required": True,
            "exact_design_manifest_required": True,
            "separate_digest_bound_execution_decision_required": True,
        },
        "authorization_flags": {
            "design_preparation_authorized": True,
            "network_access_authorized": False,
            "source_access_authorized": False,
            "extraction_authorized": False,
            "contact_authorized": False,
            "publication_authorized": False,
            "release_authorized": False,
            "g2_passage_authorized": False,
        },
    }
    return {"plan": plan, "ledger": ledger, "query_manifest": query_manifest}


def main() -> int:
    DESIGN.mkdir(parents=True, exist_ok=True)
    artifacts = build()
    for name, value in artifacts.items():
        path = DESIGN / f"{name.replace('_', '-')}.json"
        path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
