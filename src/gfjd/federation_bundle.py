"""Reference-only federation drafts, not source custody or publication.

Existing estate helpers and this compiler fingerprint their implementation files.
No metadata identifier, source path or remote endpoint is opened.
"""

import hashlib
import json
from pathlib import Path
from typing import Any

from gfjd.federation_croissant import PROFILE_SHA256, assess_croissant
from gfjd.federation_dcat import SHAPE_SHA256, validate_catalogue
from gfjd.federation_metadata import MetadataError, parse_json, require
from gfjd.federation_openlineage import SCHEMA_SHA256, validate_design_event
from gfjd.federation_references import reconcile_references
from gfjd.federation_rocrate import CONTEXT_SHA256, assess_rocrate
from gfjd.medallion_estate import prepare_estate

ASSETS = {
    "openlineage-2-0-2.json": SCHEMA_SHA256,
    "dcat-ap-3.0.1-shapes.ttl": SHAPE_SHA256["shapes.ttl"],
    "dcat-ap-3.0.1-range.ttl": SHAPE_SHA256["range.ttl"],
    "ro-crate-1.3-context.jsonld": CONTEXT_SHA256,
    "gfjd-croissant-profile-v1.json": PROFILE_SHA256,
}


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _encode(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode() + b"\n"
    )


def _assess(raw: bytes, media: str, standards: dict[str, bytes]) -> dict[str, Any]:
    if media == "application/n-triples":
        return validate_catalogue(
            raw,
            {
                "shapes.ttl": standards["dcat-ap-3.0.1-shapes.ttl"],
                "range.ttl": standards["dcat-ap-3.0.1-range.ttl"],
            },
        )
    document = parse_json(raw)
    require(isinstance(document, dict))
    if "@graph" in document:
        return assess_rocrate(raw, standards["ro-crate-1.3-context.jsonld"])
    if "@context" in document or document.get("@type") == "sc:Dataset":
        return assess_croissant(raw, standards["gfjd-croissant-profile-v1.json"])
    if "schemaURL" in document:
        return validate_design_event(raw, standards["openlineage-2-0-2.json"])
    return {
        "status": "profile_not_selected",
        "metadata_sha256": _sha(raw),
        "full_conformance": "unverified",
        "factual_evidence": "unverified",
    }


def prepare_bundle(
    scope_raw: bytes,
    expected_sha256: str,
    metadata_bank: dict[str, bytes],
    estate_inputs: dict[str, bytes],
    standards: dict[str, bytes],
) -> dict[str, bytes]:
    """Recompute all declarations; never fetch references or copy input metadata."""
    try:
        require(type(standards) is dict and set(standards) == set(ASSETS))
        for name, digest in ASSETS.items():
            raw = standards[name]
            require(type(raw) is bytes and 0 < len(raw) <= 256 * 1024)
            require(_sha(raw) == digest)
        references = reconcile_references(scope_raw, expected_sha256, metadata_bank, estate_inputs)
        estate = prepare_estate(estate_inputs)
        scope = parse_json(scope_raw)
        media: dict[str, str] = {}
        for item in scope["objects"]:
            digest = item["metadata_sha256"]
            require(digest not in media or media[digest] == item["media_type"])
            media[digest] = item["media_type"]
        assessments = {
            digest: _assess(raw, media[digest], standards)
            for digest, raw in sorted(metadata_bank.items())
        }
        outputs = {"estate/" + name: raw for name, raw in estate.items()}
        outputs["reference-manifest.json"] = _encode(references)
        outputs["metadata-assessments.json"] = _encode(assessments)
        outputs["README.md"] = (
            b"# Offline federation draft\n\nReferences and assessment reports only; "
            b"no input metadata or source payload is copied. Desired estate links are "
            b"not requested or registered. Standards/profile checks do not establish "
            b"factual evidence, custody, rights, maturity, Gold, gates or publication. "
            b"PROV replay exports remain separately bound, not implicitly attached.\n"
        )
        manifest = {
            "contract_version": "gfjd-federation-draft-bundle-v1",
            "state": "offline_federation_draft",
            "scope_sha256": _sha(scope_raw),
            "metadata_sha256": sorted(metadata_bank),
            "estate_input_sha256": {name: _sha(raw) for name, raw in sorted(estate_inputs.items())},
            "standard_sha256": dict(sorted(ASSETS.items())),
            "implementation_sha256": _sha(Path(__file__).read_bytes()),
            "artifact_sha256": {name: _sha(raw) for name, raw in sorted(outputs.items())},
            "incomplete_document_count": sum(
                report.get("status")
                in {"profile_not_selected", "profile_incomplete", "shape_checks_failed"}
                for report in assessments.values()
            ),
            "factual_evidence": "unverified",
            "full_conformance": "unverified",
            "provenance_integration": "pending_exact_replay_binding",
            "authority": dict.fromkeys(
                (
                    "network",
                    "source_access",
                    "publication",
                    "release",
                    "rights_clearance",
                    "custody",
                    "maturity",
                    "gold_promotion",
                    "gate_acceptance",
                    "partner_registration",
                ),
                False,
            ),
        }
        outputs["bundle-manifest.json"] = _encode(manifest)
        return dict(sorted(outputs.items()))
    except Exception:
        raise MetadataError("Federation bundle contract violation") from None


def verify_bundle(
    scope_raw: bytes,
    expected_sha256: str,
    metadata_bank: dict[str, bytes],
    estate_inputs: dict[str, bytes],
    standards: dict[str, bytes],
    artifacts: dict[str, bytes],
) -> None:
    try:
        expected = prepare_bundle(
            scope_raw, expected_sha256, metadata_bank, estate_inputs, standards
        )
        require(type(artifacts) is dict and set(artifacts) == set(expected))
        require(
            all(type(raw) is bytes and raw == expected[name] for name, raw in artifacts.items())
        )
    except Exception:
        raise MetadataError("Federation bundle contract violation") from None
