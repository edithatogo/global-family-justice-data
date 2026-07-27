"""Evidence-driven programme conductor for tracks, work, maturity and gates."""

from __future__ import annotations

import json
import os
from collections.abc import Iterable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from .io import read_csv, sha256_file, write_csv, write_json
from .project import Project, load_project, load_toml
from .reporting import Report, Severity

EVIDENCE_STATUSES = {
    "missing",
    "draft",
    "in_review",
    "accepted",
    "rejected",
    "expired",
    "waived",
}
WORK_STATUSES = {
    "not_started",
    "planned",
    "in_progress",
    "blocked",
    "in_review",
    "done",
    "accepted",
    "review",
    "waived",
    "deferred",
}
PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}


@dataclass(frozen=True)
class Track:
    id: str
    name: str
    purpose: str
    accountable_role: str
    dependency_ids: tuple[str, ...]
    mandatory: bool
    v1_outcome: str


@dataclass(frozen=True)
class Criterion:
    id: str
    track_id: str
    description: str
    evidence_ids: tuple[str, ...]
    mandatory: bool
    waivable: bool


@dataclass(frozen=True)
class Gate:
    id: str
    name: str
    target_release: str
    dependency_ids: tuple[str, ...]
    objective: str
    criteria: tuple[Criterion, ...]


@dataclass(frozen=True)
class Evidence:
    id: str
    title: str
    track_id: str
    gate_ids: tuple[str, ...]
    status: str
    path: str | None
    owner_role: str
    reviewer_role: str
    reviewed_on: date | None
    expires_on: date | None
    sha256: str | None
    notes: str


@dataclass(frozen=True)
class WorkItem:
    id: str
    track_id: str
    gate_id: str
    title: str
    status: str
    priority: str
    owner_role: str
    deputy_role: str
    dependency_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    definition_of_done: str
    notes: str


@dataclass(frozen=True)
class MaturityAssessment:
    dimension_id: str
    name: str
    target_level: int
    assessed_level: int
    evidence_ids: tuple[str, ...]
    assessor_role: str
    assessed_on: date | None
    status: str
    notes: str


@dataclass(frozen=True)
class GateDecision:
    gate_id: str
    status: str
    decided_on: date | None
    decision_authority: str
    decision_reference: str
    conditions: str
    expires_on: date | None
    notes: str


@dataclass(frozen=True)
class Risk:
    id: str
    title: str
    likelihood: str
    inherent_severity: str
    residual_severity: str
    status: str
    owner_tracks: tuple[str, ...]
    controls: str
    trigger: str
    review_gate: str
    reviewed_on: date | None
    next_review_on: date | None
    notes: str


@dataclass(frozen=True)
class Defect:
    id: str
    severity: str
    title: str
    affected_release: str
    owner_role: str
    opened_on: date | None
    target_resolution: date | None
    status: str
    public_note: str


@dataclass(frozen=True)
class ExceptionRecord:
    id: str
    criterion_id: str
    severity: str
    rationale: str
    owner_role: str
    approved_by: str
    approved_on: date | None
    expires_on: date | None
    public_path: str
    status: str


@dataclass
class CriterionResult:
    criterion: Criterion
    passed: bool
    state: str
    missing_evidence: list[str] = field(default_factory=list)
    nonaccepted_evidence: list[str] = field(default_factory=list)


@dataclass
class GateResult:
    gate: Gate
    passed: bool
    ready: bool
    state: str
    criteria: list[CriterionResult]
    dependency_failures: list[str]
    work_failures: list[str] = field(default_factory=list)
    risk_failures: list[str] = field(default_factory=list)
    defect_failures: list[str] = field(default_factory=list)
    maturity_failure: str | None = None
    decision_status: str = "not_evaluated"

    @property
    def passed_count(self) -> int:
        return sum(result.passed for result in self.criteria)

    @property
    def total_count(self) -> int:
        return len(self.criteria)

    @property
    def completed_requirements(self) -> int:
        completed = self.passed_count
        completed += 1 if not self.dependency_failures else 0
        completed += 1 if not self.work_failures else 0
        completed += 1 if not self.risk_failures else 0
        completed += 1 if not self.defect_failures else 0
        completed += 1 if self.maturity_failure is None else 0
        return completed

    @property
    def total_requirements(self) -> int:
        return self.total_count + 5

    @property
    def completion_percent(self) -> float:
        return round(self.completed_requirements / self.total_requirements * 100, 1)

    @property
    def gate_id(self) -> str:
        return self.gate.id

    @property
    def name(self) -> str:
        return self.gate.name

    @property
    def blockers(self) -> list[str]:
        values: list[str] = []
        values.extend(f"dependency gate not accepted: {item}" for item in self.dependency_failures)
        values.extend(f"required work not accepted: {item}" for item in self.work_failures)
        values.extend(f"blocking risk: {item}" for item in self.risk_failures)
        values.extend(f"blocking defect: {item}" for item in self.defect_failures)
        if self.maturity_failure:
            values.append(self.maturity_failure)
        for result in self.criteria:
            if not result.passed:
                values.append(f"criterion {result.criterion.id}: {result.state}")
        if self.ready and not self.passed:
            values.append(f"gate decision is {self.decision_status}")
        return values

    def as_dict(self) -> dict[str, Any]:
        return {
            "gate_id": self.gate.id,
            "name": self.gate.name,
            "target_release": self.gate.target_release,
            "ready": self.ready,
            "passed": self.passed,
            "state": self.state,
            "decision_status": self.decision_status,
            "completed_requirements": self.completed_requirements,
            "total_requirements": self.total_requirements,
            "completion_percent": self.completion_percent,
            "dependency_failures": self.dependency_failures,
            "work_failures": self.work_failures,
            "risk_failures": self.risk_failures,
            "defect_failures": self.defect_failures,
            "maturity_failure": self.maturity_failure,
            "blockers": self.blockers,
            "criteria": [
                {
                    "criterion_id": item.criterion.id,
                    "track_id": item.criterion.track_id,
                    "description": item.criterion.description,
                    "state": item.state,
                    "passed": item.passed,
                    "missing_evidence": item.missing_evidence,
                    "nonaccepted_evidence": item.nonaccepted_evidence,
                }
                for item in self.criteria
            ],
        }


class Conductor:
    """Loads programme state and calculates evidence-linked readiness."""

    def __init__(self, project: Project):
        self.project = project
        self.tracks = self._load_tracks()
        self.gates = self._load_gates()
        self.evidence = self._load_evidence()
        self.work_items = self._load_work_items()
        self.maturity = self._load_maturity()
        self.gate_decisions = self._load_gate_decisions()
        self.risks = self._load_risks()
        self.defects = self._load_defects()
        self.exceptions = self._load_exceptions()
        self._gate_cache: dict[str, GateResult] = {}

    @classmethod
    def load(cls, project: Project | Path | str | None = None) -> Conductor:
        if isinstance(project, Project):
            resolved = project
        else:
            resolved = load_project(Path(project) if project is not None else None)
        return cls(resolved)

    def _load_tracks(self) -> dict[str, Track]:
        config = load_toml(self.project.resolve(self.project.paths["tracks"]))
        tracks: dict[str, Track] = {}
        for raw in config.get("tracks", []):
            track = Track(
                id=str(raw["id"]),
                name=str(raw["name"]),
                purpose=str(raw["purpose"]),
                accountable_role=str(raw["accountable_role"]),
                dependency_ids=tuple(str(value) for value in raw.get("dependency_ids", [])),
                mandatory=bool(raw.get("mandatory", True)),
                v1_outcome=str(raw.get("v1_outcome", "")),
            )
            # Retain the first definition; duplicate detection happens in validate().
            tracks.setdefault(track.id, track)
        return tracks

    def _load_gates(self) -> dict[str, Gate]:
        config = load_toml(self.project.resolve(self.project.paths["gates"]))
        gates: dict[str, Gate] = {}
        for raw in config.get("gates", []):
            criteria = tuple(
                Criterion(
                    id=str(item["id"]),
                    track_id=str(item["track_id"]),
                    description=str(item["description"]),
                    evidence_ids=tuple(str(value) for value in item.get("evidence_ids", [])),
                    mandatory=bool(item.get("mandatory", True)),
                    waivable=bool(item.get("waivable", False)),
                )
                for item in raw.get("criteria", [])
            )
            gate = Gate(
                id=str(raw["id"]),
                name=str(raw["name"]),
                target_release=str(raw["target_release"]),
                dependency_ids=tuple(str(value) for value in raw.get("dependency_ids", [])),
                objective=str(raw.get("objective", "")),
                criteria=criteria,
            )
            gates.setdefault(gate.id, gate)
        return gates

    def _load_evidence(self) -> dict[str, Evidence]:
        path = self.project.resolve(self.project.paths["evidence"])
        if not path.exists():
            return {}
        _, rows = read_csv(path)
        evidence: dict[str, Evidence] = {}
        for row in rows:
            item = Evidence(
                id=row.get("evidence_id", "").strip(),
                title=row.get("title", "").strip(),
                track_id=row.get("track_id", "").strip(),
                gate_ids=split_refs(row.get("gate_ids", "")),
                status=row.get("status", "").strip(),
                path=row.get("path", "").strip() or None,
                owner_role=row.get("owner_role", "").strip(),
                reviewer_role=row.get("reviewer_role", "").strip(),
                reviewed_on=parse_optional_date(row.get("reviewed_on", "")),
                expires_on=parse_optional_date(row.get("expires_on", "")),
                sha256=row.get("sha256", "").strip() or None,
                notes=row.get("notes", "").strip(),
            )
            evidence.setdefault(item.id, item)
        return evidence

    def _load_work_items(self) -> dict[str, WorkItem]:
        path = self.project.resolve(self.project.paths["work_items"])
        if not path.exists():
            return {}
        _, rows = read_csv(path)
        items: dict[str, WorkItem] = {}
        for row in rows:
            item = WorkItem(
                id=row.get("work_item_id", "").strip(),
                track_id=row.get("track_id", "").strip(),
                gate_id=row.get("gate_id", "").strip(),
                title=row.get("title", "").strip(),
                status=row.get("status", "").strip(),
                priority=row.get("priority", "").strip(),
                owner_role=row.get("owner_role", "").strip(),
                deputy_role=row.get("deputy_role", "").strip(),
                dependency_ids=split_refs(row.get("depends_on", "")),
                evidence_ids=split_refs(row.get("evidence_ids", "")),
                definition_of_done=row.get("definition_of_done", "").strip(),
                notes=row.get("notes", "").strip(),
            )
            items.setdefault(item.id, item)
        return items

    def _load_maturity(self) -> dict[str, MaturityAssessment]:
        path = self.project.resolve(self.project.paths["maturity"])
        if not path.exists():
            return {}
        _, rows = read_csv(path)
        assessments: dict[str, MaturityAssessment] = {}
        for row in rows:
            try:
                target = int(row.get("target_level", "0"))
                assessed = int(row.get("assessed_level", "0"))
            except ValueError:
                target, assessed = -1, -1
            item = MaturityAssessment(
                dimension_id=row.get("dimension_id", "").strip(),
                name=row.get("name", "").strip(),
                target_level=target,
                assessed_level=assessed,
                evidence_ids=split_refs(row.get("evidence_ids", "")),
                assessor_role=row.get("assessor_role", "").strip(),
                assessed_on=parse_optional_date(row.get("assessed_on", "")),
                status=row.get("status", "").strip(),
                notes=row.get("notes", "").strip(),
            )
            assessments.setdefault(item.dimension_id, item)
        return assessments

    def _load_gate_decisions(self) -> dict[str, GateDecision]:
        path_value = self.project.paths.get("gate_decisions")
        if not path_value:
            return {}
        path = self.project.resolve(path_value)
        if not path.exists():
            return {}
        _, rows = read_csv(path)
        decisions: dict[str, GateDecision] = {}
        for row in rows:
            item = GateDecision(
                gate_id=row.get("gate_id", "").strip(),
                status=row.get("status", "").strip(),
                decided_on=parse_optional_date(row.get("decided_on", "")),
                decision_authority=row.get("decision_authority", "").strip(),
                decision_reference=row.get("decision_reference", "").strip(),
                conditions=row.get("conditions", "").strip(),
                expires_on=parse_optional_date(row.get("expires_on", "")),
                notes=row.get("notes", "").strip(),
            )
            decisions.setdefault(item.gate_id, item)
        return decisions

    def _load_risks(self) -> dict[str, Risk]:
        path_value = self.project.paths.get("risks")
        if not path_value:
            return {}
        path = self.project.resolve(path_value)
        if not path.exists():
            return {}
        _, rows = read_csv(path)
        risks: dict[str, Risk] = {}
        for row in rows:
            item = Risk(
                id=row.get("risk_id", "").strip(),
                title=row.get("title", "").strip(),
                likelihood=row.get("likelihood", "").strip(),
                inherent_severity=row.get("inherent_severity", "").strip(),
                residual_severity=row.get("residual_severity", "").strip(),
                status=row.get("status", "").strip(),
                owner_tracks=split_refs(row.get("owner_tracks", "")),
                controls=row.get("controls", "").strip(),
                trigger=row.get("trigger", "").strip(),
                review_gate=row.get("review_gate", "").strip(),
                reviewed_on=parse_optional_date(row.get("reviewed_on", "")),
                next_review_on=parse_optional_date(row.get("next_review_on", "")),
                notes=row.get("notes", "").strip(),
            )
            risks.setdefault(item.id, item)
        return risks

    def _load_defects(self) -> dict[str, Defect]:
        path_value = self.project.paths.get("defects")
        if not path_value:
            return {}
        path = self.project.resolve(path_value)
        if not path.exists():
            return {}
        _, rows = read_csv(path)
        defects: dict[str, Defect] = {}
        for row in rows:
            item = Defect(
                id=row.get("defect_id", "").strip(),
                severity=row.get("severity", "").strip(),
                title=row.get("title", "").strip(),
                affected_release=row.get("affected_release", "").strip(),
                owner_role=row.get("owner_role", "").strip(),
                opened_on=parse_optional_date(row.get("opened_on", "")),
                target_resolution=parse_optional_date(row.get("target_resolution", "")),
                status=row.get("status", "").strip(),
                public_note=row.get("public_note", "").strip(),
            )
            if item.id:
                defects.setdefault(item.id, item)
        return defects

    def _load_exceptions(self) -> dict[str, ExceptionRecord]:
        path_value = self.project.paths.get("exceptions")
        if not path_value:
            return {}
        path = self.project.resolve(path_value)
        if not path.exists():
            return {}
        _, rows = read_csv(path)
        records: dict[str, ExceptionRecord] = {}
        for row in rows:
            item = ExceptionRecord(
                id=row.get("exception_id", "").strip(),
                criterion_id=row.get("criterion_id", "").strip(),
                severity=row.get("severity", "").strip(),
                rationale=row.get("rationale", "").strip(),
                owner_role=row.get("owner_role", "").strip(),
                approved_by=row.get("approved_by", "").strip(),
                approved_on=parse_optional_date(row.get("approved_on", "")),
                expires_on=parse_optional_date(row.get("expires_on", "")),
                public_path=row.get("public_path", "").strip(),
                status=row.get("status", "").strip(),
            )
            if item.id:
                records.setdefault(item.id, item)
        return records

    def validate(self, *, as_of: date | None = None) -> Report:
        as_of = as_of or date.today()
        report = Report("Programme conductor validation")
        self._validate_uniqueness(report)
        self._validate_tracks(report)
        self._validate_gates(report)
        self._validate_evidence(report, as_of=as_of)
        self._validate_work_items(report)
        self._validate_maturity(report)
        self._validate_operational_controls(report, as_of=as_of)
        report.metrics.update(
            {
                "tracks": len(self.tracks),
                "gates": len(self.gates),
                "criteria": sum(len(gate.criteria) for gate in self.gates.values()),
                "evidence_records": len(self.evidence),
                "work_items": len(self.work_items),
                "maturity_dimensions": len(self.maturity),
                "gate_decisions": len(self.gate_decisions),
                "risks": len(self.risks),
                "defects": len(self.defects),
                "exceptions": len(self.exceptions),
            }
        )
        return report

    def _validate_uniqueness(self, report: Report) -> None:
        # Dictionary loading retains first duplicates, so inspect source files directly.
        checks = [
            (self.project.resolve(self.project.paths["evidence"]), "evidence_id"),
            (self.project.resolve(self.project.paths["work_items"]), "work_item_id"),
            (self.project.resolve(self.project.paths["maturity"]), "dimension_id"),
            (self.project.resolve(self.project.paths["gate_decisions"]), "gate_id"),
            (self.project.resolve(self.project.paths["risks"]), "risk_id"),
            (self.project.resolve(self.project.paths["defects"]), "defect_id"),
            (self.project.resolve(self.project.paths["exceptions"]), "exception_id"),
        ]
        for path, key_field in checks:
            if not path.exists():
                report.error("PROGRAMME_FILE_MISSING", f"Missing programme file {path}", path=path)
                continue
            _, rows = read_csv(path)
            seen: set[str] = set()
            for row_number, row in enumerate(rows, start=2):
                value = row.get(key_field, "").strip()
                if not value:
                    report.error(
                        "PROGRAMME_ID_BLANK",
                        f"Blank {key_field}",
                        path=path,
                        row=row_number,
                    )
                elif value in seen:
                    report.error(
                        "PROGRAMME_ID_DUPLICATE",
                        f"Duplicate {field} {value!r}",
                        path=path,
                        row=row_number,
                    )
                seen.add(value)

    def _validate_tracks(self, report: Report) -> None:
        if len(self.tracks) != 10:
            report.warning(
                "TRACK_COUNT_UNEXPECTED",
                f"Expected ten programme tracks; found {len(self.tracks)}",
                path=self.project.paths["tracks"],
            )
        for track in self.tracks.values():
            for dependency in track.dependency_ids:
                if dependency not in self.tracks:
                    report.error(
                        "TRACK_DEPENDENCY_UNKNOWN",
                        f"Track {track.id} depends on unknown track {dependency}",
                        path=self.project.paths["tracks"],
                    )
        cycle = find_cycle({key: value.dependency_ids for key, value in self.tracks.items()})
        if cycle:
            report.error(
                "TRACK_DEPENDENCY_CYCLE",
                f"Track dependency cycle: {' -> '.join(cycle)}",
                path=self.project.paths["tracks"],
            )

    def _validate_gates(self, report: Report) -> None:
        criterion_ids: set[str] = set()
        for gate in self.gates.values():
            if not gate.criteria:
                report.error(
                    "GATE_EMPTY",
                    f"Gate {gate.id} has no criteria",
                    path=self.project.paths["gates"],
                )
            for dependency in gate.dependency_ids:
                if dependency not in self.gates:
                    report.error(
                        "GATE_DEPENDENCY_UNKNOWN",
                        f"Gate {gate.id} depends on unknown gate {dependency}",
                        path=self.project.paths["gates"],
                    )
            for criterion in gate.criteria:
                if criterion.id in criterion_ids:
                    report.error(
                        "CRITERION_ID_DUPLICATE",
                        f"Duplicate criterion id {criterion.id}",
                        path=self.project.paths["gates"],
                    )
                criterion_ids.add(criterion.id)
                if criterion.track_id not in self.tracks:
                    report.error(
                        "CRITERION_TRACK_UNKNOWN",
                        f"Criterion {criterion.id} references unknown track {criterion.track_id}",
                        path=self.project.paths["gates"],
                    )
                if not criterion.evidence_ids:
                    report.error(
                        "CRITERION_EVIDENCE_EMPTY",
                        f"Criterion {criterion.id} has no evidence requirement",
                        path=self.project.paths["gates"],
                    )
                for evidence_id in criterion.evidence_ids:
                    if evidence_id not in self.evidence:
                        report.error(
                            "CRITERION_EVIDENCE_UNKNOWN",
                            f"Criterion {criterion.id} references unknown evidence {evidence_id}",
                            path=self.project.paths["gates"],
                        )
        cycle = find_cycle({key: value.dependency_ids for key, value in self.gates.items()})
        if cycle:
            report.error(
                "GATE_DEPENDENCY_CYCLE",
                f"Gate dependency cycle: {' -> '.join(cycle)}",
                path=self.project.paths["gates"],
            )

    def _validate_evidence(self, report: Report, *, as_of: date) -> None:
        validation_cfg = self.project.config.get("validation", {})
        require_hash = bool(validation_cfg.get("accepted_evidence_requires_hash", True))
        require_reviewer = bool(validation_cfg.get("accepted_evidence_requires_reviewer", True))
        for evidence in self.evidence.values():
            path_label = self.project.paths["evidence"]
            if evidence.status not in EVIDENCE_STATUSES:
                report.error(
                    "EVIDENCE_STATUS_INVALID",
                    f"Evidence {evidence.id} has invalid status {evidence.status!r}",
                    path=path_label,
                )
            if evidence.track_id not in self.tracks:
                report.error(
                    "EVIDENCE_TRACK_UNKNOWN",
                    f"Evidence {evidence.id} references unknown track {evidence.track_id}",
                    path=path_label,
                )
            for gate_id in evidence.gate_ids:
                if gate_id not in self.gates:
                    report.error(
                        "EVIDENCE_GATE_UNKNOWN",
                        f"Evidence {evidence.id} references unknown gate {gate_id}",
                        path=path_label,
                    )
            resolved_path: Path | None = None
            if evidence.path:
                try:
                    resolved_path = self._safe_project_path(evidence.path)
                except ValueError as exc:
                    report.error("EVIDENCE_PATH_UNSAFE", str(exc), path=path_label)
                else:
                    if not resolved_path.exists():
                        severity = (
                            Severity.ERROR if evidence.status == "accepted" else Severity.WARNING
                        )
                        report.add(
                            severity,
                            "EVIDENCE_PATH_MISSING",
                            f"Evidence {evidence.id} path does not exist: {evidence.path}",
                            path=path_label,
                        )
                    elif evidence.sha256:
                        actual = sha256_file(resolved_path)
                        if actual != evidence.sha256:
                            report.error(
                                "EVIDENCE_HASH_MISMATCH",
                                f"Evidence {evidence.id} hash does not match {evidence.path}",
                                path=path_label,
                                context={"expected": evidence.sha256, "actual": actual},
                            )
            if evidence.status == "accepted":
                if not evidence.path:
                    report.error(
                        "EVIDENCE_ACCEPTED_WITHOUT_PATH",
                        f"Accepted evidence {evidence.id} has no path",
                        path=path_label,
                    )
                if require_hash and not evidence.sha256:
                    report.error(
                        "EVIDENCE_ACCEPTED_WITHOUT_HASH",
                        f"Accepted evidence {evidence.id} has no SHA-256",
                        path=path_label,
                    )
                if require_reviewer and not evidence.reviewer_role:
                    report.error(
                        "EVIDENCE_ACCEPTED_WITHOUT_REVIEWER",
                        f"Accepted evidence {evidence.id} has no reviewer role",
                        path=path_label,
                    )
                distinct_required = bool(
                    self.project.config.get("conductor", {}).get(
                        "require_distinct_evidence_reviewer", True
                    )
                )
                if (
                    distinct_required
                    and evidence.reviewer_role
                    and evidence.owner_role
                    and evidence.reviewer_role.casefold() == evidence.owner_role.casefold()
                ):
                    report.error(
                        "EVIDENCE_REVIEWER_NOT_INDEPENDENT",
                        f"Accepted evidence {evidence.id} has the same owner and reviewer role",
                        path=path_label,
                    )
                if evidence.reviewed_on is None:
                    report.error(
                        "EVIDENCE_ACCEPTED_WITHOUT_DATE",
                        f"Accepted evidence {evidence.id} has no reviewed_on date",
                        path=path_label,
                    )
            if (
                evidence.expires_on
                and evidence.expires_on < as_of
                and evidence.status == "accepted"
            ):
                report.error(
                    "EVIDENCE_EXPIRED",
                    f"Accepted evidence {evidence.id} expired on {evidence.expires_on.isoformat()}",
                    path=path_label,
                )

    def _validate_work_items(self, report: Report) -> None:
        path_label = self.project.paths["work_items"]
        for item in self.work_items.values():
            if item.status not in WORK_STATUSES:
                report.error(
                    "WORK_STATUS_INVALID",
                    f"Work item {item.id} has invalid status {item.status!r}",
                    path=path_label,
                )
            if item.priority not in PRIORITY_ORDER:
                report.error(
                    "WORK_PRIORITY_INVALID",
                    f"Work item {item.id} has invalid priority {item.priority!r}",
                    path=path_label,
                )
            if item.track_id not in self.tracks:
                report.error(
                    "WORK_TRACK_UNKNOWN",
                    f"Work item {item.id} references unknown track {item.track_id}",
                    path=path_label,
                )
            if item.gate_id not in self.gates:
                report.error(
                    "WORK_GATE_UNKNOWN",
                    f"Work item {item.id} references unknown gate {item.gate_id}",
                    path=path_label,
                )
            if not item.owner_role or not item.deputy_role:
                report.warning(
                    "WORK_OWNER_OR_DEPUTY_BLANK",
                    f"Work item {item.id} must have owner and deputy roles",
                    path=path_label,
                )
            for dependency in item.dependency_ids:
                if dependency not in self.work_items:
                    report.error(
                        "WORK_DEPENDENCY_UNKNOWN",
                        f"Work item {item.id} depends on unknown item {dependency}",
                        path=path_label,
                    )
            for evidence_id in item.evidence_ids:
                if evidence_id not in self.evidence:
                    report.error(
                        "WORK_EVIDENCE_UNKNOWN",
                        f"Work item {item.id} references unknown evidence {evidence_id}",
                        path=path_label,
                    )
            if item.status == "done" and item.evidence_ids:
                missing = [
                    evidence_id
                    for evidence_id in item.evidence_ids
                    if self.evidence.get(evidence_id) is None
                    or self.evidence[evidence_id].status == "missing"
                ]
                if missing:
                    report.warning(
                        "WORK_DONE_WITH_MISSING_EVIDENCE",
                        f"Work item {item.id} is done but evidence is missing: "
                        f"{', '.join(missing)}",
                        path=path_label,
                    )
            if item.status == "accepted":
                unsatisfied = [
                    evidence_id
                    for evidence_id in item.evidence_ids
                    if self.evidence.get(evidence_id) is None
                    or self.evidence[evidence_id].status not in {"accepted", "waived"}
                ]
                if unsatisfied:
                    report.error(
                        "WORK_ACCEPTED_WITHOUT_EVIDENCE",
                        f"Work item {item.id} is accepted without accepted evidence: "
                        f"{', '.join(unsatisfied)}",
                        path=path_label,
                    )
        cycle = find_cycle({key: value.dependency_ids for key, value in self.work_items.items()})
        if cycle:
            report.error(
                "WORK_DEPENDENCY_CYCLE",
                f"Work-item dependency cycle: {' -> '.join(cycle)}",
                path=path_label,
            )

    def _validate_maturity(self, report: Report) -> None:
        path_label = self.project.paths["maturity"]
        for assessment in self.maturity.values():
            if not 0 <= assessment.assessed_level <= 5:
                report.error(
                    "MATURITY_LEVEL_INVALID",
                    f"{assessment.dimension_id} assessed_level must be 0-5",
                    path=path_label,
                )
            if not 0 <= assessment.target_level <= 5:
                report.error(
                    "MATURITY_TARGET_INVALID",
                    f"{assessment.dimension_id} target_level must be 0-5",
                    path=path_label,
                )
            for evidence_id in assessment.evidence_ids:
                if evidence_id not in self.evidence:
                    report.error(
                        "MATURITY_EVIDENCE_UNKNOWN",
                        f"{assessment.dimension_id} references unknown evidence {evidence_id}",
                        path=path_label,
                    )

    def _validate_operational_controls(self, report: Report, *, as_of: date) -> None:
        decision_path = self.project.paths.get("gate_decisions", "programme/gate_decisions.csv")
        decision_statuses = {"not_evaluated", "accepted", "rejected", "conditional", "superseded"}
        for gate_id in self.gates:
            if gate_id not in self.gate_decisions:
                report.error(
                    "GATE_DECISION_MISSING",
                    f"Gate {gate_id} has no decision-control record",
                    path=decision_path,
                )
        for decision in self.gate_decisions.values():
            if decision.gate_id not in self.gates:
                report.error(
                    "GATE_DECISION_GATE_UNKNOWN",
                    f"Decision references unknown gate {decision.gate_id}",
                    path=decision_path,
                )
            if decision.status not in decision_statuses:
                report.error(
                    "GATE_DECISION_STATUS_INVALID",
                    f"Gate {decision.gate_id} has invalid decision status {decision.status!r}",
                    path=decision_path,
                )
            if decision.status in {"accepted", "rejected", "conditional"} and (
                decision.decided_on is None
                or not decision.decision_authority
                or not decision.decision_reference
            ):
                report.error(
                    "GATE_DECISION_INCOMPLETE",
                    f"Gate {decision.gate_id} decision lacks date, authority or reference",
                    path=decision_path,
                )
            if (
                decision.expires_on
                and decision.expires_on < as_of
                and decision.status in {"accepted", "conditional"}
            ):
                report.error(
                    "GATE_DECISION_EXPIRED",
                    f"Gate {decision.gate_id} decision expired on "
                    f"{decision.expires_on.isoformat()}",
                    path=decision_path,
                )

        risk_path = self.project.paths.get("risks", "programme/risk_register.csv")
        for risk in self.risks.values():
            if risk.residual_severity not in {"critical", "high", "medium", "low"}:
                report.error(
                    "RISK_SEVERITY_INVALID",
                    f"Risk {risk.id} has invalid residual severity {risk.residual_severity!r}",
                    path=risk_path,
                )
            if risk.status not in {"open", "mitigating", "accepted", "closed"}:
                report.error(
                    "RISK_STATUS_INVALID",
                    f"Risk {risk.id} has invalid status {risk.status!r}",
                    path=risk_path,
                )
            for track_id in risk.owner_tracks:
                if track_id not in self.tracks:
                    report.error(
                        "RISK_TRACK_UNKNOWN",
                        f"Risk {risk.id} references unknown track {track_id}",
                        path=risk_path,
                    )
            if risk.review_gate and risk.review_gate not in self.gates:
                report.error(
                    "RISK_GATE_UNKNOWN",
                    f"Risk {risk.id} references unknown review gate {risk.review_gate}",
                    path=risk_path,
                )
            if risk.next_review_on and risk.next_review_on < as_of and risk.status != "closed":
                report.warning(
                    "RISK_REVIEW_OVERDUE",
                    f"Risk {risk.id} review was due {risk.next_review_on.isoformat()}",
                    path=risk_path,
                )

        defect_path = self.project.paths.get("defects", "programme/defect_register.csv")
        for defect in self.defects.values():
            if defect.severity not in {"P0", "P1", "P2", "P3"}:
                report.error(
                    "DEFECT_SEVERITY_INVALID",
                    f"Defect {defect.id} has invalid severity {defect.severity!r}",
                    path=defect_path,
                )
            if defect.status not in {
                "open",
                "triaged",
                "in_progress",
                "resolved",
                "closed",
                "accepted",
            }:
                report.error(
                    "DEFECT_STATUS_INVALID",
                    f"Defect {defect.id} has invalid status {defect.status!r}",
                    path=defect_path,
                )

        criterion_ids = {
            criterion.id for gate in self.gates.values() for criterion in gate.criteria
        }
        exception_path = self.project.paths.get("exceptions", "programme/exception_register.csv")
        for record in self.exceptions.values():
            if record.criterion_id not in criterion_ids:
                report.error(
                    "EXCEPTION_CRITERION_UNKNOWN",
                    f"Exception {record.id} references unknown criterion {record.criterion_id}",
                    path=exception_path,
                )
            if record.status == "approved" and (
                not record.approved_by or record.approved_on is None or not record.public_path
            ):
                report.error(
                    "EXCEPTION_APPROVAL_INCOMPLETE",
                    f"Approved exception {record.id} lacks approval evidence",
                    path=exception_path,
                )
            if record.expires_on and record.expires_on < as_of and record.status == "approved":
                report.error(
                    "EXCEPTION_EXPIRED",
                    f"Approved exception {record.id} expired on {record.expires_on.isoformat()}",
                    path=exception_path,
                )

    def gate_result(self, gate_id: str, _stack: tuple[str, ...] = ()) -> GateResult:
        if gate_id in self._gate_cache:
            return self._gate_cache[gate_id]
        if gate_id not in self.gates:
            raise KeyError(f"Unknown gate {gate_id}")
        if gate_id in _stack:
            raise RuntimeError(f"Gate cycle while evaluating {' -> '.join((*_stack, gate_id))}")

        gate = self.gates[gate_id]
        criteria_results = [self._criterion_result(item) for item in gate.criteria]
        dependency_failures = [
            dependency
            for dependency in gate.dependency_ids
            if not self.gate_result(dependency, (*_stack, gate_id)).passed
        ]

        conductor_cfg = self.project.config.get("conductor", {})
        accepted_work = set(conductor_cfg.get("accepted_work_statuses", ["accepted", "waived"]))
        required_work = [
            item
            for item in self.work_items.values()
            if item.gate_id == gate_id and not item.id.endswith("-CLOSE")
        ]
        work_failures = [item.id for item in required_work if item.status not in accepted_work]

        gate_number = int(gate_id[1:]) if gate_id[1:].isdigit() else 0
        risk_key = (
            "blocking_risk_severities_at_rc"
            if gate_number >= 5
            else "blocking_risk_severities_before_rc"
        )
        blocking_risk_severities = set(conductor_cfg.get(risk_key, ["critical"]))
        resolved_risk_statuses = {"accepted", "closed"} if gate_number < 5 else {"closed"}
        risk_failures = [
            risk.id
            for risk in self.risks.values()
            if risk.residual_severity in blocking_risk_severities
            and risk.status not in resolved_risk_statuses
        ]
        blocking_defect_severities = set(
            conductor_cfg.get("blocking_defect_severities", ["P0", "P1"])
        )
        defect_failures = [
            defect.id
            for defect in self.defects.values()
            if defect.severity in blocking_defect_severities
            and defect.status not in {"resolved", "closed"}
        ]

        minimum_levels = conductor_cfg.get("minimum_maturity_by_gate", {})
        minimum_maturity = int(minimum_levels.get(gate_id, 0))
        assured_floor = int(self.maturity_status().get("assured_floor", 0))
        maturity_failure = None
        if assured_floor < minimum_maturity:
            maturity_failure = (
                f"evidence-assured maturity floor L{assured_floor} is below "
                f"required L{minimum_maturity}"
            )

        mandatory_results = [result for result in criteria_results if result.criterion.mandatory]
        ready = (
            not dependency_failures
            and not work_failures
            and not risk_failures
            and not defect_failures
            and maturity_failure is None
            and all(result.passed for result in mandatory_results)
        )
        decision = self.gate_decisions.get(gate_id)
        decision_status = decision.status if decision else "missing"
        decision_valid = bool(
            decision
            and decision.status == conductor_cfg.get("accepted_gate_decision_status", "accepted")
            and (decision.expires_on is None or decision.expires_on >= date.today())
        )
        require_decision = bool(conductor_cfg.get("require_recorded_gate_decision", True))
        passed = ready and (decision_valid or not require_decision)

        if passed:
            state = "passed"
        elif ready:
            state = "ready_for_decision"
        elif dependency_failures:
            state = "blocked_by_dependency"
        elif risk_failures or defect_failures:
            state = "blocked_by_assurance"
        elif maturity_failure:
            state = "blocked_by_maturity"
        elif work_failures:
            state = "work_incomplete"
        elif any(result.state == "rejected" for result in mandatory_results):
            state = "rejected"
        elif any(result.state == "in_review" for result in mandatory_results):
            state = "in_review"
        elif any(result.state == "draft" for result in mandatory_results):
            state = "draft"
        else:
            state = "not_ready"

        result = GateResult(
            gate=gate,
            passed=passed,
            ready=ready,
            state=state,
            criteria=criteria_results,
            dependency_failures=dependency_failures,
            work_failures=work_failures,
            risk_failures=risk_failures,
            defect_failures=defect_failures,
            maturity_failure=maturity_failure,
            decision_status=decision_status,
        )
        self._gate_cache[gate_id] = result
        return result

    def _criterion_result(self, criterion: Criterion) -> CriterionResult:
        satisfactory = set(
            self.project.config.get("conductor", {}).get(
                "satisfactory_evidence_statuses", ["accepted", "waived"]
            )
        )
        missing: list[str] = []
        nonaccepted: list[str] = []
        states: list[str] = []
        for evidence_id in criterion.evidence_ids:
            item = self.evidence.get(evidence_id)
            if item is None:
                missing.append(evidence_id)
                states.append("missing")
                continue
            states.append(item.status)
            if item.status in satisfactory:
                continue
            if item.status == "missing":
                missing.append(evidence_id)
            else:
                nonaccepted.append(evidence_id)

        approved_exception = any(
            record.criterion_id == criterion.id
            and record.status == "approved"
            and (record.expires_on is None or record.expires_on >= date.today())
            for record in self.exceptions.values()
        )
        if approved_exception and criterion.waivable:
            return CriterionResult(criterion=criterion, passed=True, state="waived")

        passed = not missing and not nonaccepted
        if passed:
            state = "passed"
        elif "rejected" in states:
            state = "rejected"
        elif "in_review" in states:
            state = "in_review"
        elif "draft" in states:
            state = "draft"
        elif "expired" in states:
            state = "expired"
        else:
            state = "missing"
        return CriterionResult(
            criterion=criterion,
            passed=passed,
            state=state,
            missing_evidence=missing,
            nonaccepted_evidence=nonaccepted,
        )

    def track_status(self, track_id: str) -> dict[str, Any]:
        if track_id not in self.tracks:
            raise KeyError(track_id)
        items = [item for item in self.work_items.values() if item.track_id == track_id]
        implemented = [
            item for item in items if item.status in {"done", "in_review", "accepted", "waived"}
        ]
        accepted_items = [item for item in items if item.status in {"accepted", "waived"}]
        blocked = [item for item in items if item.status == "blocked"]
        evidence = [item for item in self.evidence.values() if item.track_id == track_id]
        accepted_evidence = [item for item in evidence if item.status in {"accepted", "waived"}]
        return {
            "track_id": track_id,
            "name": self.tracks[track_id].name,
            "work_items": len(items),
            "implemented_work_items": len(implemented),
            "completed_work_items": len(accepted_items),
            "completion_percent": round((len(accepted_items) / len(items) * 100), 1)
            if items
            else 0.0,
            "implementation_percent": round((len(implemented) / len(items) * 100), 1)
            if items
            else 0.0,
            "blocked_work_items": len(blocked),
            "evidence_records": len(evidence),
            "accepted_evidence": len(accepted_evidence),
        }

    def dependencies_satisfied(self, item: WorkItem | dict[str, Any]) -> bool:
        dependency_ids = (
            item.dependency_ids
            if isinstance(item, WorkItem)
            else tuple(item.get("dependencies", item.get("depends_on", ())))
        )
        return all(
            self.work_items.get(dependency) is not None
            and self.work_items[dependency].status in {"accepted", "waived"}
            for dependency in dependency_ids
        )

    def next_actions(self, limit: int = 20, gate_id: str | None = None) -> list[WorkItem]:
        ready: list[WorkItem] = []
        for item in self.work_items.values():
            if item.status in {"accepted", "waived", "deferred"}:
                continue
            if gate_id and item.gate_id != gate_id:
                continue
            if self.dependencies_satisfied(item):
                ready.append(item)
        gate_order = {gate_id: index for index, gate_id in enumerate(self.gates)}
        ready.sort(
            key=lambda item: (
                PRIORITY_ORDER.get(item.priority, 99),
                gate_order.get(item.gate_id, 99),
                item.track_id,
                item.id,
            )
        )
        return ready[:limit]

    def topological_work_items(self) -> list[str]:
        indegree = {item_id: 0 for item_id in self.work_items}
        dependents: dict[str, list[str]] = {item_id: [] for item_id in self.work_items}
        for item_id, item in self.work_items.items():
            for dependency in item.dependency_ids:
                if dependency in indegree:
                    indegree[item_id] += 1
                    dependents[dependency].append(item_id)
        ready = sorted(item_id for item_id, degree in indegree.items() if degree == 0)
        order: list[str] = []
        while ready:
            current = ready.pop(0)
            order.append(current)
            for dependent in sorted(dependents[current]):
                indegree[dependent] -= 1
                if indegree[dependent] == 0:
                    ready.append(dependent)
                    ready.sort()
        if len(order) != len(self.work_items):
            raise RuntimeError("work-item dependency graph contains a cycle")
        return order

    def maturity_status(self) -> dict[str, Any]:
        if not self.maturity:
            return {"self_assessed_floor": 0, "assured_floor": 0, "dimensions": []}
        dimensions = []
        assured_levels: list[int] = []
        for item in self.maturity.values():
            satisfactory = set(
                self.project.config.get("conductor", {}).get(
                    "satisfactory_evidence_statuses", ["accepted", "waived"]
                )
            )
            accepted = all(
                evidence_id in self.evidence and self.evidence[evidence_id].status in satisfactory
                for evidence_id in item.evidence_ids
            )
            assured_level = item.assessed_level if accepted else 0
            assured_levels.append(assured_level)
            dimensions.append(
                {
                    "dimension_id": item.dimension_id,
                    "name": item.name,
                    "assessed_level": item.assessed_level,
                    "target_level": item.target_level,
                    "evidence_assured": accepted,
                    "assured_level": assured_level,
                    "status": item.status,
                }
            )
        return {
            "self_assessed_floor": min(item.assessed_level for item in self.maturity.values()),
            "assured_floor": min(assured_levels),
            "dimensions": dimensions,
        }

    def status_payload(self, *, generated_at: datetime | None = None) -> dict[str, Any]:
        validation = self.validate()
        gates = []
        for gate_id in self.gates:
            result = self.gate_result(gate_id)
            gates.append(
                {
                    "gate_id": gate_id,
                    "name": result.gate.name,
                    "target_release": result.gate.target_release,
                    "state": result.state,
                    "ready": result.ready,
                    "passed": result.passed,
                    "decision_status": result.decision_status,
                    "criteria_passed": result.passed_count,
                    "criteria_total": result.total_count,
                    "completed_requirements": result.completed_requirements,
                    "total_requirements": result.total_requirements,
                    "completion_percent": result.completion_percent,
                    "dependency_failures": result.dependency_failures,
                    "work_failures": result.work_failures,
                    "risk_failures": result.risk_failures,
                    "defect_failures": result.defect_failures,
                    "maturity_failure": result.maturity_failure,
                    "blockers": result.blockers,
                    "criteria": [
                        {
                            "criterion_id": criterion.criterion.id,
                            "track_id": criterion.criterion.track_id,
                            "description": criterion.criterion.description,
                            "state": criterion.state,
                            "passed": criterion.passed,
                            "missing_evidence": criterion.missing_evidence,
                            "nonaccepted_evidence": criterion.nonaccepted_evidence,
                        }
                        for criterion in result.criteria
                    ],
                }
            )
        return {
            "generated_at": (generated_at or datetime.now(UTC))
            .astimezone(UTC)
            .replace(microsecond=0)
            .isoformat(),
            "project": dict(self.project.project_config),
            "validation": validation.to_dict(),
            "gates": gates,
            "tracks": [self.track_status(track_id) for track_id in self.tracks],
            "maturity": self.maturity_status(),
            "controls": {
                "risks": len(self.risks),
                "open_critical_or_high_risks": sum(
                    1
                    for risk in self.risks.values()
                    if risk.residual_severity in {"critical", "high"} and risk.status != "closed"
                ),
                "defects": len(self.defects),
                "open_p0_p1_defects": sum(
                    1
                    for defect in self.defects.values()
                    if defect.severity in {"P0", "P1"}
                    and defect.status not in {"resolved", "closed"}
                ),
                "exceptions": len(self.exceptions),
            },
            "next_actions": [work_item_to_dict(item) for item in self.next_actions()],
        }

    def summary(self) -> dict[str, Any]:
        maturity = self.maturity_status()
        gate_results = [self.gate_result(gate_id) for gate_id in self.gates]
        first_unpassed = next(
            (result.gate.id for result in gate_results if not result.passed), None
        )
        return {
            "programme_id": self.project.project_config.get("id", "GFJD"),
            "current_release": self.project.project_config.get("version", "unknown"),
            "target_release": "1.0.0",
            "current_gate": first_unpassed or max(self.gates, key=lambda value: int(value[1:])),
            "declared_current_gate": self.project.project_config.get("current_gate", "G1"),
            "programme_maturity": maturity.get("assured_floor", 0),
            "self_assessed_maturity": maturity.get("self_assessed_floor", 0),
            "passed_gates": [result.gate.id for result in gate_results if result.passed],
            "ready_gates": [result.gate.id for result in gate_results if result.ready],
            "track_count": len(self.tracks),
            "work_item_count": len(self.work_items),
            "evidence_count": len(self.evidence),
        }

    def canonical_summary_json(self, *, generated_at: datetime | None = None) -> str:
        return (
            json.dumps(
                self.status_payload(generated_at=generated_at),
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
            + "\n"
        )

    def render_status_markdown(self, *, generated_at: datetime | None = None) -> str:
        return render_status_markdown(self.status_payload(generated_at=generated_at))

    def render_mermaid(self) -> str:
        lines = ["flowchart LR"]
        for gate in self.gates.values():
            result = self.gate_result(gate.id)
            label = f"{gate.id}: {gate.name}\n{result.state}".replace('"', "'")
            lines.append(f'  {gate.id}["{label}"]')
            for dependency in gate.dependency_ids:
                lines.append(f"  {dependency} --> {gate.id}")
        lines.append("  subgraph Tracks")
        for track in self.tracks.values():
            label = f"{track.id}: {track.name}".replace('"', "'")
            lines.append(f'    {track.id}["{label}"]')
        lines.append("  end")
        return "\n".join(lines) + "\n"

    def set_work_status(
        self,
        work_item_id: str,
        status: str,
        *,
        actor: str,
        note: str = "",
    ) -> WorkItem:
        if status not in WORK_STATUSES:
            raise ValueError(f"Invalid work status {status!r}")
        current = self.work_items.get(work_item_id)
        if current is None:
            raise KeyError(f"Unknown work item {work_item_id}")
        transitions = {
            "not_started": {"planned", "deferred"},
            "planned": {"in_progress", "blocked", "deferred"},
            "in_progress": {"blocked", "in_review", "done"},
            "blocked": {"in_progress", "deferred"},
            "done": {"in_review"},
            "review": {"accepted", "blocked"},
            "in_review": {"accepted", "blocked", "in_progress"},
            "accepted": set(),
            "waived": set(),
            "deferred": {"planned"},
        }
        if status != current.status and status not in transitions.get(current.status, set()):
            raise ValueError(f"Invalid work transition {current.status!r} -> {status!r}")
        if status == "accepted":
            unsatisfied = [
                evidence_id
                for evidence_id in current.evidence_ids
                if self.evidence.get(evidence_id) is None
                or self.evidence[evidence_id].status not in {"accepted", "waived"}
            ]
            if unsatisfied:
                raise ValueError(
                    f"Cannot accept {work_item_id}; evidence not accepted: {', '.join(unsatisfied)}"
                )
        updates = {"status": status}
        if note:
            updates["notes"] = note
        self._mutate_csv(
            self.project.paths["work_items"],
            "work_item_id",
            work_item_id,
            updates,
            actor=actor,
            event_type="work_status_changed",
        )
        return self.work_items[work_item_id]

    def review_evidence(
        self,
        evidence_id: str,
        status: str,
        *,
        reviewer_role: str,
        reviewed_on: date | None = None,
        notes: str | None = None,
    ) -> Evidence:
        if status not in {"in_review", "accepted", "rejected", "expired"}:
            raise ValueError(f"Invalid review status {status!r}")
        current = self.evidence.get(evidence_id)
        if current is None:
            raise KeyError(f"Unknown evidence {evidence_id}")
        updates: dict[str, str] = {
            "status": status,
            "reviewer_role": reviewer_role,
            "reviewed_on": (reviewed_on or date.today()).isoformat(),
        }
        if notes is not None:
            updates["notes"] = notes
        if status == "accepted":
            if not current.path:
                raise ValueError(f"Cannot accept {evidence_id}; no evidence path is recorded")
            path = self._safe_project_path(current.path)
            if not path.is_file():
                raise ValueError(
                    f"Cannot accept {evidence_id}; evidence path is not a file: {current.path}"
                )
            if reviewer_role.casefold() == current.owner_role.casefold():
                raise ValueError("Evidence reviewer must be independent of the evidence owner role")
            updates["sha256"] = sha256_file(path)
        self._mutate_csv(
            self.project.paths["evidence"],
            "evidence_id",
            evidence_id,
            updates,
            actor=reviewer_role,
            event_type="evidence_reviewed",
        )
        return self.evidence[evidence_id]

    def record_gate_decision(
        self,
        gate_id: str,
        status: str,
        *,
        authority: str,
        reference: str,
        conditions: str = "",
        expires_on: date | None = None,
        notes: str = "",
    ) -> GateDecision:
        if status not in {"accepted", "rejected", "conditional", "superseded"}:
            raise ValueError(f"Invalid gate decision status {status!r}")
        if gate_id not in self.gates:
            raise KeyError(f"Unknown gate {gate_id}")
        if status == "accepted" and not self.gate_result(gate_id).ready:
            blockers = "; ".join(self.gate_result(gate_id).blockers)
            raise ValueError(f"Cannot accept {gate_id}; gate is not ready: {blockers}")
        self._mutate_csv(
            self.project.paths["gate_decisions"],
            "gate_id",
            gate_id,
            {
                "status": status,
                "decided_on": date.today().isoformat(),
                "decision_authority": authority,
                "decision_reference": reference,
                "conditions": conditions,
                "expires_on": expires_on.isoformat() if expires_on else "",
                "notes": notes,
            },
            actor=authority,
            event_type="gate_decision_recorded",
        )
        return self.gate_decisions[gate_id]

    def update_risk(
        self,
        risk_id: str,
        *,
        actor: str,
        status: str | None = None,
        residual_severity: str | None = None,
        next_review_on: date | None = None,
        notes: str | None = None,
    ) -> Risk:
        if risk_id not in self.risks:
            raise KeyError(f"Unknown risk {risk_id}")
        updates: dict[str, str] = {"reviewed_on": date.today().isoformat()}
        if status is not None:
            if status not in {"open", "mitigating", "accepted", "closed"}:
                raise ValueError(f"Invalid risk status {status!r}")
            updates["status"] = status
        if residual_severity is not None:
            if residual_severity not in {"critical", "high", "medium", "low"}:
                raise ValueError(f"Invalid residual severity {residual_severity!r}")
            updates["residual_severity"] = residual_severity
        if next_review_on is not None:
            updates["next_review_on"] = next_review_on.isoformat()
        if notes is not None:
            updates["notes"] = notes
        self._mutate_csv(
            self.project.paths["risks"],
            "risk_id",
            risk_id,
            updates,
            actor=actor,
            event_type="risk_updated",
        )
        return self.risks[risk_id]

    def _mutate_csv(
        self,
        relative_path: str,
        key_field: str,
        key_value: str,
        updates: dict[str, str],
        *,
        actor: str,
        event_type: str,
    ) -> None:
        if not actor.strip():
            raise ValueError("actor is required for programme mutations")
        path = self.project.resolve(relative_path)
        lock_path = self.project.root / "programme" / ".conductor.lock"
        with programme_lock(lock_path):
            headers, rows = read_csv(path)
            matching = [row for row in rows if row.get(key_field, "").strip() == key_value]
            if len(matching) != 1:
                raise ValueError(
                    f"Expected exactly one {key_field}={key_value!r} in "
                    f"{relative_path}; found {len(matching)}"
                )
            before = dict(matching[0])
            for field_name in updates:
                if field_name not in headers:
                    raise ValueError(f"Unknown field {field_name!r} in {relative_path}")
            matching[0].update(updates)
            write_csv(path, headers, rows)
            event = {
                "event_id": f"AUD-{uuid4().hex.upper()}",
                "occurred_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
                "actor": actor,
                "event_type": event_type,
                "record_path": relative_path,
                "record_key": {key_field: key_value},
                "before": before,
                "after": dict(matching[0]),
            }
            audit_path = self.project.resolve(
                self.project.paths.get("audit_log", "programme/audit-log.jsonl")
            )
            audit_path.parent.mkdir(parents=True, exist_ok=True)
            with audit_path.open("a", encoding="utf-8", newline="\n") as handle:
                handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
                handle.flush()
                os.fsync(handle.fileno())
        refreshed = Conductor(load_project(self.project.root))
        self.__dict__.update(refreshed.__dict__)

    def render(
        self,
        output_dir: Path,
        *,
        generated_at: datetime | None = None,
    ) -> tuple[Path, Path, Path]:
        output_dir.mkdir(parents=True, exist_ok=True)
        payload = self.status_payload(generated_at=generated_at)
        json_path = output_dir / "programme-status.json"
        markdown_path = output_dir / "programme-status.md"
        graph_path = output_dir / "programme-dependencies.dot"
        write_json(json_path, payload)
        markdown_path.write_text(render_status_markdown(payload), encoding="utf-8")
        graph_path.write_text(self.render_dependency_graph(), encoding="utf-8")
        return json_path, markdown_path, graph_path

    def render_dependency_graph(self) -> str:
        lines = ["digraph GFJD_Programme {", "  rankdir=LR;", "  node [shape=box];"]
        for track in self.tracks.values():
            label = f"{track.id}\\n{track.name}".replace('"', "'")
            lines.append(f'  "{track.id}" [label="{label}"];')
        for track in self.tracks.values():
            for dependency in track.dependency_ids:
                lines.append(f'  "{dependency}" -> "{track.id}";')
        lines.append("  subgraph cluster_gates {")
        lines.append('    label="Stage gates";')
        for gate in self.gates.values():
            label = f"{gate.id}\\n{gate.target_release}".replace('"', "'")
            lines.append(f'    "{gate.id}" [shape=ellipse,label="{label}"];')
        for gate in self.gates.values():
            for dependency in gate.dependency_ids:
                lines.append(f'    "{dependency}" -> "{gate.id}";')
        lines.append("  }")
        lines.append("}")
        return "\n".join(lines) + "\n"

    def _safe_project_path(self, value: str) -> Path:
        candidate = (self.project.root / value).resolve()
        try:
            candidate.relative_to(self.project.root)
        except ValueError as exc:
            raise ValueError(f"Evidence path escapes project root: {value}") from exc
        return candidate


@contextmanager
def programme_lock(path: Path) -> Iterator[None]:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+b") as handle:
        if os.name == "nt":  # pragma: no cover - Windows CI only
            import msvcrt

            handle.seek(0)
            if handle.read(1) == b"":
                handle.write(b"0")
                handle.flush()
            handle.seek(0)
            lock_mode = msvcrt.LK_LOCK  # type: ignore[attr-defined]
            msvcrt.locking(  # type: ignore[attr-defined]
                handle.fileno(), lock_mode, 1
            )
        else:
            import fcntl

            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            if os.name == "nt":  # pragma: no cover
                import msvcrt

                handle.seek(0)
                unlock_mode = msvcrt.LK_UNLCK  # type: ignore[attr-defined]
                msvcrt.locking(  # type: ignore[attr-defined]
                    handle.fileno(), unlock_mode, 1
                )
            else:
                import fcntl

                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def split_refs(value: str | None) -> tuple[str, ...]:
    if not value:
        return ()
    return tuple(part.strip() for part in value.split(";") if part.strip())


def parse_optional_date(value: str | None) -> date | None:
    if not value or not value.strip():
        return None
    try:
        return date.fromisoformat(value.strip())
    except ValueError:
        return None


def find_cycle(graph: dict[str, Iterable[str]]) -> list[str] | None:
    visiting: set[str] = set()
    visited: set[str] = set()
    path: list[str] = []

    def visit(node: str) -> list[str] | None:
        if node in visited:
            return None
        if node in visiting:
            index = path.index(node)
            return [*path[index:], node]
        visiting.add(node)
        path.append(node)
        for dependency in graph.get(node, ()):
            if dependency not in graph:
                continue
            cycle = visit(dependency)
            if cycle:
                return cycle
        path.pop()
        visiting.remove(node)
        visited.add(node)
        return None

    for node in graph:
        cycle = visit(node)
        if cycle:
            return cycle
    return None


def work_item_to_dict(item: WorkItem) -> dict[str, Any]:
    return {
        "work_item_id": item.id,
        "track_id": item.track_id,
        "gate_id": item.gate_id,
        "title": item.title,
        "status": item.status,
        "priority": item.priority,
        "owner_role": item.owner_role,
        "deputy_role": item.deputy_role,
        "depends_on": list(item.dependency_ids),
        "evidence_ids": list(item.evidence_ids),
        "definition_of_done": item.definition_of_done,
        "notes": item.notes,
    }


def render_status_markdown(payload: dict[str, Any]) -> str:
    project = payload["project"]
    validation = payload["validation"]
    lines = [
        "# Generated programme status",
        "",
        f"Generated: `{payload['generated_at']}`",
        "",
        f"Current repository version: **{project.get('version', 'unknown')}**",
        f"Declared current gate: **{project.get('current_gate', 'unknown')}**  ",
        f"Conductor validation: **{'PASS' if validation['counts']['errors'] == 0 else 'FAIL'}** "
        f"({validation['counts']['errors']} errors, {validation['counts']['warnings']} warnings)",
        "",
        "## Gate readiness",
        "",
        "| Gate | Target | State | Ready | Decision | Controls complete | Principal blockers |",
        "|---|---:|---|---:|---|---:|---|",
    ]
    for gate in payload["gates"]:
        blockers = "; ".join(gate.get("blockers", [])[:3]) or "—"
        if len(gate.get("blockers", [])) > 3:
            blockers += f"; +{len(gate['blockers']) - 3} more"
        lines.append(
            f"| {gate['gate_id']} — {gate['name']} | {gate['target_release']} | {gate['state']} | "
            f"{'yes' if gate.get('ready') else 'no'} | {gate.get('decision_status', 'missing')} | "
            f"{gate.get('completed_requirements', gate['criteria_passed'])}/"
            f"{gate.get('total_requirements', gate['criteria_total'])} | {blockers} |"
        )
    lines.extend(
        [
            "",
            "## Track maturity",
            "",
            "| Track | Implemented work | Accepted work | Blocked | Accepted evidence |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for track in payload["tracks"]:
        lines.append(
            f"| {track['track_id']} — {track['name']} | "
            f"{track.get('implemented_work_items', track['completed_work_items'])}/"
            f"{track['work_items']} "
            f"({track.get('implementation_percent', track['completion_percent'])}%) | "
            f"{track['completed_work_items']}/{track['work_items']} "
            f"({track['completion_percent']}%) | {track['blocked_work_items']} | "
            f"{track['accepted_evidence']}/{track['evidence_records']} |"
        )
    maturity = payload["maturity"]
    lines.extend(
        [
            "",
            "## Evidence-assured maturity",
            "",
            f"Self-assessed maturity floor: **L{maturity['self_assessed_floor']}**  ",
            f"Evidence-assured maturity floor: **L{maturity['assured_floor']}**",
            "",
            "| Dimension | Assessed | Assured | Target |",
            "|---|---:|---:|---:|",
        ]
    )
    for dimension in maturity["dimensions"]:
        lines.append(
            f"| {dimension['dimension_id']} — {dimension['name']} | "
            f"L{dimension['assessed_level']} | "
            f"L{dimension['assured_level']} | L{dimension['target_level']} |"
        )
    controls = payload.get("controls", {})
    lines.extend(
        [
            "",
            "## Assurance controls",
            "",
            f"- Risks: **{controls.get('risks', 0)}**; open critical/high: "
            f"**{controls.get('open_critical_or_high_risks', 0)}**.",
            f"- Defects: **{controls.get('defects', 0)}**; open P0/P1: "
            f"**{controls.get('open_p0_p1_defects', 0)}**.",
            f"- Approved or pending exceptions recorded: **{controls.get('exceptions', 0)}**.",
            "",
            "## Next dependency-ready actions",
            "",
        ]
    )
    for item in payload["next_actions"]:
        lines.append(
            f"- **{item['priority']} {item['work_item_id']}** "
            f"({item['track_id']}/{item['gate_id']}): "
            f"{item['title']} — _{item['status']}_"
        )
    if not payload["next_actions"]:
        lines.append("No dependency-ready open work item was found.")
    lines.extend(
        [
            "",
            "> A gate is ready only after evidence, work, maturity, risk, defect and "
            "dependency controls pass. It passes only after a recorded governance "
            "decision. Document presence and self-assessment do not "
            "constitute acceptance.",
            "",
        ]
    )
    return "\n".join(lines)
