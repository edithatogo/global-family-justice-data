"""Prepare and verify the metadata-only G2 structural-preflight design bundle."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from .g2_concordance import G2ConcordanceResult, compare_g2_extractions
from .g2_holdout import _canonical_public_url, _verified_denylists
from .io import canonical_json_bytes, sha256_bytes, sha256_file, write_json


class G2StructuralPreflightError(ValueError):
    """Raised when a proposed preflight bundle is unsafe or irreproducible."""


DESIGN_MANIFEST_FILES = (
    "config/contract_lock.json",
    "config/g2_holdout_generic_extraction_contract.json",
    "config/g2_holdout_semantic_vocabulary.json",
    "config/g2_structural_eligibility_policy.json",
    "config/g2_structural_preflight_plan.json",
    "config/g2_structural_role_bundles.json",
    "config/g2_structural_selection_policy.json",
    "data/methods/g2/G2HOLDOUT-STRUCTURAL-PREFLIGHT-20260815-01/design/design-receipt.json",
    "data/methods/g2/G2HOLDOUT-STRUCTURAL-PREFLIGHT-20260815-01/design/oversampled-metadata-frame.json",
    "data/methods/g2/G2HOLDOUT-STRUCTURAL-PREFLIGHT-20260815-01/design/proposed-acquisition-manifest.json",
    "data/methods/g2/G2HOLDOUT-STRUCTURAL-PREFLIGHT-20260815-01/design/proposed-url-resolution-manifest.json",
    "data/methods/g2/G2HOLDOUT-STRUCTURAL-PREFLIGHT-20260815-01/panels/methods-design-report.json",
    "data/methods/g2/G2HOLDOUT-STRUCTURAL-PREFLIGHT-20260815-01/panels/operations-resource-report.json",
    "data/methods/g2/G2HOLDOUT-STRUCTURAL-PREFLIGHT-20260815-01/panels/security-access-report.json",
    "docs/methods/g2-two-stage-structural-preflight-plan-2026-08-15.md",
    "schemas/g2_artifact_access_receipt.schema.json",
    "schemas/g2_holdout_extraction_contract.schema.json",
    "schemas/g2_holdout_extraction_run_receipt.schema.json",
    "schemas/g2_holdout_extraction_row.schema.json",
    "schemas/g2_holdout_semantic_vocabulary.schema.json",
    "schemas/g2_extractor_bundle.schema.json",
    "schemas/g2_merged_eligibility_receipt.schema.json",
    "schemas/g2_proposed_acquisition_manifest.schema.json",
    "schemas/g2_proposed_url_resolution_manifest.schema.json",
    "schemas/g2_structural_capacity_receipt.schema.json",
    "schemas/g2_structural_eligibility_policy.schema.json",
    "schemas/g2_structural_preflight_design_receipt.schema.json",
    "schemas/g2_structural_preflight_frame.schema.json",
    "schemas/g2_structural_preflight_plan.schema.json",
    "schemas/g2_structural_preflight_record.schema.json",
    "schemas/g2_structural_role_bundles.schema.json",
    "schemas/g2_structural_selection_policy.schema.json",
    "schemas/g2_sealed_selection.schema.json",
    "src/gfjd/g2_concordance.py",
    "src/gfjd/g2_holdout.py",
    "src/gfjd/g2_structural_preflight.py",
    "src/gfjd/tooling_cli.py",
    "tests/test_g2_structural_preflight.py",
)


def classify_structural_record(root: Path, record: dict[str, Any]) -> str:
    """Validate a source-text-free record and recompute its structural class."""

    root = root.expanduser().resolve()
    _validate(root, "g2_structural_preflight_record.schema.json", record)
    policy = _load_object(root / "config/g2_structural_eligibility_policy.json")
    _validate(root, "g2_structural_eligibility_policy.schema.json", policy)
    safe = all(record[key] == value for key, value in policy["required_safe_conditions"].items())
    expected = _structural_stratum(record, policy)
    if record["disposition"] == "structurally_eligible":
        if not safe:
            raise G2StructuralPreflightError("eligible record violates a required safe condition")
        if expected == "indeterminate" or record["assigned_stratum"] != expected:
            raise G2StructuralPreflightError("eligible record has an inconsistent stratum")
        if record["reason_codes"]:
            raise G2StructuralPreflightError("eligible record cannot contain rejection reasons")
    elif not record["reason_codes"]:
        raise G2StructuralPreflightError("rejected record requires a reason code")
    return expected


def verify_artifact_access_receipt(
    root: Path,
    receipt_path: Path,
    *,
    expected_role: str,
    authority_path: Path,
    input_bundle_path: Path,
    tool_bundle_path: Path,
) -> list[str]:
    """Verify a role receipt against the exact frozen role bundle."""

    root = root.expanduser().resolve()
    try:
        receipt = _load_object(_confined(root, receipt_path))
        _validate(root, "g2_artifact_access_receipt.schema.json", receipt)
        bundles = _load_object(root / "config/g2_structural_role_bundles.json")
        _validate(root, "g2_structural_role_bundles.schema.json", bundles)
        roles = {str(item["role"]): item for item in bundles["roles"]}
        bundle = roles[str(receipt["role"])]
        if receipt["role"] != expected_role:
            raise G2StructuralPreflightError("access receipt role differs")
        expected_role_bundle = _artifact(root, root / "config/g2_structural_role_bundles.json")
        if receipt["role_bundle"] != expected_role_bundle:
            raise G2StructuralPreflightError("access receipt role-bundle digest differs")
        expected_descriptors = {
            "authority": _artifact(root, authority_path),
            "input_bundle": _artifact(root, input_bundle_path),
            "tool_bundle": _artifact(root, tool_bundle_path),
        }
        for name, expected in expected_descriptors.items():
            _verify_artifact_descriptor(root, receipt[name], label=f"access receipt {name}")
            if receipt[name] != expected:
                raise G2StructuralPreflightError(f"access receipt {name} binding differs")
        if receipt["network_mode"] != bundle["network"]:
            raise G2StructuralPreflightError("access receipt network mode differs")
        canonical_urls = [_canonical_public_url(url) for url in receipt["network_url_allowlist"]]
        if canonical_urls != receipt["network_url_allowlist"]:
            raise G2StructuralPreflightError("network URL allowlist is not canonical")
        expected_urls = _expected_network_urls(root, expected_role)
        if canonical_urls != expected_urls:
            raise G2StructuralPreflightError("access receipt network URL allowlist differs")
        allowed = set(bundle["input_allowlist"])
        denied = set(bundle["input_denylist"])
        path_allowlist = set(receipt["path_allowlist"])
        input_path = str(receipt["input_bundle"]["path"])
        if input_path not in path_allowlist:
            raise G2StructuralPreflightError("access input bundle is outside path allowlist")
        input_event_seen = False
        for event in receipt["access_events"]:
            artifact_class = str(event["artifact_class"])
            if artifact_class not in allowed or artifact_class in denied:
                raise G2StructuralPreflightError("access receipt contains forbidden class")
            if event["path"] not in path_allowlist:
                raise G2StructuralPreflightError("access event is outside the path allowlist")
            path = _confined(root, Path(event["path"]))
            if sha256_file(path) != event["sha256"]:
                raise G2StructuralPreflightError("access event digest differs")
            if event["path"] == input_path and event["sha256"] == receipt["input_bundle"]["sha256"]:
                input_event_seen = True
        if not input_event_seen:
            raise G2StructuralPreflightError("access input bundle has no matching access event")
        output_prefix = _confined(root, Path(receipt["output_prefix"]), require_exists=False)
        for output in receipt["outputs"]:
            if output["artifact_class"] != bundle["output_class"]:
                raise G2StructuralPreflightError("access output class differs")
            output_path = _confined(root, Path(output["path"]))
            try:
                output_path.relative_to(output_prefix)
            except ValueError as exc:
                raise G2StructuralPreflightError("access output is outside output prefix") from exc
            if sha256_file(output_path) != output["sha256"]:
                raise G2StructuralPreflightError("access output digest differs")
        if set(receipt["artifact_class_denylist"]) != denied:
            raise G2StructuralPreflightError("access receipt denylist differs")
        if receipt["denied_access_attempts"] or receipt["violations"]:
            raise G2StructuralPreflightError("access receipt records a violation")
    except (G2StructuralPreflightError, KeyError, OSError, TypeError, json.JSONDecodeError) as exc:
        return [str(exc)]
    return []


def _expected_network_urls(root: Path, role: str) -> list[str]:
    if role == "metadata_url_resolver":
        manifest = _load_object(
            root / "data/methods/g2/G2HOLDOUT-STRUCTURAL-PREFLIGHT-20260815-01/design/"
            "proposed-url-resolution-manifest.json"
        )
        return list(dict.fromkeys(str(entry["landing_page_url"]) for entry in manifest["entries"]))
    if role == "acquisition_custodian":
        manifest = _load_object(
            root / "data/methods/g2/G2HOLDOUT-STRUCTURAL-PREFLIGHT-20260815-01/design/"
            "proposed-acquisition-manifest.json"
        )
        return list(
            dict.fromkeys(str(entry["requested_entrypoint"]) for entry in manifest["entries"])
        )
    return []


def _verify_artifact_descriptor(root: Path, descriptor: Mapping[str, Any], *, label: str) -> Path:
    path = _confined(root, Path(str(descriptor["path"])))
    if sha256_file(path) != descriptor["sha256"]:
        raise G2StructuralPreflightError(f"{label} digest differs")
    return path


def verify_role_receipt_set(
    root: Path,
    receipt_paths: Sequence[Path],
    *,
    required_roles: Sequence[str],
    expected_bindings: Mapping[str, Mapping[str, Path]],
) -> list[str]:
    """Require one valid, fresh and distinct access receipt for every requested role."""

    root = root.expanduser().resolve()
    errors: list[str] = []
    roles: list[str] = []
    sessions: list[str] = []
    for path in receipt_paths:
        receipt = _load_object(_confined(root, path))
        role = str(receipt.get("role", ""))
        binding = expected_bindings.get(role)
        if binding is None:
            errors.append(f"{path}: no expected binding for role {role}")
            continue
        receipt_errors = verify_artifact_access_receipt(
            root,
            path,
            expected_role=role,
            authority_path=binding["authority_path"],
            input_bundle_path=binding["input_bundle_path"],
            tool_bundle_path=binding["tool_bundle_path"],
        )
        errors.extend(f"{path}: {error}" for error in receipt_errors)
        if not receipt_errors:
            roles.append(str(receipt["role"]))
            sessions.append(str(receipt["session_id"]))
    if sorted(roles) != sorted(required_roles):
        errors.append("role receipt set differs from the required roster")
    if len(sessions) != len(set(sessions)):
        errors.append("role receipt sessions are not distinct")
    return errors


def verify_capacity_receipt(root: Path, receipt_path: Path) -> list[str]:
    """Verify capacity and sandbox evidence against the exact frozen plan."""

    root = root.expanduser().resolve()
    try:
        receipt = _load_object(_confined(root, receipt_path))
        _validate(root, "g2_structural_capacity_receipt.schema.json", receipt)
        plan_path = root / "config/g2_structural_preflight_plan.json"
        if receipt["resource_plan"] != _artifact(root, plan_path):
            raise G2StructuralPreflightError("capacity resource-plan binding differs")
        plan = _load_object(plan_path)
        budget_digest = sha256_bytes(canonical_json_bytes(plan["resource_budget"]))
        if receipt["resource_budget_sha256"] != budget_digest:
            raise G2StructuralPreflightError("capacity resource-budget digest differs")
        for name in (
            "private_staging_receipt",
            "network_sandbox_receipt",
            "parser_sandbox_receipt",
        ):
            _verify_artifact_descriptor(root, receipt[name], label=f"capacity {name}")
    except (G2StructuralPreflightError, KeyError, OSError, TypeError, json.JSONDecodeError) as exc:
        return [str(exc)]
    return []


def compare_holdout_extractions(
    root: Path,
    *,
    sealed_selection_path: Path,
    primary_run_receipt_path: Path,
    secondary_run_receipt_path: Path,
    owner_authorization_path: Path,
    **kwargs: Any,
) -> G2ConcordanceResult:
    """Run the generic holdout comparator using only the frozen contract."""

    root = root.expanduser().resolve()
    contract = _load_object(root / "config/g2_holdout_generic_extraction_contract.json")
    _validate(root, "g2_holdout_extraction_contract.schema.json", contract)
    forbidden = {
        "row_schema_path",
        "critical_fields",
        "overall_threshold",
        "ignored_fields",
        "threshold_policy",
        "expected_source_keys",
        "required_field_values",
        "primary_receipt",
        "secondary_receipt",
    }
    overlap = forbidden.intersection(kwargs)
    if overlap:
        raise G2StructuralPreflightError(
            "frozen comparator settings cannot be overridden: " + ", ".join(sorted(overlap))
        )
    selection_path = _confined(root, sealed_selection_path)
    selection = _load_object(selection_path)
    _validate(root, "g2_sealed_selection.schema.json", selection)
    expected_selection_policy = _artifact(root, root / "config/g2_structural_selection_policy.json")
    if selection["selection_policy"] != expected_selection_policy:
        raise G2StructuralPreflightError("sealed selection policy binding differs")
    eligibility_path = _verify_artifact_descriptor(
        root, selection["eligibility_receipt"], label="sealed eligibility receipt"
    )
    reproduced = select_structural_scope(root, eligibility_path)
    if reproduced is None:
        raise G2StructuralPreflightError("sealed selection is not reproducible")
    primary_entries = selection["primary"]
    all_entries = [*primary_entries, *selection["reserves"]]
    for field in ("source_record_key", "candidate_id", "source_edition_id", "source_sha256"):
        values = [str(entry[field]) for entry in all_entries]
        if len(values) != len(set(values)):
            raise G2StructuralPreflightError(f"sealed selection repeats {field}")
    if int(selection["prefix_end_rank"]) != int(reproduced["prefix_end_rank"]):
        raise G2StructuralPreflightError("sealed selection prefix differs")
    for name in ("primary", "reserves"):
        selected_tuples = [
            (
                str(entry["candidate_id"]),
                str(entry["source_id"]),
                str(entry["source_edition_id"]),
                str(entry["source_sha256"]),
                str(entry["assigned_stratum"]),
                int(entry["frame_rank"]),
            )
            for entry in selection[name]
        ]
        reproduced_tuples = [
            (
                str(entry["candidate_id"]),
                str(entry["source_id"]),
                str(entry["edition_id"]),
                str(entry["source_sha256"]),
                str(entry["assigned_stratum"]),
                int(entry["frame_rank"]),
            )
            for entry in reproduced[name]
        ]
        if selected_tuples != reproduced_tuples:
            raise G2StructuralPreflightError(f"sealed selection {name} differs")
    selection_artifact = _artifact(root, selection_path)
    authority_path = _confined(root, owner_authorization_path)
    authority_artifact = _artifact(root, authority_path)
    contract_artifact = _artifact(root, root / "config/g2_holdout_generic_extraction_contract.json")
    row_schema_artifact = _artifact(root, root / str(contract["row_schema"]))
    primary_output_path = _confined(root, Path(kwargs["primary_path"]))
    secondary_output_path = _confined(root, Path(kwargs["secondary_path"]))
    run_receipts: list[tuple[Path, dict[str, Any], str, Path]] = []
    for receipt_path, expected_role, output_path in (
        (primary_run_receipt_path, "primary_extractor", primary_output_path),
        (secondary_run_receipt_path, "secondary_extractor", secondary_output_path),
    ):
        resolved_receipt = _confined(root, receipt_path)
        receipt = _load_object(resolved_receipt)
        _validate(root, "g2_holdout_extraction_run_receipt.schema.json", receipt)
        if receipt["role"] != expected_role:
            raise G2StructuralPreflightError("extraction run role differs")
        if receipt["sealed_selection"] != selection_artifact:
            raise G2StructuralPreflightError("extraction run selection binding differs")
        if receipt["extraction_contract"] != contract_artifact:
            raise G2StructuralPreflightError("extraction run contract binding differs")
        if receipt["row_schema"] != row_schema_artifact:
            raise G2StructuralPreflightError("extraction run row-schema binding differs")
        if receipt["output"] != _artifact(root, output_path):
            raise G2StructuralPreflightError("extraction run output binding differs")
        bundle_path = _verify_artifact_descriptor(
            root, receipt["extractor_bundle"], label="extractor bundle"
        )
        _verify_extractor_bundle(root, bundle_path, primary_entries, authority_artifact)
        access_path = _verify_artifact_descriptor(
            root, receipt["access_receipt"], label="extraction access receipt"
        )
        access_errors = verify_artifact_access_receipt(
            root,
            access_path,
            expected_role=expected_role,
            authority_path=authority_path,
            input_bundle_path=bundle_path,
            tool_bundle_path=_confined(root, Path(str(contract["row_schema"]))),
        )
        if access_errors:
            raise G2StructuralPreflightError(access_errors[0])
        access = _load_object(access_path)
        if access["role"] != expected_role or access["session_id"] != receipt["session_id"]:
            raise G2StructuralPreflightError("access receipt role or session differs")
        if access["input_bundle"] != receipt["extractor_bundle"]:
            raise G2StructuralPreflightError("access receipt input bundle differs")
        expected_output_class = f"{expected_role.removesuffix('_extractor')}_extraction_output"
        expected_output = {"artifact_class": expected_output_class, **receipt["output"]}
        if access["outputs"] != [expected_output]:
            raise G2StructuralPreflightError("access receipt output binding differs")
        run_receipts.append((resolved_receipt, receipt, expected_role, output_path))
    if run_receipts[0][1]["session_id"] == run_receipts[1][1]["session_id"]:
        raise G2StructuralPreflightError("extraction sessions must be distinct")
    if any(receipt[1]["source_commit"] != kwargs["source_commit"] for receipt in run_receipts):
        raise G2StructuralPreflightError("extraction run source commit differs")
    expected_keys = [str(entry["source_record_key"]) for entry in primary_entries]
    required_values = {
        str(entry["source_record_key"]): {
            "candidate_id": entry["candidate_id"],
            "source_id": entry["source_id"],
            "source_edition_id": entry["source_edition_id"],
        }
        for entry in primary_entries
    }
    return compare_g2_extractions(
        root,
        row_schema_path=Path(contract["row_schema"]),
        critical_fields=contract["critical_fields"],
        overall_threshold=float(contract["overall_populated_concordance"]),
        ignored_fields=("extracted_row_id", "source_record_key", "notes"),
        threshold_policy=_artifact(
            root, root / "config/g2_holdout_generic_extraction_contract.json"
        ),
        expected_source_keys=expected_keys,
        required_field_values=required_values,
        primary_receipt=_artifact(root, run_receipts[0][0]),
        secondary_receipt=_artifact(root, run_receipts[1][0]),
        **kwargs,
    )


def _verify_extractor_bundle(
    root: Path,
    bundle_path: Path,
    primary_entries: Sequence[Mapping[str, Any]],
    expected_authority: Mapping[str, Any],
) -> None:
    bundle = _load_object(bundle_path)
    _validate(root, "g2_extractor_bundle.schema.json", bundle)
    expected_contract = _artifact(root, root / "config/g2_holdout_generic_extraction_contract.json")
    expected_schema = _artifact(root, root / "schemas/g2_holdout_extraction_row.schema.json")
    if (
        bundle["extraction_contract"] != expected_contract
        or bundle["row_schema"] != expected_schema
    ):
        raise G2StructuralPreflightError("extractor bundle contract binding differs")
    selected = {
        (
            str(entry["candidate_id"]),
            str(entry["source_id"]),
            str(entry["source_edition_id"]),
            str(entry["source_sha256"]),
        )
        for entry in primary_entries
    }
    bundled = {
        (
            str(entry["candidate_id"]),
            str(entry["source_id"]),
            str(entry["source_edition_id"]),
            str(entry["source_sha256"]),
        )
        for entry in bundle["primary_editions"]
    }
    if bundled != selected:
        raise G2StructuralPreflightError("extractor bundle differs from sealed primary selection")
    source_paths: set[str] = set()
    for entry in bundle["primary_editions"]:
        private_path = str(entry["private_source_path"])
        if private_path in source_paths:
            raise G2StructuralPreflightError("extractor bundle repeats a private source path")
        source_paths.add(private_path)
        source_path = _confined(root, Path(private_path))
        if sha256_file(source_path) != entry["source_sha256"]:
            raise G2StructuralPreflightError("extractor bundle source digest differs")
    _verify_artifact_descriptor(root, bundle["owner_authorization"], label="owner authorization")
    if bundle["owner_authorization"] != expected_authority:
        raise G2StructuralPreflightError("extractor bundle owner authorization binding differs")


def select_structural_scope(root: Path, eligibility_receipt_path: Path) -> dict[str, Any] | None:
    """Select the first feasible exact 24+6 scope using the frozen algorithm."""

    root = root.expanduser().resolve()
    policy = _load_object(root / "config/g2_structural_selection_policy.json")
    _validate(root, "g2_structural_selection_policy.schema.json", policy)
    receipt = _load_object(_confined(root, eligibility_receipt_path))
    _validate(root, "g2_merged_eligibility_receipt.schema.json", receipt)
    expected_bindings = {
        "structural_policy": root / "config/g2_structural_eligibility_policy.json",
        "selection_policy": root / "config/g2_structural_selection_policy.json",
    }
    for name, path in expected_bindings.items():
        if receipt[name] != _artifact(root, path):
            raise G2StructuralPreflightError(f"eligibility receipt {name} binding differs")
    frame_path = _verify_artifact_descriptor(root, receipt["frame"], label="eligibility frame")
    frame = _load_object(frame_path)
    _validate(root, "g2_structural_preflight_frame.schema.json", frame)
    frame_by_id = {str(item["candidate_id"]): item for item in frame["candidates"]}
    records: list[dict[str, Any]] = []
    seen_record_paths: set[str] = set()
    for descriptor in receipt["records"]:
        relative = str(descriptor["path"])
        if relative in seen_record_paths:
            raise G2StructuralPreflightError("eligibility receipt repeats a record path")
        seen_record_paths.add(relative)
        record_path = _confined(root, Path(relative))
        if descriptor != _artifact(root, record_path):
            raise G2StructuralPreflightError(f"eligibility record binding differs: {relative}")
        record = _load_object(record_path)
        classify_structural_record(root, record)
        framed = frame_by_id.get(str(record["candidate_id"]))
        if framed is None:
            raise G2StructuralPreflightError("eligibility record is outside the frozen frame")
        for key in (
            "edition_id",
            "jurisdiction_id",
            "source_series_id",
            "source_url",
            "frame_rank",
        ):
            if record[key] != framed[key]:
                raise G2StructuralPreflightError(f"eligibility record frame mismatch: {key}")
        records.append(record)
    prefix_end = int(receipt["inspected_prefix_end_rank"])
    record_ranks = [int(record["frame_rank"]) for record in records]
    if sorted(record_ranks) != list(range(1, prefix_end + 1)):
        raise G2StructuralPreflightError(
            "eligibility receipt must cover every rank in the inspected prefix exactly once"
        )
    eligible = sorted(
        (
            dict(record)
            for record in records
            if record.get("disposition") == "structurally_eligible"
        ),
        key=lambda record: (int(record["frame_rank"]), str(record["candidate_id"])),
    )
    ranks = [int(record["frame_rank"]) for record in eligible]
    if len(ranks) != len(set(ranks)):
        raise G2StructuralPreflightError("eligible records contain duplicate frame ranks")
    for end in ranks:
        prefix = [record for record in eligible if int(record["frame_rank"]) <= end]
        chosen = _assign_structural_slots(prefix, policy)
        if chosen is not None:
            primary, reserves = chosen
            return {"prefix_end_rank": end, "primary": primary, "reserves": reserves}
    return None


def _assign_structural_slots(
    candidates: Sequence[dict[str, Any]], policy: Mapping[str, Any]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]] | None:
    slots: list[tuple[str, str]] = []
    for spec in policy["slot_order"]:
        assignment, stratum, span = str(spec).split(":", 2)
        count = int(span.split("-")[-1])
        slots.extend((assignment, stratum) for _ in range(count))
    selected: list[tuple[str, dict[str, Any]]] = []
    jurisdiction_counts: Counter[str] = Counter()
    used_editions: set[str] = set()
    used_series: set[str] = set()
    used_urls: set[str] = set()
    search_nodes = 0

    def visit(position: int, offsets: dict[str, int]) -> bool:
        nonlocal search_nodes
        search_nodes += 1
        if search_nodes > int(policy["maximum_search_nodes"]):
            raise G2StructuralPreflightError("selection search-node budget exhausted")
        if position == len(slots):
            primary_jurisdictions = {
                item["jurisdiction_id"] for assignment, item in selected if assignment == "primary"
            }
            return len(primary_jurisdictions) >= int(policy["minimum_primary_jurisdictions"])
        assignment, stratum = slots[position]
        matches = [item for item in candidates if item["assigned_stratum"] == stratum]
        for index in range(offsets.get(stratum, 0), len(matches)):
            item = matches[index]
            jurisdiction = str(item["jurisdiction_id"])
            edition = str(item["edition_id"])
            series = str(item["source_series_id"])
            source_url = _canonical_public_url(item["source_url"])
            if (
                jurisdiction_counts[jurisdiction]
                >= int(policy["maximum_selected_per_jurisdiction"])
                or edition in used_editions
                or series in used_series
                or source_url in used_urls
            ):
                continue
            selected.append((assignment, item))
            jurisdiction_counts[jurisdiction] += 1
            used_editions.add(edition)
            used_series.add(series)
            used_urls.add(source_url)
            next_offsets = dict(offsets)
            next_offsets[stratum] = index + 1
            if visit(position + 1, next_offsets):
                return True
            selected.pop()
            jurisdiction_counts[jurisdiction] -= 1
            used_editions.remove(edition)
            used_series.remove(series)
            used_urls.remove(source_url)
        return False

    if not visit(0, {}):
        return None
    primary = [item for assignment, item in selected if assignment == "primary"]
    reserves = [item for assignment, item in selected if assignment == "reserve"]
    return primary, reserves


def _structural_stratum(record: dict[str, Any], policy: dict[str, Any]) -> str:
    classifier = policy["classifier"]
    if (
        record["raster_page_ratio"]
        >= classifier["embedded_raster_or_dashboard_pdf"]["minimum_raster_page_ratio"]
    ):
        return "embedded_raster_or_dashboard_pdf"
    if (
        record["complex_page_ratio"]
        >= classifier["structurally_complex_mixed_layout_pdf"]["minimum_complex_page_ratio"]
    ):
        return "structurally_complex_mixed_layout_pdf"
    language = record["primary_language_code"]
    if language != classifier["non_english_text_native"]["primary_language_must_not_equal"]:
        return "non_english_text_native"
    if language == classifier["english_text_native"]["primary_language_must_equal"]:
        return "english_text_native"
    return "indeterminate"


def prepare_structural_preflight_design(
    root: Path,
    *,
    output_dir: Path,
    generated_at: str,
    plan_path: Path = Path("config/g2_structural_preflight_plan.json"),
) -> tuple[Path, Path, Path]:
    """Freeze a frame and proposed manifest without performing source access."""

    root = root.expanduser().resolve()
    plan_file = _confined(root, plan_path)
    plan = _load_object(plan_file)
    _validate(root, "g2_structural_preflight_plan.schema.json", plan)
    role_bundles = _load_object(root / plan["contracts"]["role_bundle_contract"])
    _validate(root, "g2_structural_role_bundles.schema.json", role_bundles)
    selection_policy = _load_object(root / plan["contracts"]["selection_policy"])
    _validate(root, "g2_structural_selection_policy.schema.json", selection_policy)
    extraction_contract = _load_object(root / plan["contracts"]["generic_extraction_contract"])
    _validate(root, "g2_holdout_extraction_contract.schema.json", extraction_contract)
    semantic_vocabulary = _load_object(root / plan["contracts"]["semantic_vocabulary"])
    _validate(root, "g2_holdout_semantic_vocabulary.schema.json", semantic_vocabulary)
    eligibility_policy = _load_object(root / plan["contracts"]["structural_eligibility_policy"])
    _validate(root, "g2_structural_eligibility_policy.schema.json", eligibility_policy)
    for schema_key in (
        "artifact_access_receipt_schema",
        "capacity_receipt_schema",
        "generic_extraction_row_schema",
        "extractor_bundle_schema",
        "extraction_run_receipt_schema",
        "merged_eligibility_receipt_schema",
        "sealed_selection_schema",
        "structural_preflight_record_schema",
    ):
        _load_object(_confined(root, Path(plan["contracts"][schema_key])))
    policy = plan["frame_policy"]
    universe_file = _confined(root, Path(policy["candidate_universe"]))
    ledger_file = _confined(root, Path(policy["exposure_ledger"]))
    universe = _load_object(universe_file)
    ledger = _load_object(ledger_file)
    _validate(root, "g2_holdout_candidate_universe.schema.json", universe)
    _validate(root, "g2_holdout_exposure_ledger.schema.json", ledger)
    denied_editions, denied_series, denied_urls = _verified_denylists(root, ledger)

    candidates: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    seen_editions: set[str] = set()
    seen_series: set[str] = set()
    for candidate in universe["candidates"]:
        if not _frame_candidate(candidate, denied_editions, denied_series, denied_urls):
            continue
        candidate_id = str(candidate["candidate_id"])
        edition_id = str(candidate["edition_id"])
        source_series_id = str(candidate["source_series_id"])
        if (
            candidate_id in seen_ids
            or edition_id in seen_editions
            or source_series_id in seen_series
        ):
            raise G2StructuralPreflightError("frame contains a duplicate identity or source series")
        seen_ids.add(candidate_id)
        seen_editions.add(edition_id)
        seen_series.add(source_series_id)
        score = _score(str(policy["ordering_seed"]), candidate_id, edition_id, source_series_id)
        source_url = candidate["source_url"]
        entrypoint = source_url or candidate["landing_page_url"]
        candidates.append(
            {
                "frame_score": score,
                "candidate_id": candidate_id,
                "edition_id": edition_id,
                "jurisdiction_id": candidate["jurisdiction_id"],
                "source_series_id": source_series_id,
                "edition_title": candidate["edition_title"],
                "publisher": candidate["publisher"],
                "languages": candidate["languages"],
                "landing_page_url": _canonical_public_url(candidate["landing_page_url"]),
                "source_url": _canonical_public_url(source_url) if source_url else None,
                "retrieval_entrypoint": _canonical_public_url(entrypoint),
                "retrieval_entrypoint_kind": (
                    "exact_pdf_url" if source_url else "official_landing_page_requires_resolution"
                ),
                "metadata_provenance_urls": sorted(
                    {_canonical_public_url(url) for url in candidate["metadata_evidence_urls"]}
                ),
                "proposed_stratum": candidate["proposed_stratum"],
                "prior_metadata_eligibility": candidate["eligibility"],
                "rights_screen": candidate["rights_screen"],
                "privacy_screen": candidate["privacy_screen"],
                "security_screen": candidate["security_screen"],
                "prohibited_data_screen": candidate["prohibited_data_screen"],
                "source_content_accessed": False,
                "source_access_authorized": False,
            }
        )
    candidates.sort(key=lambda row: (row["frame_score"], row["candidate_id"]))
    for rank, candidate in enumerate(candidates, 1):
        candidate["frame_rank"] = rank
    expected = int(policy["expected_frame_count"])
    if len(candidates) != expected:
        raise G2StructuralPreflightError(
            f"frame count drift: expected {expected}, reproduced {len(candidates)}"
        )

    destination = _confined(root, output_dir, require_exists=False)
    destination.mkdir(parents=True, exist_ok=True)
    frame_path = destination / "oversampled-metadata-frame.json"
    frame = {
        "schema_version": "1.0",
        "frame_id": "G2HOLDOUT-STRUCTURAL-FRAME-20260815-01",
        "plan_id": plan["plan_id"],
        "metadata_only": True,
        "source_content_accessed": False,
        "ordering_seed": policy["ordering_seed"],
        "ordering_algorithm": policy["ordering_algorithm"],
        "candidate_count": len(candidates),
        "candidates": candidates,
        "limitations": [
            "The 44-candidate frame is the complete safe projection of already archived "
            "metadata under the frozen rules; it is only 1.47 times the required "
            "30-edition sealed scope.",
            "Only metadata is frozen; exact bytes, content digests, structural classes "
            "and extraction eligibility remain unknown.",
            "A landing-page entrypoint is not an exact PDF URL and must be resolved only "
            "after separate owner authorization.",
            "The design may fail closed if the frozen frame cannot yield the exact "
            "24-primary plus six-reserve scope.",
        ],
    }
    write_json(frame_path, frame)
    _validate(root, "g2_structural_preflight_frame.schema.json", frame)

    exact_candidates = [row for row in candidates if row["source_url"] is not None]
    resolution_candidates = [row for row in candidates if row["source_url"] is None]
    exact_urls = [str(row["source_url"]) for row in exact_candidates]
    if len(set(exact_urls)) != len(exact_urls):
        raise G2StructuralPreflightError("exact acquisition URLs must be unique")

    resolution_path = destination / "proposed-url-resolution-manifest.json"
    resolution = {
        "schema_version": "1.0",
        "manifest_id": "G2HOLDOUT-PROPOSED-URL-RESOLUTION-20260815-01",
        "plan_id": plan["plan_id"],
        "frame": _artifact(root, frame_path),
        "status": "proposed_not_authorized",
        "metadata_request_performed": False,
        "entry_count": len(resolution_candidates),
        "entries": [
            {
                "frame_rank": row["frame_rank"],
                "candidate_id": row["candidate_id"],
                "edition_id": row["edition_id"],
                "landing_page_url": row["landing_page_url"],
                "method": "proposed_metadata_html_resolution",
                "expected_media_type": "text/html",
                "source_content_access_allowed": False,
                "status": "proposed_not_authorized",
                "resolved_exact_pdf_url": None,
            }
            for row in resolution_candidates
        ],
    }
    write_json(resolution_path, resolution)
    _validate(root, "g2_proposed_url_resolution_manifest.schema.json", resolution)

    acquisition_path = destination / "proposed-acquisition-manifest.json"
    budget = plan["resource_budget"]
    acquisition = {
        "schema_version": "1.0",
        "manifest_id": "G2HOLDOUT-PROPOSED-ACQUISITION-20260815-01",
        "plan_id": plan["plan_id"],
        "frame": _artifact(root, frame_path),
        "status": "proposed_not_authorized",
        "source_request_performed": False,
        "entry_count": len(exact_candidates),
        "entries": [
            {
                "frame_rank": row["frame_rank"],
                "candidate_id": row["candidate_id"],
                "edition_id": row["edition_id"],
                "jurisdiction_id": row["jurisdiction_id"],
                "source_series_id": row["source_series_id"],
                "requested_entrypoint": row["source_url"],
                "entrypoint_kind": "exact_pdf_url",
                "expected_media_type": "application/pdf",
                "method": "proposed_https_get",
                "status": "proposed_not_authorized",
                "maximum_bytes": budget["maximum_bytes_per_edition"],
                "maximum_pages": budget["maximum_pages_per_edition"],
                "custody_class": "controlled_local_private",
                "redistribution_boundary": "metadata_and_citation_only",
                "acquisition_role": "acquisition_custodian",
                "actual_sha256": None,
                "retrieved_at": None,
                "final_url": None,
                "byte_count": None,
                "actual_content_type": None,
                "stored_path": None,
            }
            for row in exact_candidates
        ],
        "limits": budget,
    }
    write_json(acquisition_path, acquisition)
    _validate(root, "g2_proposed_acquisition_manifest.schema.json", acquisition)

    receipt_path = destination / "design-receipt.json"
    receipt = {
        "schema_version": "1.0",
        "receipt_id": "G2HOLDOUT-STRUCTURAL-DESIGN-RECEIPT-20260815-01",
        "plan": _artifact(root, plan_file),
        "plan_schema": _artifact(root, root / "schemas/g2_structural_preflight_plan.schema.json"),
        "owner_decision": _artifact(
            root,
            root / "docs/governance/g2-blind-holdout-intake-stop-owner-decision-2026-08-15.md",
        ),
        "candidate_universe": _artifact(root, universe_file),
        "exposure_ledger": _artifact(root, ledger_file),
        "frame": _artifact(root, frame_path),
        "frame_schema": _artifact(root, root / "schemas/g2_structural_preflight_frame.schema.json"),
        "proposed_acquisition_manifest": _artifact(root, acquisition_path),
        "proposed_acquisition_schema": _artifact(
            root, root / "schemas/g2_proposed_acquisition_manifest.schema.json"
        ),
        "proposed_url_resolution_manifest": _artifact(root, resolution_path),
        "proposed_url_resolution_schema": _artifact(
            root, root / "schemas/g2_proposed_url_resolution_manifest.schema.json"
        ),
        "source_access_performed": False,
        "source_access_authorized": False,
        "frame_count": len(candidates),
        "generated_at": generated_at,
    }
    write_json(receipt_path, receipt)
    _validate(root, "g2_structural_preflight_design_receipt.schema.json", receipt)
    return frame_path, acquisition_path, receipt_path


def verify_structural_preflight_design(root: Path, *, output_dir: Path) -> list[str]:
    """Recompute and byte-compare the frozen metadata-only design artifacts."""

    root = root.expanduser().resolve()
    destination = _confined(root, output_dir)
    try:
        existing_receipt = _load_object(destination / "design-receipt.json")
        generated_at = str(existing_receipt["generated_at"])
        import tempfile

        build_root = root / "build"
        build_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="gfjd-g2-preflight-", dir=build_root) as temporary:
            temp_path = Path(temporary)
            frame_path, acquisition_path, receipt_path = prepare_structural_preflight_design(
                root, output_dir=temp_path, generated_at=generated_at
            )
            actual_frame = destination / "oversampled-metadata-frame.json"
            if actual_frame.read_bytes() != frame_path.read_bytes():
                raise G2StructuralPreflightError("frame does not reproduce")
            actual_manifest_path = destination / "proposed-acquisition-manifest.json"
            actual_manifest = _load_object(actual_manifest_path)
            expected_manifest = _load_object(acquisition_path)
            expected_manifest["frame"] = _artifact(root, actual_frame)
            if actual_manifest != expected_manifest:
                raise G2StructuralPreflightError("proposed acquisition manifest does not reproduce")
            actual_resolution = destination / "proposed-url-resolution-manifest.json"
            expected_resolution = temp_path / "proposed-url-resolution-manifest.json"
            actual_resolution_value = _load_object(actual_resolution)
            expected_resolution_value = _load_object(expected_resolution)
            expected_resolution_value["frame"] = _artifact(root, actual_frame)
            if actual_resolution_value != expected_resolution_value:
                raise G2StructuralPreflightError(
                    "proposed URL-resolution manifest does not reproduce"
                )
            actual_receipt = _load_object(destination / "design-receipt.json")
            expected_receipt = _load_object(receipt_path)
            expected_receipt["frame"] = _artifact(root, actual_frame)
            expected_receipt["proposed_acquisition_manifest"] = _artifact(
                root, actual_manifest_path
            )
            expected_receipt["proposed_url_resolution_manifest"] = _artifact(
                root, actual_resolution
            )
            if actual_receipt != expected_receipt:
                raise G2StructuralPreflightError("design receipt does not reproduce")
        canonical_design = root / (
            "data/methods/g2/G2HOLDOUT-STRUCTURAL-PREFLIGHT-20260815-01/design"
        )
        if destination == canonical_design:
            _verify_detached_manifest(root, destination.parent / "DESIGN_MANIFEST.sha256")
            _verify_panel_bindings(root, destination.parent / "panels")
    except (G2StructuralPreflightError, OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        return [str(exc)]
    return []


def _verify_detached_manifest(root: Path, manifest_path: Path) -> None:
    lines = manifest_path.read_text(encoding="utf-8").splitlines()
    found: dict[str, str] = {}
    for line in lines:
        digest, separator, relative = line.partition("  ")
        if (
            separator != "  "
            or relative in found
            or len(digest) != 64
            or any(character not in "0123456789abcdef" for character in digest)
        ):
            raise G2StructuralPreflightError("detached design manifest is malformed")
        found[relative] = digest
    expected = set(DESIGN_MANIFEST_FILES)
    if set(found) != expected:
        raise G2StructuralPreflightError("detached design manifest artifact set differs")
    for relative in sorted(expected):
        path = _confined(root, Path(relative))
        if sha256_file(path) != found[relative]:
            raise G2StructuralPreflightError(f"detached design manifest mismatch: {relative}")
    design_dir = root / "data/methods/g2/G2HOLDOUT-STRUCTURAL-PREFLIGHT-20260815-01/design"
    expected_design = {Path(path).name for path in expected if "/design/" in path}
    if {path.name for path in design_dir.iterdir() if path.is_file()} != expected_design:
        raise G2StructuralPreflightError("design directory artifact set differs")


def _verify_panel_bindings(root: Path, panel_dir: Path) -> None:
    panel_schema = _load_object(root / "schemas/agent_panel_report.schema.json")
    expected_names = {
        "methods-design-report.json",
        "operations-resource-report.json",
        "security-access-report.json",
    }
    if {path.name for path in panel_dir.glob("*.json")} != expected_names:
        raise G2StructuralPreflightError("panel artifact set differs")
    validator = Draft202012Validator(panel_schema, format_checker=FormatChecker())
    for panel_path in sorted(panel_dir.glob("*.json")):
        panel = _load_object(panel_path)
        errors = list(validator.iter_errors(panel))
        if errors:
            raise G2StructuralPreflightError(f"panel schema failure: {panel_path.name}")
        for artifact in panel["evidence_inputs"]:
            path = _confined(root, Path(artifact["path"]))
            if sha256_file(path) != artifact["sha256"]:
                raise G2StructuralPreflightError(
                    f"panel evidence mismatch: {panel_path.name}: {artifact['path']}"
                )


def _frame_candidate(
    candidate: dict[str, Any],
    denied_editions: set[str],
    denied_series: set[str],
    denied_urls: set[str],
) -> bool:
    if (
        candidate["eligibility"] == "ineligible"
        or not candidate["official_publisher"]
        or candidate["format"] != "pdf"
        or candidate["source_content_accessed"]
        or candidate["edition_id"] in denied_editions
        or candidate["source_series_id"] in denied_series
    ):
        return False
    urls = [candidate["landing_page_url"], *candidate["metadata_evidence_urls"]]
    if candidate["source_url"]:
        urls.append(candidate["source_url"])
    return not any(_canonical_public_url(url) in denied_urls for url in urls)


def _score(seed: str, candidate_id: str, edition_id: str, source_series_id: str) -> str:
    value = "\0".join((seed, candidate_id, edition_id, source_series_id)).encode()
    return hashlib.sha256(value).hexdigest()


def _artifact(root: Path, path: Path) -> dict[str, str]:
    resolved = path.resolve()
    return {"path": resolved.relative_to(root).as_posix(), "sha256": sha256_file(resolved)}


def _load_object(path: Path) -> dict[str, Any]:
    def no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise G2StructuralPreflightError(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=no_duplicates)
    if not isinstance(value, dict):
        raise G2StructuralPreflightError(f"expected JSON object: {path}")
    return value


def _validate(root: Path, schema_name: str, value: dict[str, Any]) -> None:
    schema = _load_object(root / "schemas" / schema_name)
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(value),
        key=lambda item: list(item.absolute_path),
    )
    if errors:
        raise G2StructuralPreflightError(f"{schema_name}: {errors[0].message}")


def _confined(root: Path, path: Path, *, require_exists: bool = True) -> Path:
    resolved = path.resolve() if path.is_absolute() else (root / path).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise G2StructuralPreflightError("path escapes repository") from exc
    if require_exists and not resolved.exists():
        raise G2StructuralPreflightError(f"required path is missing: {resolved}")
    return resolved
