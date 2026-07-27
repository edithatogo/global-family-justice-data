"""Deterministic, fail-closed governance assurance packs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from .conductor import Conductor
from .io import read_json, sha256_file, write_csv, write_json
from .project import Project

PACK_ARTIFACTS = (
    "criterion-matrix.csv",
    "defect-exception-summary.json",
    "governance-pack.json",
    "release-decision-template.json",
)


@dataclass(frozen=True)
class GovernancePack:
    output: Path
    gates: int
    sha256: str

    def to_dict(self) -> dict[str, Any]:
        return {"output": str(self.output), "gates": self.gates, "sha256": self.sha256}


def build_governance_pack(
    project: Project, output: Path, *, as_of: date | None = None
) -> GovernancePack:
    """Build a point-in-time pack without converting readiness into approval."""
    conductor = Conductor.load(project)
    output = output if output.is_absolute() else project.root / output
    output.mkdir(parents=True, exist_ok=True)
    effective_date = (as_of or date.today()).isoformat()

    criteria_rows: list[dict[str, Any]] = []
    gate_payloads: list[dict[str, Any]] = []
    for gate_id in conductor.gates:
        result = conductor.gate_result(gate_id)
        gate_payload = result.as_dict()
        gate_payload["approval_recorded"] = result.decision_status == "accepted"
        gate_payloads.append(gate_payload)
        for item in result.criteria:
            criteria_rows.append(
                {
                    "gate_id": gate_id,
                    "criterion_id": item.criterion.id,
                    "track_id": item.criterion.track_id,
                    "mandatory": item.criterion.mandatory,
                    "waivable": item.criterion.waivable,
                    "state": item.state,
                    "passed": item.passed,
                    "evidence_ids": ";".join(item.criterion.evidence_ids),
                }
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
            item.status != "accepted"
            or not item.public_path
            or item.expires_on is None
            or item.expires_on < (as_of or date.today())
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


def verify_governance_pack(output: Path) -> list[str]:
    """Verify pack integrity and its fail-closed approval semantics."""
    errors: list[str] = []
    manifest_path = output / "manifest.json"
    if not manifest_path.is_file():
        return ["missing manifest.json"]
    manifest = read_json(manifest_path)
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
        pack = read_json(pack_path)
        if pack.get("governance_state") != "pending_external_acceptance":
            errors.append("governance state must remain pending external acceptance")
        decision = pack.get("release_decision", {})
        if decision.get("decision") != "pending":
            errors.append("release decision template must remain pending")
        for signatory in decision.get("signatories", []):
            if signatory.get("name") or signatory.get("signed_on"):
                errors.append("release decision template contains an inferred signature")
    return errors
