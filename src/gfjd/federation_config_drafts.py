"""Actual-configuration metadata drafts, not factual dataset declarations.

Supplied configuration is reconciled by the estate compiler. Only implementation
fingerprinting reads files; no source, context, identifier or remote loader runs.
Generated metadata is retained deliberately, unlike the input-no-copy bundle API.
"""

import hashlib
import json
from pathlib import Path
from typing import Any, cast

from gfjd import federation_croissant, federation_metadata, federation_rocrate, medallion_estate
from gfjd.federation_metadata import MetadataError, parse_json, require

ASSETS = {
    "ro-crate-1.3-context.jsonld": federation_rocrate.CONTEXT_SHA256,
    "gfjd-croissant-profile-v1.json": federation_croissant.PROFILE_SHA256,
}
MISSING_FACTS = [
    "publication_date",
    "dataset_license",
    "creator",
    "publisher",
    "distribution_content",
    "content_hashes_sizes_formats",
    "release_version",
    "runtime_lineage",
    "publication_receipt",
    "registration_receipt",
    "custody_receipts",
]


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _encode(value: Any) -> bytes:
    return (
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
        ).encode()
        + b"\n"
    )


def _boundary() -> dict[str, Any]:
    return {
        "factual_states": dict.fromkeys(
            (
                "publication",
                "source_truth",
                "ownership",
                "custody",
                "full_conformance",
                "accepted_gold",
                "maturity",
                "gates",
            ),
            "unverified",
        ),
        "authority": dict.fromkeys(
            (
                "network",
                "source_access",
                "publication",
                "release",
                "rights_clearance",
                "custody",
                "gold_promotion",
                "maturity",
                "gate_acceptance",
                "partner_registration",
                "execution",
            ),
            False,
        ),
        "filesystem_access": "compiler-and-component-implementation-fingerprints-only",
    }


def _prepare(estate_inputs: dict[str, bytes], standards: dict[str, bytes]) -> dict[str, bytes]:
    estate = medallion_estate.prepare_estate(estate_inputs)
    require(type(standards) is dict and set(standards) == set(ASSETS))
    for name, digest in ASSETS.items():
        raw = standards[name]
        require(type(raw) is bytes and 0 < len(raw) <= 256 * 1024 and _sha(raw) == digest)
    profile = parse_json(standards["gfjd-croissant-profile-v1.json"])
    estate_raw = estate["estate-manifest.json"]
    estate_sha = _sha(estate_raw)
    manifest = parse_json(estate_raw)
    input_hashes = {name: _sha(raw) for name, raw in sorted(estate_inputs.items())}
    outputs = {"estate/" + name: raw for name, raw in estate.items()}
    assessments: dict[str, Any] = {}
    declarations = []
    for index, role in enumerate(manifest["roles"]):
        record = {
            "declaration": role,
            "missing_facts": list(MISSING_FACTS),
            "profile_assessments": [],
            "field_provenance": {},
        }
        if role["repo_type"] == "space":
            record["missing_facts"] = [
                "space_content_license" if fact == "dataset_license" else fact
                for fact in MISSING_FACTS
            ]
        if role["repo_type"] == "dataset":
            name = "Draft: " + role["repository"]
            description = (
                "Prospective preparation only. Declared role: "
                + role["id"]
                + "; declared payload policy: "
                + role["payload_policy"]
                + "."
            )
            docs = {
                "croissant.json": {
                    "@context": profile["context"],
                    "@type": "sc:Dataset",
                    "conformsTo": profile["conformsTo"],
                    "name": name,
                    "description": description,
                },
                "ro-crate-metadata.json": {
                    "@context": federation_rocrate.CONTEXT_URI,
                    "@graph": [
                        {
                            "@id": "ro-crate-metadata.json",
                            "@type": "CreativeWork",
                            "about": {"@id": "./"},
                            "conformsTo": {"@id": federation_rocrate.VERSION_URI},
                        },
                        {"@id": "./", "@type": "Dataset", "name": name, "description": description},
                    ],
                },
            }
            paths = []
            for filename, document in docs.items():
                path = "metadata/" + role["id"] + "/" + filename
                paths.append(path)
                outputs[path] = _encode(document)
                if filename == "croissant.json":
                    report = federation_croissant.assess_croissant(
                        outputs[path], standards["gfjd-croissant-profile-v1.json"]
                    )
                else:
                    report = federation_rocrate.assess_rocrate(
                        outputs[path], standards["ro-crate-1.3-context.jsonld"]
                    )
                require(report["status"] == "profile_incomplete")
                assessments[path] = report
            record["profile_assessments"] = paths
            record["field_provenance"] = {
                field: {
                    "estate_manifest_sha256": estate_sha,
                    "estate_json_pointers": [f"/roles/{index}/{key}" for key in keys],
                    "derivation_rule": rule,
                    "input_sha256": input_hashes,
                    "generated_field_pointers": {
                        paths[0]: "/" + field,
                        paths[1]: "/@graph/1/" + field,
                    },
                }
                for field, keys, rule in (
                    ("name", ["repository"], "literal Draft: followed by exact repository"),
                    (
                        "description",
                        ["id", "payload_policy"],
                        "Prospective preparation only. Declared role: {id}; "
                        "declared payload policy: {payload_policy}.",
                    ),
                )
            }
        declarations.append(record)
    outputs["metadata-assessments.json"] = _encode(assessments)
    outputs["declaration-report.json"] = _encode(
        {
            "contract_version": "gfjd-config-metadata-declarations-v1",
            "state": "incomplete_configuration_draft",
            "estate_manifest_sha256": estate_sha,
            "input_sha256": input_hashes,
            "roles": declarations,
            "diagnostics": manifest["diagnostics"],
            "provenance_scope": "reconciled-configuration-only-not-source-edition-or-ownership",
            "scaffolding": {
                "standard_sha256": ASSETS,
                "meaning": "profile-targets-not-verified-conformance",
            },
            "coverage": "five-dataset-rocrate-croissant-profiles-explorer-space-declaration-only",
            **_boundary(),
        }
    )
    outputs["README.md"] = (
        b"# Actual-configuration federation drafts\n\n"
        b"Incomplete prospective metadata derived from supplied configuration, not fictional "
        b"empirical fixtures or verified published datasets. Desired links are unrequested. "
        b"No publication date, licence, creator, publisher, distribution, content digest, "
        b"release or runtime lineage is inferred. Explorer remains a Space declaration. "
        b"Profile scaffolding does not establish conformance. Configuration provenance is "
        b"not source/edition provenance or authenticated ownership. Only RO-Crate and the "
        b"restricted GFJD Croissant profile are assessed; no DCAT, PROV, OpenLineage or "
        b"partner acceptance is claimed. Source truth, rights, custody, Gold, maturity, "
        b"publication and gates remain unverified. All authority is false. Compiler and "
        b"component fingerprint reads are the only filesystem access.\n"
    )
    components = (federation_croissant, federation_rocrate, federation_metadata, medallion_estate)
    outputs["draft-manifest.json"] = _encode(
        {
            "contract_version": "gfjd-config-metadata-draft-v1",
            "state": "incomplete_configuration_draft",
            "input_sha256": input_hashes,
            "standard_sha256": ASSETS,
            "estate_manifest_sha256": estate_sha,
            "implementation_sha256": _sha(Path(__file__).read_bytes()),
            "component_implementation_sha256": {
                module.__name__: _sha(Path(cast(str, module.__file__)).read_bytes())
                for module in components
            },
            "artifact_sha256": {name: _sha(raw) for name, raw in sorted(outputs.items())},
            "dataset_document_count": len(assessments),
            "role_count": len(declarations),
            **_boundary(),
        }
    )
    return dict(sorted(outputs.items()))


def prepare_config_metadata_draft(
    estate_inputs: dict[str, bytes], standards: dict[str, bytes]
) -> dict[str, bytes]:
    """Regenerate estate, ten incomplete metadata documents and bound assessments."""
    try:
        return _prepare(estate_inputs, standards)
    except Exception:
        raise MetadataError("Configuration metadata draft contract violation") from None


def verify_config_metadata_draft(
    estate_inputs: dict[str, bytes], standards: dict[str, bytes], artifacts: dict[str, bytes]
) -> None:
    """Regenerate the exact set and bytes rather than trusting rewritten self-hashes."""
    try:
        expected = prepare_config_metadata_draft(estate_inputs, standards)
        require(type(artifacts) is dict and set(artifacts) == set(expected))
        require(
            all(type(raw) is bytes and raw == expected[name] for name, raw in artifacts.items())
        )
    except Exception:
        raise MetadataError("Configuration metadata draft contract violation") from None
