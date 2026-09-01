"""Recompute native candidate evidence and bind it to declared candidate bytes.

The returned summaries contain only guarded identifiers, hashes, closed statuses
and counts. Native source/review prose is deliberately not propagated.
"""

from pathlib import Path
from typing import Any

from . import medallion_lifecycle, medallion_qualification, medallion_restore
from .medallion_qualification_inputs import canonical, parse, sha

QUALIFICATION_ROLES = {
    ("b0", "data"): {"source"},
    ("b1", "data"): {"rows"},
    ("silver", "data"): {"rows"},
    ("gold", "data"): {"rows"},
    ("b1", "transformation"): {"contract"},
    ("silver", "transformation"): {"contract"},
    ("platinum", "manifest"): {"manifest"},
}
METADATA_ROLES = {
    "wrapper",
    "capture",
    "safety",
    "custody",
    "rights",
    "restore",
    "receipt",
    "history",
    "checkpoint",
    "semantic",
    "quality",
    "policy",
    "disclosure",
    "owner",
    "scope",
    "federation",
}


class NativeEvidenceError(ValueError):
    """Native evidence is invalid or associated with the wrong candidate."""


def _require(value: bool) -> None:
    if not value:
        raise NativeEvidenceError("Native evidence association failed")


def _all_bytes(value: Any) -> list[bytes]:
    if type(value) is bytes:
        return [value]
    if type(value) is dict:
        return [raw for item in value.values() for raw in _all_bytes(item)]
    if type(value) is list:
        return [raw for item in value for raw in _all_bytes(item)]
    return []


def _closed_summary(report: dict[str, Any], cells: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "status": "recomputed",
        "report_sha256": sha(canonical(report)),
        "cells": cells,
        "cell_count": len(cells),
    }


def _qualification(
    bundle: dict[str, Any],
    prepared: dict[str, Any],
    provenance: dict[str, dict[str, Any]],
    disclosure: dict[str, str],
) -> tuple[dict[str, Any], dict[str, Any]]:
    report = medallion_qualification.qualify_layers(
        bundle["scope_raw"],
        bundle["scope_sha256"],
        bundle["layer_contract_raw"],
        bundle["record_bank"],
        bundle["payload_bank"],
        as_of=bundle["as_of"],
    )
    _require(bundle["as_of"] == prepared["plan"]["as_of"])
    objects = prepared["scope"]["objects"]
    by_identity: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for obj in objects:
        by_identity.setdefault(
            (obj["logical_object_id"], obj["edition_id"], obj["layer"]), []
        ).append(obj)
    # Every supplied wrapper has a candidate metadata representation.
    wrapper_candidates: set[str] = set()
    wrappers = {}
    for digest, raw in bundle["record_bank"].items():
        wrapper = parse(raw)
        wrappers[(wrapper["object_id"], wrapper["edition_id"], wrapper["record"]["layer"])] = (
            digest,
            wrapper,
        )
        candidates = [
            obj for obj in objects if obj["role"] == "metadata" and obj["sha256"] == digest
        ]
        _require(len(candidates) == 1)
        wrapper_candidates.add(candidates[0]["object_id"])
    cells = []
    for cell in report["coverage"]:
        key = (cell["object_id"], cell["edition_id"], cell["layer"])
        wrapper_entry = wrappers.get(key)
        mapped = []
        if wrapper_entry is not None:
            wrapper_digest, wrapper = wrapper_entry
            refs = {"wrapper": wrapper_digest, **wrapper["artifacts"]}
            for obj in by_identity.get(key, []):
                eligible = (
                    METADATA_ROLES
                    if obj["role"] == "metadata"
                    else QUALIFICATION_ROLES.get((obj["layer"], obj["role"]), set())
                )
                roles = sorted(role for role in eligible if refs.get(role) == obj["sha256"])
                _require(len(roles) <= 1)
                if roles:
                    provenance[obj["object_id"]] = {
                        "status": (
                            "checked_no_findings"
                            if cell["dimensions"].get("lineage") == "verified"
                            or (
                                obj["layer"] == "b0"
                                and cell["dimensions"].get("fixity") == "verified"
                            )
                            or obj["role"] == "metadata"
                            else "failed"
                            if cell["dimensions"].get("lineage") == "failed"
                            else "missing_evidence"
                        ),
                        "roles": roles,
                        "references": [obj["sha256"], cell["record_sha256"]],
                    }
                    mapped.append(obj["object_id"])
                if obj["layer"] == "gold" and obj["role"] == "data" and roles == ["rows"]:
                    quality = cell["dimensions"].get("quality")
                    quarantine = cell["dimensions"].get("quarantine")
                    disclosure[obj["object_id"]] = (
                        "checked_no_findings"
                        if quality == quarantine == "verified"
                        else "failed"
                        if "failed" in {quality, quarantine} or quarantine == "blocked"
                        else "missing_evidence"
                    )
        cells.append(
            {
                "object_id_sha256": sha(cell["object_id"].encode()),
                "edition_id_sha256": sha(cell["edition_id"].encode()),
                "layer": cell["layer"],
                "record_sha256": cell["record_sha256"],
                "lifecycle_state": cell["lifecycle"]["state"],
                "dimensions": cell["dimensions"],
                "mapped_candidate_ids": sorted(mapped),
            }
        )
    return report, _closed_summary(report, cells)


def _restore(
    bundle: dict[str, Any], prepared: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    _require(
        all(
            set(bank) == set(prepared["candidate_bank"])
            for bank in bundle["replica_banks"].values()
        )
    )
    report = medallion_restore.assess_restore_rehearsal(
        bundle["plan_raw"],
        bundle["expected_plan_sha256"],
        bundle["scope_raw"],
        bundle["expected_scope_sha256"],
        bundle["layer_contract_raw"],
        bundle["replica_banks"],
    )
    _require(report["release_id"] == prepared["plan"]["candidate_id"])
    _require(report["as_of"] == prepared["plan"]["as_of"])
    cells = [
        {
            "object_id_sha256": sha(cell["object_id"].encode()),
            "edition_id_sha256": sha(cell["edition_id"].encode()),
            "layer": cell["layer"],
            "record_sha256": cell["record_sha256"],
            "dimensions": cell["dimensions"],
        }
        for cell in report["qualification"]["coverage"]
    ]
    summary = _closed_summary(report, cells)
    summary.update(
        {
            "offline_rebuild_verified": report["offline_rebuild_verified"],
            "replica_inventory_count": {
                key: value["inventory"]["object_count"] for key, value in report["replicas"].items()
            },
        }
    )
    return report, summary


def _lifecycle(bundle: dict[str, Any], prepared: dict[str, Any]) -> dict[str, Any]:
    report = medallion_lifecycle.assess_lifecycle_journal(
        bundle["plan_raw"],
        bundle["expected_plan_sha256"],
        bundle["scope_raw"],
        bundle["layer_contract_raw"],
        bundle["checkpoint_raw"],
        bundle["event_bank"],
        bundle["receipt_bank"],
    )
    _require(report["as_of"] == prepared["plan"]["as_of"])
    candidates: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for obj in prepared["scope"]["objects"]:
        candidates.setdefault(
            (obj["logical_object_id"], obj["edition_id"], obj["layer"]), []
        ).append(obj)
    active = {row["artifact_id"] for row in report["heads"] if row["state"] == "active"}
    gaps, cells = [], []
    for item in report["inventory"]:
        siblings = candidates.get((item["object_id"], item["edition_id"], item["layer"]), [])
        matching = [
            candidate for candidate in siblings if candidate["sha256"] == item["content_sha256"]
        ]
        _require(len(matching) <= 1)
        candidate = matching[0] if matching else None
        if item["artifact_id"] in active:
            _require(candidate is not None)
            assert candidate is not None
            _require(candidate["lifecycle"] == "active")
        elif candidate is None and not siblings:
            gaps.append(sha(item["artifact_id"].encode()))
        elif candidate is None:
            _require(False)
        else:
            _require(candidate["lifecycle"] == item["state"])
        cells.append(
            {
                "artifact_id_sha256": sha(item["artifact_id"].encode()),
                "object_id_sha256": sha(item["object_id"].encode()),
                "layer": item["layer"],
                "content_sha256": item["content_sha256"],
                "state": item["state"],
                "candidate_id": candidate["object_id"] if candidate else None,
            }
        )
    summary = _closed_summary(report, cells)
    summary.update(
        {
            "historical_digest_only_gaps": sorted(gaps),
            "declared_provider_backlog_count": len(report["declared_provider_backlog"]),
        }
    )
    return summary


def assess_native_evidence(prepared: dict[str, Any]) -> dict[str, Any]:
    """Recompute supplied native bundles and reject candidate association drift."""
    try:
        objects = prepared["scope"]["objects"]
        provenance = {
            obj["object_id"]: {"status": "missing_evidence", "roles": [], "references": []}
            for obj in objects
        }
        disclosure = {obj["object_id"]: "unsupported" for obj in objects}
        summaries: dict[str, Any] = {
            name: {"status": "missing_evidence"}
            for name in ("qualification", "restore", "lifecycle")
        }
        bank_values = set(prepared["candidate_bank"].values())
        for name, bundle in prepared["evidence_bundles"].items():
            if name != "dependencies":
                _require(all(raw in bank_values for raw in _all_bytes(bundle)))
        qualification_report = None
        if "qualification" in prepared["evidence_bundles"]:
            qualification_report, summaries["qualification"] = _qualification(
                prepared["evidence_bundles"]["qualification"], prepared, provenance, disclosure
            )
        if "restore" in prepared["evidence_bundles"]:
            restore_report, summaries["restore"] = _restore(
                prepared["evidence_bundles"]["restore"], prepared
            )
            if qualification_report is not None:
                _require(
                    restore_report["qualification_sha256"] == sha(canonical(qualification_report))
                )
        if "lifecycle" in prepared["evidence_bundles"]:
            summaries["lifecycle"] = _lifecycle(prepared["evidence_bundles"]["lifecycle"], prepared)
        return {
            "provenance": provenance,
            "disclosure": disclosure,
            "summaries": summaries,
            "implementation_sha256": sha(Path(__file__).read_bytes()),
        }
    except Exception:
        raise NativeEvidenceError("Native evidence association failed") from None
