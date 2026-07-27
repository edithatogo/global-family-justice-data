"""Quality and gold-layer promotion rules."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class GoldDecision:
    eligible: bool
    reasons: tuple[str, ...]


MANDATORY_GOLD_FIELDS = (
    "observation_id",
    "jurisdiction_id",
    "indicator_id",
    "source_id",
    "matter_type_original",
    "matter_type_harmonised",
    "measure_original",
    "statistic_type",
    "unit",
    "period_start",
    "period_end",
    "cohort_basis",
    "definition_original",
    "definition_english",
    "provenance_locator",
    "extraction_method",
)


def assess_gold_eligibility(row: dict[str, Any]) -> GoldDecision:
    reasons: list[str] = []
    for field in MANDATORY_GOLD_FIELDS:
        if row.get(field) in {None, ""}:
            reasons.append(f"missing:{field}")
    if row.get("second_reviewed") is not True:
        reasons.append("second_review_required")
    if row.get("quality_grade") not in {"A", "B"}:
        reasons.append("quality_grade_must_be_A_or_B")
    if str(row.get("comparability_tier")) not in {"1", "2"}:
        reasons.append("comparability_tier_must_be_1_or_2")
    try:
        raw_value = row.get("value")
        if raw_value is None or float(raw_value) < 0:
            reasons.append("value_must_be_non_negative")
    except (TypeError, ValueError):
        reasons.append("value_must_be_numeric")

    indicator = str(row.get("indicator_id") or "")
    if indicator.startswith("TIME_"):
        if not row.get("stage_start"):
            reasons.append("timeliness_requires_stage_start")
        if not row.get("stage_end"):
            reasons.append("timeliness_requires_stage_end")
    if row.get("unit") == "percent":
        try:
            percent_value = row.get("value")
            if percent_value is None:
                raise TypeError
            value = float(percent_value)
            if not 0 <= value <= 100:
                reasons.append("percent_out_of_range")
        except (TypeError, ValueError):
            pass
    return GoldDecision(not reasons, tuple(sorted(set(reasons))))
