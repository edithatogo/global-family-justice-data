from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path

from gfjd.g2_metadata_search import verify_search_index_bundle


def _canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def _bundle(root: Path) -> dict[str, object]:
    relative = Path(
        "data/methods/g2/G2HOLDOUT-METADATA-EXPANSION-20260815-01/"
        "design/search-index-query-manifest.json"
    )
    path = root / relative
    manifest = json.loads(path.read_text())
    events = []
    for query in manifest["queries"]:
        results: list[object] = []
        events.append(
            {
                "query_order": query["query_order"],
                "query_id": query["query_id"],
                "query_text": query["query_text"],
                "language": query["language"],
                "searched_on": "2026-08-15",
                "result_count": 0,
                "results": results,
                "query_sha256": hashlib.sha256(query["query_text"].encode()).hexdigest(),
                "result_sha256": hashlib.sha256(_canonical(results)).hexdigest(),
                "access_issue": None,
            }
        )
    return {
        "schema_version": "1.0",
        "bundle_id": "G2-SEARCH-TEST",
        "query_manifest": {
            "path": relative.as_posix(),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        },
        "tool_name": "web__run.search_query",
        "tool_version": "test",
        "provider_config": manifest["provider_config"],
        "query_events": events,
        "candidate_hypotheses": [],
        "exposure_events": [],
        "proposed_official_html_allowlist": [],
        "violations": [],
        "result_url_requests": 0,
        "landing_page_requests": 0,
        "source_file_requests": 0,
    }


def test_search_index_bundle_verifies(project_root: Path) -> None:
    assert verify_search_index_bundle(project_root, _bundle(project_root)) == []


def test_search_index_bundle_rejects_mutations(project_root: Path) -> None:
    valid = _bundle(project_root)
    mutations = []
    wrong_query = deepcopy(valid)
    wrong_query["query_events"][0]["query_text"] = "changed"
    mutations.append(wrong_query)
    opened = deepcopy(valid)
    opened["result_url_requests"] = 1
    mutations.append(opened)
    config = deepcopy(valid)
    config["provider_config"]["pagination"] = True
    mutations.append(config)
    missing = deepcopy(valid)
    missing["query_events"].pop()
    mutations.append(missing)
    for mutation in mutations:
        assert verify_search_index_bundle(project_root, mutation)
