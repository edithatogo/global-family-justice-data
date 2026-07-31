"""Deterministic, fail-closed governance assurance packs."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from .conductor import Conductor
from .io import atomic_write_text, read_json, sha256_file, write_csv, write_json
from .project import Project

PACK_ARTIFACTS = (
    "criterion-matrix.csv",
    "defect-exception-summary.json",
    "governance-pack.json",
    "release-decision-template.json",
)
GATE_ARTIFACTS = ("criterion-matrix.csv", "evidence-index.csv", "gate-pack.json")


@dataclass(frozen=True)
class GovernancePack:
    output: Path
    gates: int
    sha256: str

    def to_dict(self) -> dict[str, Any]:
        return {"output": str(self.output), "gates": self.gates, "sha256": self.sha256}


def build_governance_pack(
    project: Project,
    output: Path,
    *,
    as_of: date | None = None,
    gate_output: Path | None = None,
) -> GovernancePack:
    """Build a point-in-time pack without converting readiness into approval."""
    conductor = Conductor.load(project)
    output = output if output.is_absolute() else project.root / output
    gate_root = gate_output or output / "gate-packs"
    gate_root = gate_root if gate_root.is_absolute() else project.root / gate_root
    output.mkdir(parents=True, exist_ok=True)
    effective_date = (as_of or date.today()).isoformat()
    effective_day = as_of or date.today()

    criteria_rows: list[dict[str, Any]] = []
    gate_payloads: list[dict[str, Any]] = []
    for gate_id in conductor.gates:
        result = conductor.gate_result(gate_id)
        gate_payload = result.as_dict()
        gate_payload["approval_recorded"] = result.decision_status == "accepted"
        gate_payloads.append(gate_payload)
        gate_rows: list[dict[str, Any]] = []
        for item in result.criteria:
            row = {
                "gate_id": gate_id,
                "criterion_id": item.criterion.id,
                "track_id": item.criterion.track_id,
                "mandatory": item.criterion.mandatory,
                "waivable": item.criterion.waivable,
                "state": item.state,
                "passed": item.passed,
                "evidence_ids": ";".join(item.criterion.evidence_ids),
            }
            criteria_rows.append(row)
            gate_rows.append(row)
        _write_gate_pack(
            gate_root / gate_id,
            gate_payload,
            gate_rows,
            conductor,
            effective_date,
        )

    open_serious = [
        item.id
        for item in conductor.defects.values()
        if item.severity in {"P0", "P1"} and item.status not in {"resolved", "closed"}
    ]
    invalid_p2 = [
        item.id
        for item in conductor.exceptions.values()
        if item.severity == "P2"
        and (
            item.status != "approved"
            or not item.owner_role
            or not item.approved_by
            or item.approved_on is None
            or not item.public_path
            or item.expires_on is None
            or item.expires_on < effective_day
        )
    ]
    controls = {
        "as_of": effective_date,
        "open_p0_p1_defects": open_serious,
        "noncompliant_p2_exceptions": invalid_p2,
        "release_control_satisfied": not open_serious and not invalid_p2,
    }
    decision = {
        "release": "v1.0",
        "decision": "pending",
        "decision_date": None,
        "conditions": [],
        "signatories": [
            {"role": role, "name": None, "signed_on": None, "status": "pending"}
            for role in (
                "programme executive",
                "independent release assurance",
                "methods lead",
                "security and data-governance owner",
                "service and release manager",
            )
        ],
        "guardrail": "This template is not an approval and contains no inferred identity.",
    }
    write_csv(
        output / "criterion-matrix.csv",
        (
            "gate_id",
            "criterion_id",
            "track_id",
            "mandatory",
            "waivable",
            "state",
            "passed",
            "evidence_ids",
        ),
        criteria_rows,
    )
    write_json(output / "defect-exception-summary.json", controls)
    write_json(output / "release-decision-template.json", decision)
    payload = {
        "schema_version": "1.0",
        "as_of": effective_date,
        "programme_id": project.project_config.get("id", "GFJD"),
        "governance_state": "pending_external_acceptance",
        "gate_count": len(gate_payloads),
        "gates": gate_payloads,
        "release_control": controls,
        "release_decision": decision,
    }
    write_json(output / "governance-pack.json", payload)
    manifest = {name: sha256_file(output / name) for name in PACK_ARTIFACTS}
    write_json(output / "manifest.json", manifest)
    return GovernancePack(output, len(gate_payloads), sha256_file(output / "manifest.json"))


def _write_gate_pack(
    output: Path,
    gate_payload: dict[str, Any],
    criterion_rows: list[dict[str, Any]],
    conductor: Conductor,
    as_of: str,
) -> None:
    gate_id = str(gate_payload["gate_id"])
    evidence_ids = sorted(
        {
            evidence_id
            for criterion in conductor.gates[gate_id].criteria
            for evidence_id in criterion.evidence_ids
        }
    )
    evidence_rows = []
    for evidence_id in evidence_ids:
        item = conductor.evidence.get(evidence_id)
        evidence_rows.append(
            {
                "evidence_id": evidence_id,
                "status": item.status if item else "missing",
                "path": item.path if item and item.path else "",
                "sha256": item.sha256 if item and item.sha256 else "",
                "owner_role": item.owner_role if item else "",
                "reviewer_role": item.reviewer_role if item else "",
            }
        )
    write_csv(
        output / "criterion-matrix.csv",
        (
            "gate_id",
            "criterion_id",
            "track_id",
            "mandatory",
            "waivable",
            "state",
            "passed",
            "evidence_ids",
        ),
        criterion_rows,
    )
    write_csv(
        output / "evidence-index.csv",
        ("evidence_id", "status", "path", "sha256", "owner_role", "reviewer_role"),
        evidence_rows,
    )
    write_json(
        output / "gate-pack.json",
        {
            "schema_version": "1.0",
            "as_of": as_of,
            "governance_state": "pending_external_acceptance",
            **gate_payload,
        },
    )
    lines = [f"{sha256_file(output / name)}  {name}" for name in GATE_ARTIFACTS]
    atomic_write_text(output / "MANIFEST.sha256", "\n".join(lines) + "\n")


def verify_governance_pack(output: Path, *, gate_output: Path | None = None) -> list[str]:
    """Verify pack integrity and its fail-closed approval semantics."""
    errors: list[str] = []
    manifest_path = output / "manifest.json"
    if not manifest_path.is_file():
        return ["missing manifest.json"]
    try:
        manifest = read_json(manifest_path)
    except (OSError, json.JSONDecodeError) as exc:
        return [f"invalid manifest.json: {exc}"]
    if not isinstance(manifest, dict) or set(manifest) != set(PACK_ARTIFACTS):
        return ["manifest artifact set is invalid"]
    for name in PACK_ARTIFACTS:
        expected = manifest[name]
        path = output / name
        if not path.is_file():
            errors.append(f"missing artifact: {name}")
        elif sha256_file(path) != expected:
            errors.append(f"checksum mismatch: {name}")
    pack_path = output / "governance-pack.json"
    if pack_path.is_file():
        try:
            pack = read_json(pack_path)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"invalid governance-pack.json: {exc}")
            return errors
        if not isinstance(pack, dict):
            errors.append("governance-pack.json must contain an object")
            return errors
        if pack.get("governance_state") != "pending_external_acceptance":
            errors.append("governance state must remain pending external acceptance")
        decision = pack.get("release_decision", {})
        if not isinstance(decision, dict):
            errors.append("release decision must contain an object")
            return errors
        if decision.get("decision") != "pending":
            errors.append("release decision template must remain pending")
        signatories = decision.get("signatories", [])
        if not isinstance(signatories, list):
            errors.append("release decision signatories must contain a list")
            return errors
        for signatory in signatories:
            if not isinstance(signatory, dict):
                errors.append("release decision contains an invalid signatory")
                continue
            if signatory.get("name") or signatory.get("signed_on"):
                errors.append("release decision template contains an inferred signature")
        try:
            template = read_json(output / "release-decision-template.json")
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"invalid release-decision-template.json: {exc}")
        else:
            if template != decision:
                errors.append("release decision artifacts disagree")
    gate_root = gate_output or output / "gate-packs"
    for gate_id in ("G1", "G2", "G3", "G4", "G5", "G6"):
        errors.extend(_verify_gate_pack(gate_root / gate_id, gate_id))
    return errors


def _verify_gate_pack(output: Path, gate_id: str) -> list[str]:
    errors: list[str] = []
    manifest_path = output / "MANIFEST.sha256"
    if not manifest_path.is_file():
        return [f"{gate_id}: missing MANIFEST.sha256"]
    expected_lines = manifest_path.read_text(encoding="utf-8").splitlines()
    expected: dict[str, str] = {}
    for line in expected_lines:
        parts = line.split("  ", 1)
        if len(parts) != 2 or parts[1] not in GATE_ARTIFACTS:
            return [f"{gate_id}: invalid manifest entry"]
        expected[parts[1]] = parts[0]
    if set(expected) != set(GATE_ARTIFACTS):
        return [f"{gate_id}: manifest artifact set is invalid"]
    for name in GATE_ARTIFACTS:
        path = output / name
        if not path.is_file():
            errors.append(f"{gate_id}: missing artifact: {name}")
        elif sha256_file(path) != expected[name]:
            errors.append(f"{gate_id}: checksum mismatch: {name}")
    return errors
