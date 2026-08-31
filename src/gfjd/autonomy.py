"""Deterministic context packets for safe single-maintainer autonomous work."""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .conductor import Conductor
from .io import read_json, sha256_file, write_json
from .project import Project

CONTEXT_FILES = (
    "AGENTS.md",
    "START_HERE.md",
    "BOOTSTRAP_AND_HANDOFF_PROMPT.md",
    "CODEX_IMPLEMENTATION_PROMPT.md",
    "docs/governance/standing-owner-direction-policy-2026-08-20.md",
    "AUTONOMOUS_IMPLEMENTATION.md",
    "docs/engineering/medallion-autonomous-continuation-2026-08-30.md",
    "docs/engineering/medallion-layer-qualification-plan-2026-08-31.md",
    "docs/engineering/medallion-estate-preparation-plan-2026-08-31.md",
    "IMPLEMENTATION_STATUS.md",
    "PROJECT_PLAN.md",
    "docs/governance/t0-acceptance-runbook.md",
    "config/project.toml",
    "config/tracks.toml",
    "config/stage_gates.toml",
    "config/workflows.toml",
    "programme/work_items.csv",
    "programme/evidence_register.csv",
    "programme/gate_decisions.csv",
    "programme/risk_register.csv",
)
CONTEXT_ARTIFACTS = ("autonomy-context.json", "autonomy-context.md")
MAX_CONTEXT_BYTES = 512_000

# Reviewed routing scopes, not authority grants. Unknown work fails closed;
# lifecycle status alone never authorizes external execution or publication.
REPOSITORY_IMPLEMENTATION_SCOPES = {
    "WI-G4-MED-02": (
        "Repository-only lineage, correction and replay implementation with synthetic tests. "
        "No source access, acquisition, publication, rights clearance or gate acceptance."
    ),
    "WI-G4-MED-03": (
        "Repository-only qualification adapters, synthetic rehearsal and advisory review. "
        "No source access, real evidence acceptance, rights clearance, maturity or Gold "
        "promotion, publication, release or gate acceptance. Programme dependencies remain binding."
    ),
}


@dataclass(frozen=True)
class AutonomyContext:
    output: Path
    sha256: str
    next_actions: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "output": str(self.output),
            "sha256": self.sha256,
            "next_actions": self.next_actions,
        }


def build_autonomy_context(
    project: Project,
    output: Path,
    *,
    generated_at: datetime | None = None,
) -> AutonomyContext:
    """Build a bounded, secret-free resume packet from authoritative repository state."""
    destination = output if output.is_absolute() else project.root / output
    destination.mkdir(parents=True, exist_ok=True)
    conductor = Conductor.load(project)
    timestamp = (generated_at or datetime.now(UTC)).astimezone(UTC).replace(microsecond=0)
    status = conductor.status_payload(generated_at=timestamp)
    files = []
    context_bytes = 0
    for relative in CONTEXT_FILES:
        path = project.root / relative
        content = path.read_text(encoding="utf-8") if path.is_file() else None
        encoded_bytes = len(content.encode("utf-8")) if content is not None else 0
        if context_bytes + encoded_bytes > MAX_CONTEXT_BYTES:
            content = None
        else:
            context_bytes += encoded_bytes
        files.append(
            {
                "path": relative,
                "exists": path.is_file(),
                "bytes": path.stat().st_size if path.is_file() else 0,
                "sha256": sha256_file(path) if path.is_file() else None,
                "content": content,
            }
        )
    git = {
        "head": _git(project.root, "rev-parse", "HEAD"),
        "branch": _git(project.root, "branch", "--show-current"),
        "upstream": _git(project.root, "rev-parse", "--abbrev-ref", "@{upstream}"),
        "working_tree": _git_lines(project.root, "status", "--short"),
        "recent_commits": _git_lines(project.root, "log", "-5", "--oneline"),
    }
    external = _external_boundaries(status)
    autonomous_queue, external_actions = _classify_actions(status["next_actions"])
    blocker_matrix = _blocker_matrix(status)
    dependency_sequence = [
        {
            "track_id": track.id,
            "depends_on": list(track.dependency_ids),
            "ready_after": list(track.dependency_ids),
        }
        for track in conductor.tracks.values()
    ]
    payload = {
        "schema_version": "1.0",
        "generated_at": timestamp.isoformat(),
        "operating_mode": "single_maintainer_autonomous",
        "authority_order": list(CONTEXT_FILES),
        "context_bytes": context_bytes,
        "context_byte_limit": MAX_CONTEXT_BYTES,
        "files": files,
        "git": git,
        "programme": status,
        "next_actions": status["next_actions"],
        "autonomous_queue": autonomous_queue,
        "external_actions": external_actions,
        "external_boundaries": external,
        "blocker_matrix": blocker_matrix,
        "dependency_sequence": dependency_sequence,
        "execution": {
            "fast_gate": ["make", "PYTHON=uv run python", "autonomy-fast"],
            "full_gate": ["make", "PYTHON=uv run python", "autonomy-full"],
            "context_refresh": [
                "uv",
                "run",
                "python",
                "-m",
                "gfjd",
                "autonomy",
                "context",
            ],
            "rules": [
                "Continue through safe repository-owned actions without routine confirmation.",
                "Use focused commits and leave the working tree reviewable.",
                (
                    "Stop at destructive, credential, publication, or genuine "
                    "human-approval boundaries."
                ),
                "Never convert technical validation into evidence or governance acceptance.",
            ],
        },
    }
    write_json(destination / "autonomy-context.json", payload)
    (destination / "autonomy-context.md").write_text(_render_markdown(payload), encoding="utf-8")
    manifest = {name: sha256_file(destination / name) for name in CONTEXT_ARTIFACTS}
    write_json(destination / "manifest.json", manifest)
    return AutonomyContext(
        destination,
        sha256_file(destination / "manifest.json"),
        len(status["next_actions"]),
    )


def verify_autonomy_context(output: Path) -> list[str]:
    """Verify the resume packet's fixed artifact set and hashes."""
    manifest_path = output / "manifest.json"
    if not manifest_path.is_file():
        return ["missing manifest.json"]
    try:
        manifest = read_json(manifest_path)
    except (OSError, json.JSONDecodeError) as exc:
        return [f"invalid manifest.json: {exc}"]
    if not isinstance(manifest, dict) or set(manifest) != set(CONTEXT_ARTIFACTS):
        return ["manifest artifact set is invalid"]
    errors = []
    for name in CONTEXT_ARTIFACTS:
        path = output / name
        if not path.is_file():
            errors.append(f"missing artifact: {name}")
        elif manifest[name] != sha256_file(path):
            errors.append(f"checksum mismatch: {name}")
    return errors


def _git(root: Path, *args: str) -> str | None:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    value = result.stdout.strip()
    return value if result.returncode == 0 and value else None


def _git_lines(root: Path, *args: str) -> list[str]:
    value = _git(root, *args)
    return value.splitlines() if value else []


def _external_boundaries(status: dict[str, Any]) -> list[dict[str, str]]:
    boundaries = []
    for gate in status["gates"]:
        if not gate["passed"]:
            boundaries.append(
                {
                    "id": gate["gate_id"],
                    "kind": "governance_decision",
                    "status": gate["decision_status"],
                    "reason": gate["state"],
                }
            )
    return boundaries


def _classify_actions(
    actions: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    repository_owned = []
    external = []
    for item in actions:
        work_id = item.get("work_item_id")
        status = item.get("status")
        scope = REPOSITORY_IMPLEMENTATION_SCOPES.get(work_id) if isinstance(work_id, str) else None
        if scope and isinstance(status, str) and status in {"planned", "in_progress"}:
            repository_owned.append({**item, "execution_scope": scope})
        else:
            external.append(item)
    return repository_owned, external


def _blocker_matrix(status: dict[str, Any]) -> list[dict[str, Any]]:
    """Flatten gate state into an actionable, fail-closed blocker register."""
    matrix: list[dict[str, Any]] = []
    for gate in status.get("gates", []):
        matrix.append(
            {
                "gate_id": gate["gate_id"],
                "state": gate["state"],
                "status": "blocked" if not gate["passed"] else "passed",
                "dependencies": list(gate.get("dependency_failures", [])),
                "work_items": list(gate.get("work_failures", [])),
                "risks": list(gate.get("risk_failures", [])),
                "defects": list(gate.get("defect_failures", [])),
                "criteria": [
                    {
                        "criterion_id": criterion["criterion_id"],
                        "track_id": criterion["track_id"],
                        "state": criterion["state"],
                        "missing_evidence": list(criterion.get("missing_evidence", [])),
                        "nonaccepted_evidence": list(criterion.get("nonaccepted_evidence", [])),
                    }
                    for criterion in gate.get("criteria", [])
                    if not criterion.get("passed", False)
                ],
                "external_boundary": gate["gate_id"]
                in {item["id"] for item in _external_boundaries(status)},
            }
        )
    return matrix


def _render_markdown(payload: dict[str, Any]) -> str:
    git = payload["git"]
    lines = [
        "# Autonomous implementation context",
        "",
        f"Generated: `{payload['generated_at']}`",
        f"Branch: `{git['branch'] or 'unavailable'}`",
        f"HEAD: `{git['head'] or 'unavailable'}`",
        f"Working-tree entries: **{len(git['working_tree'])}**",
        "",
        "## Resume order",
        "",
        "1. Read `AGENTS.md` and this packet.",
        "2. Inspect the working tree and preserve unrelated changes.",
        "3. Select the first safe repository-owned next action.",
        "4. Run the fast gate while iterating and the full gate at a checkpoint.",
        "5. Commit a coherent unit, refresh this packet, and report external gates separately.",
        "",
        "## Next actions",
        "",
    ]
    actions = payload["autonomous_queue"]
    if actions:
        lines.extend(
            f"- `{item['work_item_id']}` [{item['track_id']}/{item['gate_id']}]: {item['title']}\n"
            f"  Execution scope: {item['execution_scope']}"
            for item in actions
        )
    else:
        lines.append("- No safe repository-owned action is currently selected.")
    lines.extend(["", "## Actions awaiting scope review, external authority or acceptance", ""])
    external_actions = payload["external_actions"]
    lines.extend(
        f"- `{item['work_item_id']}` [{item['track_id']}/{item['gate_id']}]: {item['title']}"
        for item in external_actions
    )
    lines.extend(["", "## External boundaries", ""])
    lines.extend(
        f"- `{item['id']}`: {item['kind']} — {item['status']} ({item['reason']})"
        for item in payload["external_boundaries"]
    )
    lines.extend(["", "## Blocker matrix", ""])
    for blocker in payload["blocker_matrix"]:
        lines.append(
            f"- `{blocker['gate_id']}` [{blocker['state']}]: "
            f"{len(blocker['dependencies'])} dependencies, "
            f"{len(blocker['work_items'])} work items, "
            f"{len(blocker['risks'])} risks, "
            f"{len(blocker['criteria'])} criteria"
        )
    lines.extend(["", "## Track dependency sequence", ""])
    lines.extend(
        f"- `{item['track_id']}` after "
        f"{', '.join(item['depends_on']) if item['depends_on'] else 'no track dependencies'}"
        for item in payload["dependency_sequence"]
    )
    lines.extend(["", "## Authoritative context inventory", ""])
    lines.extend(
        f"- `{item['path']}` — {item['bytes']} bytes — `{item['sha256'] or 'missing'}`"
        for item in payload["files"]
    )
    return "\n".join(lines) + "\n"
