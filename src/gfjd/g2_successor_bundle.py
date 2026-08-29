"""Build the repository-only G2 successor preparation bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from .g2_successor_controls import (
    ROLE_POLICY,
    SUCCESSOR_CAMPAIGN_ID,
    collect_exposure_identities,
)
from .io import canonical_json_bytes, sha256_file


class SuccessorBundleError(ValueError):
    """Raised when a preparation bundle cannot be built safely."""


QUERY_SPECS = (
    ("api_or_json", "official court family justice annual statistics open data API JSON"),
    ("api_or_json", "official judiciary family proceedings annual statistics API dataset"),
    ("api_or_json", "official court administration family cases statistics JSON download"),
    ("api_or_json", "official justice ministry family court caseload open data API"),
    ("html_or_dashboard", "official family court annual statistics interactive dashboard"),
    ("html_or_dashboard", "official judiciary family proceedings statistics data visualisation"),
    ("html_or_dashboard", "official court service family cases annual statistical table HTML"),
    ("html_or_dashboard", "official justice department family court caseload dashboard"),
    ("spreadsheet", "official family court annual statistics spreadsheet xlsx"),
    ("spreadsheet", "official judiciary family proceedings statistical tables ods"),
    ("spreadsheet", "official court administration family cases annual workbook"),
    ("spreadsheet", "official justice ministry family court statistics csv download"),
    ("pdf", "official family court annual statistical report PDF"),
    ("pdf", "official judiciary family proceedings caseload report PDF"),
    ("pdf", "official court administration family cases performance report PDF"),
    ("pdf", "official justice ministry family court annual report PDF statistics"),
)


def build(root: Path, output_dir: Path) -> dict[str, Any]:
    """Build deterministic, non-executing successor control artifacts."""

    root = root.resolve()
    output_dir = (root / output_dir).resolve()
    output_dir.relative_to(root)
    output_dir.mkdir(parents=True, exist_ok=True)
    query_manifest = _query_manifest()
    exposure = _exposure_snapshot(root, output_dir)
    roles = _role_bundles()
    transport = _transport_contract(root)
    resources = _resource_contract(root)
    artifacts = {
        "query-manifest.json": query_manifest,
        "exposure-snapshot.json": exposure,
        "role-bundles.json": roles,
        "transport-contract.json": transport,
        "resource-and-stop-contract.json": resources,
    }
    for name, value in artifacts.items():
        (output_dir / name).write_bytes(canonical_json_bytes(value) + b"\n")
    bindings = [
        _descriptor(root, path.relative_to(root))
        for path in sorted(output_dir.glob("*.json"))
        if path.name != "preparation-packet.json"
    ]
    packet = _preparation_packet(bindings)
    packet_path = output_dir / "preparation-packet.json"
    packet_path.write_bytes(canonical_json_bytes(packet) + b"\n")
    return packet


def _transport_contract(root: Path) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "campaign_id": SUCCESSOR_CAMPAIGN_ID,
        "adapter_contract": "peer_reported_before_body_read_v1",
        "requirements": {
            "resolve_hostname_to_public_addresses": True,
            "connect_only_to_validated_address": True,
            "verify_tls_for_original_hostname": True,
            "report_connected_peer_address": True,
            "verify_peer_before_headers_or_body_are_persisted": True,
            "peer_mismatch_is_terminal": True,
        },
        "implementation_bindings": [
            _descriptor(root, Path("src/gfjd/g2_successor_controls.py")),
            _descriptor(root, Path("src/gfjd/g2_successor_transport.py")),
            _descriptor(root, Path("tests/test_g2_successor_transport.py")),
        ],
        "execution_enabled": False,
    }


def _resource_contract(root: Path) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "campaign_id": SUCCESSOR_CAMPAIGN_ID,
        "query_calls": 16,
        "retries": 0,
        "requested_results_per_query": 10,
        "absolute_results_per_query": 50,
        "maximum_observed_locators": 800,
        "maximum_selected_sources": 4,
        "maximum_source_bytes_each": 26214400,
        "maximum_source_bytes_total": 104857600,
        "prospective_extraction_contracts": [
            _descriptor(root, Path(path))
            for path in (
                "data/methods/g2/G2PROSPECTIVE-CALIBRATION-PREPARATION-20260829-01/row.schema.json",
                "data/methods/g2/G2PROSPECTIVE-CALIBRATION-PREPARATION-20260829-01/comparator-contract.json",
                "data/methods/g2/G2PROSPECTIVE-SEMANTIC-CONTRACT-20260827-01/semantic-contract.schema.json",
                "config/g2_holdout_generic_extraction_contract.json",
                "schemas/g2_extraction_run.schema.json",
            )
        ],
        "terminal_stops": [
            "binding_or_schema_mismatch",
            "provider_returns_more_than_absolute_cap",
            "snippet_or_nonlocator_metadata_observed",
            "exposure_overlap_or_incomplete_exposure_accounting",
            "non_https_or_non_public_network_target",
            "connected_peer_mismatch_before_body_read",
            "role_isolation_or_output_prefix_failure",
            "source_identity_content_type_or_size_failure",
            "personal_identifying_sensitive_or_case_level_material",
            "critical_concordance_below_100_percent",
            "overall_populated_concordance_below_99_percent",
        ],
    }


def _preparation_packet(bindings: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "campaign_id": SUCCESSOR_CAMPAIGN_ID,
        "status": "frozen_repository_preparation_awaiting_grouped_owner_authorization",
        "bindings": bindings,
        "stages": {
            "metadata_registration": "awaiting_owner_authorization",
            "source_access": "disabled_until_exact_selection_and_pre_source_interlock_pass",
            "extraction_and_comparison": "disabled_until_acquisition_receipts_pass",
        },
        "authority_boundary": {
            "network_access": False,
            "source_access": False,
            "publication": False,
            "release": False,
            "g2_passage": False,
        },
    }


def verify(root: Path, output_dir: Path) -> list[str]:
    """Rebuild in memory and verify the stored preparation artifacts."""

    root = root.resolve()
    output_dir = (root / output_dir).resolve()
    try:
        query = _load(output_dir / "query-manifest.json")
        if query != _query_manifest():
            return ["query manifest differs"]
        snapshot = _load(output_dir / "exposure-snapshot.json")
        if snapshot != _exposure_snapshot(root, output_dir):
            return ["exposure snapshot differs"]
        roles = _load(output_dir / "role-bundles.json")
        if roles != _role_bundles():
            return ["role bundles differ"]
        if _load(output_dir / "transport-contract.json") != _transport_contract(root):
            return ["transport contract differs"]
        if _load(output_dir / "resource-and-stop-contract.json") != _resource_contract(root):
            return ["resource and stop contract differs"]
        packet = _load(output_dir / "preparation-packet.json")
        for descriptor in packet.get("bindings", []):
            if _descriptor(root, Path(descriptor["path"])) != descriptor:
                return [f"binding differs: {descriptor['path']}"]
        expected_bindings = [
            _descriptor(root, path.relative_to(root))
            for path in sorted(output_dir.glob("*.json"))
            if path.name != "preparation-packet.json"
        ]
        if packet != _preparation_packet(expected_bindings):
            return ["preparation packet differs"]
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        return [str(exc)]
    return []


def _query_manifest() -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "campaign_id": SUCCESSOR_CAMPAIGN_ID,
        "status": "frozen_not_executed",
        "ordering": "ascending_ordinal_one_call_each_zero_retries",
        "provider_result_policy": {"requested_maximum": 10, "absolute_safety_cap": 50},
        "provider_config": {
            "provider": "openai_web_search_query",
            "operation": "search_query",
            "one_query_object_per_call": True,
            "pagination": "none",
            "recency_filter": "none",
            "domain_filter": "none",
            "response_length": "short",
            "ranking": "provider_defined_unmodified",
            "execution_time_basis": "provider_index_at_call_time",
        },
        "queries": [
            {
                "ordinal": index,
                "query_id": f"G2SUCQ-{index:02d}",
                "route_stratum": route,
                "query_text": text,
            }
            for index, (route, text) in enumerate(QUERY_SPECS, 1)
        ],
    }


def _exposure_snapshot(root: Path, output_dir: Path) -> dict[str, Any]:
    urls: set[str] = set()
    digests: set[str] = set()
    inputs: list[dict[str, str]] = []
    base = root / "data/methods/g2"
    for path in sorted(base.rglob("*.json")):
        if output_dir in path.parents or path.name.endswith(".schema.json"):
            continue
        value = _load(path)
        if path.name == "exposure-snapshot.json" and isinstance(value.get("exposure"), dict):
            prior = value["exposure"]
            found = {
                "urls": list(prior.get("urls", [])),
                "content_sha256": list(prior.get("content_sha256", [])),
            }
        else:
            found = collect_exposure_identities(value)
        urls.update(found["urls"])
        digests.update(found["content_sha256"])
        inputs.append(_descriptor(root, path.relative_to(root)))
    values = {"urls": sorted(urls), "content_sha256": sorted(digests)}
    return {
        "schema_version": "1.0",
        "campaign_id": SUCCESSOR_CAMPAIGN_ID,
        "collector": "g2_successor_controls.collect_exposure_identities",
        "inputs": inputs,
        "exposure": values,
        "counts": {key: len(value) for key, value in values.items()},
        "digests": {
            key: hashlib.sha256(canonical_json_bytes(value)).hexdigest()
            for key, value in values.items()
        },
    }


def _role_bundles() -> dict[str, Any]:
    bundles = []
    for role, policy in ROLE_POLICY.items():
        bundles.append(
            {
                "role": role,
                "activation": "pending_stage_interlock",
                "network_mode": policy["network_mode"],
                "network_url_allowlist": [],
                "input_artifact_classes": policy["inputs"],
                "prohibited_artifact_classes": policy["prohibited"],
                "output_prefix": f"build/g2-successor/{role}",
            }
        )
    return {"schema_version": "1.0", "campaign_id": SUCCESSOR_CAMPAIGN_ID, "bundles": bundles}


def _descriptor(root: Path, path: Path) -> dict[str, str]:
    target = (root / path).resolve()
    target.relative_to(root)
    return {"path": path.as_posix(), "sha256": sha256_file(target)}


def _load(path: Path) -> dict[str, Any]:
    def object_without_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        value: dict[str, Any] = {}
        for key, item in pairs:
            if key in value:
                raise SuccessorBundleError(f"duplicate JSON key: {key}")
            value[key] = item
        return value

    value = json.loads(
        path.read_text(encoding="utf-8"), object_pairs_hook=object_without_duplicates
    )
    if not isinstance(value, dict):
        raise SuccessorBundleError(f"JSON object required: {path}")
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("build", "verify"))
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.action == "build":
        build(args.root, args.output)
        return 0
    errors = verify(args.root, args.output)
    for error in errors:
        print(error)
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
