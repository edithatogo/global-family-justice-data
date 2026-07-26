"""Cross-cutting release blockers from defects, exceptions and gate decisions."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Any

from .conductor import Conductor
from .io import read_csv, read_json, sha256_bytes
from .project import Project, load_project


@dataclass(frozen=True, slots=True)
class AssuranceBlocker:
    code: str
    message: str
    severity: str
    record_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def release_blockers(
    project: Project | Path | str | None,
    *,
    release_status: str,
    required_gate: str | None,
    as_of: date,
) -> list[AssuranceBlocker]:
    """Return governance and assurance conditions that block a release.

    Draft 0.x releases are intentionally permissive. Release candidates and stable
    releases enforce defect, exception and current gate-decision controls. A historic
    approval is not sufficient: the latest decision must approve the gate and be tied
    to the current canonical conductor-state hash.
    """

    resolved = (
        project
        if isinstance(project, Project)
        else load_project(Path(project))
        if project is not None
        else load_project()
    )
    blockers: list[AssuranceBlocker] = []
    strict = release_status in {"release_candidate", "stable"}

    defects_path = resolved.resolve(resolved.paths.get("defects", "programme/defect_register.csv"))
    if defects_path.exists():
        _, defects = read_csv(defects_path)
        for row in defects:
            severity = str(row.get("severity") or "").upper()
            status = str(row.get("status") or "").lower()
            if status in {"closed", "resolved", "accepted"}:
                continue
            if severity in {"P0", "P1"} or (strict and severity == "P2"):
                blockers.append(
                    AssuranceBlocker(
                        "OPEN_RELEASE_DEFECT",
                        f"Open {severity} defect: {row.get('title', '')}",
                        severity or "unknown",
                        row.get("defect_id") or None,
                    )
                )

    exceptions_path = resolved.resolve(
        resolved.paths.get("exceptions", "programme/exception_register.csv")
    )
    if exceptions_path.exists():
        _, exceptions = read_csv(exceptions_path)
        for row in exceptions:
            status = str(row.get("status") or "").lower()
            if status not in {"approved", "active"}:
                continue
            expires = _parse_date(row.get("expires_on"))
            identifier = row.get("exception_id") or None
            if expires is None:
                blockers.append(
                    AssuranceBlocker(
                        "EXCEPTION_EXPIRY_MISSING",
                        "Active exception has no valid expiry date",
                        str(row.get("severity") or "unknown"),
                        identifier,
                    )
                )
            elif expires < as_of:
                blockers.append(
                    AssuranceBlocker(
                        "EXCEPTION_EXPIRED",
                        f"Active exception expired on {expires.isoformat()}",
                        str(row.get("severity") or "unknown"),
                        identifier,
                    )
                )

    if strict:
        licensing = resolved.config.get("licensing", {})
        if not isinstance(licensing, dict):
            licensing = {}
        require_key = (
            "stable_release_requires_approved_license"
            if release_status == "stable"
            else "release_candidate_requires_approved_license"
        )
        if bool(licensing.get(require_key, True)):
            decision = str(licensing.get("decision_status", "pending"))
            license_file = resolved.root / str(licensing.get("license_file", "LICENSE"))
            if decision != "approved":
                blockers.append(
                    AssuranceBlocker(
                        "LICENSE_DECISION_PENDING",
                        "Release licence has not been formally approved",
                        "P1",
                        None,
                    )
                )
            elif not license_file.is_file():
                blockers.append(
                    AssuranceBlocker(
                        "LICENSE_FILE_MISSING",
                        f"Approved licence file is missing: {license_file.name}",
                        "P1",
                        None,
                    )
                )

    if strict:
        publication = resolved.config.get("publication", {})
        if not isinstance(publication, dict):
            publication = {}
        require_key = (
            "stable_release_requires_approved_identity"
            if release_status == "stable"
            else "release_candidate_requires_approved_identity"
        )
        if bool(publication.get(require_key, True)):
            identity_status = str(publication.get("identity_status", "pending"))
            if identity_status != "approved":
                blockers.append(
                    AssuranceBlocker(
                        "PUBLICATION_IDENTITY_PENDING",
                        "Canonical project, repository and builder identities are not approved",
                        "P1",
                        None,
                    )
                )
            else:
                invalid_fields = [
                    field
                    for field in ("project_uri", "repository_uri", "builder_id")
                    if not _approved_publication_uri(publication.get(field))
                ]
                if invalid_fields:
                    blockers.append(
                        AssuranceBlocker(
                            "PUBLICATION_IDENTITY_INVALID",
                            "Approved publication identity has invalid field(s): "
                            + ", ".join(invalid_fields),
                            "P1",
                            None,
                        )
                    )

    if required_gate and strict:
        blockers.extend(_gate_decision_blockers(resolved, required_gate))

    return blockers


def _gate_decision_blockers(project: Project, required_gate: str) -> list[AssuranceBlocker]:
    decisions_path = project.resolve(
        project.paths.get("gate_decisions", "programme/gate-decisions.json")
    )
    decisions: list[dict[str, Any]] = []
    if decisions_path.exists():
        payload = read_json(decisions_path)
        raw_decisions = payload.get("decisions", []) if isinstance(payload, dict) else []
        if isinstance(raw_decisions, list):
            decisions = [
                item
                for item in raw_decisions
                if isinstance(item, dict) and item.get("gate_id") == required_gate
            ]

    if not decisions:
        return [
            AssuranceBlocker(
                "GATE_DECISION_MISSING",
                f"No recorded decision exists for {required_gate}",
                "P1",
                required_gate,
            )
        ]

    # Decisions are append-only in normal operation, but use the explicit timestamp
    # and identifier so verification remains deterministic after data migration.
    latest = max(
        decisions,
        key=lambda item: (str(item.get("decided_at", "")), str(item.get("decision_id", ""))),
    )
    decision = str(latest.get("decision") or "")
    decision_id = str(latest.get("decision_id") or required_gate)
    if decision != "approved":
        return [
            AssuranceBlocker(
                "GATE_DECISION_NOT_APPROVED",
                f"Latest recorded decision for {required_gate} is {decision or 'invalid'}",
                "P1",
                decision_id,
            )
        ]

    conductor = Conductor.load(project)
    current_hash = sha256_bytes(conductor.canonical_summary_json().encode("utf-8"))
    decision_hash = str(latest.get("status_sha256") or "").lower()
    if decision_hash != current_hash:
        return [
            AssuranceBlocker(
                "GATE_DECISION_STALE",
                f"Latest approval for {required_gate} does not match current programme state",
                "P1",
                decision_id,
            )
        ]
    return []


def _approved_publication_uri(value: Any) -> bool:
    text = str(value or "").strip().lower()
    if not (text.startswith("https://") or text.startswith("git+https://")):
        return False
    forbidden = (".example", ".invalid", "pending", "localhost", "127.0.0.1")
    return not any(fragment in text for fragment in forbidden)


def _parse_date(value: Any) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        return None
