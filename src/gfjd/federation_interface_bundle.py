"""Compose replay and declaration checks without payload/partner acceptance.

All input locators remain unopened. Existing component helpers and this compiler
read implementation files for fingerprints. No source or partner code is copied.
"""

import hashlib
from pathlib import Path
from types import ModuleType
from typing import Any

from gfjd import (
    federation_bundle,
    federation_croissant,
    federation_dcat,
    federation_metadata,
    federation_openlineage,
    federation_parquet_references,
    federation_partner_interfaces,
    federation_prov,
    federation_rdf_input,
    federation_references,
    federation_replayed_bundle,
    federation_rocrate,
)
from gfjd.federation_metadata import MetadataError, parse_json, require
from gfjd.federation_prov import _canonical


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _encode(value: Any) -> bytes:
    return _canonical(value) + b"\n"


def _known_replay(raw: bytes, bank: dict[str, bytes]) -> set[str]:
    """Classify only after successful replay of explicitly supported formats."""
    envelope = parse_json(raw)
    refs = envelope["inputs"]
    known = set(bank)
    if envelope["mode"] == "projection":
        contract = parse_json(bank[refs["contract_sha256"]])
        require(contract["contract_version"] == "gfjd-json-projection-v1")
        receipt = parse_json(bank[refs["receipt_sha256"]])
        known.add(_sha(_canonical(receipt["rows"])))
    else:
        require(envelope["mode"] == "pipeline_history")
        for digest in refs["contracts"]:
            contract = parse_json(bank[digest])
            require(contract["pipeline_version"] == "gfjd-custody-xlsx-projection-v1")
            require(
                contract["extraction_contract"]["extraction_version"] == "gfjd-medallion-xlsx-v1"
            )
            require(
                contract["projection_contract"]["contract_version"] == "gfjd-json-projection-v1"
            )
        entries = parse_json(bank[refs["entries_sha256"]])
        for entry in entries:
            for layer in ("b1", "silver"):
                known.add(_sha(_canonical(entry["pipeline"][layer]["rows"])))
    return known


def _fingerprint(module: ModuleType) -> str:
    require(type(module.__file__) is str)
    return _sha(Path(str(module.__file__)).read_bytes())


def prepare_interface_bundle(
    scope_raw: bytes,
    expected_scope_sha256: str,
    metadata_bank: dict[str, bytes],
    estate_inputs: dict[str, bytes],
    standards: dict[str, bytes],
    replay_raw: bytes,
    expected_replay_sha256: str,
    replay_bank: dict[str, bytes],
    parquet_raw: bytes,
    expected_parquet_sha256: str,
    partner_raw: bytes,
    expected_partner_sha256: str,
    contract_bank: dict[str, bytes],
) -> dict[str, bytes]:
    """Recompute one scoped replay and both mandatory declaration sidecars."""
    try:
        outputs = federation_replayed_bundle.prepare_replayed_bundle(
            scope_raw,
            expected_scope_sha256,
            metadata_bank,
            estate_inputs,
            standards,
            replay_raw,
            expected_replay_sha256,
            replay_bank,
        )
        parquet = federation_parquet_references.assess_parquet_references(
            parquet_raw,
            expected_parquet_sha256,
            scope_raw,
            expected_scope_sha256,
            metadata_bank,
            estate_inputs,
        )
        partner = federation_partner_interfaces.assess_partner_interfaces(
            partner_raw,
            expected_partner_sha256,
            scope_raw,
            expected_scope_sha256,
            metadata_bank,
            estate_inputs,
            contract_bank,
        )
        # Each component has validated its own bank and size limits. Check shared
        # keys across the three digest-addressed banks without silently replacing.
        merged: dict[str, bytes] = {}
        for bank in (metadata_bank, replay_bank, contract_bank):
            for digest, payload in bank.items():
                require(digest not in merged or merged[digest] == payload)
                merged[digest] = payload
        known = set(metadata_bank) | set(contract_bank) | _known_replay(replay_raw, replay_bank)
        known.update(_sha(raw) for raw in (*estate_inputs.values(), *standards.values()))
        known.update(_sha(raw) for raw in (scope_raw, replay_raw, parquet_raw, partner_raw))
        # All generated component artifacts are JSON, RDF, HTML or text, never
        # Parquet. Include both the base artifacts and the composed report/README
        # bytes; declaration-dependent hashes are not a reason to omit known bytes.
        known.update(_sha(raw) for raw in outputs.values())
        outputs["interfaces/parquet-reference-report.json"] = _encode(parquet)
        outputs["interfaces/partner-interface-report.json"] = _encode(partner)
        outputs["README.md"] += (
            b"\nParquet and partner reports are declaration/reference checks only. "
            b"Known non-Parquet input contradictions are rejected; unknown payload formats "
            b"and digests remain unverified. No partner ownership or layer equivalence is "
            b"conferred. Component compiler fingerprint reads are performed.\n"
        )
        known.update(_sha(raw) for raw in outputs.values())
        require(
            all(
                obj["content_sha256"] is None or obj["content_sha256"] not in known
                for obj in parquet["objects"]
            )
        )
        manifest = parse_json(outputs.pop("bundle-manifest.json"))
        modules = (
            federation_bundle,
            federation_croissant,
            federation_dcat,
            federation_metadata,
            federation_openlineage,
            federation_parquet_references,
            federation_partner_interfaces,
            federation_prov,
            federation_rdf_input,
            federation_references,
            federation_replayed_bundle,
            federation_rocrate,
        )
        manifest.update(
            {
                "contract_version": "gfjd-federation-interface-bundle-v1",
                "parquet_declaration_sha256": expected_parquet_sha256,
                "partner_declaration_sha256": expected_partner_sha256,
                "partner_contract_sha256": sorted(contract_bank),
                "interface_implementation_sha256": _sha(Path(__file__).read_bytes()),
                "component_implementation_sha256": {
                    module.__name__: _fingerprint(module) for module in modules
                },
                "parquet_declaration_status": parquet["status"],
                "parquet_pending_object_ids": parquet["pending_object_ids"],
                "parquet_declaration_issues": parquet["issues"],
                "partner_reference_status": partner["status"],
                "partner_pending_ids": partner["pending_partner_ids"],
                "parquet_format_verified": False,
                "payload_digest_verified": False,
                "partner_interoperability": "unverified",
                "artifact_sha256": {name: _sha(raw) for name, raw in sorted(outputs.items())},
            }
        )
        require(not any(manifest["authority"].values()))
        outputs["bundle-manifest.json"] = _encode(manifest)
        return dict(sorted(outputs.items()))
    except Exception:
        raise MetadataError("Federation interface bundle contract violation") from None


def verify_interface_bundle(
    scope_raw: bytes,
    expected_scope_sha256: str,
    metadata_bank: dict[str, bytes],
    estate_inputs: dict[str, bytes],
    standards: dict[str, bytes],
    replay_raw: bytes,
    expected_replay_sha256: str,
    replay_bank: dict[str, bytes],
    parquet_raw: bytes,
    expected_parquet_sha256: str,
    partner_raw: bytes,
    expected_partner_sha256: str,
    contract_bank: dict[str, bytes],
    artifacts: dict[str, bytes],
) -> None:
    """Regenerate every output; no self-hash or supplied report substitutes for replay."""
    try:
        expected = prepare_interface_bundle(
            scope_raw,
            expected_scope_sha256,
            metadata_bank,
            estate_inputs,
            standards,
            replay_raw,
            expected_replay_sha256,
            replay_bank,
            parquet_raw,
            expected_parquet_sha256,
            partner_raw,
            expected_partner_sha256,
            contract_bank,
        )
        require(type(artifacts) is dict and set(artifacts) == set(expected))
        require(
            all(type(raw) is bytes and raw == expected[name] for name, raw in artifacts.items())
        )
    except Exception:
        raise MetadataError("Federation interface bundle contract violation") from None
