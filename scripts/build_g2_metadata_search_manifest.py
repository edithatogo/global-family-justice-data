"""Materialize the exact source-disabled G2 metadata search-index query set."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DESIGN = ROOT / "data/methods/g2/G2HOLDOUT-METADATA-EXPANSION-20260815-01/design"
LANGUAGE = {
    "AUS": "en",
    "BRA": "pt",
    "CAN": "en",
    "CAN-BC": "en",
    "CAN-ON": "en",
    "CHL": "es",
    "DNK": "da",
    "ESP": "es",
    "FRA": "fr",
    "GBR": "en",
    "GBR-EAW": "en",
    "IND": "en",
    "IRL": "en",
    "ITA": "it",
    "JPN": "ja",
    "KEN": "en",
    "KOR": "ko",
    "MEX": "es",
    "NLD": "nl",
    "NOR": "no",
    "NZL": "en",
    "PER": "es",
    "PHL": "en",
    "POL": "pl",
    "SGP": "en",
    "SWE": "sv",
    "USA": "en",
    "USA-CA": "en",
    "USA-MN": "en",
    "USA-NY": "en",
    "USA-WA": "en",
    "ZAF": "en",
}
HINT = {
    "english_text_native": "text native PDF",
    "non_english_text_native": "statistical yearbook PDF",
    "embedded_raster_or_dashboard_pdf": "infographic dashboard PDF",
    "structurally_complex_mixed_layout_pdf": "annex tables mixed layout PDF",
}


def _read(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(path)
    return value


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    plan_path = DESIGN / "metadata-expansion-plan.json"
    registry_path = DESIGN / "jurisdiction-query-registry.json"
    plan = _read(plan_path)
    registry = _read(registry_path)["entries"]
    rows = []
    order = 0
    years = plan["year_order"]
    for stream_index, stream in enumerate(plan["search_streams"]):
        for jurisdiction_index, jurisdiction_id in enumerate(stream["jurisdiction_order"]):
            values = registry[jurisdiction_id]
            year = years[(stream_index * 13 + jurisdiction_index) % 4]
            for template in plan["query_templates"]:
                order += 1
                base = template["template"].format(year=year, **values)
                if f"site:{values['official_domain']}" not in base:
                    base = f"{base} site:{values['official_domain']}"
                query_text = " ".join(f"{base} {HINT[stream['stream_id']]}".split())
                rows.append(
                    {
                        "query_order": order,
                        "query_id": f"G2Q-{order:03d}",
                        "stream_id": stream["stream_id"],
                        "jurisdiction_id": jurisdiction_id,
                        "language": LANGUAGE[jurisdiction_id],
                        "official_domain": values["official_domain"],
                        "year": year,
                        "template_id": template["query_id"],
                        "query_text": query_text,
                    }
                )
    if len(rows) != 208 or len({row["query_text"] for row in rows}) != 208:
        raise ValueError("query manifest must contain 208 unique materialized queries")
    payload = {
        "schema_version": "1.0",
        "manifest_id": "G2HOLDOUT-METADATA-SEARCH-QUERIES-20260815-01",
        "plan": {"path": plan_path.relative_to(ROOT).as_posix(), "sha256": _sha(plan_path)},
        "registry": {
            "path": registry_path.relative_to(ROOT).as_posix(),
            "sha256": _sha(registry_path),
        },
        "provider_config": {
            "tool": "web__run.search_query",
            "response_length": "short",
            "queries_per_call_maximum": 4,
            "recorded_results_per_query_maximum": 5,
            "pagination": False,
            "recency_filter": None,
            "domain_filter": None,
            "execution_date": "2026-08-15",
            "timezone": "Australia/Sydney",
            "indexing_basis": "provider index state at execution time",
        },
        "query_count": 208,
        "queries": rows,
        "authorization_flags": {
            "search_index_execution_authorized": False,
            "result_url_access_authorized": False,
            "landing_page_access_authorized": False,
            "source_file_access_authorized": False,
        },
    }
    output = DESIGN / "search-index-query-manifest.json"
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
