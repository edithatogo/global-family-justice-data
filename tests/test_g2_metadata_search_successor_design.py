from __future__ import annotations

import hashlib
import importlib.util
import json
from copy import deepcopy
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

DESIGN = Path("data/methods/g2/G2HOLDOUT-METADATA-EXPANSION-20260816-02/design")


def _read(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _build(project_root: Path) -> dict[str, object]:
    script = project_root / "scripts/build_g2_metadata_search_successor_manifest.py"
    spec = importlib.util.spec_from_file_location("g2_successor_builder", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build()


def test_successor_plan_and_manifest_are_schema_valid(project_root: Path) -> None:
    for payload_name, schema_name in (
        ("successor-plan.json", "successor-plan.schema.json"),
        ("successor-query-manifest.json", "successor-query-manifest.schema.json"),
    ):
        payload = _read(project_root / DESIGN / payload_name)
        schema = _read(project_root / DESIGN / schema_name)
        errors = list(
            Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(payload)
        )
        assert errors == []
    for schema_name in (
        "successor-execution-bundle.schema.json",
        "successor-authority-receipt.schema.json",
        "successor-owner-decision.schema.json",
    ):
        Draft202012Validator.check_schema(_read(project_root / DESIGN / schema_name))


def test_successor_manifest_is_reproducible_and_original_is_immutable(
    project_root: Path,
) -> None:
    recorded = _read(project_root / DESIGN / "successor-query-manifest.json")
    assert _build(project_root) == recorded
    assert (
        _sha(
            project_root / "data/methods/g2/G2HOLDOUT-METADATA-EXPANSION-20260815-01/design/"
            "search-index-query-manifest.json"
        )
        == "d7419c0bc281ac9e940819d01005a922e2e6612e40ab1b573ba941eee3b8dddc"
    )


def test_successor_has_208_isolated_calls_and_four_distinct_replacements(
    project_root: Path,
) -> None:
    successor = _read(project_root / DESIGN / "successor-query-manifest.json")
    failed = _read(
        project_root / "data/methods/g2/G2HOLDOUT-METADATA-EXPANSION-20260815-01/design/"
        "search-index-query-manifest.json"
    )
    assert successor["query_count"] == successor["provider_call_count"] == 208
    assert successor["retry_count"] == 0
    assert successor["cumulative_lineage_submission_count_after_execution"] == 212
    rows = successor["queries"]
    assert sum(row["origin"] == "prospective_replacement" for row in rows) == 4
    assert {row["query_text"] for row in rows[:4]}.isdisjoint(
        {row["query_text"] for row in failed["queries"][:4]}
    )
    assert [row["query_text"] for row in rows[4:]] == [
        row["query_text"] for row in failed["queries"][4:]
    ]


def test_successor_plan_schema_rejects_authority_and_exposure_mutations(
    project_root: Path,
) -> None:
    plan = _read(project_root / DESIGN / "successor-plan.json")
    schema = _read(project_root / DESIGN / "successor-plan.schema.json")
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    mutations = []
    authorized = deepcopy(plan)
    authorized["authorization_flags"]["search_index_execution_authorized"] = True
    mutations.append(authorized)
    reconstructed = deepcopy(plan)
    reconstructed["contamination_control"]["prior_passive_url_reconstruction_complete"] = True
    mutations.append(reconstructed)
    resubmit = deepcopy(plan)
    resubmit["contamination_control"]["prior_queries_may_be_resubmitted"] = True
    mutations.append(resubmit)
    batched = deepcopy(plan)
    batched["query_contract"]["queries_per_provider_call"] = 4
    mutations.append(batched)
    for mutation in mutations:
        assert list(validator.iter_errors(mutation))


def test_successor_detached_design_manifest_is_exact(project_root: Path) -> None:
    manifest = project_root / DESIGN / "SUCCESSOR_DESIGN_MANIFEST.sha256"
    entries = [line.split("  ", 1) for line in manifest.read_text().splitlines()]
    paths = [path for _, path in entries]
    assert paths == sorted(paths)
    assert len(paths) == 19
    assert manifest.relative_to(project_root).as_posix() not in paths
    for expected_sha, relative_path in entries:
        assert _sha(project_root / relative_path) == expected_sha
