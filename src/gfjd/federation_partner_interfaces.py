"""Pinned technical interface references, never runtime federation or data access."""

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from gfjd.federation_metadata import MetadataError, parse_json, require
from gfjd.federation_references import reconcile_references

VERSION = "gfjd-partner-interface-references-v1"
PINNED = {
    "archive-govt-nz": {
        "commit": "af427c2632239a8869684c849c0fcc1981277b02",
        "artifacts": {
            "src/archive_govt_nz/foi_ownership.py": (
                "9bdbecd2cd84f1faff7d69b5bdad729f8add68baa98b9345b066ccc1775d031a"
            ),
            "schemas/archive/v1/publication-receipt.schema.json": (
                "6097ba87f4eafa04bcea8f586144cb9129961d085709fe99350e600274137c9d"
            ),
        },
    },
    "global-medicines-atlas": {
        "commit": "f7550d5f84b6a831cd99c3b6882c0d33c4b0c939",
        "artifacts": {
            "contracts/medallion/v4/federation.schema.json": (
                "ac28485a70e0853266e4c140f9a07cd557eb27816b0b408b9bf2927a4cffacec"
            ),
            "src/global_medicines_atlas/federation.py": (
                "2a21eb2d09a8a9ba1e956c1b0d5c123529c185d79bb31ced2c2a0cb8bebaeb78"
            ),
        },
    },
}


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _encode(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def _digest(value: Any) -> None:
    require(type(value) is str and re.fullmatch(r"[a-f0-9]{64}", value) is not None)


def assess_partner_interfaces(
    declaration_raw: bytes,
    expected_declaration_sha256: str,
    scope_raw: bytes,
    expected_scope_sha256: str,
    metadata_bank: dict[str, bytes],
    estate_inputs: dict[str, bytes],
    contract_bank: dict[str, bytes],
) -> dict[str, Any]:
    """Bind reviewed technical references, without executing or resolving them.

    This module and existing estate helper read their implementation fingerprints.
    No partner checkout, metadata locator or source payload is opened.
    """
    try:
        require(type(declaration_raw) is bytes and 0 < len(declaration_raw) <= 1024 * 1024)
        _digest(expected_declaration_sha256)
        require(_sha(declaration_raw) == expected_declaration_sha256)
        document = parse_json(declaration_raw)
        require(
            type(document) is dict
            and set(document) == {"contract_version", "scope_sha256", "state", "partners"}
        )
        require(document["contract_version"] == VERSION and document["state"] == "preparation")
        require(document["scope_sha256"] == expected_scope_sha256)
        refs = reconcile_references(scope_raw, expected_scope_sha256, metadata_bank, estate_inputs)
        partners = document["partners"]
        require(type(partners) is list and len(partners) <= 4)
        require(type(contract_bank) is dict and len(contract_bank) <= 8)
        total = 0
        for digest, raw in contract_bank.items():
            _digest(digest)
            require(type(raw) is bytes and 0 < len(raw) <= 1024 * 1024)
            total += len(raw)
            require(total <= 8 * 1024 * 1024 and _sha(raw) == digest)
        seen: set[str] = set()
        used: set[str] = set()
        records = []
        for partner in partners:
            require(type(partner) is dict and set(partner) == {"partner_id", "commit", "artifacts"})
            identifier = partner["partner_id"]
            require(
                type(identifier) is str
                and identifier in refs["partners"]
                and identifier not in seen
            )
            seen.add(identifier)
            if partner["commit"] is None:
                require(type(partner["artifacts"]) is dict and not partner["artifacts"])
                records.append(
                    {**partner, "status": "reference_unavailable", "compatibility": "unverified"}
                )
                continue
            require(identifier in PINNED)
            pinned = PINNED[identifier]
            require(
                partner["commit"] == pinned["commit"]
                and partner["artifacts"] == pinned["artifacts"]
            )
            checked = []
            for path, digest in partner["artifacts"].items():
                require(digest in contract_bank)
                used.add(digest)
                if path.endswith(".schema.json"):
                    schema = parse_json(contract_bank[digest])
                    require(type(schema) is dict)
                    Draft202012Validator.check_schema(schema)
                    checked.append(path)
            qualification = (
                {
                    "ownership_transfer": "unsupported_for_gfjd",
                    "allowed_owners": ["edithatogo/archive-govt-nz", "edithatogo/fyi-archive"],
                    "publication_receipt": "requires_actual_publication_evidence",
                }
                if identifier == "archive-govt-nz"
                else {
                    "gma_bronze_strata": {"B0": "index", "B1": "metadata", "B2": "raw"},
                    "direct_gfjd_layer_aliasing": False,
                    "remaining_validation": [
                        "record_schema",
                        "record_semantics",
                        "authentic_receipts",
                        "remote_bytes",
                    ],
                }
            )
            records.append(
                {
                    **partner,
                    "status": "pinned_reference_bound",
                    "schema_syntax_checked": sorted(checked),
                    "qualification": qualification,
                    "compatibility": "unverified",
                }
            )
        require(seen == set(refs["partners"]) and used == set(contract_bank))
        pending = sorted(
            item["partner_id"] for item in records if item["status"] == "reference_unavailable"
        )
        return {
            "contract_version": "gfjd-partner-interface-report-v1",
            "status": "partial_reference_binding" if pending else "selected_references_bound",
            "declaration_sha256": expected_declaration_sha256,
            "scope_sha256": expected_scope_sha256,
            "reference_report_sha256": _sha(_encode(refs)),
            "contract_sha256": sorted(contract_bank),
            "contract_bytes": total,
            "implementation_sha256": _sha(Path(__file__).read_bytes()),
            "partners": sorted(records, key=lambda item: item["partner_id"]),
            "pending_partner_ids": pending,
            "bound_partner_count": len(records) - len(pending),
            "semantic_code_executed": False,
            "factual_evidence": "unverified",
            "hosted_revisions": "unverified",
            "live_interoperability": "unverified",
            "partner_registration": "unverified",
            "coverage": "pinned-technical-reference-and-schema-syntax-only",
            "filesystem_access": "compiler-and-estate-implementation-fingerprints-only",
            "authority": dict(refs["authority"]),
        }
    except Exception:
        raise MetadataError("Partner interface reference contract violation") from None


def verify_partner_interfaces(
    declaration_raw: bytes,
    expected_declaration_sha256: str,
    scope_raw: bytes,
    expected_scope_sha256: str,
    metadata_bank: dict[str, bytes],
    estate_inputs: dict[str, bytes],
    contract_bank: dict[str, bytes],
    report: dict[str, Any],
) -> None:
    """Recompute full bindings and reject rehashed or forged report assertions."""
    try:
        expected = assess_partner_interfaces(
            declaration_raw,
            expected_declaration_sha256,
            scope_raw,
            expected_scope_sha256,
            metadata_bank,
            estate_inputs,
            contract_bank,
        )
        require(type(report) is dict and report == expected)
        require(_encode(report) == _encode(expected))
    except Exception:
        raise MetadataError("Partner interface reference contract violation") from None
