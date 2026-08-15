#!/usr/bin/env python3
"""Archive and normalize role-separated G2 metadata-only discovery drafts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import urlparse

from jsonschema import Draft202012Validator, FormatChecker


def _read(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _screen_urls(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str)]
    return []


def _candidate_rows(value: object) -> list[dict[str, object]]:
    if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
        raise ValueError("candidate intake must contain an array of objects")
    return [dict(item) for item in value]


def _candidate(raw: dict[str, object], lane: str) -> dict[str, object]:
    candidate_id = str(raw["candidate_id"])
    landing = str(raw.get("official_landing_page_url") or raw.get("landing_page_url"))
    source_url = raw.get("direct_pdf_url")
    status = str(raw.get("pre_screen_status") or raw.get("eligibility_status") or "uncertain")
    uncertainty = str(raw.get("uncertainty") or "Metadata-only classification is incomplete.")
    proposed = raw.get("proposed_stratum")
    basis = str(raw.get("metadata_only_stratum_basis") or raw.get("metadata_only_basis") or "")
    format_claim = str(raw.get("mime_or_format_claim") or raw.get("format_claim") or "")
    format_value = (
        "non_pdf"
        if "ineligible_format" in status
        else "pdf"
        if "pdf" in format_claim.lower()
        else "uncertain"
    )
    explicit_structure = any(
        token in basis.lower()
        for token in (
            "expressly labels",
            "explicitly identifies bookmarks",
            "multiple regional",
            "multiple case types",
            "graphic format",
            "charts and tables",
            "mixed sections",
            "long audited annual report",
            "multi-programme report",
        )
    )
    stratum_support = (
        "supported_by_public_metadata"
        if proposed is not None and explicit_structure
        else "uncertain_without_content_inspection"
    )
    terms = _screen_urls(raw.get("terms_or_licence_urls")) or _screen_urls(
        raw.get("terms_or_licence_url")
    )
    privacy = raw.get("privacy_url")
    security = raw.get("security_url")
    exact_identity = not any(
        token in uncertainty.lower()
        for token in ("exact edition", "exact attachment", "multiple pdf", "edition identity")
    )
    original_plausible = status.startswith("plausible")
    sensitive = any(
        token in (str(raw.get("edition_title")) + " " + uncertainty).lower()
        for token in ("victim", "sensitive", "individual")
    )
    aggregate_supported = any(
        token in (basis + " " + str(raw.get("edition_title"))).lower()
        for token in (
            "statistics",
            "statistical",
            "caseload",
            "number of cases",
            "annual report",
            "court activity",
        )
    )
    terms_screen = "no_known_metadata_blocker" if terms else "uncertain"
    rights_screen = "no_known_metadata_blocker" if terms else "uncertain"
    privacy_screen = (
        "no_known_metadata_blocker" if aggregate_supported and not sensitive else "uncertain"
    )
    security_screen = "no_known_metadata_blocker" if landing.startswith("https://") else "uncertain"
    prohibited_screen = (
        "no_known_metadata_blocker" if aggregate_supported and not sensitive else "uncertain"
    )
    eligibility = (
        "ineligible"
        if status.startswith("ineligible")
        else "eligible_metadata_only"
        if original_plausible
        and format_value == "pdf"
        and proposed is not None
        and stratum_support == "supported_by_public_metadata"
        and exact_identity
        and all(
            screen == "no_known_metadata_blocker"
            for screen in (
                terms_screen,
                rights_screen,
                privacy_screen,
                security_screen,
                prohibited_screen,
            )
        )
        else "uncertain"
    )
    jurisdiction = str(raw.get("jurisdiction_code") or raw.get("jurisdiction"))
    series = str(raw.get("source_series_id") or raw.get("source_series"))
    languages = raw.get("language") or raw.get("languages") or ["und"]
    assert isinstance(languages, list)
    host = urlparse(landing).hostname or "official publisher"
    return {
        "candidate_id": f"G2CAND-{candidate_id.upper()}",
        "edition_id": f"ED-{candidate_id.upper()}",
        "edition_title": str(raw["edition_title"]),
        "jurisdiction_id": jurisdiction,
        "source_series_id": series,
        "publisher": host,
        "official_publisher": "official" in str(raw.get("access_status", "")).lower(),
        "landing_page_url": landing,
        "source_url": source_url if isinstance(source_url, str) else None,
        "edition_date_or_period": str(
            raw.get("edition_date_or_period") or raw.get("edition_period")
        ),
        "languages": sorted({str(item).lower() for item in languages}),
        "format": format_value,
        "proposed_stratum": proposed,
        "supported_strata": [proposed]
        if proposed is not None and stratum_support == "supported_by_public_metadata"
        else [],
        "stratum_support": stratum_support,
        "stratum_basis": basis
        or "No defensible public-metadata structure classification was available.",
        "exact_edition_identity_established": exact_identity,
        "metadata_evidence_urls": [landing],
        "terms_url": terms[0] if terms else None,
        "rights_url": terms[0] if terms else None,
        "privacy_url": privacy if isinstance(privacy, str) else None,
        "security_url": security if isinstance(security, str) else None,
        "terms_screen": terms_screen,
        "rights_screen": rights_screen,
        "rights_screen_rationale": (
            "A public terms or licence page was identified; this is only a preliminary "
            "metadata screen and is not rights acceptance."
            if terms
            else "No edition-linked public rights or licence page was identified; "
            "status remains uncertain."
        ),
        "privacy_screen": privacy_screen,
        "security_screen": security_screen,
        "prohibited_data_screen": prohibited_screen,
        "eligibility": eligibility,
        "checked_at": "2026-08-15T04:20:00Z",
        "source_content_accessed": False,
        "notes": f"{lane} discovery status={status}. {uncertainty}",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--west", type=Path, required=True)
    parser.add_argument("--global-intake", type=Path, required=True)
    parser.add_argument("--exposure-ledger", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    output = (
        (root / args.output).resolve() if not args.output.is_absolute() else args.output.resolve()
    )
    output.relative_to(root)
    output.mkdir(parents=True, exist_ok=True)
    west = _read(args.west)
    global_intake = _read(args.global_intake)
    ledger = _read(args.exposure_ledger)
    _write(output / "raw/candidates-west.json", west)
    _write(output / "raw/candidates-global.json", global_intake)
    _write(output / "exposure-ledger.json", ledger)
    candidates = [
        *[_candidate(item, "west") for item in _candidate_rows(west["candidates"])],
        *[_candidate(item, "global") for item in _candidate_rows(global_intake["candidates"])],
    ]
    universe = {
        "schema_version": "1.0",
        "universe_id": "G2HOLDOUT-UNIVERSE-PROSPECTIVE-20260815-01",
        "design_id": "G2HOLDOUT-PROSPECTIVE-20260815-01",
        "as_of": "2026-08-15T04:20:00Z",
        "metadata_only": True,
        "source_content_accessed": False,
        "candidates": sorted(candidates, key=lambda item: str(item["candidate_id"])),
        "limitations": [
            "Public HTML metadata does not establish internal PDF content, values or locators.",
            "A metadata screen is not rights acceptance or legal, privacy, security "
            "or prohibited-data assurance.",
            "Only one candidate had public metadata explicitly supporting the "
            "embedded-raster or dashboard stratum; the frozen six-edition quota is "
            "therefore not currently assembleable.",
            "Search snippets exposing substantive source content were added to the "
            "exposure denylist and excluded.",
        ],
    }
    _write(output / "candidate-universe.json", universe)
    schema = _read(root / "schemas/g2_holdout_candidate_universe.schema.json")
    errors = list(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(universe)
    )
    if errors:
        raise ValueError(errors[0].message)
    ledger_schema = _read(root / "schemas/g2_holdout_exposure_ledger.schema.json")
    ledger_errors = list(
        Draft202012Validator(ledger_schema, format_checker=FormatChecker()).iter_errors(ledger)
    )
    if ledger_errors:
        raise ValueError(ledger_errors[0].message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
