"""Build the source-disabled G2 metadata-search successor query manifest."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DESIGN = ROOT / "data/methods/g2/G2HOLDOUT-METADATA-EXPANSION-20260816-02/design"
PREDECESSOR = (
    ROOT / "data/methods/g2/G2HOLDOUT-METADATA-EXPANSION-20260815-01/design/"
    "search-index-query-manifest.json"
)
REPLACEMENTS = (
    "Federal Circuit and Family Court performance statistics 2024-25 "
    "site:fcfcoa.gov.au text native PDF",
    "Australian federal family law annual report 2024 site:fcfcoa.gov.au text native PDF",
    "Australian family court filings statistics 2024 site:fcfcoa.gov.au text native PDF",
    "FCFCOA annual report family law caseload 2024 site:fcfcoa.gov.au text native PDF",
)


def _read(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict[str, Any]:
    predecessor = _read(PREDECESSOR)
    old_rows = predecessor["queries"]
    denied_texts = {row["query_text"] for row in old_rows[:4]}
    if denied_texts & set(REPLACEMENTS):
        raise ValueError("replacement query repeats a contaminated query")
    rows: list[dict[str, Any]] = []
    for index, old in enumerate(old_rows, start=1):
        replacement = index <= 4
        query_text = REPLACEMENTS[index - 1] if replacement else old["query_text"]
        rows.append(
            {
                "query_order": index,
                "query_id": f"G2S2Q-{index:03d}",
                "origin": "prospective_replacement" if replacement else "retained_unsubmitted",
                "replaces_or_retains_query_id": old["query_id"],
                "stream_id": old["stream_id"],
                "jurisdiction_id": old["jurisdiction_id"],
                "language": old["language"],
                "official_domain": old["official_domain"],
                "year": 2024 if replacement else old["year"],
                "template_id": f"S2R{index}" if replacement else old["template_id"],
                "query_text": query_text,
                "query_sha256": hashlib.sha256(query_text.encode()).hexdigest(),
            }
        )
    if len(rows) != 208 or len({row["query_text"] for row in rows}) != 208:
        raise ValueError("successor must contain exactly 208 unique logical queries")
    if sum(row["origin"] == "prospective_replacement" for row in rows) != 4:
        raise ValueError("successor must contain exactly four replacements")
    plan_path = DESIGN / "successor-plan.json"
    return {
        "schema_version": "1.0",
        "manifest_id": "G2HOLDOUT-METADATA-SEARCH-SUCCESSOR-QUERIES-20260816-02",
        "status": "prepared_not_authorized",
        "plan": {
            "path": plan_path.relative_to(ROOT).as_posix(),
            "sha256": _sha(plan_path),
        },
        "failed_predecessor_manifest": {
            "path": PREDECESSOR.relative_to(ROOT).as_posix(),
            "sha256": _sha(PREDECESSOR),
        },
        "provider_config": {
            "tool": "web__run.search_query",
            "response_length": "short",
            "logical_queries_per_call": 1,
            "recorded_results_per_query_maximum": 5,
            "pagination": False,
            "recency_filter": None,
            "domain_filter": None,
            "execution_date": None,
            "timezone": "Australia/Sydney",
            "indexing_basis": "provider index state at truthful execution date",
        },
        "query_count": 208,
        "provider_call_count": 208,
        "retry_count": 0,
        "prior_lineage_submission_count": 4,
        "cumulative_lineage_submission_count_after_execution": 212,
        "denied_prior_query_ids": ["G2Q-001", "G2Q-002", "G2Q-003", "G2Q-004"],
        "prior_aggregate_exposure_reconstruction_complete": False,
        "unknown_prior_urls_captured": False,
        "queries": rows,
        "authorization_flags": {
            "search_index_execution_authorized": False,
            "result_url_access_authorized": False,
            "landing_page_access_authorized": False,
            "source_file_access_authorized": False,
        },
    }


def main() -> int:
    output = DESIGN / "successor-query-manifest.json"
    output.write_text(json.dumps(build(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
