"""Offline, layer-local mechanical checks with explicit factual/authority gaps.

All inputs are supplied bytes. No request, promotion or publication is performed.
Review claims and recorded custody do not authenticate facts or their signers.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from blake3 import blake3

from . import (
    medallion_b0_checks,
    medallion_history_checks,
    medallion_quality_checks,
    medallion_release_checks,
    medallion_replay,
    medallion_review_bindings,
    medallion_xlsx,
)
from . import (
    medallion_qualification_inputs as inputs,
)
from . import (
    medallion_qualification_payloads as payloads,
)

DIMENSIONS = (
    "completeness",
    "fixity",
    "rights",
    "lineage",
    "reproducibility",
    "quality",
    "quarantine",
    "restore",
)
VERSION = "gfjd-layer-qualification-v1"


class MissingEvidence(ValueError):
    """Required active-layer bytes are absent."""


class FixityFailure(ValueError):
    """Supplied original bytes contradict their declared content binding."""


def _require(value: bool) -> None:
    if not value:
        raise inputs.QualificationInputError("layer evidence binding failed")


def _get(refs: dict[str, str], bank: dict[str, bytes], role: str) -> bytes:
    if role not in refs or refs[role] not in bank:
        raise MissingEvidence("missing layer input")
    return bank[refs[role]]


def _bound(raw: bytes, evidence: dict[str, Any], name: str) -> None:
    _require(inputs.sha(raw) == evidence.get(name))


def _reviews(
    cell: dict[str, Any],
    refs: dict[str, str],
    bank: dict[str, bytes],
    content: bytes,
    as_of: str,
    evidence: dict[str, Any],
) -> None:
    details = cell["review_bindings"]
    for role in ("rights", "semantic", "disclosure", "owner", "restore"):
        if role not in refs:
            continue
        try:
            raw = _get(refs, bank, role)
            report = medallion_review_bindings.assess_review(
                raw,
                object_id=cell["object_id"],
                edition_id=cell["edition_id"],
                layer=cell["layer"],
                content_sha256=inputs.sha(content),
                as_of=as_of,
            )
            _require(report["review_kind"] == role)
            if role == "disclosure" and cell["layer"] == "gold":
                _bound(raw, evidence, "disclosure_assessment_sha256")
            reference_field = (
                "owner_decision_reference"
                if role == "owner" and cell["layer"] == "gold"
                else "release_gate_reference"
                if role == "owner" and cell["layer"] == "platinum"
                else "semantic_review_reference"
                if role == "semantic" and cell["layer"] == "silver"
                else None
            )
            if reference_field is not None:
                _require(report["decision_reference"] == evidence[reference_field])
            details[role] = report
            status = (
                "failed"
                if (
                    report["temporal_status"] != "current"
                    or report["declared_status"] == "rejected"
                    or report["conflicts_present"]
                )
                else "pending"
            )
        except MissingEvidence:
            status = "missing"
            details[role] = {"status": status, "code": "review_bytes_missing"}
        except (ValueError, TypeError, KeyError):
            status = "failed"
            details[role] = {"status": status, "code": "review_scope_kind_or_contract_invalid"}
        dimension = role if role in {"rights", "restore"} else None
        if dimension:
            cell["dimensions"][dimension] = status
        if status == "failed":
            cell["blockers"].append(f"{role}_review_failed")


def qualify_layers(
    scope_raw: bytes,
    scope_sha256: str,
    layer_contract_raw: bytes,
    record_bank: dict[str, bytes],
    payload_bank: dict[str, bytes],
    *,
    as_of: str,
) -> dict[str, Any]:
    """Recompute five layers and eight dimensions without accepting any layer.

    Verified dimension values are bounded mechanical results only. Explicit pending
    requirements, dependency blockers and all-false authority remain controlling.
    """
    medallion_replay._timestamp(as_of)
    binding = inputs.bind_layer_records(scope_raw, scope_sha256, layer_contract_raw, record_bank)
    resolved = payloads.resolve_payloads(
        scope_raw, scope_sha256, layer_contract_raw, record_bank, payload_bank
    )
    scope = inputs.parse_scope(scope_raw, scope_sha256)
    release_ids = {
        item["object_id"]
        for item in scope["objects"]
        if item["layers"]["platinum"]["state"] == "active"
    }
    rows_by_layer: dict[tuple[str, str], bytes] = {}
    cells = []
    indexed: dict[tuple[str, str], dict[str, Any]] = {}
    # Gold for all objects must be evaluated before cohort-wide Platinum.
    ordered = sorted(
        binding["coverage"], key=lambda c: (inputs.LAYERS.index(c["layer"]), c["object_id"])
    )
    for record_cell in ordered:
        identity, layer = record_cell["object_id"], record_cell["layer"]
        cell: dict[str, Any] = {
            "object_id": identity,
            "edition_id": record_cell["edition_id"],
            "layer": layer,
            "record_sha256": record_cell["record_sha256"],
            "lifecycle": record_cell["lifecycle"],
            "dimensions": dict.fromkeys(DIMENSIONS, "pending"),
            "blockers": list(record_cell["dependency_blockers"]),
            "mechanical_checks": {},
            "review_bindings": {},
            "pending_requirements": [
                "accountable_layer_acceptance",
                "rights_adjudication",
                "actual_layer_restore",
            ],
            "promotion_authorized": False,
        }
        dimensions = cell["dimensions"]
        state = record_cell["record_status"]
        position = inputs.LAYERS.index(layer)
        previous = inputs.LAYERS[position - 1] if position else None
        predecessor = indexed.get((identity, previous)) if previous else None
        if predecessor and predecessor["blockers"]:
            cell["blockers"].append("upstream_mechanical_or_review_blocker")
        if predecessor and predecessor["dimensions"]["quarantine"] == "blocked":
            state = "lifecycle_blocked"
        if state != "structurally_valid":
            dimensions["completeness"] = "failed" if state == "invalid" else "missing"
            dimensions["quarantine"] = "blocked" if state == "lifecycle_blocked" else "pending"
            cell["blockers"].append(f"record_{state}")
        else:
            dimensions["completeness"] = "verified"
            dimensions["quarantine"] = "verified"
            wrapper = inputs.parse(record_bank[record_cell["record_sha256"]])
            evidence, refs = wrapper["record"]["evidence"], record_cell["artifacts"]
            content: bytes | None = None
            try:
                if layer == "b0":
                    content = _get(refs, payload_bank, "source")
                    if not (
                        inputs.sha(content) == evidence["content_sha256"]
                        and blake3(content).hexdigest() == evidence["content_blake3"]
                        and type(evidence["size_bytes"]) is int
                        and len(content) == evidence["size_bytes"]
                    ):
                        raise FixityFailure("original content fixity mismatch")
                    dimensions["fixity"] = "verified"
                    for role in ("capture", "safety", "custody"):
                        if role not in refs or refs[role] not in payload_bank:
                            dimensions["completeness"] = "missing"
                            cell["blockers"].append(f"required_{role}_evidence_missing")
                    result = medallion_b0_checks.assess_b0(
                        content,
                        evidence,
                        object_id=identity,
                        safety_raw=payload_bank.get(refs.get("safety", "")),
                        custody_raw=payload_bank.get(refs.get("custody", "")),
                    )
                    dimensions["fixity"] = result["checks"]["fixity"]
                    dimensions["quality"] = result["checks"]["safety"]
                    if result["checks"]["safety"] == "failed":
                        dimensions["quarantine"] = "blocked"
                        cell["blockers"].append("source_safety_failed")
                    elif result["checks"]["safety"] != "verified":
                        dimensions["quarantine"] = "pending"
                        cell["blockers"].append(f"source_safety_{result['checks']['safety']}")
                    if "capture" in refs and refs["capture"] in payload_bank:
                        _bound(payload_bank[refs["capture"]], evidence, "capture_receipt_sha256")
                    cell["mechanical_checks"]["b0"] = result
                    cell["pending_requirements"].extend(
                        [
                            "capture_authenticity",
                            "current_remote_custody",
                            "comprehensive_privacy_and_public_safety",
                        ]
                    )
                elif layer in {"b1", "silver"}:
                    source = _get(refs, payload_bank, "source")
                    assert previous is not None
                    upstream = rows_by_layer.get((identity, previous))
                    if upstream is not None:
                        _require(source == upstream)
                        dimensions["lineage"] = "verified"
                    else:
                        cell["blockers"].append("predecessor_content_not_recomputed")
                    contract_raw = _get(refs, payload_bank, "contract")
                    receipt_raw = _get(refs, payload_bank, "receipt")
                    declared_rows = _get(refs, payload_bank, "rows")
                    contract = inputs.parse(contract_raw)
                    _bound(
                        contract_raw,
                        evidence,
                        "extraction_contract_sha256"
                        if layer == "b1"
                        else "mapping_contract_sha256",
                    )
                    result = (
                        medallion_xlsx.extract_xlsx(source, contract)
                        if layer == "b1"
                        else medallion_replay.replay_projection(source, contract)
                    )
                    _require(
                        inputs.canonical(result) == inputs.canonical(inputs.parse(receipt_raw))
                    )
                    content = inputs.canonical(result["rows"])
                    _require(content == declared_rows)
                    if layer == "b1":
                        _bound(receipt_raw, evidence, "transformation_receipt_sha256")
                    else:
                        _bound(
                            inputs.canonical(result["field_lineage"]),
                            evidence,
                            "field_lineage_sha256",
                        )
                        _require(
                            result["valid_from"] == evidence["valid_from"]
                            and result["recorded_at"] == evidence["recorded_at"]
                        )
                        if "history" in refs and "checkpoint" in refs:
                            history = medallion_history_checks.assess_history(
                                _get(refs, payload_bank, "history"),
                                _get(refs, payload_bank, "checkpoint"),
                                object_id=identity,
                                edition_id=cell["edition_id"],
                                expected_projection=result,
                            )
                            cell["mechanical_checks"]["history"] = history
                        else:
                            cell["pending_requirements"].append("full_history_and_checkpoint")
                        cell["pending_requirements"].append("checkpoint_authenticity")
                    dimensions["fixity"] = dimensions["reproducibility"] = "verified"
                    cell["mechanical_checks"]["transformation_sha256"] = inputs.sha(
                        inputs.canonical(result)
                    )
                elif layer == "gold":
                    content = _get(refs, payload_bank, "rows")
                    upstream = rows_by_layer.get((identity, "silver"))
                    if upstream is not None:
                        _require(content == upstream)
                        dimensions["lineage"] = "verified"
                    else:
                        cell["blockers"].append("predecessor_content_not_recomputed")
                    policy = inputs.parse(_get(refs, payload_bank, "policy"))
                    quality_raw = _get(refs, payload_bank, "quality")
                    _bound(quality_raw, evidence, "quality_report_sha256")
                    result = medallion_quality_checks.assess_quality(content, policy)
                    _require(
                        inputs.canonical(result) == inputs.canonical(inputs.parse(quality_raw))
                    )
                    dimensions["fixity"] = dimensions["reproducibility"] = "verified"
                    dimensions["quality"] = (
                        "verified" if all(result["technical_checks"].values()) else "failed"
                    )
                    if dimensions["quality"] == "failed" or result["counts"]["small_cell_rows"]:
                        dimensions["quarantine"] = "blocked"
                        cell["blockers"].append("gold_quality_or_small_cell_review_required")
                    cell["mechanical_checks"]["quality"] = result
                    cell["pending_requirements"].extend(
                        [
                            "semantic_adjudication",
                            "disclosure_adjudication",
                            "gold_owner_acceptance",
                        ]
                    )
                else:
                    manifest = _get(refs, payload_bank, "manifest")
                    federation = _get(refs, payload_bank, "federation")
                    expected_raw = _get(refs, payload_bank, "scope")
                    _bound(manifest, evidence, "release_manifest_sha256")
                    _bound(federation, evidence, "federation_manifest_sha256")
                    expected = inputs.parse(expected_raw)
                    _require(set(expected["object_ids"]) == release_ids)
                    gold_bank = {}
                    for member in release_ids:
                        gold = rows_by_layer.get((member, "gold"))
                        if gold is None:
                            raise MissingEvidence("Gold content not recomputed")
                        if indexed[(member, "gold")]["blockers"]:
                            raise ValueError("Gold mechanical blocker")
                        gold_bank[inputs.sha(gold)] = gold
                    result = medallion_release_checks.assess_release(
                        manifest, federation, gold_bank, expected_raw
                    )
                    # Prevent swapping objects whose content bytes differ.
                    for member in result["members"]:
                        _require(
                            member["sha256"]
                            == inputs.sha(rows_by_layer[(member["object_id"], "gold")])
                        )
                    content = manifest
                    dimensions["fixity"] = dimensions["lineage"] = dimensions["reproducibility"] = (
                        "verified"
                    )
                    cell["mechanical_checks"]["composition"] = result
                    cell["pending_requirements"].extend(
                        [
                            "accepted_gold_cohort",
                            "public_snapshot",
                            "release_authority",
                            "federation_standard_conformance",
                        ]
                    )
                if content is not None:
                    rows_by_layer[(identity, layer)] = content
                    _reviews(cell, refs, payload_bank, content, as_of, evidence)
            except MissingEvidence:
                dimensions["completeness"] = "missing"
                cell["blockers"].append("required_layer_input_missing")
            except FixityFailure:
                dimensions["fixity"] = "failed"
                dimensions["quarantine"] = "blocked"
                cell["blockers"].append("original_content_fixity_failed")
            except (ValueError, TypeError, KeyError, AttributeError, OSError):
                dimensions["reproducibility"] = "failed"
                cell["blockers"].append("layer_contract_or_evidence_binding_failed")
        cell["blockers"] = sorted(set(cell["blockers"]))
        cell["pending_requirements"] = sorted(set(cell["pending_requirements"]))
        cells.append(cell)
        indexed[(identity, layer)] = cell
    report = {
        "contract_version": VERSION,
        "as_of": as_of,
        "scope_sha256": scope_sha256,
        "binding_sha256": binding["report_sha256"],
        "payload_resolution_sha256": resolved["report_sha256"],
        "implementation_sha256": inputs.sha(Path(__file__).read_bytes()),
        "coverage": sorted(cells, key=lambda c: (c["object_id"], inputs.LAYERS.index(c["layer"]))),
        "scope": "bounded mechanical evidence only; factual qualification remains pending",
        "authority": dict.fromkeys(
            ["source_access", "network", "promotion", "publication", "release", "gate_acceptance"],
            False,
        ),
    }
    report["report_sha256"] = inputs.sha(inputs.canonical(report))
    return report


def verify_qualification(
    scope_raw: bytes,
    scope_sha256: str,
    layer_contract_raw: bytes,
    record_bank: dict[str, bytes],
    payload_bank: dict[str, bytes],
    report: dict[str, Any],
    *,
    as_of: str,
) -> None:
    expected = qualify_layers(
        scope_raw, scope_sha256, layer_contract_raw, record_bank, payload_bank, as_of=as_of
    )
    _require(inputs.canonical(report) == inputs.canonical(expected))
