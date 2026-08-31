"""Conspicuously fictional diagnostic rows; no empirical input or acceptance."""

import copy
import hashlib
import json

import pytest

from gfjd.medallion_quality_checks import (
    VERSION,
    QualityChecksError,
    assess_quality,
    verify_quality,
)
from gfjd.quality import MANDATORY_GOLD_FIELDS


def row() -> dict[str, str]:
    result = dict.fromkeys(MANDATORY_GOLD_FIELDS, "FICTIONAL")
    result.update(
        observation_id="FICTIONAL-1",
        value="10",
        unit="count",
        period_start="2026-01-01",
        period_end="2026-12-31",
        stage_start="explicit-fictional-start",
        stage_end="explicit-fictional-end",
    )
    return result


def inputs(rows: list | None = None) -> tuple[bytes, dict]:
    raw = json.dumps([row()] if rows is None else rows).encode()
    return raw, {
        "contract_version": VERSION,
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "small_cell_threshold": 5,
    }


def test_positive_exact_recomputation_no_rows_or_authority() -> None:
    raw, policy = inputs()
    report = assess_quality(raw, policy)
    assert report["row_issues"] == [{"row_index": 0, "issue_codes": []}]
    assert report["counts"]["rows_with_issues"] == 0
    assert report["counts"]["comparability_signatures"] == 1
    assert all(value is False for value in report["authority"].values())
    assert report["pending_reviews"] == ["semantic_review", "disclosure_review", "owner_decision"]
    assert "FICTIONAL-1" not in json.dumps(report)
    assert assess_quality(raw, policy) == report
    assert verify_quality(raw, policy, report) is None


@pytest.mark.parametrize(
    "value,code",
    [
        ("-1", "negative_value"),
        ("NaN", "nonfinite_value"),
        ("Infinity", "nonfinite_value"),
        ("not-a-number", "invalid_numeric_value"),
        ("1e999999999999999999", "numeric_budget_exceeded"),
        ("1e1001", "numeric_budget_exceeded"),
        ("1e-1001", "numeric_budget_exceeded"),
        ("9" * 129, "numeric_budget_exceeded"),
        (" 10 ", "invalid_numeric_value"),
    ],
)
def test_numeric_diagnostics(value: str, code: str) -> None:
    item = row()
    item["value"] = value
    raw, policy = inputs([item])
    assert code in assess_quality(raw, policy)["row_issues"][0]["issue_codes"]


def test_percent_exact_decimal_and_small_cell_count_only() -> None:
    item = row()
    item.update(unit="percent", value="100.00000000000000000000000000001")
    raw, policy = inputs([item])
    assert "percent_out_of_range" in assess_quality(raw, policy)["row_issues"][0]["issue_codes"]
    item["value"] = "1"
    raw, policy = inputs([item])
    assert assess_quality(raw, policy)["counts"]["small_cell_rows"] == 0
    item["unit"] = "count"
    raw, policy = inputs([item])
    assert assess_quality(raw, policy)["counts"]["small_cell_rows"] == 1
    for value in ("0", "5", "-0", "1e1000"):
        item["value"] = value
        raw, policy = inputs([item])
        assert assess_quality(raw, policy)["counts"]["small_cell_rows"] == 0


@pytest.mark.parametrize(
    "start,end,code",
    [
        ("2026-02-30", "2026-12-31", "invalid_period_start"),
        ("2026-01-01", "2026-13-01", "invalid_period_end"),
        ("2026-12-31", "2026-01-01", "period_reversed"),
        ("20260101", "2026-12-31", "invalid_period_start"),
        ("2026-01-01T00:00:00Z", "2026-12-31", "invalid_period_start"),
    ],
)
def test_explicit_period_validation(start: str, end: str, code: str) -> None:
    item = row()
    item.update(period_start=start, period_end=end)
    raw, policy = inputs([item])
    assert code in assess_quality(raw, policy)["row_issues"][0]["issue_codes"]


def test_missing_blank_duplicate_and_signature_diversity() -> None:
    first, second = row(), row()
    first.pop("definition_original")
    second.update(definition_english="  ", unit="percent")
    second.pop("stage_start")
    raw, policy = inputs([first, second])
    report = assess_quality(raw, policy)
    assert report["counts"]["duplicate_observation_rows"] == 2
    assert report["counts"]["comparability_signatures"] == 1
    assert report["counts"]["incomplete_signature_rows"] == 1
    assert "missing_required:definition_original" in report["row_issues"][0]["issue_codes"]
    assert "blank_required:definition_english" in report["row_issues"][1]["issue_codes"]
    second["stage_start"] = first["stage_start"]
    raw, policy = inputs([first, second])
    assert assess_quality(raw, policy)["counts"]["comparability_signatures"] == 2


@pytest.mark.parametrize(
    "field,value",
    [
        ("small_cell_threshold", True),
        ("small_cell_threshold", 0),
        ("small_cell_threshold", 101),
        ("source_sha256", "0" * 64),
        ("contract_version", "unknown"),
        ("extra", "not allowed"),
    ],
)
def test_policy_is_exact(field: str, value: object) -> None:
    raw, policy = inputs()
    policy[field] = value
    with pytest.raises(QualityChecksError):
        assess_quality(raw, policy)


@pytest.mark.parametrize(
    "raw",
    [
        b'[{"value":"1","value":"2"}]',
        b'[{"value":NaN}]',
        b'[{"value":1e9999}]',
        b'[{"value":true}]',
        b'[{"value":null}]',
        b"{}",
        b"[]",
        b"\xff",
        b"not JSON",
        b'[{"value":"\\ud800"}]',
    ],
)
def test_unsafe_json_and_types(raw: bytes) -> None:
    _, policy = inputs()
    policy["source_sha256"] = hashlib.sha256(raw).hexdigest()
    with pytest.raises(QualityChecksError):
        assess_quality(raw, policy)


def test_limits() -> None:
    for rows in ([row()] * 5001, [{str(i): "x" for i in range(101)}], [{"value": "x" * 4097}]):
        raw, policy = inputs(rows)
        with pytest.raises(QualityChecksError):
            assess_quality(raw, policy)
    raw = b"x" * (1024 * 1024 + 1)
    _, policy = inputs()
    policy["source_sha256"] = hashlib.sha256(raw).hexdigest()
    with pytest.raises(QualityChecksError):
        assess_quality(raw, policy)


def test_forged_receipt_and_self_hash_fail() -> None:
    raw, policy = inputs()
    report = assess_quality(raw, policy)
    for field in ("counts", "row_issues", "authority", "pending_reviews"):
        forged = copy.deepcopy(report)
        forged[field] = {}
        del forged["report_sha256"]
        forged["report_sha256"] = hashlib.sha256(
            json.dumps(forged, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        with pytest.raises(QualityChecksError):
            verify_quality(raw, policy, forged)


def test_unassessed_units_and_values_never_mean_disclosure_pass() -> None:
    first, second, third = row(), row(), row()
    first.update(unit="persons", observation_id="FICTIONAL-1")
    second.update(value="not-numeric", observation_id="FICTIONAL-2")
    third.update(value="0", observation_id="FICTIONAL-3")
    raw, policy = inputs([first, second, third])
    before = copy.deepcopy(policy)
    report = assess_quality(raw, policy)
    assert report["counts"]["small_cell_rows"] == 0
    assert report["counts"]["small_cell_unassessed_unit_rows"] == 1
    assert report["counts"]["small_cell_unassessed_value_rows"] == 1
    assert report["counts"]["small_cell_assessed_rows"] == 1
    assert report["authority"]["disclosure_acceptance"] is False
    assert "disclosure_review" in report["pending_reviews"]
    assert policy == before


def test_row_count_boundary_and_long_keys() -> None:
    raw, policy = inputs([{}] * 5000)
    assert assess_quality(raw, policy)["counts"]["rows"] == 5000
    for rows in ([{}] * 5001, [{"x" * 4097: "value"}]):
        raw, policy = inputs(rows)
        with pytest.raises(QualityChecksError):
            assess_quality(raw, policy)


def test_leap_day_and_equal_period_are_literal_valid_dates() -> None:
    item = row()
    item.update(period_start="2024-02-29", period_end="2024-02-29")
    raw, policy = inputs([item])
    assert assess_quality(raw, policy)["technical_checks"]["calendar_periods_ordered"] is True
    item["period_start"] = "0000-01-01"
    raw, policy = inputs([item])
    assert "invalid_period_start" in assess_quality(raw, policy)["row_issues"][0]["issue_codes"]


def test_nonbyte_input_and_missing_policy_field_stop() -> None:
    raw, policy = inputs()
    with pytest.raises(QualityChecksError):
        assess_quality("not bytes", policy)  # type: ignore[arg-type]
    del policy["small_cell_threshold"]
    with pytest.raises(QualityChecksError):
        assess_quality(raw, policy)
