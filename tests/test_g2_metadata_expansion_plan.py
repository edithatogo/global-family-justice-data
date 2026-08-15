from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

DESIGN_ROOT = Path("data/methods/g2/G2HOLDOUT-METADATA-EXPANSION-20260815-01/design")


def _read(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_metadata_expansion_plan_is_schema_valid_and_fail_closed(
    project_root: Path,
) -> None:
    plan = _read(project_root / DESIGN_ROOT / "metadata-expansion-plan.json")
    schema = _read(project_root / DESIGN_ROOT / "metadata-expansion-plan.schema.json")
    errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(plan))
    assert errors == []
    assert plan["frame_contract"] == {
        "adaptive_replenishment": False,
        "baseline_records": 44,
        "final_records": 96,
        "new_records": 52,
        "preserve_baseline_verbatim": True,
        "silent_shrink": False,
        "source_content_access": False,
    }
    assert sum(stream["required_new_records"] for stream in plan["search_streams"]) == 52
    assert len({stream["stream_id"] for stream in plan["search_streams"]}) == 4
    assert [query["query_id"] for query in plan["query_templates"]] == [
        "Q1",
        "Q2",
        "Q3",
        "Q4",
    ]
    assert plan["budgets"]["maximum_total_gets"] == (
        plan["budgets"]["maximum_search_queries"] + plan["budgets"]["maximum_official_html_gets"]
    )
    assert plan["recording_policy"]["persist_search_snippets"] is False
    assert plan["recording_policy"]["persist_source_excerpts"] is False
    assert plan["recording_policy"]["persist_target_facts"] is False
    registry = _read(project_root / plan["query_registry"]["path"])
    queries = []
    templates = plan["query_templates"]
    years = plan["year_order"]
    for stream_index, stream in enumerate(plan["search_streams"]):
        for jurisdiction_index, jurisdiction_id in enumerate(stream["jurisdiction_order"]):
            values = registry["entries"][jurisdiction_id]
            year = years[(stream_index * 13 + jurisdiction_index) % 4]
            for template in templates:
                queries.append(template["template"].format(year=year, **values))
    assert len(queries) == 208
    assert all("{" not in query and "}" not in query for query in queries)
    flags = plan["authorization_flags"]
    assert flags["metadata_expansion_prepared"] is True
    assert all(
        value is False for key, value in flags.items() if key != "metadata_expansion_prepared"
    )


def test_metadata_expansion_predecessor_bindings(project_root: Path) -> None:
    plan = _read(project_root / DESIGN_ROOT / "metadata-expansion-plan.json")
    for descriptor in (
        plan["baseline_frame"],
        plan["url_resolution_manifest"],
        plan["query_registry"],
    ):
        assert _sha(project_root / descriptor["path"]) == descriptor["sha256"]


def test_metadata_expansion_schema_rejects_safety_mutations(project_root: Path) -> None:
    plan = _read(project_root / DESIGN_ROOT / "metadata-expansion-plan.json")
    schema = _read(project_root / DESIGN_ROOT / "metadata-expansion-plan.schema.json")
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    mutations = []
    direct_open = deepcopy(plan)
    direct_open["search_index_stage"]["direct_url_open_allowed"] = True
    mutations.append(direct_open)
    snippets = deepcopy(plan)
    snippets["recording_policy"]["persist_search_snippets"] = True
    mutations.append(snippets)
    source_access = deepcopy(plan)
    source_access["frame_contract"]["source_content_access"] = True
    mutations.append(source_access)
    arbitrary_stop = deepcopy(plan)
    arbitrary_stop["stopping_rules"] = ["continue"]
    mutations.append(arbitrary_stop)
    role_overlap = deepcopy(plan)
    role_overlap["roles"][0]["may_be_extractor_or_comparator"] = True
    mutations.append(role_overlap)
    for mutation in mutations:
        assert list(validator.iter_errors(mutation))


def test_metadata_expansion_design_manifest_is_exact(project_root: Path) -> None:
    manifest_path = project_root / DESIGN_ROOT / "EXPANSION_DESIGN_MANIFEST.sha256"
    entries = [line.split("  ", 1) for line in manifest_path.read_text().splitlines()]
    assert [path for _, path in entries] == sorted(
        [
            f"{DESIGN_ROOT.as_posix()}/metadata-expansion-plan.json",
            f"{DESIGN_ROOT.as_posix()}/metadata-expansion-plan.schema.json",
            f"{DESIGN_ROOT.as_posix()}/jurisdiction-query-registry.json",
            "tests/test_g2_metadata_expansion_plan.py",
        ]
    )
    for expected_sha, relative_path in entries:
        assert _sha(project_root / relative_path) == expected_sha
