"""Offline validation for the byte-pinned shared medallion contract family.

The common vocabulary and GFJD's native layer names are deliberately distinct.
This module validates portable v1-v4 documents and exposes an explicit mapping;
it never treats schema conformance as factual evidence or promotion authority.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from gfjd.federation_metadata import parse_json


class SharedMedallionError(ValueError):
    """A shared contract, document, or GFJD mapping failed closed."""


ROOT = Path(__file__).resolve().parents[2]
CONTRACT_ROOT = ROOT / "contracts" / "medallion"
PACKAGE_CONTRACT_ROOT = Path(__file__).resolve().parent / "federation_specs"
MAPPING_PROFILE_SHA256 = "8cf918f88ef60afe5ac0fdaece6836f6bf640465f34ddd0ac5c2a63d26a4f4ed"
SHARED_CONTRACTS: dict[str, dict[str, str]] = {
    "v1": {
        "schema": "medallion-conformance.schema.json",
        "package_schema": "shared-medallion-v1.schema.json",
        "sha256": "4c1ee81b026c64cf8f962d602cd64441a4a023c132346349c8b27dab0981f10e",
    },
    "v2": {
        "schema": "field-lineage.schema.json",
        "package_schema": "shared-medallion-v2.schema.json",
        "sha256": "bf31ee62a3566a8fde512748b79f644e0fab760f60924e4eb9d510d3c1ef6f8a",
    },
    "v3": {
        "schema": "backfill-replay.schema.json",
        "package_schema": "shared-medallion-v3.schema.json",
        "sha256": "5d0f472b124701ef66dcc1a5c39670826b8e95e5faf576cc394a3cd22df9419c",
    },
    "v4": {
        "schema": "federation.schema.json",
        "package_schema": "partner-gma-federation.schema.json",
        "sha256": "ac28485a70e0853266e4c140f9a07cd557eb27816b0b408b9bf2927a4cffacec",
    },
}

# Shared v1 uses GMA's Bronze strata. GFJD B0 is raw evidence, so it projects to
# bronze_b2 rather than the unrelated shared bronze_b0 source-index concept.
# GFJD B1 and Silver are distinct native stages inside the shared Silver class;
# their boundary remains visible through v2 field lineage, never a false v1
# promotion edge.
GFJD_LAYER_PROJECTION: dict[str, dict[str, Any]] = {
    "B0": {
        "native_layer": "B0",
        "shared_layer": "bronze_b2",
        "semantic_role": "immutable_raw_evidence",
        "direct_alias": False,
        "v1_promotion_boundary": True,
    },
    "B1": {
        "native_layer": "B1",
        "shared_layer": "silver",
        "semantic_role": "source_faithful_analytical_representation",
        "direct_alias": False,
        "v1_promotion_boundary": True,
    },
    "Silver": {
        "native_layer": "Silver",
        "shared_layer": "silver",
        "semantic_role": "harmonised_evidence",
        "direct_alias": False,
        "v1_promotion_boundary": False,
    },
    "Gold": {
        "native_layer": "Gold",
        "shared_layer": "gold",
        "semantic_role": "owner_accepted_comparable_evidence",
        "direct_alias": False,
        "v1_promotion_boundary": True,
    },
    "Platinum": {
        "native_layer": "Platinum",
        "shared_layer": "platinum",
        "semantic_role": "release_bound_product",
        "direct_alias": False,
        "v1_promotion_boundary": True,
    },
}

_ALLOWED_V1_TRANSITIONS = {
    ("bronze_b0", "bronze_b1"),
    ("bronze_b1", "bronze_b2"),
    ("bronze_b1", "silver"),
    ("bronze_b2", "silver"),
    ("silver", "gold"),
    ("gold", "platinum"),
}
_NO_AUTHORITY = {
    "gate_acceptance": False,
    "gold_promotion": False,
    "publication": False,
    "release": False,
    "rights_clearance": False,
}
_UPSTREAM_CONTRACT_REVISIONS = {
    "archive-govt-nz": "dcc8f37f5642fc6b4337c49bd482b126325e6b6c",
    "global-medicines-atlas": "0190183f6b313ad21746c5b15b7cf4bd7153085c",
}
_CANARIES = {
    "v1": ("valid.json", "invalid-missing-gate.json"),
    "v2": ("valid-field-lineage.json", "invalid-unversioned-code.json"),
    "v3": ("valid-backfill-replay.json", "invalid-overwrite-policy.json"),
    "v4": ("valid.json", "invalid-mismatched-digest.json"),
}


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _schema(version: str) -> tuple[bytes, dict[str, Any]]:
    if version not in SHARED_CONTRACTS:
        raise SharedMedallionError("unsupported shared medallion contract")
    item = SHARED_CONTRACTS[version]
    raw = (PACKAGE_CONTRACT_ROOT / item["package_schema"]).read_bytes()
    if _sha(raw) != item["sha256"]:
        raise SharedMedallionError("shared medallion schema digest mismatch")
    schema = json.loads(raw)
    Draft202012Validator.check_schema(schema)
    return raw, schema


def verify_contract_assets() -> dict[str, Any]:
    """Verify every repository and installed-package schema copy byte-for-byte."""
    digests: dict[str, str] = {}
    for version in SHARED_CONTRACTS:
        packaged, _ = _schema(version)
        repository = (CONTRACT_ROOT / version / SHARED_CONTRACTS[version]["schema"]).read_bytes()
        if packaged != repository:
            raise SharedMedallionError("repository and package schema copies drift")
        digests[version] = _sha(packaged)
    mapping_name = "gfjd-layer-mapping-v1.json"
    packaged_mapping = (PACKAGE_CONTRACT_ROOT / mapping_name).read_bytes()
    repository_mapping = (CONTRACT_ROOT / mapping_name).read_bytes()
    if packaged_mapping != repository_mapping or _sha(packaged_mapping) != MAPPING_PROFILE_SHA256:
        raise SharedMedallionError("GFJD layer mapping profile drift")
    mapping = parse_json(packaged_mapping)
    if (
        type(mapping) is not dict
        or mapping.get("profile_version") != "gfjd-shared-medallion-layer-map-v1"
        or mapping.get("shared_contract_versions") != list(SHARED_CONTRACTS)
        or mapping.get("mappings") != [project_gfjd_layer(name) for name in GFJD_LAYER_PROJECTION]
    ):
        raise SharedMedallionError("GFJD layer mapping profile mismatch")
    return {
        "status": "verified",
        "versions": list(SHARED_CONTRACTS),
        "schema_sha256": digests,
        "mapping_profile_sha256": MAPPING_PROFILE_SHA256,
        "authority": dict(_NO_AUTHORITY),
    }


def project_gfjd_layer(native_layer: str) -> dict[str, Any]:
    """Return a copy of the explicit GFJD-to-common semantic projection."""
    try:
        return dict(GFJD_LAYER_PROJECTION[native_layer])
    except (KeyError, TypeError):
        raise SharedMedallionError("unsupported GFJD native layer") from None


def build_compatibility_report() -> dict[str, Any]:
    """Recompute the repository's portable canaries and loss-aware mapping."""
    assets = verify_contract_assets()
    positive = []
    negative = []
    for version, (positive_name, negative_name) in _CANARIES.items():
        fixture_root = CONTRACT_ROOT / version / "fixtures"
        positive_raw = (fixture_root / positive_name).read_bytes()
        validation = validate_shared_document(version, positive_raw)
        positive.append(
            {
                "version": version,
                "fixture": positive_name,
                "document_sha256": validation["document_sha256"],
                "status": validation["status"],
            }
        )
        negative_raw = (fixture_root / negative_name).read_bytes()
        try:
            validate_shared_document(version, negative_raw)
        except SharedMedallionError:
            rejected = True
        else:
            rejected = False
        if not rejected:
            raise SharedMedallionError("negative shared-contract canary passed")
        negative.append(
            {
                "version": version,
                "fixture": negative_name,
                "document_sha256": _sha(negative_raw),
                "rejected": True,
            }
        )
    return {
        "contract_version": "gfjd-shared-medallion-compatibility-report-v1",
        "status": "repository_compatibility_verified",
        "upstream_contract_revisions": dict(_UPSTREAM_CONTRACT_REVISIONS),
        "schema_sha256": assets["schema_sha256"],
        "mapping_profile_sha256": assets["mapping_profile_sha256"],
        "gfjd_layer_projection": [project_gfjd_layer(name) for name in GFJD_LAYER_PROJECTION],
        "positive_canaries": positive,
        "negative_canaries": negative,
        "live_interoperability": "unverified",
        "authority": dict(_NO_AUTHORITY),
    }


def verify_compatibility_report(report: dict[str, Any]) -> None:
    """Reject any report that differs from a complete local recomputation."""
    try:
        if type(report) is not dict or report != build_compatibility_report():
            raise SharedMedallionError("shared compatibility report mismatch")
    except SharedMedallionError:
        raise
    except Exception:
        raise SharedMedallionError("shared compatibility report violation") from None


def validate_shared_document(version: str, raw: bytes) -> dict[str, Any]:
    """Validate one supplied document offline against pinned schema and semantics."""
    try:
        if type(raw) is not bytes or not 0 < len(raw) <= 8 * 1024 * 1024:
            raise SharedMedallionError("shared document byte boundary")
        _, schema = _schema(version)
        document = parse_json(raw)
        if type(document) is not dict:
            raise SharedMedallionError("shared document must be an object")
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        if next(validator.iter_errors(document), None) is not None:
            raise SharedMedallionError("shared document schema violation")
        if version == "v1":
            _validate_v1_semantics(document)
        elif version == "v4":
            _validate_v4_semantics(document)
        return {
            "status": "conformant",
            "version": version,
            "schema_sha256": SHARED_CONTRACTS[version]["sha256"],
            "document_sha256": _sha(raw),
            "validation_scope": (
                "schema_and_shared_semantics" if version in {"v1", "v4"} else "schema"
            ),
            "authority": dict(_NO_AUTHORITY),
        }
    except SharedMedallionError:
        raise
    except Exception:
        raise SharedMedallionError("shared medallion document violation") from None


def _validate_v1_semantics(document: dict[str, Any]) -> None:
    artifacts = {item["artifact_id"]: item for item in document["artifacts"]}
    if len(artifacts) != len(document["artifacts"]):
        raise SharedMedallionError("duplicate v1 artifact identity")
    for decision in document["promotion_decisions"]:
        if (decision["from_layer"], decision["to_layer"]) not in _ALLOWED_V1_TRANSITIONS:
            raise SharedMedallionError("non-adjacent v1 transition")
        subject = artifacts.get(decision["subject_artifact_id"])
        if subject is None or subject["layer"] != decision["to_layer"]:
            raise SharedMedallionError("v1 promotion subject mismatch")
        if set(subject["lineage"]["input_sha256"]) != set(decision["input_sha256"]):
            raise SharedMedallionError("v1 lineage digest mismatch")
        if decision["status"] == "approved":
            if not set(decision["required_gate_ids"]).issubset(decision["passed_gate_ids"]):
                raise SharedMedallionError("v1 required gate missing")
            if decision["rights_decision"]["status"] != "approved":
                raise SharedMedallionError("v1 rights not approved")
            if subject["promotion_status"] != "approved_within_scope":
                raise SharedMedallionError("v1 artifact is not approved")


def _validate_v4_semantics(document: dict[str, Any]) -> None:
    location = document["location"]
    verification = document["verification"]
    rights = document["rights"]
    for field in ("dataset", "revision", "path", "sha256", "bytes"):
        if location[field] != verification[field]:
            raise SharedMedallionError(f"v4 verification identity mismatch: {field}")
    if (
        rights["subject_sha256"] != location["sha256"]
        or rights["dataset"] != location["dataset"]
        or rights["path"] != location["path"]
    ):
        raise SharedMedallionError("v4 authorization identity mismatch")
    _validate_v4_layers(document)
    _validate_v4_lifecycle(document)
    _validate_v4_recovery(document["recovery"])


def _validate_v4_layers(document: dict[str, Any]) -> None:
    source = document["source"]
    is_bronze = source["layer"] == "bronze"
    if source["bronze_stratum"] == "B0" and source["representation"] != "index":
        raise SharedMedallionError("v4 B0 requires index representation")
    if is_bronze != (source["bronze_stratum"] is not None):
        raise SharedMedallionError("v4 Bronze stratum mismatch")
    if source["representation"] == "raw" and (not is_bronze or source["bronze_stratum"] != "B2"):
        raise SharedMedallionError("v4 raw evidence requires Bronze B2")
    if source["representation"] == "projection" and not document["lineage"]["inputs"]:
        raise SharedMedallionError("v4 projection lineage is empty")
    if not is_bronze and document["lineage"]["promotion_receipt"] is None:
        raise SharedMedallionError("v4 derived layer lacks promotion receipt")
    expected = {"index": "B0", "metadata": "B1"}
    if source["representation"] in expected and (
        not is_bronze or source["bronze_stratum"] != expected[source["representation"]]
    ):
        raise SharedMedallionError("v4 index or metadata stratum mismatch")
    if (document["evidence_kind"] == "synthetic") != (source["comparison_cohort"] == "synthetic"):
        raise SharedMedallionError("v4 evidence/cohort mismatch")


def _validate_v4_lifecycle(document: dict[str, Any]) -> None:
    source = document["source"]
    verification = document["verification"]
    cache = document["cache"]
    producer = document["authority"]["producer_repository"]
    if not document["publication"]["run"].startswith(
        f"https://github.com/{producer}/actions/runs/"
    ):
        raise SharedMedallionError("v4 publication run producer mismatch")
    if datetime.fromisoformat(source["retrieved_at"]) > datetime.fromisoformat(
        verification["verified_at"]
    ):
        raise SharedMedallionError("v4 retrieval/verification time order")
    if datetime.fromisoformat(cache["created_at"]) >= datetime.fromisoformat(cache["expires_at"]):
        raise SharedMedallionError("v4 cache time order")
    if (cache["state"] == "removed") != (cache["cleanup_receipt"] is not None):
        raise SharedMedallionError("v4 cache cleanup state mismatch")


def _validate_v4_recovery(recovery: dict[str, Any]) -> None:
    distinct = (
        recovery["administrative_domain"].strip().casefold()
        != recovery["primary_administrative_domain"].strip().casefold()
        and recovery["region"].strip().casefold() != recovery["primary_region"].strip().casefold()
        and "unverified"
        not in {
            recovery["region"].strip().casefold(),
            recovery["primary_region"].strip().casefold(),
        }
    )
    evidenced = (
        recovery["restore_receipt"] is not None
        and recovery["authorization_receipt"] is not None
        and recovery["rpo_seconds"] is not None
        and recovery["rto_seconds"] is not None
    )
    if recovery["role"] == "independent_replica" and not (distinct and evidenced):
        raise SharedMedallionError("v4 independent replica evidence incomplete")
    if recovery["role"] == "compatibility_replica" and recovery["independent"]:
        raise SharedMedallionError("v4 compatibility replica claims independence")
    if recovery["independent"] != (recovery["role"] == "independent_replica"):
        raise SharedMedallionError("v4 independent role mismatch")
