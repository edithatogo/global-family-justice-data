"""Static policy enforcement for GitHub Actions workflow definitions."""

from __future__ import annotations

import re
import tomllib
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml
from yaml.constructor import ConstructorError
from yaml.nodes import MappingNode
from yaml.tokens import AliasToken, AnchorToken

_SHA = re.compile(r"[0-9a-f]{40}")
_FORBIDDEN_SHELL = (
    re.compile(r"(?:curl|wget)\b[^\n|]*\|\s*(?:ba)?sh\b", re.IGNORECASE),
    re.compile(r"\$\{\{\s*(?:github\.event|inputs\.)", re.IGNORECASE),
)
_MAX_WORKFLOW_BYTES = 256_000
_MAX_YAML_ALIASES = 20
_SETUP_UV_REPOSITORY = "astral-sh/setup-uv"


class _Yaml12SafeLoader(yaml.SafeLoader):
    """SafeLoader variant that does not coerce YAML 1.1 yes/no/on/off booleans."""


_Yaml12SafeLoader.yaml_implicit_resolvers = {
    key: [item for item in value if item[0] != "tag:yaml.org,2002:bool"]
    for key, value in yaml.SafeLoader.yaml_implicit_resolvers.items()
}
_Yaml12SafeLoader.add_implicit_resolver(  # type: ignore[no-untyped-call]
    "tag:yaml.org,2002:bool",
    re.compile(r"^(?:true|false)$", re.IGNORECASE),
    list("tTfF"),
)


def _construct_unique_mapping(
    loader: _Yaml12SafeLoader, node: MappingNode, deep: bool = False
) -> dict[Any, Any]:
    """Construct a mapping while rejecting duplicate YAML keys."""

    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in mapping
        except TypeError as exc:
            raise ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                "found an unhashable key",
                key_node.start_mark,
            ) from exc
        if duplicate:
            raise ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key {key!r}",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


_Yaml12SafeLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_unique_mapping
)


@dataclass(frozen=True, slots=True)
class ActionPin:
    repository: str
    tag: str
    sha: str
    purpose: str


@dataclass(frozen=True, slots=True)
class PolicyIssue:
    severity: str
    code: str
    path: str
    context: str
    message: str

    def render(self) -> str:
        location = f"{self.path}:{self.context}" if self.context else self.path
        return f"[{self.severity.upper()}] {self.code} {location} — {self.message}"

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class PolicyReport:
    workflow_count: int
    step_count: int
    issues: tuple[PolicyIssue, ...]

    @property
    def error_count(self) -> int:
        return sum(issue.severity == "error" for issue in self.issues)

    @property
    def warning_count(self) -> int:
        return sum(issue.severity == "warning" for issue in self.issues)

    def to_dict(self) -> dict[str, Any]:
        return {
            "workflow_count": self.workflow_count,
            "step_count": self.step_count,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "issues": [issue.to_dict() for issue in self.issues],
        }

    def render_text(self) -> str:
        header = (
            f"GitHub Actions policy: {self.workflow_count} workflow(s), "
            f"{self.step_count} step(s), {self.error_count} error(s), "
            f"{self.warning_count} warning(s)."
        )
        if not self.issues:
            return header
        return "\n".join([header, *(issue.render() for issue in self.issues)])


def load_action_pins(path: Path) -> dict[str, ActionPin]:
    """Load and validate the reviewed third-party action allow-list."""

    try:
        with path.open("rb") as handle:
            payload = tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise ValueError(f"Could not load GitHub action lock {path}: {exc}") from exc
    raw_actions = payload.get("action", [])
    if not isinstance(raw_actions, list):
        raise ValueError("config/github_actions.toml must contain [[action]] tables")
    pins: dict[str, ActionPin] = {}
    seen_shas: set[str] = set()
    for index, raw in enumerate(raw_actions, start=1):
        if not isinstance(raw, Mapping):
            raise ValueError(f"Action lock entry {index} is not a table")
        repository = str(raw.get("repository", "")).lower()
        tag = str(raw.get("tag", ""))
        sha = str(raw.get("sha", "")).lower()
        purpose = str(raw.get("purpose", ""))
        if not re.fullmatch(r"[a-z0-9_.-]+/[a-z0-9_.-]+", repository):
            raise ValueError(f"Invalid action repository in lock entry {index}: {repository!r}")
        if not _SHA.fullmatch(sha):
            raise ValueError(f"Invalid action SHA in lock entry {index}: {sha!r}")
        if repository in pins:
            raise ValueError(f"Duplicate action repository in lock: {repository}")
        if sha in seen_shas:
            raise ValueError(f"Action SHA is reused across repositories: {sha}")
        if not tag or not purpose:
            raise ValueError(f"Action lock entry {index} requires tag and purpose")
        pins[repository] = ActionPin(repository, tag, sha, purpose)
        seen_shas.add(sha)
    return pins


def audit_workflows(root: Path) -> PolicyReport:
    """Audit all GitHub Actions files against the repository's fail-closed policy."""

    root = root.expanduser().resolve()
    issues: list[PolicyIssue] = []
    lock_path = root / "config" / "github_actions.toml"
    try:
        pins = load_action_pins(lock_path)
    except ValueError as exc:
        pins = {}
        issues.append(PolicyIssue("error", "ACTION_LOCK_INVALID", str(lock_path), "", str(exc)))

    expected_uv_version = _expected_uv_version(root, issues)
    merge_queue_workflows = _merge_queue_workflows(root, issues)

    workflow_dir = root / ".github" / "workflows"
    paths = sorted([*workflow_dir.glob("*.yml"), *workflow_dir.glob("*.yaml")])
    step_count = 0
    for path in paths:
        relative = path.relative_to(root).as_posix()
        try:
            raw = path.read_bytes()
            if len(raw) > _MAX_WORKFLOW_BYTES:
                issues.append(
                    PolicyIssue(
                        "error",
                        "WORKFLOW_TOO_LARGE",
                        relative,
                        "",
                        f"Workflow exceeds {_MAX_WORKFLOW_BYTES} bytes",
                    )
                )
                continue
            text = raw.decode("utf-8")
            alias_count = sum(
                isinstance(token, (AliasToken, AnchorToken)) for token in yaml.scan(text)
            )
            if alias_count > _MAX_YAML_ALIASES:
                issues.append(
                    PolicyIssue(
                        "error",
                        "WORKFLOW_ALIAS_LIMIT",
                        relative,
                        "",
                        f"Workflow contains {alias_count} YAML anchors/aliases",
                    )
                )
                continue
            # The custom loader subclasses SafeLoader and only changes YAML 1.2 scalar handling.
            payload = yaml.load(text, Loader=_Yaml12SafeLoader)  # nosec B506
        except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
            issues.append(PolicyIssue("error", "WORKFLOW_PARSE", relative, "", str(exc)))
            continue
        if not isinstance(payload, Mapping):
            issues.append(
                PolicyIssue("error", "WORKFLOW_ROOT", relative, "", "Workflow root must be a map")
            )
            continue
        events = payload.get("on")
        if _contains_event(events, "pull_request_target"):
            issues.append(
                PolicyIssue(
                    "error",
                    "PR_TARGET_FORBIDDEN",
                    relative,
                    "on",
                    "pull_request_target executes privileged base-repository code and is forbidden",
                )
            )
        if path.name in merge_queue_workflows and not _contains_event(events, "merge_group"):
            issues.append(
                PolicyIssue(
                    "error",
                    "MERGE_GROUP_REQUIRED",
                    relative,
                    "on",
                    "Workflow supplies required merge-queue checks and must handle merge_group",
                )
            )
        _check_concurrency(
            payload.get("concurrency"),
            relative,
            issues,
            stable_release=path.name == "stable-release.yml",
        )
        _check_top_permissions(payload.get("permissions"), relative, issues)
        jobs = payload.get("jobs")
        if not isinstance(jobs, Mapping) or not jobs:
            issues.append(PolicyIssue("error", "JOBS_MISSING", relative, "jobs", "No jobs defined"))
            continue
        for job_id, raw_job in jobs.items():
            context = f"jobs.{job_id}"
            if not isinstance(raw_job, Mapping):
                issues.append(
                    PolicyIssue("error", "JOB_INVALID", relative, context, "Job must be a map")
                )
                continue
            timeout = raw_job.get("timeout-minutes")
            if not isinstance(timeout, int) or isinstance(timeout, bool) or not 1 <= timeout <= 360:
                issues.append(
                    PolicyIssue(
                        "error",
                        "JOB_TIMEOUT_REQUIRED",
                        relative,
                        context,
                        "Every job needs timeout-minutes between 1 and 360",
                    )
                )
            _check_job_permissions(raw_job, relative, str(job_id), issues)
            steps = raw_job.get("steps", [])
            if not isinstance(steps, list):
                issues.append(
                    PolicyIssue("error", "STEPS_INVALID", relative, context, "steps must be a list")
                )
                continue
            for index, raw_step in enumerate(steps, start=1):
                step_count += 1
                step_context = f"{context}.steps[{index}]"
                if not isinstance(raw_step, Mapping):
                    issues.append(
                        PolicyIssue(
                            "error", "STEP_INVALID", relative, step_context, "Step must be a map"
                        )
                    )
                    continue
                if raw_step.get("continue-on-error") in {True, "true"}:
                    issues.append(
                        PolicyIssue(
                            "error",
                            "CONTINUE_ON_ERROR_FORBIDDEN",
                            relative,
                            step_context,
                            "Protected repository workflows must fail closed",
                        )
                    )
                uses = raw_step.get("uses")
                if uses is not None:
                    _check_action(
                        str(uses),
                        raw_step,
                        pins,
                        relative,
                        step_context,
                        issues,
                        expected_uv_version=expected_uv_version,
                    )
                run = raw_step.get("run")
                if isinstance(run, str):
                    for pattern in _FORBIDDEN_SHELL:
                        if pattern.search(run):
                            issues.append(
                                PolicyIssue(
                                    "error",
                                    "UNSAFE_SHELL",
                                    relative,
                                    step_context,
                                    (
                                        "Shell command contains an unsafe download pipe or "
                                        "direct untrusted expression"
                                    ),
                                )
                            )
                    if "sudo pip" in run or "sudo python -m pip" in run:
                        issues.append(
                            PolicyIssue(
                                "error",
                                "SUDO_PIP_FORBIDDEN",
                                relative,
                                step_context,
                                "Privileged package installation is forbidden",
                            )
                        )
    return PolicyReport(len(paths), step_count, tuple(sorted(issues, key=_issue_sort_key)))


def _contains_event(events: Any, event: str) -> bool:
    if isinstance(events, str):
        return events == event
    if isinstance(events, list):
        return event in events
    if isinstance(events, Mapping):
        return event in events
    return False


def _check_concurrency(
    value: Any,
    path: str,
    issues: list[PolicyIssue],
    *,
    stable_release: bool,
) -> None:
    if not isinstance(value, Mapping):
        issues.append(
            PolicyIssue(
                "error",
                "CONCURRENCY_REQUIRED",
                path,
                "concurrency",
                "Workflow must declare an explicit concurrency group",
            )
        )
        return
    cancel = value.get("cancel-in-progress")
    expected_cancel = not stable_release
    if not value.get("group") or cancel is not expected_cancel:
        expected = "false" if stable_release else "true"
        issues.append(
            PolicyIssue(
                "error",
                "CONCURRENCY_INCOMPLETE",
                path,
                "concurrency",
                f"concurrency requires group and cancel-in-progress: {expected}",
            )
        )


def _check_top_permissions(value: Any, path: str, issues: list[PolicyIssue]) -> None:
    if not isinstance(value, Mapping):
        issues.append(
            PolicyIssue(
                "error",
                "TOP_PERMISSIONS_REQUIRED",
                path,
                "permissions",
                "Workflow must declare read-only top-level permissions",
            )
        )
        return
    for name, level in value.items():
        if str(level) not in {"read", "none"}:
            issues.append(
                PolicyIssue(
                    "error",
                    "TOP_PERMISSION_WRITE",
                    path,
                    f"permissions.{name}",
                    "Write permission is only permitted at a narrowly scoped job",
                )
            )


def _check_job_permissions(
    job: Mapping[str, Any], path: str, job_id: str, issues: list[PolicyIssue]
) -> None:
    value = job.get("permissions")
    context = f"jobs.{job_id}.permissions"
    if not isinstance(value, Mapping):
        issues.append(
            PolicyIssue(
                "error",
                "JOB_PERMISSIONS_REQUIRED",
                path,
                context,
                "Every job must declare its own least-privilege permissions",
            )
        )
        return
    environment = job.get("environment")
    for name, level in value.items():
        level_text = str(level)
        if level_text not in {"read", "write", "none"}:
            issues.append(
                PolicyIssue(
                    "error", "PERMISSION_INVALID", path, context, f"Invalid level {level_text!r}"
                )
            )
            continue
        if level_text != "write":
            continue
        if name == "security-events" and Path(path).name == "codeql.yml":
            continue
        if name in {"contents", "id-token", "attestations"} and environment:
            continue
        issues.append(
            PolicyIssue(
                "error",
                "WRITE_PERMISSION_UNGUARDED",
                path,
                f"{context}.{name}",
                "Write permission requires a protected environment (except CodeQL security-events)",
            )
        )


def _check_action(
    uses: str,
    step: Mapping[str, Any],
    pins: Mapping[str, ActionPin],
    path: str,
    context: str,
    issues: list[PolicyIssue],
    *,
    expected_uv_version: str | None,
) -> None:
    if uses.startswith("./"):
        return
    if uses.startswith("docker://"):
        issues.append(
            PolicyIssue(
                "error",
                "DOCKER_ACTION_FORBIDDEN",
                path,
                context,
                "Container actions need a separately reviewed digest policy",
            )
        )
        return
    try:
        action_path, ref = uses.rsplit("@", 1)
    except ValueError:
        issues.append(
            PolicyIssue(
                "error", "ACTION_REF_MISSING", path, context, f"Invalid uses value {uses!r}"
            )
        )
        return
    parts = action_path.lower().split("/")
    if len(parts) < 2:
        issues.append(PolicyIssue("error", "ACTION_REPOSITORY_INVALID", path, context, uses))
        return
    repository = "/".join(parts[:2])
    if not _SHA.fullmatch(ref.lower()):
        issues.append(
            PolicyIssue(
                "error",
                "ACTION_NOT_IMMUTABLE",
                path,
                context,
                f"{uses!r} must use a full 40-character commit SHA",
            )
        )
        return
    pin = pins.get(repository)
    if pin is None or pin.sha != ref.lower():
        issues.append(
            PolicyIssue(
                "error",
                "ACTION_NOT_ALLOWLISTED",
                path,
                context,
                f"{repository}@{ref} is absent from config/github_actions.toml",
            )
        )
    if repository == "actions/checkout":
        with_values = step.get("with", {})
        persist = (
            with_values.get("persist-credentials") if isinstance(with_values, Mapping) else None
        )
        if persist not in {False, "false"}:
            issues.append(
                PolicyIssue(
                    "error",
                    "CHECKOUT_CREDENTIALS",
                    path,
                    context,
                    "actions/checkout must set persist-credentials: false",
                )
            )
        depth = with_values.get("fetch-depth") if isinstance(with_values, Mapping) else None
        if depth not in {1, "1"}:
            issues.append(
                PolicyIssue(
                    "error",
                    "CHECKOUT_DEPTH",
                    path,
                    context,
                    "actions/checkout must explicitly set fetch-depth: 1",
                )
            )
    if repository == _SETUP_UV_REPOSITORY:
        with_values = step.get("with", {})
        if not isinstance(with_values, Mapping):
            with_values = {}
        expected = {
            "version": expected_uv_version,
            "enable-cache": True,
            "cache-dependency-glob": "uv.lock",
            "download-from-astral-mirror": False,
        }
        for key, expected_value in expected.items():
            actual = with_values.get(key)
            accepted = {expected_value}
            if isinstance(expected_value, bool):
                accepted.add(str(expected_value).lower())
            if actual not in accepted:
                issues.append(
                    PolicyIssue(
                        "error",
                        "SETUP_UV_POLICY",
                        path,
                        f"{context}.with.{key}",
                        f"Expected {expected_value!r}; found {actual!r}",
                    )
                )


def _expected_uv_version(root: Path, issues: list[PolicyIssue]) -> str | None:
    path = root / "config" / "project.toml"
    try:
        with path.open("rb") as handle:
            payload = tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        issues.append(PolicyIssue("error", "PROJECT_CONFIG_INVALID", str(path), "", str(exc)))
        return None
    toolchain = payload.get("toolchain", {})
    if not isinstance(toolchain, Mapping) or not toolchain.get("uv_version"):
        issues.append(
            PolicyIssue(
                "error",
                "UV_VERSION_MISSING",
                str(path),
                "toolchain.uv_version",
                "Reviewed uv version is required",
            )
        )
        return None
    return str(toolchain["uv_version"])


def _merge_queue_workflows(root: Path, issues: list[PolicyIssue]) -> set[str]:
    path = root / "config" / "github_repository_controls.toml"
    try:
        with path.open("rb") as handle:
            payload = tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        issues.append(PolicyIssue("error", "REPOSITORY_CONFIG_INVALID", str(path), "", str(exc)))
        return set()
    section = payload.get("merge_queue", {})
    values = section.get("required_workflows", []) if isinstance(section, Mapping) else []
    if not isinstance(values, list) or not values:
        issues.append(
            PolicyIssue(
                "error",
                "MERGE_QUEUE_WORKFLOWS_MISSING",
                str(path),
                "merge_queue.required_workflows",
                "At least one required merge-queue workflow must be declared",
            )
        )
        return set()
    return {str(item) for item in values}


def _issue_sort_key(issue: PolicyIssue) -> tuple[str, str, str, str]:
    return (issue.path, issue.context, issue.severity, issue.code)
