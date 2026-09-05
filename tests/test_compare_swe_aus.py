"""Fictional-only regressions; never load sealed empirical outputs."""

import copy
import hashlib
import json
import runpy
import sys
from pathlib import Path

import pytest


@pytest.fixture
def comparator() -> dict:
    return runpy.run_path(str(Path(__file__).resolve().parents[1] / "scripts/compare_swe_aus.py"))


@pytest.fixture
def fictional() -> tuple[dict, dict]:
    common = [
        "source_row",
        "inventory_id",
        "source_sha256",
        "period_label_source",
        "period_start",
        "period_end",
        "comparison_eligible",
        "quarantined",
        "locator",
    ]
    cohort = []
    rows = []
    for index, format_name in enumerate(("xlsx", "pdf")):
        source = {
            "inventory_id": f"FICTIONAL-ONLY-{index}",
            "sha256": hashlib.sha256(f"fictional source {index}".encode()).hexdigest(),
            "period_label": "FICTIONAL PERIOD",
            "format": format_name,
            "sheet": "Fictional",
            "row_fields": ["label_source", "value_source", "unit_source"],
            "data_rows" if format_name == "xlsx" else "table_rows_one_based": list(range(1, 8)),
        }
        cohort.append(source)
        for number in range(1, 8):
            rows.append(
                {
                    "source_row": number,
                    "inventory_id": source["inventory_id"],
                    "source_sha256": source["sha256"],
                    "period_label_source": source["period_label"],
                    "period_start": None,
                    "period_end": None,
                    "comparison_eligible": False,
                    "quarantined": True,
                    "locator": (
                        f"Fictional!B{number}:D{number}"
                        if format_name == "xlsx"
                        else f"PDF page 102; Table 3.3.1(a); data row {number}"
                    ),
                    "label_source": "FICTIONAL LABEL",
                    "value_source": "001.00",
                    "unit_source": "FICTIONAL UNIT",
                }
            )
    contract = {
        "contract_id": "FICTIONAL-ONLY-REGRESSION",
        "cohort": cohort,
        "output_contract": {"common_fields": common},
    }
    return contract, {"contract_id": contract["contract_id"], "rows": rows}


def test_valid_fictional_schema(comparator: dict, fictional: tuple[dict, dict]) -> None:
    contract, value = fictional
    comparator["validate"](value, contract)


@pytest.mark.parametrize(
    ("key", "replacement"),
    [
        ("source_row", True),
        ("source_row", 1.0),
        ("source_row", "1"),
        ("comparison_eligible", 0),
        ("quarantined", 1),
        ("period_start", ""),
        ("period_end", False),
        ("value_source", 1),
        ("value_source", None),
        ("value_source", ""),
        ("label_source", []),
    ],
)
def test_wrong_field_types_rejected(
    comparator: dict, fictional: tuple[dict, dict], key: str, replacement: object
) -> None:
    contract, value = fictional
    value["rows"][0][key] = replacement
    with pytest.raises(AssertionError):
        comparator["validate"](value, contract)


@pytest.mark.parametrize("mutation", ["extra", "missing", "short", "long", "contract"])
def test_schema_drift_rejected(
    comparator: dict, fictional: tuple[dict, dict], mutation: str
) -> None:
    contract, value = fictional
    if mutation == "extra":
        value["rows"][0]["unexpected"] = "FICTIONAL"
    elif mutation == "missing":
        del value["rows"][0]["value_source"]
    elif mutation == "short":
        value["rows"].pop()
    elif mutation == "long":
        value["rows"].append(copy.deepcopy(value["rows"][0]))
    else:
        value["contract_id"] = "FICTIONAL-WRONG-CONTRACT"
    with pytest.raises(AssertionError):
        comparator["validate"](value, contract)


@pytest.mark.parametrize("raw", [b'{"x":1,"x":2}', b'{"rows":[{"x":1,"x":2}]}'])
def test_duplicate_keys_rejected(comparator: dict, tmp_path: Path, raw: bytes) -> None:
    path = tmp_path / "fictional.json"
    path.write_bytes(raw)
    with pytest.raises(ValueError, match="duplicate key"):
        comparator["load"](path, hashlib.sha256(raw).hexdigest())


def test_digest_mismatch_rejected(comparator: dict, tmp_path: Path) -> None:
    path = tmp_path / "fictional.json"
    path.write_text('{"fictional":true}', encoding="utf-8")
    with pytest.raises(ValueError, match="seal mismatch"):
        comparator["load"](path, hashlib.sha256(b"different fictional bytes").hexdigest())


@pytest.mark.parametrize("changed", [False, True])
def test_main_exact_lexical_comparison_and_honest_counts(
    comparator: dict,
    fictional: tuple[dict, dict],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    changed: bool,
) -> None:
    contract, left = fictional
    right = copy.deepcopy(left)
    if changed:
        # Numerically equal is not lexically equal: no normalization is allowed.
        right["rows"][0]["value_source"] = "1.00"
    output = tmp_path / "fictional-report.json"
    argv = ["compare_swe_aus.py", "--output", str(output)]
    digests = {}
    for name, value in (("contract", contract), ("a", left), ("b", right)):
        path = tmp_path / f"fictional-{name}.json"
        raw = json.dumps(value).encode("utf-8")
        path.write_bytes(raw)
        digests[name] = hashlib.sha256(raw).hexdigest()
        argv.extend([f"--{name}", str(path), f"--{name}-sha256", digests[name]])
    monkeypatch.setattr(sys, "argv", argv)
    assert comparator["main"]() == (2 if changed else 0)
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report == {
        "contract_sha256": digests["contract"],
        "a_sha256": digests["a"],
        "b_sha256": digests["b"],
        "critical_matches": 168 - int(changed),
        "critical_fields": 168,
        "populated_matches": 140 - int(changed),
        "populated_fields": 140,
        "passed": not changed,
        "source_accuracy_review_required": True,
        "gate_acceptance": False,
    }
