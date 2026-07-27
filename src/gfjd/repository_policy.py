"""Validation of the declared GitHub repository and release-control baseline."""

from __future__ import annotations

import itertools
import re
import tomllib
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml

from .ci_policy import _Yaml12SafeLoader, load_action_pins


@dataclass(frozen=True, slots=True)
class RepositoryPolicyIssue:
    severity: str
    code: str
    subject: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)

    def render(self) -> str:
        return f"[{self.severity.upper()}] {self.code} {self.subject} — {self.message}"


@dataclass(frozen=True, slots=True)
class RepositoryPolicyReport:
    issues: tuple[RepositoryPolicyIssue, ...]
    controls_checked: int

    @property
    def error_count(self) -> int:
        return sum(issue.severity == "error" for issue in self.issues)

    @property
    def warning_count(self) -> int:
        return sum(issue.severity == "warning" for issue in self.issues)

    def to_dict(self) -> dict[str, Any]:
        return {
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "controls_checked": self.controls_checked,
            "issues": [issue.to_dict() for issue in self.issues],
        }

    def render_text(self) -> str:
        lines = [
            "GitHub repository controls: "
            f"{self.controls_checked} checked, {self.error_count} error(s), "
            f"{self.warning_count} warning(s)."
        ]
        lines.extend(issue.render() for issue in self.issues)
        return "\n".join(lines)


def audit_repository_controls(root: Path) -> RepositoryPolicyReport:
    """Validate a fail-closed desired-state declaration for GitHub controls."""

    path = root / "config" / "github_repository_controls.toml"
    try:
        with path.open("rb") as handle:
            config = tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        return RepositoryPolicyReport(
            (RepositoryPolicyIssue("error", "REPOSITORY_POLICY_READ", str(path), str(exc)),),
            0,
        )

    issues: list[RepositoryPolicyIssue] = []
    checked = 0

    checked += _expect_equal(issues, config, "schema_version", "1.0", "REPOSITORY_POLICY_SCHEMA")
    repository = _table(config, "repository", issues)
    actions = _table(config, "actions", issues)
    rulesets = _table(config, "rulesets", issues)
    environments = _table(config, "environments", issues)
    security = _table(config, "security", issues)
    retention = _table(config, "retention", issues)
    ownership = _table(config, "ownership", issues)
    merge_queue = _table(config, "merge_queue", issues)
    governance = _table(config, "governance", issues)
    solo_agent = str(governance.get("review_model", "")) == "solo_agent"

    checked += _expect_equal(issues, repository, "default_branch", "main", "DEFAULT_BRANCH")
    for key in (
        "require_linear_history",
        "require_signed_commits",
        "block_force_pushes",
        "block_deletions",
        "require_conversation_resolution",
    ):
        checked += _expect_true(issues, repository, key, "BRANCH_BASELINE")

    checked += _expect_equal(
        issues, actions, "default_workflow_permissions", "read", "ACTIONS_PERMISSIONS"
    )
    checked += _expect_true(issues, actions, "require_immutable_action_shas", "ACTIONS_SHA_PINNING")
    for key in ("allow_actions_create_pull_requests", "allow_untrusted_fork_write_tokens"):
        checked += _expect_false(issues, actions, key, "ACTIONS_TOKEN_POLICY")
    checked += _expect_equal(
        issues,
        actions,
        "fork_pull_request_approval",
        "all_external_contributors",
        "FORK_APPROVAL_POLICY",
    )
    checked += 1
    allowed_actions = actions.get("allowed_action_repositories", [])
    try:
        locked_actions = set(load_action_pins(root / "config" / "github_actions.toml"))
    except ValueError as exc:
        locked_actions = set()
        issues.append(
            RepositoryPolicyIssue(
                "error", "ACTION_LOCK_INVALID", "config/github_actions.toml", str(exc)
            )
        )
    if not isinstance(allowed_actions, list) or set(map(str, allowed_actions)) != locked_actions:
        issues.append(
            RepositoryPolicyIssue(
                "error",
                "ALLOWED_ACTIONS_DRIFT",
                "actions.allowed_action_repositories",
                "Allowed GitHub action repositories must exactly match the reviewed action lock",
            )
        )

    main = _table(rulesets, "main", issues, prefix="rulesets")
    checked += _expect_equal(issues, main, "enforcement", "active", "MAIN_RULESET")
    checked += _expect_equal(issues, main, "target", "refs/heads/main", "MAIN_RULESET")
    approvals = _integer(main.get("required_approvals"))
    checked += 1
    if approvals < (0 if solo_agent else 2):
        issues.append(
            RepositoryPolicyIssue(
                "error",
                "REVIEW_THRESHOLD",
                "rulesets.main.required_approvals",
                "At least two approving reviews are required unless review_model=solo_agent",
            )
        )
    main_control_keys = (
        "dismiss_stale_approvals",
        "require_last_push_approval",
        "require_merge_queue",
        "prevent_bypass",
        "require_status_checks_up_to_date",
    )
    for key in main_control_keys:
        checked += _expect_true(issues, main, key, "MAIN_RULESET")
    if not solo_agent:
        checked += _expect_true(issues, main, "require_code_owner_review", "MAIN_RULESET")
    checks = main.get("required_status_checks", [])
    checked += 1
    if not isinstance(checks, list) or len({str(item) for item in checks}) < 8:
        issues.append(
            RepositoryPolicyIssue(
                "error",
                "REQUIRED_CHECKS",
                "rulesets.main.required_status_checks",
                "A broad, duplicate-free required-check set is required",
            )
        )
    elif len(checks) != len({str(item) for item in checks}):
        issues.append(
            RepositoryPolicyIssue(
                "error",
                "REQUIRED_CHECKS_DUPLICATE",
                "rulesets.main.required_status_checks",
                "Required status checks must be unique",
            )
        )

    checked += 1
    required_workflows = merge_queue.get("required_workflows", [])
    if not isinstance(required_workflows, list) or not required_workflows:
        issues.append(
            RepositoryPolicyIssue(
                "error",
                "MERGE_QUEUE_WORKFLOWS",
                "merge_queue.required_workflows",
                "At least one merge-queue workflow is required",
            )
        )
    else:
        discovered, workflow_errors = _discover_check_names(
            root, tuple(str(item) for item in required_workflows)
        )
        issues.extend(workflow_errors)
        required_set = {str(item) for item in checks} if isinstance(checks, list) else set()
        missing = sorted(required_set - discovered)
        unprotected = sorted(discovered - required_set)
        if missing:
            issues.append(
                RepositoryPolicyIssue(
                    "error",
                    "REQUIRED_CHECK_NOT_EMITTED",
                    "rulesets.main.required_status_checks",
                    "Configured checks not emitted by merge-queue workflows: " + ", ".join(missing),
                )
            )
        if unprotected:
            issues.append(
                RepositoryPolicyIssue(
                    "error",
                    "WORKFLOW_CHECK_NOT_REQUIRED",
                    "merge_queue.required_workflows",
                    "Workflow jobs not protected by the main ruleset: " + ", ".join(unprotected),
                )
            )

    tags = _table(rulesets, "release_tags", issues, prefix="rulesets")
    checked += _expect_equal(issues, tags, "enforcement", "active", "TAG_RULESET")
    checked += _expect_equal(issues, tags, "target", "refs/tags/v*", "TAG_RULESET")
    checked += _expect_true(issues, tags, "block_updates", "TAG_RULESET")
    checked += _expect_true(issues, tags, "block_deletions", "TAG_RULESET")

    for name in ("release_candidate", "stable_release"):
        environment = _table(environments, name, issues, prefix="environments")
        checked += 1
        if _integer(environment.get("required_reviewers")) < (0 if solo_agent else 2):
            issues.append(
                RepositoryPolicyIssue(
                    "error",
                    "ENVIRONMENT_REVIEWERS",
                    f"environments.{name}.required_reviewers",
                    "At least two independent reviewers are required unless review_model=solo_agent",
                )
            )
        if not solo_agent:
            checked += _expect_true(
                issues, environment, "prevent_self_review", "ENVIRONMENT_PROTECTION"
            )
        checked += _expect_true(
            issues, environment, "protected_branches_only", "ENVIRONMENT_PROTECTION"
        )
        expected_pattern = "refs/heads/main" if name == "release_candidate" else "refs/tags/v*"
        checked += _expect_equal(
            issues,
            environment,
            "deployment_ref_pattern",
            expected_pattern,
            "ENVIRONMENT_REF_POLICY",
        )

    for key in (
        "dependency_graph",
        "dependabot_alerts",
        "dependabot_security_updates",
        "secret_scanning",
        "secret_scanning_push_protection",
        "private_vulnerability_reporting",
    ):
        checked += _expect_true(issues, security, key, "SECURITY_CONTROL")

    minimum_retention = {
        "ordinary_artifacts_days": 14,
        "security_artifacts_days": 30,
        "release_candidate_artifacts_days": 90,
        "stable_release_artifacts_days": 90,
        "provenance_artifacts_days": 90,
    }
    for key, minimum in minimum_retention.items():
        checked += 1
        if _integer(retention.get(key)) < minimum:
            issues.append(
                RepositoryPolicyIssue(
                    "error",
                    "ARTIFACT_RETENTION",
                    f"retention.{key}",
                    f"Must be at least {minimum} days",
                )
            )

    checked += 1
    implementation = str(config.get("implementation_status", ""))
    if implementation not in {"verified_applied", "verified_baseline_applied"}:
        issues.append(
            RepositoryPolicyIssue(
                "warning",
                "REPOSITORY_CONTROLS_UNVERIFIED",
                "implementation_status",
                "Desired controls are defined but have not been verified against GitHub",
            )
        )
    checked += 1
    if str(ownership.get("codeowners_status", "")) != "verified_real_handles":
        issues.append(
            RepositoryPolicyIssue(
                "warning",
                "CODEOWNERS_PENDING",
                "ownership.codeowners_status",
                (
                    "Replace CODEOWNERS.example with verified real maintainers "
                    "before protected release"
                ),
            )
        )
    return RepositoryPolicyReport(tuple(issues), checked)


_MATRIX_PATTERN = re.compile(r"\$\{\{\s*matrix\.([A-Za-z0-9_-]+)\s*\}\}")


def _discover_check_names(
    root: Path, workflows: tuple[str, ...]
) -> tuple[set[str], list[RepositoryPolicyIssue]]:
    names: set[str] = set()
    issues: list[RepositoryPolicyIssue] = []
    for filename in workflows:
        path = root / ".github" / "workflows" / filename
        if not path.is_file():
            issues.append(
                RepositoryPolicyIssue(
                    "error", "MERGE_QUEUE_WORKFLOW_MISSING", filename, "Workflow file is missing"
                )
            )
            continue
        try:
            # The custom loader subclasses SafeLoader and rejects duplicate mapping keys.
            payload = yaml.load(path.read_text(encoding="utf-8"), Loader=_Yaml12SafeLoader)  # nosec B506
        except (OSError, yaml.YAMLError) as exc:
            issues.append(
                RepositoryPolicyIssue("error", "MERGE_QUEUE_WORKFLOW_PARSE", filename, str(exc))
            )
            continue
        if not isinstance(payload, dict):
            issues.append(
                RepositoryPolicyIssue(
                    "error", "MERGE_QUEUE_WORKFLOW_ROOT", filename, "Workflow root is not a map"
                )
            )
            continue
        events = payload.get("on", {})
        if not isinstance(events, dict) or "merge_group" not in events:
            issues.append(
                RepositoryPolicyIssue(
                    "error",
                    "MERGE_QUEUE_TRIGGER_MISSING",
                    filename,
                    "Required-check workflow must handle merge_group",
                )
            )
        jobs = payload.get("jobs", {})
        if not isinstance(jobs, dict):
            issues.append(
                RepositoryPolicyIssue("error", "MERGE_QUEUE_JOBS", filename, "jobs is not a map")
            )
            continue
        for job_id, raw_job in jobs.items():
            if not isinstance(raw_job, dict):
                continue
            template = str(raw_job.get("name", job_id))
            matrix = raw_job.get("strategy", {}).get("matrix", {})
            axes = _matrix_axes(matrix)
            referenced = set(_MATRIX_PATTERN.findall(template))
            if not referenced:
                names.add(template)
                continue
            if not referenced <= set(axes):
                issues.append(
                    RepositoryPolicyIssue(
                        "error",
                        "CHECK_NAME_MATRIX_UNRESOLVED",
                        f"{filename}:{job_id}",
                        "Job name references a matrix axis that cannot be expanded",
                    )
                )
                continue
            for values in itertools.product(*(axes[key] for key in sorted(referenced))):
                rendered = template
                for key, value in zip(sorted(referenced), values, strict=True):
                    rendered = re.sub(
                        rf"\$\{{\{{\s*matrix\.{re.escape(key)}\s*\}}\}}",
                        str(value),
                        rendered,
                    )
                names.add(rendered)
    return names, issues


def _matrix_axes(value: Any) -> dict[str, tuple[str, ...]]:
    if not isinstance(value, dict):
        return {}
    axes: dict[str, tuple[str, ...]] = {}
    for key, raw in value.items():
        if key in {"include", "exclude"} or not isinstance(raw, list):
            continue
        axes[str(key)] = tuple(str(item) for item in raw)
    return axes


def _table(
    parent: dict[str, Any],
    name: str,
    issues: list[RepositoryPolicyIssue],
    *,
    prefix: str = "",
) -> dict[str, Any]:
    value = parent.get(name)
    subject = f"{prefix}.{name}".strip(".")
    if not isinstance(value, dict):
        issues.append(
            RepositoryPolicyIssue(
                "error", "REPOSITORY_POLICY_TABLE", subject, "Required TOML table is missing"
            )
        )
        return {}
    return value


def _expect_true(
    issues: list[RepositoryPolicyIssue],
    table: dict[str, Any],
    key: str,
    code: str,
) -> int:
    if table.get(key) is not True:
        issues.append(RepositoryPolicyIssue("error", code, key, "Must be true"))
    return 1


def _expect_false(
    issues: list[RepositoryPolicyIssue],
    table: dict[str, Any],
    key: str,
    code: str,
) -> int:
    if table.get(key) is not False:
        issues.append(RepositoryPolicyIssue("error", code, key, "Must be false"))
    return 1


def _expect_equal(
    issues: list[RepositoryPolicyIssue],
    table: dict[str, Any],
    key: str,
    expected: Any,
    code: str,
) -> int:
    if table.get(key) != expected:
        issues.append(
            RepositoryPolicyIssue(
                "error", code, key, f"Expected {expected!r}; found {table.get(key)!r}"
            )
        )
    return 1


def _integer(value: Any) -> int:
    return value if isinstance(value, int) and not isinstance(value, bool) else 0
