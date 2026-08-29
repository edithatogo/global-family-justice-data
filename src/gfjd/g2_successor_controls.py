"""Prospective hardening controls for a successor G2 calibration campaign.

These controls are deliberately separate from the immutable failed lineage in
``g2_future_*``.  They can be frozen into a future execution contract without
rewriting the evidence produced by that predecessor.
"""

from __future__ import annotations

import hashlib
import ipaddress
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from .g2_future_exposure import canonical_url
from .io import canonical_json_bytes, sha256_file


class G2SuccessorControlError(ValueError):
    """Raised when a successor control fails closed."""


CONTENT_DIGEST_FIELDS = frozenset({"content_sha256", "source_sha256"})
PROVIDER_RESULT_FIELDS = frozenset({"provider_result_id", "canonical_url", "display_title"})
URL_LIST_FIELDS = frozenset({"denied_urls", "observed_urls", "urls"})
EXPLICIT_URL_FIELDS = frozenset(
    {
        "canonical_url",
        "direct_pdf_url",
        "download_url",
        "endpoint",
        "final_url",
        "landing_page_url",
        "models_endpoint",
        "proposed_pdf_url",
        "proposed_url",
        "query_endpoint",
        "redirect_location",
        "requested_entrypoint",
        "requested_url",
        "request_url",
        "result_url",
        "retrieval_entrypoint",
        "source_definition_pdf",
        "source_url",
        "url",
    }
)

ROLE_POLICY: dict[str, dict[str, object]] = {
    "candidate_registrar": {
        "network_mode": "frozen_query_calls_only",
        "inputs": ["query_manifest", "exposure_snapshot"],
        "prohibited": ["source_artifact", "extractor_output", "comparison_output"],
    },
    "orchestrator": {
        "network_mode": "exact_allowlist_only",
        "inputs": ["selection_receipt", "source_access_authorization"],
        "prohibited": ["extractor_output", "comparison_output"],
    },
    "extractor_a": {
        "network_mode": "none",
        "inputs": ["source_artifact", "semantic_contract", "row_schema"],
        "prohibited": ["extractor_b_output", "comparison_output", "prior_failed_output"],
    },
    "extractor_b": {
        "network_mode": "none",
        "inputs": ["source_artifact", "semantic_contract", "row_schema"],
        "prohibited": ["extractor_a_output", "comparison_output", "prior_failed_output"],
    },
    "network_disabled_comparator": {
        "network_mode": "none",
        "inputs": ["extractor_a_output", "extractor_b_output", "comparison_contract"],
        "prohibited": ["source_artifact", "prior_failed_output"],
    },
    "advisory_reviewer": {
        "network_mode": "none",
        "inputs": ["comparison_output", "control_receipts"],
        "prohibited": ["source_artifact", "extractor_workspace"],
    },
}

SUCCESSOR_CAMPAIGN_ID = "G2PROSPECTIVE-SUCCESSOR-20260829-02"
SUCCESSOR_STATUS = "repository_design_complete_external_execution_not_authorized"
SUCCESSOR_EXTERNAL_BOUNDARY = (
    "one_digest_bound_execution_authorization_after_query_manifest_exposure_snapshot_"
    "role_bundles_and_transport_adapter_are_frozen"
)
SUCCESSOR_CONTROLS: dict[str, object] = {
    "provider_result_handling": {
        "requested_maximum": 10,
        "absolute_safety_cap": 50,
        "over_return_policy": (
            "record_every_observed_result_as_exposure_and_limit_registration_to_requested_prefix"
        ),
        "truncation_permitted": False,
        "automatic_retry_permitted": False,
    },
    "authorization_anchor": {
        "trust_anchor": "execution_contract.owner_authorization",
        "interlock_must_match_exact_descriptor": True,
        "self_declared_interlock_authorization_permitted": False,
    },
    "exposure": {
        "digest_fields": ["content_sha256", "source_sha256"],
        "explicit_locator_fields": sorted(EXPLICIT_URL_FIELDS),
        "plural_locator_fields": sorted(URL_LIST_FIELDS),
        "generic_url_suffixes": True,
        "rebuild_before_candidate_registration": True,
    },
    "role_isolation": {
        "exact_per_role_input_and_prohibited_classes": True,
        "distinct_nonoverlapping_output_prefixes": True,
        "extractors_artifact_isolated": True,
        "comparator_network_disabled": True,
        "advisory_review_non_independent": True,
    },
    "network": {
        "https_only": True,
        "exact_url_allowlist": True,
        "validated_public_dns_required": True,
        "connected_peer_must_match_validated_address": True,
        "hostname_tls_verification_required": True,
        "peer_mismatch_action": "terminal_stop_before_body_read",
    },
}


def record_complete_provider_results(
    results: Sequence[Mapping[str, Any]],
    *,
    requested_maximum: int,
    absolute_safety_cap: int,
) -> dict[str, Any]:
    """Record every provider result while bounding selection and memory use.

    A provider may return more results than requested.  That is not itself a
    contract failure: every result is retained as exposure, while only the
    requested prefix is eligible for candidate registration.  The separately
    frozen absolute cap remains a hard resource stop.
    """

    if requested_maximum < 1 or absolute_safety_cap < requested_maximum:
        raise G2SuccessorControlError("result limits are inconsistent")
    if len(results) > absolute_safety_cap:
        raise G2SuccessorControlError("provider result count exceeds absolute safety cap")
    observed: list[dict[str, Any]] = []
    for rank, result in enumerate(results, 1):
        if not isinstance(result, Mapping):
            raise G2SuccessorControlError("provider result must be an object")
        if not result or not set(result).issubset(PROVIDER_RESULT_FIELDS):
            raise G2SuccessorControlError("provider result contains non-locator metadata")
        if "canonical_url" not in result:
            raise G2SuccessorControlError("provider result lacks canonical_url")
        normalised = canonical_url(str(result["canonical_url"]))
        if urlsplit(normalised).scheme != "https" or normalised != result["canonical_url"]:
            raise G2SuccessorControlError("provider result URL is not canonical")
        observed.append(
            {
                "result_rank": rank,
                "locator_metadata": dict(result),
                "eligible_for_registration": rank <= requested_maximum,
            }
        )
    return {
        "requested_maximum": requested_maximum,
        "absolute_safety_cap": absolute_safety_cap,
        "observed_result_count": len(observed),
        "provider_over_returned": len(observed) > requested_maximum,
        "all_observed_results_recorded": True,
        "observed_results": observed,
    }


def collect_exposure_identities(value: Any) -> dict[str, list[str]]:
    """Collect established locator and content-digest aliases recursively."""

    collected: dict[str, set[str]] = {"urls": set(), "content_sha256": set()}

    def visit(node: Any) -> None:
        if isinstance(node, Mapping):
            for key, child in node.items():
                if child is None:
                    continue
                if key in EXPLICIT_URL_FIELDS or key.endswith("_url"):
                    if not isinstance(child, str):
                        raise G2SuccessorControlError(f"{key} must be a URL string")
                    collected["urls"].add(canonical_url(child))
                elif key in URL_LIST_FIELDS:
                    if not isinstance(child, list) or not all(
                        isinstance(item, str) for item in child
                    ):
                        raise G2SuccessorControlError(f"{key} must be a URL string list")
                    for item in child:
                        collected["urls"].add(canonical_url(item))
                elif key in CONTENT_DIGEST_FIELDS:
                    values = [child] if isinstance(child, str) else child
                    if not isinstance(values, list):
                        raise G2SuccessorControlError(f"{key} must be a digest or digest list")
                    for digest in values:
                        if not isinstance(digest, str) or not _is_sha256(digest):
                            raise G2SuccessorControlError(f"{key} contains an invalid digest")
                        collected["content_sha256"].add(digest)
                visit(child)
        elif isinstance(node, list):
            for child in node:
                visit(child)

    visit(value)
    return {key: sorted(values) for key, values in collected.items()}


def verify_authorization_anchor(
    root: Path,
    *,
    execution_contract_path: Path,
    interlock_path: Path,
) -> list[str]:
    """Require the interlock to use the authorization frozen by its contract."""

    try:
        root = root.expanduser().resolve()
        contract = _json_object(_confined(root, execution_contract_path))
        interlock = _json_object(_confined(root, interlock_path))
        frozen = contract.get("owner_authorization")
        supplied = interlock.get("owner_authorization")
        if not isinstance(frozen, Mapping) or not isinstance(supplied, Mapping):
            raise G2SuccessorControlError("authorization descriptor is missing")
        if dict(frozen) != dict(supplied):
            raise G2SuccessorControlError(
                "interlock authorization differs from the execution-contract trust anchor"
            )
        _verify_descriptor(root, frozen, "owner authorization")
        preparation = contract.get("preparation_bundle")
        if not isinstance(preparation, Mapping):
            raise G2SuccessorControlError("execution contract lacks preparation binding")
        if interlock.get("preparation_bundle") != preparation:
            raise G2SuccessorControlError("interlock preparation differs from trust anchor")
        _verify_descriptor(root, preparation, "preparation bundle")
    except (G2SuccessorControlError, OSError, json.JSONDecodeError) as exc:
        return [str(exc)]
    return []


def verify_role_isolation(
    bundles: Sequence[Mapping[str, Any]], *, selected_urls: Sequence[str]
) -> list[str]:
    """Recompute the exact per-role isolation matrix and distinct outputs."""

    try:
        by_role = {str(bundle.get("role")): bundle for bundle in bundles}
        if set(by_role) != set(ROLE_POLICY) or len(bundles) != len(ROLE_POLICY):
            raise G2SuccessorControlError("role bundle set differs from frozen policy")
        prefixes: list[Path] = []
        canonical_selected = sorted(canonical_url(url) for url in selected_urls)
        if any(urlsplit(url).scheme != "https" for url in canonical_selected):
            raise G2SuccessorControlError("selected URL is not HTTPS")
        for role, expected in ROLE_POLICY.items():
            bundle = by_role[role]
            if bundle.get("network_mode") != expected["network_mode"]:
                raise G2SuccessorControlError(f"{role} network mode differs")
            urls = bundle.get("network_url_allowlist")
            expected_urls = canonical_selected if role == "orchestrator" else []
            if urls != expected_urls:
                raise G2SuccessorControlError(f"{role} network allowlist differs")
            if bundle.get("input_artifact_classes") != expected["inputs"]:
                raise G2SuccessorControlError(f"{role} input classes differ")
            if bundle.get("prohibited_artifact_classes") != expected["prohibited"]:
                raise G2SuccessorControlError(f"{role} prohibited classes differ")
            prefix = str(bundle.get("output_prefix", ""))
            path = Path(prefix)
            if not prefix or path == Path(".") or path.is_absolute() or ".." in path.parts:
                raise G2SuccessorControlError(f"{role} output prefix is unsafe")
            if any(_paths_overlap(path, existing) for existing in prefixes):
                raise G2SuccessorControlError("role output prefixes are not distinct and disjoint")
            prefixes.append(path)
    except (G2SuccessorControlError, ValueError) as exc:
        return [str(exc)]
    return []


def verify_connected_peer(
    *, validated_addresses: Sequence[str], connected_peer_address: str
) -> None:
    """Bind the actual connection peer to the validated public DNS result."""

    if not validated_addresses:
        raise G2SuccessorControlError("validated address set is empty")
    validated: set[ipaddress.IPv4Address | ipaddress.IPv6Address] = set()
    for address in validated_addresses:
        try:
            candidate = ipaddress.ip_address(address)
        except ValueError as exc:
            raise G2SuccessorControlError("validated address is invalid") from exc
        if not candidate.is_global:
            raise G2SuccessorControlError("validated address is not public")
        validated.add(candidate)
    try:
        peer = ipaddress.ip_address(connected_peer_address)
    except ValueError as exc:
        raise G2SuccessorControlError("connected peer address is invalid") from exc
    if not peer.is_global or peer not in validated:
        raise G2SuccessorControlError("connected peer differs from validated public addresses")


def design_digest(value: Mapping[str, Any]) -> str:
    """Return the canonical digest used by a future freeze contract."""

    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def verify_successor_design(root: Path, path: Path) -> list[str]:
    """Verify the repository-only design and every immutable predecessor binding."""

    try:
        root = root.expanduser().resolve()
        value = _json_object(_confined(root, path))
        if (
            value.get("schema_version") != "1.0"
            or value.get("campaign_id") != SUCCESSOR_CAMPAIGN_ID
        ):
            raise G2SuccessorControlError("successor design identity differs")
        if value.get("status") != SUCCESSOR_STATUS:
            raise G2SuccessorControlError("successor design status differs")
        if value.get("controls") != SUCCESSOR_CONTROLS:
            raise G2SuccessorControlError("successor semantic controls differ")
        if value.get("next_external_boundary") != SUCCESSOR_EXTERNAL_BOUNDARY:
            raise G2SuccessorControlError("successor external boundary differs")
        predecessor = value.get("predecessor")
        if not isinstance(predecessor, Mapping) or predecessor.get("reuse_permitted") is not False:
            raise G2SuccessorControlError("predecessor reuse boundary differs")
        terminal = _confined(root, Path(str(predecessor["terminal_receipt_path"])))
        if sha256_file(terminal) != predecessor.get("terminal_receipt_sha256"):
            raise G2SuccessorControlError("predecessor terminal binding differs")
        flags = value.get("execution_flags")
        if not isinstance(flags, Mapping) or not flags or any(flags.values()):
            raise G2SuccessorControlError("successor design claims execution")
        bindings = value.get("bindings")
        if not isinstance(bindings, list) or not bindings:
            raise G2SuccessorControlError("successor design lacks control bindings")
        required_paths = {
            "src/gfjd/g2_successor_controls.py",
            "tests/test_g2_successor_controls.py",
        }
        observed_paths: set[str] = set()
        for descriptor in bindings:
            if not isinstance(descriptor, Mapping):
                raise G2SuccessorControlError("successor control descriptor is malformed")
            _verify_descriptor(root, descriptor, "successor control")
            observed_paths.add(str(descriptor["path"]))
        if observed_paths != required_paths:
            raise G2SuccessorControlError("successor control binding paths differ")
    except (G2SuccessorControlError, KeyError, OSError, json.JSONDecodeError) as exc:
        return [str(exc)]
    return []


def _verify_descriptor(root: Path, descriptor: Mapping[str, Any], label: str) -> None:
    if set(descriptor) != {"path", "sha256"}:
        raise G2SuccessorControlError(f"{label} descriptor is malformed")
    path = _confined(root, Path(str(descriptor["path"])))
    digest = str(descriptor["sha256"])
    if not _is_sha256(digest) or sha256_file(path) != digest:
        raise G2SuccessorControlError(f"{label} binding differs")


def _confined(root: Path, path: Path) -> Path:
    if path.is_absolute() or ".." in path.parts:
        raise G2SuccessorControlError("artifact path escapes repository")
    resolved = (root / path).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise G2SuccessorControlError("artifact path escapes repository") from exc
    if not resolved.is_file():
        raise G2SuccessorControlError("bound artifact is missing")
    return resolved


def _json_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise G2SuccessorControlError("bound JSON artifact must be an object")
    return value


def _is_sha256(value: str) -> bool:
    return len(value) == 64 and all(character in "0123456789abcdef" for character in value)


def _paths_overlap(left: Path, right: Path) -> bool:
    return left == right or left in right.parents or right in left.parents
