"""Offline prospective estate declarations and draft cards, never publication.

Only compiler fingerprinting reads a file. No bootstrap discovery, account lookup,
source payload, credential, subprocess, transport or active explorer is invoked.
"""

from __future__ import annotations

import hashlib
import html
import json
import math
import re
import tomllib
from pathlib import Path
from typing import Any

VERSION = "gfjd-offline-estate-v2"
SOURCEFILES = (
    "config/bootstrap.toml",
    "config/archive_targets.toml",
    "portfolio/products.toml",
    ".gfjd/product.toml",
)
POLICY_REFERENCE = "docs/programme/maximal-public-medallion-federation-plan-2026-08-26.md"
POLICY_SHA256 = "5f44f2a64e49c3ac616f5dd456061d9c00bdbdfc09e218bab6fab36852109465"
MAX_CONFIG_BYTES = 1024 * 1024
ROLE_RULES = {
    "source-archive": (
        "dataset",
        "public_source_archive",
        "public_safe_exact_editions_and_capture_objects",
        "G3",
        ("b0",),
    ),
    "source-catalogue": (
        "dataset",
        "public_catalogue",
        "metadata_and_cleared_bytes_only",
        "G3",
        ("cross_layer_metadata",),
    ),
    "observations": (
        "dataset",
        "public_medallion",
        "generated_observations_only",
        "G4",
        ("b1", "silver", "gold"),
    ),
    "outcomes-evidence": (
        "dataset",
        "public_evidence",
        "generated_evidence_only",
        "G4",
        ("separately_governed_evidence",),
    ),
    "extraction-benchmark": (
        "dataset",
        "public_benchmark",
        "synthetic_or_cleared_only",
        "G4",
        ("benchmark_not_accepted_observations",),
    ),
    "explorer": (
        "space",
        "public_gold_platinum_only",
        "generated_products_only",
        "G6",
        ("accepted_gold", "released_platinum"),
    ),
}


class EstateError(ValueError):
    """Estate declaration or draft integrity mismatch; no partial bundle is returned."""


def _require(condition: bool) -> None:
    if not condition:
        raise EstateError("estate declaration validation failed")


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def _keys(value: Any, fields: str) -> dict[str, Any]:
    _require(isinstance(value, dict) and set(value) == set(fields.split()))
    return dict(value)


def _parse(raw: bytes) -> dict[str, Any]:
    _require(isinstance(raw, bytes) and 0 < len(raw) <= MAX_CONFIG_BYTES)
    root = tomllib.loads(raw.decode("utf-8"))
    pending: list[tuple[Any, int]] = [(root, 1)]
    nodes = 0
    while pending:
        value, depth = pending.pop()
        nodes += 1
        _require(nodes <= 10000 and depth <= 16)
        if isinstance(value, dict):
            _require(len(value) <= 128)
            pending.extend((key, depth + 1) for key in value)
            pending.extend((item, depth + 1) for item in value.values())
        elif isinstance(value, list):
            _require(len(value) <= 1000)
            pending.extend((item, depth + 1) for item in value)
        elif isinstance(value, str):
            _require(
                len(value) <= 4096
                and all(ord(char) >= 32 and not 0x7F <= ord(char) <= 0x9F for char in value)
            )
        elif type(value) is float:
            _require(math.isfinite(value))
        else:
            _require(type(value) in {int, bool})
    return root


def _identity(value: Any) -> str:
    _require(
        isinstance(value, str)
        and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,95}", value) is not None
    )
    return str(value)


def _types(
    table: dict[str, Any],
    *,
    strings: str = "",
    booleans: str = "",
    integers: str = "",
    string_arrays: str = "",
) -> None:
    for field in strings.split():
        _require(type(table[field]) is str)
    for field in booleans.split():
        _require(type(table[field]) is bool)
    for field in integers.split():
        _require(type(table[field]) is int and table[field] >= 0)
    for field in string_arrays.split():
        _require(isinstance(table[field], list) and all(type(item) is str for item in table[field]))


def _indexed(value: Any, expected: set[str]) -> dict[str, dict[str, Any]]:
    _require(isinstance(value, list) and len(value) == len(expected))
    indexed: dict[str, dict[str, Any]] = {}
    for row in value:
        _require(isinstance(row, dict))
        identity = _identity(row.get("id"))
        _require(identity in expected and identity not in indexed)
        indexed[identity] = row
    _require(set(indexed) == expected)
    return indexed


def _reconcile(
    config: dict[str, dict[str, Any]],
) -> tuple[str, str, list[dict[str, Any]], list[str]]:
    bootstrap = _keys(config[SOURCEFILES[0]], "bootstrap git github huggingface discovery")
    archive = _keys(config[SOURCEFILES[1]], "archive huggingface rights controls")
    portfolio = _keys(
        config[SOURCEFILES[2]], "schema_version portfolio_id canonical_control_plane products"
    )
    product = _keys(
        config[SOURCEFILES[3]],
        "schema_version product_id product_class status authority canonical_repository "
        "public_data_boundary release_mode",
    )
    base = _keys(
        bootstrap["bootstrap"],
        "schema_version repository_name description default_branch default_visibility remote_name "
        "initial_commit_message receipt_directory max_command_output_bytes",
    )
    _keys(bootstrap["git"], "pull_ff fetch_prune rerere_enabled autocrlf commit_gpgsign")
    gh = _keys(
        bootstrap["github"],
        "host owner repository visibility homepage enable_issues enable_projects enable_wiki "
        "enable_discussions allow_merge_commit allow_squash_merge allow_rebase_merge "
        "delete_branch_on_merge apply_controls_by_default topics release_environments rules",
    )
    _keys(
        gh["rules"],
        "require_pull_request required_approving_review_count require_code_owner_review "
        "require_conversation_resolution require_linear_history require_signed_commits "
        "block_force_pushes block_deletions required_checks",
    )
    _keys(
        bootstrap["discovery"],
        "max_depth max_repositories include_hidden keywords exclude_directories",
    )
    hf = _keys(
        bootstrap["huggingface"],
        "enabled namespace private_by_default create_missing_by_default repositories",
    )
    policy = _keys(
        archive["archive"],
        "schema_version policy description github_repository github_branch github_release_mode "
        "minimum_publish_gate authoritative_custody local_staging_policy "
        "minimum_provider_separated_public_replicas",
    )
    targets = _keys(
        archive["huggingface"],
        "namespace targets_are_provisional private_by_default publication_mode "
        "requires_exact_repository_approval minimum_publish_gate targets",
    )
    rights = _keys(
        archive["rights"], "unknown restricted_or_unknown open_licence_verified public_domain"
    )
    controls = _keys(
        archive["controls"],
        "require_source_manifest require_sha256 require_edition_bound_rights "
        "require_generated_product_lineage require_release_gate_acceptance "
        "require_published_receipt never_upload_unresolved_rights rights_state_is_public_metadata "
        "require_prohibited_data_scan "
        "require_secret_scan require_two_provider_separated_public_receipts "
        "require_anonymous_restore forbid_durable_local_only_objects",
    )
    _types(
        base,
        strings=" ".join(set(base) - {"max_command_output_bytes"}),
        integers="max_command_output_bytes",
    )
    _types(
        bootstrap["git"],
        strings="pull_ff autocrlf",
        booleans="fetch_prune rerere_enabled commit_gpgsign",
    )
    _types(
        bootstrap["discovery"],
        integers="max_depth max_repositories",
        booleans="include_hidden",
        string_arrays="keywords exclude_directories",
    )
    _types(
        gh,
        strings="host owner repository visibility homepage",
        booleans="enable_issues enable_projects enable_wiki enable_discussions allow_merge_commit "
        "allow_squash_merge allow_rebase_merge delete_branch_on_merge apply_controls_by_default",
        string_arrays="topics release_environments",
    )
    _types(
        gh["rules"],
        integers="required_approving_review_count",
        string_arrays="required_checks",
        booleans="require_pull_request require_code_owner_review require_conversation_resolution "
        "require_linear_history require_signed_commits block_force_pushes block_deletions",
    )
    _types(
        policy,
        strings=" ".join(set(policy) - {"minimum_provider_separated_public_replicas"}),
        integers="minimum_provider_separated_public_replicas",
    )
    _require(
        all(
            value is True
            for key, value in controls.items()
            if key != "never_upload_unresolved_rights"
        )
    )
    _require(type(controls["never_upload_unresolved_rights"]) is bool)
    _require(
        rights
        == {
            "unknown": "retain_metadata_and_citation_receipt_only",
            "restricted_or_unknown": "retain_metadata_and_citation_receipt_only",
            "open_licence_verified": "bytes_allowed_only_for_exact_edition_and_manifest",
            "public_domain": "bytes_allowed_when_edition_and_provenance_are_bound",
        }
    )
    namespace = _identity(targets["namespace"])
    _require(hf["namespace"] in {"", namespace})
    _require(
        hf["enabled"] is True
        and hf["private_by_default"] is False
        and hf["create_missing_by_default"] is False
    )
    _require(targets["private_by_default"] is False and targets["targets_are_provisional"] is False)
    _require(type(targets["requires_exact_repository_approval"]) is bool)
    _require(
        targets["publication_mode"] == "public_medallion"
        and targets["minimum_publish_gate"] == "G3"
    )
    _require(
        policy["schema_version"]
        == base["schema_version"]
        == portfolio["schema_version"]
        == product["schema_version"]
        == "1.0"
    )
    canonical = policy["github_repository"]
    _require(isinstance(canonical, str) and canonical.count("/") == 1)
    owner, repository = canonical.split("/")
    _identity(owner)
    _require(repository == "global-family-justice-data")
    _require(
        gh["owner"] in {"", owner} and gh["repository"] == base["repository_name"] == repository
    )
    _require(
        gh["host"] == "github.com" and gh["visibility"] == base["default_visibility"] == "public"
    )
    _require(base["default_branch"] == policy["github_branch"] == "main")
    _require(base["remote_name"] == "origin" and base["receipt_directory"] == "build/bootstrap")
    _require(policy["policy"] == "fail_closed" and policy["minimum_publish_gate"] == "G6")
    _require(policy["github_release_mode"] == "release-candidate-then-stable")
    _require(policy["authoritative_custody"] == "public_remote_only")
    _require(policy["local_staging_policy"] == "ephemeral_until_two_public_receipts_verify")
    _require(
        type(policy["minimum_provider_separated_public_replicas"]) is int
        and policy["minimum_provider_separated_public_replicas"] == 2
    )
    _require(
        portfolio["portfolio_id"] == "GFJD" and portfolio["canonical_control_plane"] == "github"
    )
    _require(
        product
        == {
            "schema_version": "1.0",
            "product_id": "gfjd-platform",
            "product_class": "canonical_source",
            "status": "active",
            "authority": "github",
            "canonical_repository": canonical,
            "public_data_boundary": "aggregate_only",
            "release_mode": "evidence_gated",
        }
    )
    products = _indexed(
        portfolio["products"], {"gfjd-platform", *(f"gfjd-{role}" for role in ROLE_RULES)}
    )
    platform = _keys(
        products["gfjd-platform"], "id class status authority repository local_path description"
    )
    _types(platform, strings=" ".join(platform))
    _require(
        platform["class"] == "canonical_source"
        and platform["status"] == "active"
        and platform["authority"] == "github"
    )
    _require(platform["repository"] == canonical and platform["local_path"] == ".")
    repos = _indexed(hf["repositories"], set(ROLE_RULES))
    archive_targets = _indexed(targets["targets"], set(ROLE_RULES))
    roles = []
    for role, (kind, mode, payload, gate, layers) in ROLE_RULES.items():
        repo = _keys(
            repos[role],
            "id name repo_type visibility publication_mode" + (" sdk" if kind == "space" else ""),
        )
        target = _keys(
            archive_targets[role], "id repository repo_type payload_policy minimum_publish_gate"
        )
        name = f"gfjd-{role}"
        _require(repo["name"] == target["repository"] == name)
        _require(
            repo["repo_type"] == target["repo_type"] == kind and repo["visibility"] == "public"
        )
        _require(
            repo["publication_mode"] == mode
            and target["payload_policy"] == payload
            and target["minimum_publish_gate"] == gate
        )
        if kind == "space":
            _require(repo["sdk"] == "static")
        distribution = _keys(
            products[name], "id class status authority huggingface_repository publication_mode"
        )
        classification = (
            "experimental" if role == "extraction-benchmark" else "generated_distribution"
        )
        authority = "github" if role == "extraction-benchmark" else "gfjd-platform-release"
        _require(distribution["class"] == classification and distribution["authority"] == authority)
        _require(
            distribution["status"] == "planned"
            and distribution["publication_mode"] == "generated_only"
        )
        _require(distribution["huggingface_repository"] == f"{namespace}/{name}")
        prefix = "spaces" if kind == "space" else "datasets"
        roles.append(
            {
                "id": role,
                "repository": f"{namespace}/{name}",
                "repo_type": kind,
                "visibility": "public",
                "classification": classification,
                "authority": authority,
                "publication_mode": mode,
                "payload_policy": payload,
                "minimum_publish_gate": gate,
                "layer_constraints": list(layers),
                "layer_policy_state": "desired_prospective",
                "control_plane": canonical,
                "declared_status": "planned",
                "desired_link": {
                    "url": f"https://huggingface.co/{prefix}/{namespace}/{name}",
                    "requested": False,
                },
                "factual_states": dict.fromkeys(
                    (
                        "availability",
                        "retrieval",
                        "rights",
                        "custody",
                        "accepted_gold",
                        "release_authority",
                        "publication",
                        "standards_conformance",
                    ),
                    "unverified",
                ),
            }
        )
    diagnostics = ["draft_links_are_not_availability_evidence", "benchmark_remains_experimental"]
    if controls["never_upload_unresolved_rights"] is False:
        diagnostics.append("unresolved_rights_flag_does_not_override_exact_edition_policy")
    return namespace, canonical, roles, diagnostics


def prepare_estate(config_bytes: dict[str, bytes]) -> dict[str, bytes]:
    """Compile four TOMLs and exact frozen policy bytes into eight draft files.

    SOURCEFILES remains the four configuration paths. The policy is a fifth,
    mandatory supplied input, verified before parsing configuration. No implicit
    policy-file access or current-working-directory fallback is permitted.
    """
    try:
        _require(
            isinstance(config_bytes, dict) and set(config_bytes) == {*SOURCEFILES, POLICY_REFERENCE}
        )
        policy = config_bytes[POLICY_REFERENCE]
        _require(isinstance(policy, bytes) and 0 < len(policy) <= MAX_CONFIG_BYTES)
        policy_digest = _sha(policy)
        _require(policy_digest == POLICY_SHA256)
        config = {name: _parse(config_bytes[name]) for name in SOURCEFILES}
        namespace, canonical, roles, diagnostics = _reconcile(config)
        outputs: dict[str, bytes] = {}
        links = "\n".join(
            f"- {item['id']}: [{item['repository']}]({item['desired_link']['url']}) "
            "(desired; not requested)"
            for item in roles
        )
        boundary = (
            "Draft configuration only. No remote availability, retrieval, custody, rights "
            "clearance, accepted Gold, maturity, standards conformance, publication or release "
            "is established. Unknown/restricted rights permit metadata and citation receipts "
            "only; source bytes require exact-edition rights, provenance, safety and applicable "
            "gate evidence. No licence is asserted."
        )
        for item in roles:
            role = item["id"]
            card = (
                f"# Draft: {item['repository']}\n\n{boundary}\n\n"
                f"Role: {role}\n\nClassification: {item['classification']}\n\n"
                f"Desired payload policy: {item['payload_policy']}\n\n"
                f"Prospective layer constraints: {', '.join(item['layer_constraints'])}\n\n"
                f"Minimum Hugging Face publication gate: {item['minimum_publish_gate']}; "
                "GitHub stable publication gate remains G6. No gate is accepted here.\n\n"
                f"Canonical control plane: [GitHub](https://github.com/{canonical}) "
                "(desired reference; not requested).\n\n"
                "These drafts do not establish Hugging Face card conformance.\n\n"
                f"## Desired estate links\n\n{links}\n"
            )
            path = "explorer/README.md" if role == "explorer" else f"datasets/gfjd-{role}/README.md"
            outputs[path] = card.encode("utf-8")
        page_links = "".join(
            f'<li><a href="{html.escape(item["desired_link"]["url"], quote=True)}">'
            f"{html.escape(item['repository'])}</a> (desired; not requested)</li>"
            for item in roles
        )
        outputs["explorer/index.html"] = (
            '<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            '<meta http-equiv="Content-Security-Policy" '
            "content=\"default-src 'none'; base-uri 'none'; form-action 'none'\">"
            "<title>Draft GFJD explorer</title></head><body><main><h1>Draft GFJD explorer</h1>"
            f"<p>{html.escape(boundary)}</p><p>Future inputs: "
            "accepted Gold or released Platinum only. "
            f"No dataset is loaded.</p><ul>{page_links}</ul></main></body></html>\n"
        ).encode()
        manifest = {
            "contract_version": VERSION,
            "state": "offline_draft_preparation",
            "namespace": namespace,
            "canonical_control_plane": canonical,
            "github_minimum_publish_gate": "G6",
            "roles": roles,
            "input_sha256": {
                name: _sha(config_bytes[name]) for name in (*SOURCEFILES, POLICY_REFERENCE)
            },
            "implementation_sha256": _sha(Path(__file__).read_bytes()),
            "role_policy": {
                "path": POLICY_REFERENCE,
                "sha256": policy_digest,
                "state": "approved_direction_not_qualification",
            },
            "artifact_sha256": {name: _sha(raw) for name, raw in sorted(outputs.items())},
            "diagnostics": sorted(diagnostics),
            "authority": dict.fromkeys(
                (
                    "network",
                    "source_access",
                    "remote_creation",
                    "rights_clearance",
                    "maturity",
                    "gold_promotion",
                    "publication",
                    "release",
                    "gate_acceptance",
                ),
                False,
            ),
        }
        outputs["estate-manifest.json"] = _canonical(manifest) + b"\n"
        return dict(sorted(outputs.items()))
    except (
        ValueError,
        TypeError,
        KeyError,
        AttributeError,
        OSError,
        OverflowError,
        RecursionError,
    ):
        raise EstateError("estate declaration validation failed") from None


def verify_estate(config_bytes: dict[str, bytes], artifacts: dict[str, bytes]) -> None:
    """Regenerate the exact safe artifact set and every byte; trust no self-hash."""
    expected = prepare_estate(config_bytes)
    if not isinstance(artifacts, dict) or set(artifacts) != set(expected):
        raise EstateError("estate artifact verification failed")
    if any(not isinstance(raw, bytes) or raw != expected[name] for name, raw in artifacts.items()):
        raise EstateError("estate artifact verification failed")
