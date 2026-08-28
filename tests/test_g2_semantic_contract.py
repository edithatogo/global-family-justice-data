from __future__ import annotations

import copy
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from gfjd.g2_semantic_contract import (
    find_prohibited_semantic_leakage,
    validate_prospective_semantic_bundle,
    validate_prospective_semantic_contract,
)

SCHEMA_PATH = Path(
    "data/methods/g2/G2PROSPECTIVE-SEMANTIC-CONTRACT-20260827-01/semantic-contract.schema.json"
)


def _contract(project_root: Path) -> dict[str, object]:
    return json.loads(
        (project_root / "config/g2_prospective_semantic_contract.json").read_text(encoding="utf-8")
    )


def test_prospective_contract_is_schema_valid_and_fail_closed(project_root: Path) -> None:
    contract = _contract(project_root)
    schema = json.loads((project_root / SCHEMA_PATH).read_text(encoding="utf-8"))
    assert validate_prospective_semantic_bundle(contract, schema) == []


def test_contract_rejects_open_codes_weakened_thresholds_and_authority(
    project_root: Path,
) -> None:
    baseline = _contract(project_root)
    cases: list[dict[str, object]] = []
    missing_unknown = copy.deepcopy(baseline)
    missing_unknown["codebooks"]["domain_code"].remove("unknown")  # type: ignore[index]
    cases.append(missing_unknown)
    weakened = copy.deepcopy(baseline)
    weakened["comparison_policy"]["critical_concordance"] = 0.99  # type: ignore[index]
    cases.append(weakened)
    authorized = copy.deepcopy(baseline)
    authorized["execution_authorized"] = True
    cases.append(authorized)
    components = copy.deepcopy(baseline)
    components["component_policy"]["mode"] = "open_keys"  # type: ignore[index]
    cases.append(components)
    for case in cases:
        assert validate_prospective_semantic_contract(case)


def test_schema_rejects_every_policy_object_mutation(project_root: Path) -> None:
    contract = _contract(project_root)
    schema = json.loads((project_root / SCHEMA_PATH).read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    policy_objects = (
        "fallback_policy",
        "decision_tables",
        "source_text_policy",
        "series_policy",
        "clock_policy",
        "locator_policy",
        "component_policy",
        "ambiguity_policy",
        "coverage_policy",
        "quarantine_policy",
        "date_policy",
        "comparison_policy",
        "leakage_policy",
    )
    for name in policy_objects:
        changed = copy.deepcopy(contract)
        changed[name]["unexpected_mutation"] = True  # type: ignore[index]
        assert list(validator.iter_errors(changed)), name
        assert validate_prospective_semantic_bundle(changed, schema), name


def test_leakage_scan_is_case_punctuation_and_whitespace_insensitive() -> None:
    text = "A fictional SAMPLE—ALPHA uses Value 12 345."
    assert find_prohibited_semantic_leakage(
        text, ["sample alpha", "value-12345", "absent phrase"]
    ) == ["sample alpha", "value-12345"]
