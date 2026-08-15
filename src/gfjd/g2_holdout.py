"""Fail-closed metadata-only selection for the G2 blind holdout."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from .io import sha256_file, write_json


class G2HoldoutError(ValueError):
    """Raised when a holdout intake is invalid or cannot satisfy the frozen design."""


@dataclass(frozen=True, slots=True)
class G2HoldoutSelection:
    manifest_path: Path
    receipt_path: Path
    scope_complete: bool


def select_g2_holdout(
    root: Path,
    *,
    candidate_universe_path: Path,
    exposure_ledger_path: Path,
    output_dir: Path,
    seed: str,
    generated_at: str,
    design_path: Path = Path("config/g2_blind_holdout_plan.json"),
) -> G2HoldoutSelection:
    """Select the exact primary and reserve scope without accessing source content."""

    resolved_root = root.expanduser().resolve()
    universe_path = _confined(resolved_root, candidate_universe_path)
    ledger_path = _confined(resolved_root, exposure_ledger_path)
    plan_path = _confined(resolved_root, design_path)
    destination = _confined(resolved_root, output_dir, require_exists=False)
    universe = _load_object(universe_path)
    ledger = _load_object(ledger_path)
    plan = _load_object(plan_path)
    _validate(resolved_root, "g2_holdout_candidate_universe.schema.json", universe)
    _validate(resolved_root, "g2_holdout_exposure_ledger.schema.json", ledger)
    _validate(resolved_root, "g2_blind_holdout_plan.schema.json", plan)
    if not seed or len(seed) < 16:
        raise G2HoldoutError("selection seed must contain at least 16 characters")

    design = plan["design"]
    strata = tuple(design["strata"])
    per_stratum = int(design["editions_per_stratum"])
    jurisdiction_cap = int(design["maximum_editions_per_jurisdiction"])
    series_cap = int(design["maximum_editions_per_source_series"])
    target = int(design["recommended_sample_size"])
    reserve_count = int(design["reserve_count"])
    if target != per_stratum * len(strata):
        raise G2HoldoutError("frozen sample size does not equal the stratum allocation")
    if series_cap != 1:
        raise G2HoldoutError("selector currently requires the frozen one-edition-per-series rule")

    denied_editions = set(ledger["denied_edition_ids"])
    denied_series = set(ledger["denied_source_series_ids"])
    denied_urls = set(ledger["denied_urls"])
    candidates = universe["candidates"]
    eligible: list[dict[str, Any]] = []
    rejected: list[dict[str, str]] = []
    for candidate in candidates:
        reasons = _rejection_reasons(candidate, denied_editions, denied_series, denied_urls)
        if reasons:
            rejected.append(
                {"candidate_id": candidate["candidate_id"], "reason": "; ".join(reasons)}
            )
        else:
            enriched = dict(candidate)
            enriched["selection_score"] = _score(seed, candidate["candidate_id"])
            eligible.append(enriched)

    ranked = sorted(eligible, key=lambda item: (item["selection_score"], item["candidate_id"]))
    primary = _choose_primary(
        ranked,
        strata=strata,
        per_stratum=per_stratum,
        jurisdiction_cap=jurisdiction_cap,
    )
    failure_reasons: list[str] = []
    if primary is None:
        failure_reasons.append("eligible metadata cannot satisfy the frozen primary scope")
        primary = []
    if primary and len({item["jurisdiction_id"] for item in primary}) < int(
        design["minimum_jurisdictions"]
    ):
        failure_reasons.append("selected primary scope does not meet minimum jurisdictions")

    reserves: list[dict[str, Any]] = []
    reserve_allocation: dict[str, int] = {}
    if not failure_reasons:
        used_ids = {item["candidate_id"] for item in primary}
        used_series = {item["source_series_id"] for item in primary}
        jurisdiction_counts = Counter(item["jurisdiction_id"] for item in primary)
        remaining = [
            item
            for item in ranked
            if item["candidate_id"] not in used_ids
            and item["source_series_id"] not in used_series
            and jurisdiction_counts[item["jurisdiction_id"]] < jurisdiction_cap
        ]
        reserve_allocation = _reserve_allocation(
            remaining, strata=strata, reserve_count=reserve_count
        )
        for stratum in strata:
            choices = [item for item in remaining if item["proposed_stratum"] == stratum]
            for item in choices:
                if (
                    len([r for r in reserves if r["proposed_stratum"] == stratum])
                    >= (reserve_allocation[stratum])
                ):
                    break
                if jurisdiction_counts[item["jurisdiction_id"]] >= jurisdiction_cap:
                    continue
                reserves.append(item)
                jurisdiction_counts[item["jurisdiction_id"]] += 1
                used_series.add(item["source_series_id"])
        if len(reserves) != reserve_count:
            failure_reasons.append("eligible metadata cannot satisfy the frozen reserve scope")

    scope_complete = not failure_reasons
    manifest = {
        "schema_version": "1.0",
        "manifest_id": "G2HOLDOUT-MANIFEST-PROSPECTIVE-20260815-01",
        "design_id": plan["plan_id"],
        "design_commit": "42b89486b7d71a60ed01eb7e7b1d862e6a736820",
        "selection_seed": seed,
        "selection_algorithm": "sha256_seed_nul_candidate_id_ascending_backtracking_v1",
        "metadata_only": True,
        "source_content_accessed": False,
        "scope_complete": scope_complete,
        "primary": [
            _manifest_entry(item, "primary", index + 1) for index, item in enumerate(primary)
        ],
        "reserves": [
            _manifest_entry(item, "reserve", index + 1) for index, item in enumerate(reserves)
        ],
        "reserve_allocation": reserve_allocation,
        "generated_at": generated_at,
        "limitations": failure_reasons,
    }
    destination.mkdir(parents=True, exist_ok=True)
    manifest_path = destination / "candidate-manifest.json"
    write_json(manifest_path, manifest)
    receipt = {
        "schema_version": "1.0",
        "receipt_id": "G2HOLDOUT-SELECTION-PROSPECTIVE-20260815-01",
        "design": _artifact(resolved_root, plan_path),
        "candidate_universe": _artifact(resolved_root, universe_path),
        "exposure_ledger": _artifact(resolved_root, ledger_path),
        "candidate_manifest": _artifact(resolved_root, manifest_path),
        "metadata_only": True,
        "source_content_accessed": False,
        "eligible_candidate_count": len(eligible),
        "rejected_candidates": rejected,
        "scope_complete": scope_complete,
        "failure_reasons": failure_reasons,
        "generated_at": generated_at,
    }
    receipt_path = destination / "selection-receipt.json"
    write_json(receipt_path, receipt)
    _validate(resolved_root, "g2_holdout_candidate_manifest.schema.json", manifest)
    _validate(resolved_root, "g2_holdout_selection_receipt.schema.json", receipt)
    if not scope_complete:
        raise G2HoldoutError("; ".join(failure_reasons))
    return G2HoldoutSelection(manifest_path, receipt_path, True)


def _rejection_reasons(
    item: Mapping[str, Any],
    denied_editions: set[str],
    denied_series: set[str],
    denied_urls: set[str],
) -> list[str]:
    reasons: list[str] = []
    if item["eligibility"] != "eligible_metadata_only":
        reasons.append(f"eligibility={item['eligibility']}")
    if item["source_content_accessed"]:
        reasons.append("source content accessed")
    if not item["exact_edition_identity_established"]:
        reasons.append("exact edition identity not established")
    if not item["official_publisher"]:
        reasons.append("publisher is not official")
    if item["format"] != "pdf":
        reasons.append("format is not PDF")
    if item["stratum_support"] != "supported_by_public_metadata":
        reasons.append("stratum is not supported by public metadata")
    for key in ("terms_screen", "privacy_screen", "security_screen", "prohibited_data_screen"):
        if item[key] != "no_known_metadata_blocker":
            reasons.append(f"{key}={item[key]}")
    if item["edition_id"] in denied_editions:
        reasons.append("edition appears in exposure ledger")
    if item["source_series_id"] in denied_series:
        reasons.append("source series appears in exposure ledger")
    if item["landing_page_url"] in denied_urls or item.get("source_url") in denied_urls:
        reasons.append("URL appears in exposure ledger")
    return reasons


def _choose_primary(
    ranked: Sequence[dict[str, Any]],
    *,
    strata: Sequence[str],
    per_stratum: int,
    jurisdiction_cap: int,
) -> list[dict[str, Any]] | None:
    by_stratum = {
        stratum: [c for c in ranked if c["proposed_stratum"] == stratum] for stratum in strata
    }
    wanted = [(stratum, index) for stratum in strata for index in range(per_stratum)]
    counts: Counter[str] = Counter()
    used_series: set[str] = set()
    selected: list[dict[str, Any]] = []

    def visit(position: int, offsets: dict[str, int]) -> bool:
        if position == len(wanted):
            return True
        stratum, _ = wanted[position]
        options = by_stratum[stratum]
        start = offsets.get(stratum, 0)
        for index in range(start, len(options)):
            candidate = options[index]
            jurisdiction = candidate["jurisdiction_id"]
            series = candidate["source_series_id"]
            if counts[jurisdiction] >= jurisdiction_cap or series in used_series:
                continue
            selected.append(candidate)
            counts[jurisdiction] += 1
            used_series.add(series)
            next_offsets = dict(offsets)
            next_offsets[stratum] = index + 1
            if visit(position + 1, next_offsets):
                return True
            used_series.remove(series)
            counts[jurisdiction] -= 1
            selected.pop()
        return False

    return list(selected) if visit(0, {}) else None


def _reserve_allocation(
    remaining: Sequence[Mapping[str, Any]], *, strata: Sequence[str], reserve_count: int
) -> dict[str, int]:
    if reserve_count < len(strata):
        raise G2HoldoutError("reserve count is smaller than the number of strata")
    allocation = {stratum: 1 for stratum in strata}
    counts = Counter(item["proposed_stratum"] for item in remaining)
    extras = reserve_count - len(strata)
    order = sorted(strata, key=lambda stratum: (-counts[stratum], stratum))
    for stratum in order[:extras]:
        allocation[stratum] += 1
    return allocation


def _manifest_entry(item: Mapping[str, Any], assignment: str, rank: int) -> dict[str, Any]:
    return {
        "assignment": assignment,
        "rank": rank,
        "candidate_id": item["candidate_id"],
        "edition_id": item["edition_id"],
        "jurisdiction_id": item["jurisdiction_id"],
        "source_series_id": item["source_series_id"],
        "proposed_stratum": item["proposed_stratum"],
        "landing_page_url": item["landing_page_url"],
        "source_url": item.get("source_url"),
        "selection_score": item["selection_score"],
    }


def _score(seed: str, candidate_id: str) -> str:
    return hashlib.sha256(f"{seed}\0{candidate_id}".encode()).hexdigest()


def _artifact(root: Path, path: Path) -> dict[str, str]:
    return {"path": path.relative_to(root).as_posix(), "sha256": sha256_file(path)}


def _load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise G2HoldoutError(f"expected JSON object: {path}")
    return value


def _validate(root: Path, schema_name: str, instance: object) -> None:
    schema = _load_object(root / "schemas" / schema_name)
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(instance),
        key=lambda error: tuple(str(part) for part in error.absolute_path),
    )
    if errors:
        raise G2HoldoutError(f"{schema_name}: {errors[0].message}")


def _confined(root: Path, path: Path, *, require_exists: bool = True) -> Path:
    candidate = path.expanduser()
    resolved = candidate.resolve() if candidate.is_absolute() else (root / candidate).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise G2HoldoutError(f"path escapes repository: {path}") from exc
    if require_exists and not resolved.is_file():
        raise G2HoldoutError(f"required file does not exist: {path}")
    return resolved
