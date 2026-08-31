"""Resolve active-layer supplied bytes only; fixity is not substantive evidence.

No payload is requested or opened. Inactive and malformed-record references
cannot make a payload eligible for processing. Missing inputs remain explicit.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from . import medallion_qualification_inputs as inputs

ROLES = {
    "b0": {"source", "capture", "safety", "custody", "rights", "restore"},
    "b1": {"source", "contract", "receipt", "rows", "rights", "restore"},
    "silver": {
        "source",
        "contract",
        "receipt",
        "rows",
        "history",
        "checkpoint",
        "semantic",
        "rights",
        "restore",
    },
    "gold": {"rows", "policy", "quality", "semantic", "disclosure", "owner", "rights", "restore"},
    "platinum": {"manifest", "federation", "scope", "snapshot", "owner", "rights", "restore"},
}
MAX_BYTES = 8 * 1024 * 1024
MAX_ARTIFACTS = 500


def resolve_payloads(
    scope_raw: bytes,
    scope_sha256: str,
    layer_contract_raw: bytes,
    record_bank: dict[str, bytes],
    payload_bank: dict[str, bytes],
) -> dict[str, Any]:
    """Recompute scope binding before considering any payload.

    The bank may contain only explicitly referenced active, structurally valid
    layer inputs. Missing referenced bytes are reported, not hidden from coverage.
    Byte equality across roles does not establish semantic interchangeability.
    """
    try:
        binding = inputs.bind_layer_records(
            scope_raw, scope_sha256, layer_contract_raw, record_bank
        )
        eligible: set[str] = set()
        for cell in binding["coverage"]:
            if cell["record_status"] != "structurally_valid":
                continue
            if not set(cell["artifacts"]) <= ROLES[cell["layer"]]:
                raise ValueError
            eligible.update(cell["artifacts"].values())
        if (
            not isinstance(payload_bank, dict)
            or len(payload_bank) > MAX_ARTIFACTS
            or not set(payload_bank) <= eligible
        ):
            raise ValueError
        # Eligibility and aggregate resource limits precede all payload hashing.
        total = 0
        for raw in payload_bank.values():
            if not isinstance(raw, bytes):
                raise ValueError
            total += len(raw)
            if total > MAX_BYTES:
                raise ValueError
        for digest, raw in payload_bank.items():
            if inputs.sha(raw) != digest:
                raise ValueError
        cells = []
        for cell in binding["coverage"]:
            process = cell["record_status"] == "structurally_valid"
            refs = cell["artifacts"] if process else {}
            cells.append(
                {
                    "object_id": cell["object_id"],
                    "edition_id": cell["edition_id"],
                    "layer": cell["layer"],
                    "record_status": cell["record_status"],
                    "payload_processing_eligible": process,
                    "references": {
                        role: {
                            "sha256": digest,
                            "status": "fixity_verified" if digest in payload_bank else "missing",
                            "size_bytes": len(payload_bank[digest])
                            if digest in payload_bank
                            else None,
                        }
                        for role, digest in sorted(refs.items())
                    },
                    "evidence_meaning_verified": False,
                    "promotion_authorized": False,
                }
            )
        report = {
            "contract_version": "gfjd-qualification-payloads-v1",
            "binding_sha256": binding["report_sha256"],
            "implementation_sha256": inputs.sha(Path(__file__).read_bytes()),
            "payload_bank_sha256": inputs.sha(inputs.canonical(sorted(payload_bank))),
            "artifact_count": len(payload_bank),
            "artifact_bytes": total,
            "coverage": cells,
            "promotion_authorized": False,
        }
        report["report_sha256"] = inputs.sha(inputs.canonical(report))
        return report
    except (ValueError, TypeError, KeyError, AttributeError, OSError):
        raise inputs.QualificationInputError("qualification payload contract failed") from None


def verify_payloads(
    scope_raw: bytes,
    scope_sha256: str,
    layer_contract_raw: bytes,
    record_bank: dict[str, bytes],
    payload_bank: dict[str, bytes],
    report: dict[str, Any],
) -> None:
    expected = resolve_payloads(
        scope_raw, scope_sha256, layer_contract_raw, record_bank, payload_bank
    )
    if inputs.canonical(report) != inputs.canonical(expected):
        raise inputs.QualificationInputError("qualification payload report mismatch")
