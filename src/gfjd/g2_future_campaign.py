"""Fail-closed execution controls for the prospective four-route G2 campaign."""

from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from .g2_future_exposure import (
    canonical_request_identity,
    canonical_url,
    verify_exposure_snapshot,
)
from .io import sha256_file

CAMPAIGN_ID = "G2PROSPECTIVE-CALIBRATION-20260829-01"
CONTROL_ROOT = Path("data/methods/g2") / CAMPAIGN_ID / "execution-control"
STRATA = ("api_or_json", "html_or_dashboard", "spreadsheet", "pdf")
ROLES = (
    "orchestrator",
    "candidate_registrar",
    "extractor_a",
    "extractor_b",
    "network_disabled_comparator",
    "advisory_reviewer",
)
SELECTION_ALGORITHM = "sha256_query_manifest_nul_candidate_identity_ascending_backtracking_v1"


class G2FutureCampaignError(ValueError):
    """Raised when a future-campaign artifact fails a frozen control."""


def verify_query_manifest(root: Path, path: Path) -> list[str]:
    """Verify a frozen, ordered and bounded query manifest."""

    try:
        root = root.expanduser().resolve()
        payload = _object(_confined(root, path))
        _validate(root, "query-manifest.schema.json", payload)
        queries = payload["queries"]
        if [item["ordinal"] for item in queries] != list(range(1, len(queries) + 1)):
            raise G2FutureCampaignError("query ordinals must be contiguous and ordered")
        if payload["call_policy"]["maximum_calls"] != len(queries):
            raise G2FutureCampaignError("maximum_calls must equal the frozen query count")
        for field in ("query_id", "query_text"):
            values = [str(item[field]) for item in queries]
            if len(values) != len(set(values)):
                raise G2FutureCampaignError(f"query manifest repeats {field}")
        if set(item["route_stratum"] for item in queries) != set(STRATA):
            raise G2FutureCampaignError("query manifest must cover every route stratum")
    except (G2FutureCampaignError, OSError, TypeError, KeyError, json.JSONDecodeError) as exc:
        return [str(exc)]
    return []


def verify_candidate_registry(root: Path, path: Path) -> list[str]:
    """Verify complete, ordered registration without trusting overlap claims."""

    try:
        root = root.expanduser().resolve()
        registry_path = _confined(root, path)
        registry = _object(registry_path)
        _validate(root, "candidate-registry.schema.json", registry)
        query_path = _bound(root, registry["query_manifest"], "query manifest")
        query_errors = verify_query_manifest(root, query_path)
        if query_errors:
            raise G2FutureCampaignError(query_errors[0])
        manifest = _object(query_path)
        exposure_manifest_path = _bound(
            root, registry["exposure_input_manifest"], "exposure input manifest"
        )
        exposure_snapshot_path = _bound(root, registry["exposure_snapshot"], "exposure snapshot")
        exposure_manifest = _object(exposure_manifest_path)
        exposure_snapshot = _object(exposure_snapshot_path)
        exposure_errors = verify_exposure_snapshot(root, exposure_manifest, exposure_snapshot)
        if exposure_errors:
            raise G2FutureCampaignError(exposure_errors[0])
        preliminary = root / CONTROL_ROOT / "preliminary-registrar-observations.json"
        if preliminary.is_file():
            preliminary_relative = preliminary.relative_to(root).as_posix()
            inputs = {item["path"] for item in exposure_snapshot["inputs"]}
            if preliminary_relative not in inputs:
                raise G2FutureCampaignError(
                    "exposure snapshot omits preliminary registrar observations"
                )
        exposure = exposure_snapshot["exposure"]
        queries = manifest["queries"]
        events = registry["events"]
        if registry["execution"]["calls_attempted"] != len(events):
            raise G2FutureCampaignError("calls_attempted differs from event count")
        if len(events) != len(queries):
            raise G2FutureCampaignError("registry must contain one event for every query")
        provider_ids: set[str] = set()
        candidate_ids: set[str] = set()
        for query, event in zip(queries, events, strict=True):
            expected = (query["ordinal"], query["query_id"], query["route_stratum"])
            actual = (event["ordinal"], event["query_id"], event["route_stratum"])
            if actual != expected or event["status"] != "completed":
                raise G2FutureCampaignError("registry event differs from frozen query order")
            if event["provider_call_id"] in provider_ids:
                raise G2FutureCampaignError("registry repeats provider_call_id")
            provider_ids.add(event["provider_call_id"])
            if (
                len(event["observed_results"])
                > manifest["call_policy"]["maximum_results_per_query"]
            ):
                raise G2FutureCampaignError("query result count exceeds frozen limit")
            ranks = [item["result_rank"] for item in event["observed_results"]]
            if ranks != list(range(1, len(ranks) + 1)):
                raise G2FutureCampaignError("result ranks must be contiguous and ordered")
            for item in event["observed_results"]:
                _verify_candidate(item, event["route_stratum"], exposure)
                if item["candidate_id"] in candidate_ids:
                    raise G2FutureCampaignError("registry repeats candidate_id")
                candidate_ids.add(item["candidate_id"])
    except (G2FutureCampaignError, OSError, TypeError, KeyError, json.JSONDecodeError) as exc:
        return [str(exc)]
    return []


def build_selection_receipt(
    root: Path,
    *,
    registry_path: Path,
    selection_id: str,
    generated_at: str,
) -> dict[str, Any]:
    """Recompute the first feasible exact four-stratum selection."""

    root = root.expanduser().resolve()
    resolved_registry = _confined(root, registry_path)
    errors = verify_candidate_registry(root, resolved_registry)
    if errors:
        raise G2FutureCampaignError(errors[0])
    registry = _object(resolved_registry)
    manifest_path = _bound(root, registry["query_manifest"], "query manifest")
    manifest_descriptor = _artifact(root, manifest_path)
    candidates = [
        item
        for event in registry["events"]
        for item in event["observed_results"]
        if item["eligible_for_selection"]
    ]
    ranked = sorted(
        (
            {**item, "selection_score": _score(manifest_descriptor["sha256"], item)}
            for item in candidates
        ),
        key=lambda item: (item["selection_score"], item["candidate_id"]),
    )
    selected = _first_feasible(ranked)
    entries = (
        []
        if selected is None
        else [
            {
                "selection_rank": index,
                "selection_score": item["selection_score"],
                "candidate_id": item["candidate_id"],
                "edition_id": item["edition_id"],
                "source_series_id": item["source_series_id"],
                "jurisdiction_id": item["jurisdiction_id"],
                "route_stratum": item["route_stratum"],
                "canonical_url": item["canonical_url"],
                "request_identity": item["request_identity"],
                "source_sha256": item["source_sha256"],
            }
            for index, item in enumerate(selected, 1)
        ]
    )
    receipt = {
        "schema_version": "1.0",
        "campaign_id": CAMPAIGN_ID,
        "selection_id": selection_id,
        "query_manifest": manifest_descriptor,
        "candidate_registry": _artifact(root, resolved_registry),
        "exposure_input_manifest": registry["exposure_input_manifest"],
        "exposure_snapshot": registry["exposure_snapshot"],
        "algorithm": SELECTION_ALGORITHM,
        "status": (
            "selected_pre_source_access"
            if selected is not None
            else "terminal_stop_insufficient_scope"
        ),
        "eligible_candidate_count": len(candidates),
        "selected": entries,
        "generated_at": generated_at,
        "authority_boundary": {
            "selection_completed": True,
            "source_access": False,
            "extraction": False,
            "rights_clearance": False,
            "publication": False,
            "release": False,
            "g2_passage": False,
        },
    }
    _validate(root, "selection-receipt.schema.json", receipt)
    return receipt


def verify_selection_receipt(root: Path, path: Path) -> list[str]:
    """Verify that a stored selection exactly reproduces from its registry."""

    try:
        root = root.expanduser().resolve()
        receipt = _object(_confined(root, path))
        _validate(root, "selection-receipt.schema.json", receipt)
        registry_path = _bound(root, receipt["candidate_registry"], "candidate registry")
        expected = build_selection_receipt(
            root,
            registry_path=registry_path,
            selection_id=receipt["selection_id"],
            generated_at=receipt["generated_at"],
        )
        if receipt != expected:
            raise G2FutureCampaignError("selection receipt does not reproduce")
    except (G2FutureCampaignError, OSError, TypeError, KeyError, json.JSONDecodeError) as exc:
        return [str(exc)]
    return []


def verify_pre_source_interlock(root: Path, path: Path) -> list[str]:
    """Verify every binding before bounded source access can begin."""

    try:
        root = root.expanduser().resolve()
        receipt = _object(_confined(root, path))
        _validate(root, "pre-source-interlock.schema.json", receipt)
        for name in (
            "owner_authorization",
            "preparation_bundle",
            "query_manifest",
            "candidate_registry",
            "exposure_input_manifest",
            "exposure_snapshot",
            "selection_receipt",
        ):
            _bound(root, receipt[name], name.replace("_", " "))
        _verify_owner_authorization(
            root, receipt["owner_authorization"], receipt["preparation_bundle"]
        )
        _verify_preparation_bundle(root, receipt["preparation_bundle"])
        if verify_query_manifest(root, Path(receipt["query_manifest"]["path"])):
            raise G2FutureCampaignError("interlock query manifest does not verify")
        if verify_candidate_registry(root, Path(receipt["candidate_registry"]["path"])):
            raise G2FutureCampaignError("interlock candidate registry does not verify")
        selection_path = Path(receipt["selection_receipt"]["path"])
        if verify_selection_receipt(root, selection_path):
            raise G2FutureCampaignError("interlock selection receipt does not verify")
        selection = _object(root / selection_path)
        if selection["status"] != "selected_pre_source_access":
            raise G2FutureCampaignError("interlock cannot pass without a complete selection")
        registry = _object(root / Path(receipt["candidate_registry"]["path"]))
        if (
            receipt["exposure_input_manifest"] != registry["exposure_input_manifest"]
            or receipt["exposure_snapshot"] != registry["exposure_snapshot"]
            or selection["exposure_input_manifest"] != registry["exposure_input_manifest"]
            or selection["exposure_snapshot"] != registry["exposure_snapshot"]
        ):
            raise G2FutureCampaignError("interlock exposure bindings differ")
        _verify_role_allowlists(root, receipt["role_allowlists"], selection["selected"])
    except (G2FutureCampaignError, OSError, TypeError, KeyError, json.JSONDecodeError) as exc:
        return [str(exc)]
    return []


def _verify_candidate(
    item: Mapping[str, Any], route_stratum: str, exposure: Mapping[str, set[str]]
) -> None:
    if item["route_stratum"] != route_stratum:
        raise G2FutureCampaignError("candidate route differs from its frozen query")
    try:
        normalised = canonical_url(str(item["canonical_url"]))
    except ValueError as exc:
        raise G2FutureCampaignError("candidate URL is invalid") from exc
    if normalised != item["canonical_url"]:
        raise G2FutureCampaignError("candidate URL is not canonical")
    request_identity = canonical_request_identity(
        method=str(item["request_method"]),
        url=normalised,
        body_sha256=item["request_body_sha256"],
    )
    if request_identity != item["request_identity"]:
        raise G2FutureCampaignError("candidate request identity differs")
    edition_identities = {
        str(item["edition_id"]).strip().casefold(),
        *(str(value).strip().casefold() for value in item["edition_aliases"]),
    }
    if "" in edition_identities:
        raise G2FutureCampaignError("candidate edition identity is ambiguous")
    overlap = (
        normalised in exposure["urls"]
        or request_identity in exposure["request_identities"]
        or bool(edition_identities.intersection(exposure["edition_ids"]))
        or (
            item["source_sha256"] is not None
            and item["source_sha256"] in exposure["content_sha256"]
        )
    )
    if item["prior_exposure_overlap"] is not overlap:
        raise G2FutureCampaignError("candidate prior-exposure claim differs")
    eligible = bool(item["official_publisher"] and item["exact_edition_identity"] and not overlap)
    if item["eligible_for_selection"] is not eligible:
        raise G2FutureCampaignError("candidate eligibility claim differs")
    reasons = item["rejection_reasons"]
    if eligible and reasons:
        raise G2FutureCampaignError("eligible candidate has rejection reasons")
    if not eligible and not reasons:
        raise G2FutureCampaignError("ineligible candidate requires a rejection reason")


def _first_feasible(ranked: Sequence[dict[str, Any]]) -> list[dict[str, Any]] | None:
    by_stratum = {
        stratum: [item for item in ranked if item["route_stratum"] == stratum] for stratum in STRATA
    }
    if any(not values for values in by_stratum.values()):
        return None
    for combination in itertools.product(*(by_stratum[stratum] for stratum in STRATA)):
        if len({item["edition_id"] for item in combination}) != 4:
            continue
        if len({item["source_series_id"] for item in combination}) != 4:
            continue
        if len({item["canonical_url"] for item in combination}) != 4:
            continue
        if len({item["request_identity"] for item in combination}) != 4:
            continue
        known_digests = [item["source_sha256"] for item in combination if item["source_sha256"]]
        if len(known_digests) != len(set(known_digests)):
            continue
        jurisdictions = Counter(str(item["jurisdiction_id"]) for item in combination)
        if len(jurisdictions) < 3 or max(jurisdictions.values()) > 2:
            continue
        return list(combination)
    return None


def _score(manifest_sha256: str, item: Mapping[str, Any]) -> str:
    identity = "\0".join(
        (
            manifest_sha256,
            str(item["candidate_id"]),
            str(item["edition_id"]),
            str(item["canonical_url"]),
        )
    )
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()


def _verify_role_allowlists(
    root: Path, descriptors: Sequence[Mapping[str, Any]], selected: Sequence[Mapping[str, Any]]
) -> None:
    roles = [str(item["role"]) for item in descriptors]
    if sorted(roles) != sorted(ROLES) or len(set(roles)) != len(ROLES):
        raise G2FutureCampaignError("role allowlists do not cover the frozen distinct roles")
    selected_urls = sorted(str(item["canonical_url"]) for item in selected)
    required_keys = {
        "schema_version",
        "campaign_id",
        "role",
        "network_mode",
        "network_url_allowlist",
        "input_artifact_classes",
        "output_prefix",
        "prohibited_artifact_classes",
    }
    for descriptor in descriptors:
        path = _bound(root, descriptor["artifact"], f"{descriptor['role']} allowlist")
        value = _object(path)
        if set(value) != required_keys:
            raise G2FutureCampaignError("role allowlist has an unexpected field set")
        if value["schema_version"] != "1.0" or value["campaign_id"] != CAMPAIGN_ID:
            raise G2FutureCampaignError("role allowlist campaign binding differs")
        if value["role"] != descriptor["role"]:
            raise G2FutureCampaignError("role allowlist role differs")
        urls = value["network_url_allowlist"]
        if descriptor["role"] == "orchestrator":
            if value["network_mode"] != "exact_allowlist_only" or sorted(urls) != selected_urls:
                raise G2FutureCampaignError("orchestrator URL allowlist differs from selection")
        elif value["network_mode"] != "none" or urls:
            raise G2FutureCampaignError("non-orchestrator role must be network-disabled")
        for field in ("input_artifact_classes", "prohibited_artifact_classes"):
            if (
                not isinstance(value[field], list)
                or not value[field]
                or len(value[field]) != len(set(value[field]))
            ):
                raise G2FutureCampaignError(f"role allowlist {field} is invalid")
        prefix = Path(str(value["output_prefix"]))
        if prefix.is_absolute() or ".." in prefix.parts:
            raise G2FutureCampaignError("role allowlist output prefix escapes repository")


def _verify_owner_authorization(
    root: Path,
    descriptor: Mapping[str, str],
    preparation_descriptor: Mapping[str, str],
) -> None:
    value = _object(_bound(root, descriptor, "owner authorization"))
    if value.get("decision") != "authorize_option_a_staged_future_calibration_campaign":
        raise G2FutureCampaignError("owner authorization decision differs")
    if value.get("preparation_bundle") != preparation_descriptor:
        raise G2FutureCampaignError("owner authorization preparation binding differs")
    expected_authorization = {
        "candidate_registration_and_selection": True,
        "bounded_network_and_source_access": True,
        "controlled_aggregate_only_processing": True,
        "fresh_artifact_isolated_extractors": 2,
        "network_disabled_exact_comparator": 1,
        "role_separated_non_independent_advisory_review": 1,
    }
    if value.get("authorization") != expected_authorization:
        raise G2FutureCampaignError("owner authorization scope differs")
    interlock = value.get("pre_source_access_interlock")
    if not isinstance(interlock, dict) or interlock.get("required") is not True:
        raise G2FutureCampaignError("owner authorization does not require the interlock")
    if interlock.get("satisfied_at_decision_time") is not False:
        raise G2FutureCampaignError("owner authorization retrospectively satisfies interlock")
    expected_non_authorizations = {
        "rights_clearance": False,
        "gold_promotion": False,
        "g2_c04_acceptance": False,
        "g2_c07_acceptance": False,
        "m06_promotion": False,
        "g2_passage": False,
        "publication": False,
        "release": False,
    }
    if value.get("non_authorizations") != expected_non_authorizations:
        raise G2FutureCampaignError("owner non-authorization boundary differs")
    for name in ("decision_packet", "owner_authorization_record", "preparation_manifest"):
        _bound(root, value[name], f"owner authorization {name.replace('_', ' ')}")


def _verify_preparation_bundle(root: Path, descriptor: Mapping[str, str]) -> None:
    value = _object(_bound(root, descriptor, "preparation bundle"))
    if value.get("bundle_id") != "G2PROSPECTIVE-CALIBRATION-PREPARATION-20260829-01":
        raise G2FutureCampaignError("preparation bundle identity differs")
    if value.get("status") != "prepared_not_frozen_not_authorized":
        raise G2FutureCampaignError("preparation bundle status differs")
    candidate_state = value.get("candidate_state")
    if not isinstance(candidate_state, dict) or candidate_state.get("candidate_count") != 0:
        raise G2FutureCampaignError("preparation bundle is not candidate-free")
    expected_authority = {
        "candidate_selection": False,
        "network_access": False,
        "source_access": False,
        "extraction": False,
        "comparison": False,
        "rights_clearance": False,
        "publication": False,
        "release": False,
        "g2_passage": False,
        "separate_execution_decision_required": True,
    }
    if value.get("authorization") != expected_authority:
        raise G2FutureCampaignError("preparation bundle authority boundary differs")
    bindings = value.get("bindings")
    if not isinstance(bindings, list) or not bindings:
        raise G2FutureCampaignError("preparation bundle requires artifact bindings")
    for item in bindings:
        _bound(root, item, "preparation artifact")


def _schema(root: Path, name: str) -> dict[str, Any]:
    return _object(root / CONTROL_ROOT / name)


def _validate(root: Path, name: str, payload: Mapping[str, Any]) -> None:
    errors = sorted(
        Draft202012Validator(_schema(root, name), format_checker=FormatChecker()).iter_errors(
            dict(payload)
        ),
        key=lambda item: list(item.absolute_path),
    )
    if errors:
        raise G2FutureCampaignError(
            f"{name} validation failed at {errors[0].json_path}: {errors[0].message}"
        )


def _artifact(root: Path, path: Path) -> dict[str, str]:
    resolved = _confined(root, path)
    return {"path": resolved.relative_to(root).as_posix(), "sha256": sha256_file(resolved)}


def _bound(root: Path, descriptor: Mapping[str, str], label: str) -> Path:
    if set(descriptor) != {"path", "sha256"}:
        raise G2FutureCampaignError(f"{label} descriptor is malformed")
    path = _confined(root, Path(str(descriptor["path"])))
    if sha256_file(path) != descriptor["sha256"]:
        raise G2FutureCampaignError(f"{label} digest mismatch")
    return path


def _confined(root: Path, path: Path) -> Path:
    candidate = path if path.is_absolute() else root / path
    if candidate.is_symlink():
        raise G2FutureCampaignError(f"symbolic links are prohibited: {path}")
    resolved = candidate.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise G2FutureCampaignError(f"path escapes repository: {path}") from exc
    if not resolved.is_file():
        raise G2FutureCampaignError(f"artifact is missing: {path}")
    return resolved


def _object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise G2FutureCampaignError(f"expected JSON object: {path}")
    return value
