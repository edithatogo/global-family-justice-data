"""Integrated project validation: contracts, semantics, programme and security."""

from __future__ import annotations

import csv
import json
import math
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .conductor import Conductor
from .io import sha256_file
from .project import Project, load_project
from .public_archive import verify_custody_receipt
from .reporting import Report, Severity
from .schema_validation import ValidatedTable, tables_by_contract, validate_contracts
from .security import scan_repository


def validate_project(
    root: Path | str | None = None,
    *,
    strict: bool = False,
    as_of: date | None = None,
    include_security: bool = True,
) -> Report:
    project = load_project(root)
    as_of = as_of or date.today()
    report = Report("GFJD project validation")
    tables = validate_contracts(project, report)
    _semantic_validation(project, tables, report, as_of=as_of)
    _validate_methods_contract_manifest(project, report)
    _validate_archive_inventory(project, report)
    _validate_source_rights_queue(project, report)
    _validate_external_evidence_register(project, report)

    try:
        conductor = Conductor.load(project)
        report.extend(conductor.validate(as_of=as_of).issues)
    except Exception as exc:
        report.error("CONDUCTOR_LOAD_FAILED", f"Could not load programme conductor: {exc}")

    if include_security:
        report.extend(scan_repository(project.root).issues)

    if strict and report.warning_count:
        report.metrics["strict_mode"] = True
    report.metrics["as_of"] = as_of.isoformat()
    # A check is a separately meaningful control family rather than an individual row.
    report.checks_run = int(report.metrics.get("contracts", 0)) + 4
    return report


def _validate_archive_inventory(project: Project, report: Report) -> None:
    """Bind every retained source edition across inventory, manifest and payload bytes."""

    relative = "data/raw/archive_inventory.csv"
    path = project.root / relative
    if not path.is_file():
        report.error("ARCHIVE_INVENTORY_MISSING", "Archive inventory is missing", path=relative)
        return

    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    required = {"inventory_id", "source_id", "manifest_path", "payload_path", "sha256"}
    if not rows or not required.issubset(rows[0]):
        report.error(
            "ARCHIVE_INVENTORY_SCHEMA",
            "Archive inventory columns are incomplete",
            path=relative,
        )
        return

    custody_relative = "data/preservation/public_b0_custody_20260827.json"
    custody_errors: list[str] = []
    custody_present = (project.root / custody_relative).is_file()
    if custody_present:
        custody_errors = verify_custody_receipt(project.root, project.root / custody_relative)
        for error in custody_errors:
            report.error(
                "ARCHIVE_PUBLIC_CUSTODY_INVALID",
                error,
                path=custody_relative,
            )

    for index, row in enumerate(rows, start=2):
        expected = row.get("sha256", "")
        if len(expected) != 64 or any(char not in "0123456789abcdef" for char in expected):
            report.error(
                "ARCHIVE_INVENTORY_SHA256_INVALID",
                "Archive inventory SHA-256 must be exactly 64 lowercase hexadecimal characters",
                path=relative,
                row=index,
            )
            continue

        manifest_relative = row.get("manifest_path", "")
        payload_relative = row.get("payload_path", "")
        manifest_path = project.root / manifest_relative
        payload_path = project.root / payload_relative
        if not manifest_path.is_file():
            report.error(
                "ARCHIVE_INVENTORY_MANIFEST_MISSING",
                f"Archive manifest is missing: {manifest_relative}",
                path=relative,
                row=index,
            )
            continue
        if not payload_path.is_file():
            if custody_present and not custody_errors:
                report.info(
                    "ARCHIVE_INVENTORY_PAYLOAD_PUBLIC_REMOTE",
                    f"Payload has verified provider-separated public custody: {payload_relative}",
                    path=relative,
                    row=index,
                )
            else:
                report.info(
                    "ARCHIVE_INVENTORY_PAYLOAD_LOCAL_ONLY",
                    f"Archive payload is not present in this checkout: {payload_relative}",
                    path=relative,
                    row=index,
                )
            continue

        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            report.error(
                "ARCHIVE_INVENTORY_MANIFEST_INVALID",
                f"Archive manifest cannot be read: {exc}",
                path=manifest_relative,
            )
            continue
        if manifest.get("sha256") != expected:
            report.error(
                "ARCHIVE_INVENTORY_MANIFEST_SHA256_MISMATCH",
                "Archive inventory and acquisition manifest SHA-256 values differ",
                path=relative,
                row=index,
            )
        if manifest.get("source_id") != row.get("source_id"):
            report.error(
                "ARCHIVE_INVENTORY_SOURCE_MISMATCH",
                "Archive inventory and acquisition manifest source IDs differ",
                path=relative,
                row=index,
            )
        actual = sha256_file(payload_path)
        if actual != expected:
            report.error(
                "ARCHIVE_INVENTORY_PAYLOAD_SHA256_MISMATCH",
                "Archived payload bytes do not match the recorded SHA-256",
                path=payload_relative,
                row=index,
            )


def _validate_source_rights_queue(project: Project, report: Report) -> None:
    """Keep unresolved rights routing tied to real manifests and fail-closed status."""
    relative = "docs/governance/source-rights-review-queue.csv"
    path = project.root / relative
    if not path.is_file():
        report.error(
            "SOURCE_RIGHTS_QUEUE_MISSING", "Source-rights review queue is missing", path=relative
        )
        return
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    required = {
        "source_id",
        "manifest_path",
        "manifest_status",
        "rights_status",
        "redistribution_status",
        "release_boundary",
    }
    for index, row in enumerate(rows, start=2):
        if not required.issubset(row):
            report.error(
                "SOURCE_RIGHTS_QUEUE_SCHEMA",
                "Source-rights queue columns are incomplete",
                path=relative,
                row=index,
            )
            continue
        manifest = project.root / row["manifest_path"]
        if not manifest.is_file():
            report.error(
                "SOURCE_RIGHTS_MANIFEST_MISSING",
                f"Queued source manifest is missing: {row['manifest_path']}",
                path=relative,
                row=index,
            )
        if (
            row["manifest_status"] != "metadata_only"
            or row["rights_status"] != "unknown"
            or row["redistribution_status"] != "metadata_only"
        ):
            report.error(
                "SOURCE_RIGHTS_QUEUE_NOT_FAIL_CLOSED",
                "Unresolved rights queue entry is not metadata-only/unknown",
                path=relative,
                row=index,
            )
        if "metadata" not in row["release_boundary"].lower():
            report.error(
                "SOURCE_RIGHTS_QUEUE_BOUNDARY_MISSING",
                "Rights queue entry lacks metadata-only release boundary",
                path=relative,
                row=index,
            )


def _validate_external_evidence_register(project: Project, report: Report) -> None:
    """Validate the external-evidence register without treating plans as evidence."""
    relative = "docs/governance/external-evidence-blocker-register.csv"
    path = project.root / relative
    if not path.is_file():
        report.error(
            "EXTERNAL_EVIDENCE_REGISTER_MISSING",
            "External-evidence register is missing",
            path=relative,
        )
        return
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    required = {
        "blocker_id",
        "track_id",
        "gate",
        "dependency",
        "owner_action",
        "status",
        "evidence_required",
        "recommended_option",
        "fallback_option",
        "approval_boundary",
        # Assignment metadata is planning data, not proof of authority.  It
        # must nevertheless be present so every blocker has an explicit
        # owner route and freeze point rather than silently becoming orphaned.
        "assigned_to_role",
        "assignment_status",
        "frozen_at",
    }
    if not rows or not required.issubset(rows[0]):
        report.error(
            "EXTERNAL_EVIDENCE_REGISTER_SCHEMA",
            "External-evidence register columns are incomplete",
            path=relative,
        )
        return
    seen: set[str] = set()
    allowed_status = {"pending", "accepted", "blocked", "closed"}
    for index, row in enumerate(rows, start=2):
        blocker_id = row.get("blocker_id", "")
        if not blocker_id or blocker_id in seen:
            report.error(
                "EXTERNAL_EVIDENCE_REGISTER_ID",
                "External-evidence blocker IDs must be unique and non-empty",
                path=relative,
                row=index,
            )
        seen.add(blocker_id)
        if row.get("status") not in allowed_status:
            report.error(
                "EXTERNAL_EVIDENCE_REGISTER_STATUS",
                "External-evidence blocker has an invalid status",
                path=relative,
                row=index,
            )
        for field in (
            "evidence_required",
            "recommended_option",
            "fallback_option",
            "approval_boundary",
            "assigned_to_role",
            "assignment_status",
            "frozen_at",
        ):
            if not row.get(field, "").strip():
                report.error(
                    "EXTERNAL_EVIDENCE_REGISTER_BOUNDARY",
                    f"External-evidence blocker lacks {field}",
                    path=relative,
                    row=index,
                )
        if row.get("assignment_status") not in {
            "assigned-pending-authority",
            "assigned-pending-acceptance",
            "assigned-pending-panel-adjudication",
            "assigned-pending-send-approval",
            "assigned-pending-commitment",
            "assigned-pending-safeguarding",
        }:
            report.error(
                "EXTERNAL_EVIDENCE_REGISTER_ASSIGNMENT",
                "External-evidence blocker has an invalid assignment status",
                path=relative,
                row=index,
            )
        try:
            date.fromisoformat(row.get("frozen_at", ""))
        except ValueError:
            report.error(
                "EXTERNAL_EVIDENCE_REGISTER_FREEZE_DATE",
                "External-evidence blocker freeze date must be ISO-8601",
                path=relative,
                row=index,
            )
        if row.get("status") == "closed":
            report.error(
                "EXTERNAL_EVIDENCE_REGISTER_FAIL_CLOSED",
                "External-evidence blocker cannot be marked closed in the planning register",
                path=relative,
                row=index,
            )
            return


def validate_repository(
    root: Path | str | None = None,
    *,
    today: date | None = None,
    strict: bool = False,
    include_security: bool = True,
) -> Report:
    """Compatibility alias for callers that use repository-oriented terminology."""

    return validate_project(
        root,
        strict=strict,
        as_of=today,
        include_security=include_security,
    )


def _semantic_validation(
    project: Project,
    tables: list[ValidatedTable],
    report: Report,
    *,
    as_of: date,
) -> None:
    grouped = tables_by_contract(tables)
    jurisdictions = _rows(grouped, "jurisdictions")
    sources = _rows(grouped, "sources")
    indicators = _rows(grouped, "indicators")
    matter_types = _rows(grouped, "matter_types")
    institutions = _rows(grouped, "institutions")
    source_editions = _rows(grouped, "source_editions")
    outcomes_evidence = _rows(grouped, "outcomes_evidence")
    extractions = _rows(grouped, "extractions")
    reviews = _rows(grouped, "reviews")

    jurisdiction_ids = _check_unique(jurisdictions, "jurisdiction_id", report, "jurisdictions")
    source_ids = _check_unique(sources, "source_id", report, "sources")
    indicator_ids = _check_unique(indicators, "indicator_id", report, "indicators")
    matter_ids = _check_unique(matter_types, "matter_type_id", report, "matter_types")
    institution_ids = _check_unique(institutions, "institution_id", report, "institutions")
    source_edition_ids = _check_unique(
        source_editions, "source_edition_id", report, "source_editions"
    )
    extraction_ids = _check_unique(extractions, "extraction_id", report, "extractions")
    review_ids = _check_unique(reviews, "review_id", report, "reviews")
    _check_unique(outcomes_evidence, "evidence_record_id", report, "outcomes_evidence")

    for index, row in enumerate(jurisdictions, start=2):
        parent = _text(row.get("parent_jurisdiction_id"))
        if parent and parent not in jurisdiction_ids:
            report.error(
                "JURISDICTION_PARENT_UNKNOWN",
                f"Unknown parent_jurisdiction_id {parent!r}",
                path=project.paths["jurisdictions"],
                row=index,
            )
        if parent == _text(row.get("jurisdiction_id")):
            report.error(
                "JURISDICTION_SELF_PARENT",
                "A jurisdiction cannot be its own parent",
                path=project.paths["jurisdictions"],
                row=index,
            )

    staleness_cfg = project.config.get("validation", {}).get("source_staleness_days", {})
    require_https = bool(
        project.config.get("validation", {}).get("require_https_for_sources", True)
    )
    for index, row in enumerate(sources, start=2):
        jurisdiction_id = _text(row.get("jurisdiction_id"))
        if jurisdiction_id not in jurisdiction_ids:
            report.error(
                "SOURCE_JURISDICTION_UNKNOWN",
                f"Unknown jurisdiction_id {jurisdiction_id!r}",
                path=project.paths["sources"],
                row=index,
            )
        source_url = _text(row.get("source_url"))
        parsed = urlparse(source_url)
        if require_https and parsed.scheme != "https":
            report.warning(
                "SOURCE_URL_NOT_HTTPS",
                f"Source URL is not HTTPS: {source_url}",
                path=project.paths["sources"],
                row=index,
            )
        verified = _date_value(row.get("last_verified"))
        if verified:
            if verified > as_of:
                report.error(
                    "SOURCE_VERIFIED_IN_FUTURE",
                    f"last_verified {verified.isoformat()} is after validation date "
                    f"{as_of.isoformat()}",
                    path=project.paths["sources"],
                    row=index,
                )
            priority = _text(row.get("priority"))
            threshold = int(staleness_cfg.get(priority, 365))
            age = (as_of - verified).days
            if age > threshold:
                report.warning(
                    "SOURCE_STALE",
                    f"{priority}-priority source was last verified {age} days ago "
                    f"(threshold {threshold})",
                    path=project.paths["sources"],
                    row=index,
                    context={"source_id": row.get("source_id")},
                )
        if (
            _text(row.get("licence_status")) in {"unknown", "restricted_or_unknown"}
            and _text(row.get("priority")) == "high"
        ):
            report.info(
                "SOURCE_RIGHTS_REVIEW_NEEDED",
                "High-priority source still needs a definitive rights/redistribution determination",
                path=project.paths["sources"],
                row=index,
                context={"source_id": row.get("source_id")},
            )

    for index, row in enumerate(matter_types, start=2):
        parent = _text(row.get("parent_matter_type_id"))
        if parent and parent not in matter_ids:
            report.error(
                "MATTER_PARENT_UNKNOWN",
                f"Unknown parent_matter_type_id {parent!r}",
                path="data/seed/matter_type_dictionary.csv",
                row=index,
            )

    for index, row in enumerate(institutions, start=2):
        if _text(row.get("jurisdiction_id")) not in jurisdiction_ids:
            report.error(
                "INSTITUTION_JURISDICTION_UNKNOWN",
                f"Unknown jurisdiction_id {row.get('jurisdiction_id')!r}",
                path="data/seed/institution_register.csv",
                row=index,
            )
        valid_from = _date_value(row.get("valid_from"))
        valid_to = _date_value(row.get("valid_to"))
        if valid_from and valid_to and valid_from > valid_to:
            report.error(
                "INSTITUTION_DATE_ORDER",
                "valid_from is after valid_to",
                path="data/seed/institution_register.csv",
                row=index,
            )

    for index, row in enumerate(source_editions, start=2):
        if _text(row.get("source_id")) not in source_ids:
            report.error(
                "SOURCE_EDITION_SOURCE_UNKNOWN",
                f"Unknown source_id {row.get('source_id')!r}",
                path="data/seed/source_edition_template.csv",
                row=index,
            )
        _check_period(row, report, "data/seed/source_edition_template.csv", index)

    for index, row in enumerate(outcomes_evidence, start=2):
        if _text(row.get("jurisdiction_id")) not in jurisdiction_ids:
            report.error(
                "OUTCOME_EVIDENCE_JURISDICTION_UNKNOWN",
                f"Unknown jurisdiction_id {row.get('jurisdiction_id')!r}",
                path="data/seed/outcomes_evidence_template.csv",
                row=index,
            )

    for index, row in enumerate(extractions, start=2):
        if _text(row.get("source_edition_id")) not in source_edition_ids:
            report.error(
                "EXTRACTION_SOURCE_EDITION_UNKNOWN",
                f"Unknown source_edition_id {row.get('source_edition_id')!r}",
                path="data/seed/extraction_template.csv",
                row=index,
            )

    for index, row in enumerate(reviews, start=2):
        subject_type = _text(row.get("subject_type"))
        subject_id = _text(row.get("subject_id"))
        known_sets = {
            "source": source_ids,
            "source_edition": source_edition_ids,
            "extraction": extraction_ids,
            "observation": set(),
            "series": set(),
            "mapping": set(),
            "jurisdiction": jurisdiction_ids,
            "release": set(),
        }
        known = known_sets.get(subject_type)
        if known is not None and known and subject_id not in known:
            report.warning(
                "REVIEW_SUBJECT_UNKNOWN",
                f"Review subject {subject_type}:{subject_id} is not present in the seed registers",
                path="data/seed/review_template.csv",
                row=index,
            )

    observation_tables = [
        table
        for contract_id in ("observation_template", "silver_observations", "gold_observations")
        for table in grouped.get(contract_id, [])
    ]
    observation_ids: set[str] = set()
    for table in observation_tables:
        is_gold = table.contract.layer == "gold"
        for index, row in enumerate(table.typed_rows, start=2):
            observation_id = _text(row.get("observation_id"))
            if observation_id in observation_ids:
                report.error(
                    "OBSERVATION_ID_DUPLICATE",
                    f"Duplicate observation_id {observation_id!r} across observation tables",
                    path=_relative(project, table.path),
                    row=index,
                )
            observation_ids.add(observation_id)
            _validate_observation(
                project,
                table,
                row,
                index,
                report,
                jurisdiction_ids=jurisdiction_ids,
                source_ids=source_ids,
                indicator_ids=indicator_ids,
                matter_ids=matter_ids,
                institution_ids=institution_ids,
                source_edition_ids=source_edition_ids,
                extraction_ids=extraction_ids,
                review_ids=review_ids,
                is_gold=is_gold,
            )

    report.metrics.update(
        {
            "jurisdictions": len(jurisdiction_ids),
            "sources": len(source_ids),
            "indicators": len(indicator_ids),
            "matter_types": len(matter_ids),
            "observations": len(observation_ids),
        }
    )


def _validate_methods_contract_manifest(project: Project, report: Report) -> None:
    """Require the T1 evidence bundle to bind its v0.3 semantic inputs."""

    relative = "docs/methods/v0.3-methods-contract-manifest.json"
    manifest_path = project.root / relative
    required_paths = {
        "docs/methods/scope-and-unit-of-analysis.md",
        "docs/methods/indicator-framework.md",
        "data/seed/jurisdiction_register.csv",
        "data/seed/institution_register.csv",
        "data/seed/matter_type_dictionary.csv",
        "data/seed/indicator_dictionary.csv",
        "schemas/indicator.schema.json",
        "schemas/observation.schema.json",
    }
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        report.error(
            "METHODS_CONTRACT_MANIFEST_INVALID",
            f"Could not read methods contract manifest: {exc}",
            path=relative,
        )
        return
    if not isinstance(payload, dict) or payload.get("ontology_version") != "0.3":
        report.error(
            "METHODS_CONTRACT_MANIFEST_INVALID",
            "Methods contract manifest must declare ontology_version 0.3",
            path=relative,
        )
        return
    entries = payload.get("artifacts")
    if not isinstance(entries, list):
        report.error(
            "METHODS_CONTRACT_MANIFEST_INVALID",
            "Methods contract manifest artifacts must be a list",
            path=relative,
        )
        return
    declared: dict[str, str] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            report.error(
                "METHODS_CONTRACT_MANIFEST_INVALID", "Malformed artifact entry", path=relative
            )
            continue
        path = _text(entry.get("path"))
        digest = _text(entry.get("sha256"))
        if not path or Path(path).is_absolute() or ".." in Path(path).parts:
            report.error(
                "METHODS_CONTRACT_MANIFEST_INVALID", f"Unsafe artifact path {path!r}", path=relative
            )
            continue
        if path in declared:
            report.error(
                "METHODS_CONTRACT_MANIFEST_INVALID",
                f"Duplicate artifact path {path}",
                path=relative,
            )
            continue
        declared[path] = digest
    if set(declared) != required_paths:
        report.error(
            "METHODS_CONTRACT_MANIFEST_INVALID",
            "Methods contract manifest artifact set does not match the v0.3 contract",
            path=relative,
        )
        return
    for path, expected in sorted(declared.items()):
        candidate = project.root / path
        if not candidate.is_file():
            report.error(
                "METHODS_CONTRACT_ARTIFACT_MISSING",
                f"Missing methods artifact {path}",
                path=relative,
            )
        elif sha256_file(candidate) != expected:
            report.error(
                "METHODS_CONTRACT_ARTIFACT_DRIFT",
                f"Methods contract artifact checksum mismatch: {path}",
                path=relative,
            )


def _validate_observation(
    project: Project,
    table: ValidatedTable,
    row: dict[str, Any],
    index: int,
    report: Report,
    *,
    jurisdiction_ids: set[str],
    source_ids: set[str],
    indicator_ids: set[str],
    matter_ids: set[str],
    institution_ids: set[str],
    source_edition_ids: set[str],
    extraction_ids: set[str],
    review_ids: set[str],
    is_gold: bool,
) -> None:
    path = _relative(project, table.path)
    refs = [
        ("jurisdiction_id", jurisdiction_ids, "OBSERVATION_JURISDICTION_UNKNOWN"),
        ("source_id", source_ids, "OBSERVATION_SOURCE_UNKNOWN"),
        ("indicator_id", indicator_ids, "OBSERVATION_INDICATOR_UNKNOWN"),
        ("matter_type_harmonised", matter_ids, "OBSERVATION_MATTER_UNKNOWN"),
    ]
    for field, valid, code in refs:
        value = _text(row.get(field))
        if value and value not in valid:
            report.error(code, f"Unknown {field} {value!r}", path=path, row=index)

    optional_refs = [
        ("institution_id", institution_ids, "OBSERVATION_INSTITUTION_UNKNOWN"),
        ("source_edition_id", source_edition_ids, "OBSERVATION_SOURCE_EDITION_UNKNOWN"),
        ("extraction_id", extraction_ids, "OBSERVATION_EXTRACTION_UNKNOWN"),
        ("review_id", review_ids, "OBSERVATION_REVIEW_UNKNOWN"),
    ]
    for field, valid, code in optional_refs:
        value = _text(row.get(field))
        if value and valid and value not in valid:
            report.error(code, f"Unknown {field} {value!r}", path=path, row=index)

    _check_period(row, report, path, index)
    numeric_value = row.get("value")
    if isinstance(numeric_value, (int, float)) and not math.isfinite(float(numeric_value)):
        report.error("OBSERVATION_VALUE_NONFINITE", "value must be finite", path=path, row=index)
    unit = _text(row.get("unit"))
    if isinstance(numeric_value, (int, float)):
        if unit == "percent" and not 0 <= float(numeric_value) <= 100:
            report.error(
                "OBSERVATION_PERCENT_RANGE", "percent value must be 0-100", path=path, row=index
            )
        if unit == "proportion" and not 0 <= float(value) <= 1:
            report.error(
                "OBSERVATION_PROPORTION_RANGE", "proportion value must be 0-1", path=path, row=index
            )
    denominator = row.get("denominator_value")
    if isinstance(denominator, (int, float)) and denominator < 0:
        report.error(
            "OBSERVATION_NEGATIVE_DENOMINATOR",
            "denominator_value cannot be negative",
            path=path,
            row=index,
        )
    if bool(row.get("second_reviewed")) and not _text(row.get("second_reviewer")):
        report.warning(
            "OBSERVATION_SECOND_REVIEWER_BLANK",
            "second_reviewed is true but second_reviewer is blank",
            path=path,
            row=index,
        )
    is_timeliness = _text(row.get("indicator_id")).startswith("TIME_")
    if is_timeliness and (
        not _text(row.get("stage_start"))
        or not _text(row.get("stage_end"))
        or not _text(row.get("denominator_definition"))
    ):
        report.error(
            "OBSERVATION_TIMELINESS_SEMANTICS_INCOMPLETE",
            "Timeliness observations require stage_start, stage_end and denominator_definition",
            path=path,
            row=index,
        )
    elif row.get("stage_start") and not row.get("stage_end"):
        report.warning(
            "OBSERVATION_STAGE_END_BLANK",
            "stage_start is set but stage_end is blank",
            path=path,
            row=index,
        )
    elif row.get("stage_end") and not row.get("stage_start"):
        report.warning(
            "OBSERVATION_STAGE_START_BLANK",
            "stage_end is set but stage_start is blank",
            path=path,
            row=index,
        )

    if is_gold:
        gold_requirements = {
            "source_edition_id": "Gold observations require a source edition",
            "extraction_id": "Gold observations require an extraction record",
            "review_id": "Gold observations require a review record",
            "second_reviewer": "Gold observations require a named/role-coded second reviewer",
        }
        for field, message in gold_requirements.items():
            if not _text(row.get(field)):
                report.error("GOLD_LINEAGE_INCOMPLETE", message, path=path, row=index)
        if row.get("review_status") != "accepted":
            report.error(
                "GOLD_REVIEW_NOT_ACCEPTED",
                "Gold review_status must be accepted",
                path=path,
                row=index,
            )
        if row.get("second_reviewed") is not True:
            report.error(
                "GOLD_SECOND_REVIEW_MISSING",
                "Gold observations must be second reviewed",
                path=path,
                row=index,
            )
        if row.get("quality_grade") not in {"A", "B", "C"}:
            report.error(
                "GOLD_QUALITY_TOO_LOW", "Gold quality grade must be A, B or C", path=path, row=index
            )
        if row.get("comparability_tier") not in {1, 2}:
            report.error(
                "GOLD_COMPARABILITY_TOO_LOW",
                "Gold comparability tier must be 1 or 2",
                path=path,
                row=index,
            )
        if row.get("release_eligible") is not True:
            report.error(
                "GOLD_NOT_RELEASE_ELIGIBLE",
                "Gold release_eligible must be true",
                path=path,
                row=index,
            )
        if row.get("suppression_status") == "suppressed":
            report.error(
                "GOLD_SUPPRESSED_VALUE",
                "Suppressed observations cannot contain a released value",
                path=path,
                row=index,
            )


def _rows(grouped: dict[str, list[ValidatedTable]], contract_id: str) -> list[dict[str, Any]]:
    return [row for table in grouped.get(contract_id, []) for row in table.typed_rows]


def _check_unique(
    rows: list[dict[str, Any]],
    field: str,
    report: Report,
    path: str,
) -> set[str]:
    values: set[str] = set()
    for index, row in enumerate(rows, start=2):
        value = _text(row.get(field))
        if not value:
            continue
        if value in values:
            report.error(
                "REGISTER_DUPLICATE_ID", f"Duplicate {field} {value!r}", path=path, row=index
            )
        values.add(value)
    return values


def _check_period(row: dict[str, Any], report: Report, path: str, index: int) -> None:
    start = _date_value(row.get("period_start"))
    end = _date_value(row.get("period_end"))
    if start and end and start > end:
        report.error("PERIOD_DATE_ORDER", "period_start is after period_end", path=path, row=index)


def _date_value(value: Any) -> date | None:
    if isinstance(value, date):
        return value
    if isinstance(value, str) and value:
        try:
            return date.fromisoformat(value)
        except ValueError:
            return None
    return None


def _text(value: Any) -> str:
    return "" if value is None else str(value).strip()


def _relative(project: Project, path: Path) -> str:
    try:
        return str(path.relative_to(project.root))
    except ValueError:
        return str(path)


# Backwards-compatible helper used by the original starter test.
def validate(root: Path | None = None) -> list[str]:
    report = validate_project(root, include_security=True)
    return [issue.render() for issue in report.issues if issue.severity is Severity.ERROR]
