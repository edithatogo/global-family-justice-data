"""Safe, idempotent workspace and remote bootstrap tooling for GFJD.

The bootstrap layer deliberately separates discovery/planning from mutation.  It can
inventory nearby Git repositories, inspect authenticated GitHub and Hugging Face
accounts, initialise this repository, create/wire a GitHub remote, create private
Hugging Face publication repositories, and emit checksum-bound receipts.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
from collections import defaultdict, deque
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from .io import read_json
from .project import Project


class BootstrapError(RuntimeError):
    """Raised when a bootstrap precondition or mutation fails."""


@dataclass(frozen=True)
class CommandResult:
    """Redacted command execution receipt."""

    command: tuple[str, ...]
    cwd: str
    returncode: int
    stdout: str
    stderr: str
    started_at: str
    finished_at: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ToolStatus:
    name: str
    path: str
    available: bool
    version: str
    note: str = ""


@dataclass(frozen=True)
class LocalRepository:
    path: str
    name: str
    branch: str
    head: str
    last_commit_at: str
    dirty: bool
    remotes: Mapping[str, tuple[str, ...]]
    canonical_remote: str
    github_slug: str
    huggingface_slug: str
    platform: str
    relevance_score: int
    relevance_reasons: tuple[str, ...]
    product_manifest: str
    product_id: str

    def as_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["remotes"] = {name: list(urls) for name, urls in self.remotes.items()}
        payload["relevance_reasons"] = list(self.relevance_reasons)
        return payload


@dataclass
class BootstrapContext:
    project: Project
    config: Mapping[str, Any]
    output_dir: Path
    command_results: list[CommandResult] = field(default_factory=list)

    @property
    def root(self) -> Path:
        return self.project.root

    @property
    def max_output_bytes(self) -> int:
        raw = self.config.get("bootstrap", {}).get("max_command_output_bytes", 20_000)
        return max(1_000, int(raw))


_SECRET_PATTERNS = (
    re.compile(r"(?i)(token|password|secret|authorization)=([^\s]+)"),
    re.compile(r"(?i)^(gh[pousr]_[A-Za-z0-9_]+|hf_[A-Za-z0-9]+)$"),
)
_REMOTE_PATTERNS = (
    re.compile(r"^(?:https?://|ssh://git@|git@)(github\.com)[/:]([^/]+)/([^/]+?)(?:\.git)?$"),
    re.compile(
        r"^(?:https?://|ssh://git@|git@)(huggingface\.co)[/:](?:(datasets|spaces)/)?([^/]+)/([^/]+?)(?:\.git)?$"
    ),
)
_GIT_SKIP_DEFAULTS = frozenset(
    {
        ".cache",
        ".git",
        ".hg",
        ".svn",
        ".tox",
        ".venv",
        "__pycache__",
        "Applications",
        "Library",
        "node_modules",
        "site-packages",
        "target",
    }
)


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _truncate(value: str, limit: int) -> str:
    encoded = value.encode("utf-8", errors="replace")
    if len(encoded) <= limit:
        return value
    prefix = encoded[:limit].decode("utf-8", errors="replace")
    return prefix + f"\n...[truncated {len(encoded) - limit} bytes]"


def redact_argument(value: str) -> str:
    if value.startswith(("GH_TOKEN=", "GITHUB_TOKEN=", "HF_TOKEN=")):
        return value.split("=", 1)[0] + "=<redacted>"
    for pattern in _SECRET_PATTERNS:
        if pattern.match(value):
            return "<redacted>"
        value = pattern.sub(lambda match: f"{match.group(1)}=<redacted>", value)
    return value


def run_command(
    context: BootstrapContext,
    arguments: Sequence[str],
    *,
    cwd: Path | None = None,
    timeout: int = 120,
    check: bool = False,
    env: Mapping[str, str] | None = None,
) -> CommandResult:
    """Run a command without a shell and retain a redacted bounded receipt."""

    if not arguments:
        raise BootstrapError("Cannot execute an empty command")
    started_at = utc_now()
    effective_env = os.environ.copy()
    if env:
        effective_env.update(env)
    try:
        completed = subprocess.run(  # noqa: S603 - arguments are explicit and shell is disabled
            list(arguments),
            cwd=str(cwd or context.root),
            env=effective_env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )
        returncode = completed.returncode
        stdout = _truncate(completed.stdout, context.max_output_bytes)
        stderr = _truncate(completed.stderr, context.max_output_bytes)
    except FileNotFoundError as exc:
        returncode = 127
        stdout = ""
        stderr = str(exc)
    except subprocess.TimeoutExpired as exc:
        returncode = 124
        stdout = _truncate(str(exc.stdout or ""), context.max_output_bytes)
        stderr = _truncate(
            str(exc.stderr or "") + f"\nTimed out after {timeout}s", context.max_output_bytes
        )

    result = CommandResult(
        command=tuple(redact_argument(str(part)) for part in arguments),
        cwd=str((cwd or context.root).resolve()),
        returncode=returncode,
        stdout=stdout,
        stderr=stderr,
        started_at=started_at,
        finished_at=utc_now(),
    )
    context.command_results.append(result)
    if check and not result.ok:
        message = result.stderr.strip() or result.stdout.strip() or f"exit code {result.returncode}"
        raise BootstrapError(f"Command failed: {' '.join(result.command)}\n{message}")
    return result


def load_bootstrap_config(project: Project) -> dict[str, Any]:
    path = project.root / "config" / "bootstrap.toml"
    if not path.is_file():
        raise BootstrapError(f"Missing bootstrap configuration: {path}")
    with path.open("rb") as handle:
        config = tomllib.load(handle)
    version = str(config.get("bootstrap", {}).get("schema_version", ""))
    if version != "1.0":
        raise BootstrapError(f"Unsupported bootstrap schema version {version!r}")
    return config


def create_context(project: Project, output: Path | None = None) -> BootstrapContext:
    config = load_bootstrap_config(project)
    configured = Path(str(config.get("bootstrap", {}).get("receipt_directory", "build/bootstrap")))
    output_dir = output or (configured if configured.is_absolute() else project.root / configured)
    output_dir.mkdir(parents=True, exist_ok=True)
    return BootstrapContext(project=project, config=config, output_dir=output_dir.resolve())


def tool_status(context: BootstrapContext, name: str, version_args: Sequence[str]) -> ToolStatus:
    path = shutil.which(name)
    if not path:
        return ToolStatus(name=name, path="", available=False, version="", note="not found on PATH")
    result = run_command(context, [name, *version_args], timeout=30)
    combined = (result.stdout.strip() or result.stderr.strip()).splitlines()
    version = combined[0].strip() if combined else "unknown"
    # Some CLI frameworks print their version and then incorrectly return non-zero. Presence plus
    # a version line is sufficient for preflight; actual commands are independently checked.
    return ToolStatus(
        name=name,
        path=path,
        available=True,
        version=version,
        note="" if result.ok else f"version probe returned {result.returncode}",
    )


def preflight(context: BootstrapContext) -> dict[str, Any]:
    tools = {
        "python": ToolStatus(
            name="python",
            path=sys.executable,
            available=True,
            version=sys.version.split()[0],
        ),
        "git": tool_status(context, "git", ["--version"]),
        "gh": tool_status(context, "gh", ["--version"]),
        "hf": tool_status(context, "hf", ["version"]),
    }
    root = context.root
    return {
        "tools": {name: asdict(status) for name, status in tools.items()},
        "repository_root_exists": root.is_dir(),
        "project_config_exists": (root / "config" / "project.toml").is_file(),
        "manifest_exists": (root / "MANIFEST.sha256").is_file(),
        "already_git_repository": (root / ".git").exists(),
        "filesystem": {
            "root": str(root),
            "writable": os.access(root, os.W_OK),
            "output_directory": str(context.output_dir),
        },
    }


def _git_output(context: BootstrapContext, repository: Path, *arguments: str) -> str:
    result = run_command(context, ["git", "-C", str(repository), *arguments], timeout=30)
    return result.stdout.strip() if result.ok else ""


def _parse_remote_identity(url: str) -> tuple[str, str, str]:
    clean = url.strip().rstrip("/")
    if clean.startswith("git://"):
        clean = "https://" + clean[len("git://") :]
    for pattern in _REMOTE_PATTERNS:
        match = pattern.match(clean)
        if not match:
            continue
        host = match.group(1).lower()
        if host == "github.com":
            owner, repo = match.group(2), match.group(3)
            return "github", f"{owner}/{repo.removesuffix('.git')}", ""
        repo_type = match.group(2) or "model"
        owner, repo = match.group(3), match.group(4)
        kind = {"datasets": "dataset", "spaces": "space"}.get(repo_type, repo_type)
        return "huggingface", "", f"{kind}:{owner}/{repo.removesuffix('.git')}"
    return "", "", ""


def normalise_remote_url(url: str) -> str:
    platform, github_slug, hf_slug = _parse_remote_identity(url)
    if platform == "github":
        return f"github:{github_slug.lower()}"
    if platform == "huggingface":
        return f"huggingface:{hf_slug.lower()}"
    return url.strip().removesuffix(".git").rstrip("/").lower()


def default_scan_roots(repository_root: Path) -> list[Path]:
    home = Path.home()
    candidates = [
        repository_root.parent,
        home / "Developer",
        home / "dev",
        home / "src",
        home / "code",
        home / "repos",
        home / "projects",
        home / "Documents" / "GitHub",
    ]
    roots: list[Path] = []
    seen: set[Path] = set()
    for candidate in candidates:
        try:
            resolved = candidate.expanduser().resolve()
        except OSError:
            continue
        if resolved.is_dir() and resolved not in seen:
            roots.append(resolved)
            seen.add(resolved)
    return roots


def _walk_candidate_repositories(
    roots: Iterable[Path],
    *,
    max_depth: int,
    max_repositories: int,
    include_hidden: bool,
    exclusions: set[str],
) -> list[Path]:
    found: list[Path] = []
    seen: set[Path] = set()
    queue: deque[tuple[Path, int]] = deque((root, 0) for root in roots)
    while queue and len(found) < max_repositories:
        current, depth = queue.popleft()
        try:
            resolved = current.resolve()
        except OSError:
            continue
        if resolved in seen:
            continue
        seen.add(resolved)
        if (resolved / ".git").exists():
            found.append(resolved)
            continue
        if depth >= max_depth:
            continue
        try:
            entries = sorted(os.scandir(resolved), key=lambda entry: entry.name.casefold())
        except (OSError, PermissionError):
            continue
        for entry in entries:
            if not entry.is_dir(follow_symlinks=False):
                continue
            if entry.name in exclusions:
                continue
            if not include_hidden and entry.name.startswith("."):
                continue
            queue.append((Path(entry.path), depth + 1))
    return found


def _repository_remotes(context: BootstrapContext, repository: Path) -> dict[str, tuple[str, ...]]:
    result = run_command(
        context,
        ["git", "-C", str(repository), "config", "--get-regexp", r"^remote\..*\.url$"],
        timeout=30,
    )
    values: dict[str, list[str]] = defaultdict(list)
    if result.ok:
        for line in result.stdout.splitlines():
            if not line.strip() or " " not in line:
                continue
            key, url = line.split(None, 1)
            parts = key.split(".")
            if len(parts) >= 3:
                values[parts[1]].append(url.strip())
    return {name: tuple(urls) for name, urls in sorted(values.items())}


def _score_repository(
    repository: Path,
    remotes: Mapping[str, tuple[str, ...]],
    keywords: Sequence[str],
    current_root: Path,
) -> tuple[int, tuple[str, ...]]:
    score = 0
    reasons: list[str] = []
    searchable = " ".join(
        [
            repository.name,
            repository.as_posix(),
            *(url for urls in remotes.values() for url in urls),
        ]
    ).lower()
    for keyword in keywords:
        if keyword.lower() in searchable:
            score += 2 if len(keyword) > 3 else 1
            reasons.append(f"keyword:{keyword}")
    product_manifest = repository / ".gfjd" / "product.toml"
    if product_manifest.is_file():
        score += 15
        reasons.append("gfjd-product-manifest")
    if (repository / "config" / "project.toml").is_file():
        try:
            with (repository / "config" / "project.toml").open("rb") as handle:
                payload = tomllib.load(handle)
            if str(payload.get("project", {}).get("id", "")) == "GFJD":
                score += 25
                reasons.append("gfjd-project-id")
        except (OSError, tomllib.TOMLDecodeError):
            pass
    if repository == current_root:
        score += 50
        reasons.append("current-repository")
    elif repository.parent == current_root.parent:
        score += 4
        reasons.append("sibling-repository")
    if (repository / "data").is_dir():
        score += 2
        reasons.append("data-directory")
    return score, tuple(dict.fromkeys(reasons))


def _product_id_from_manifest(path: Path) -> str:
    if not path.is_file():
        return ""
    try:
        with path.open("rb") as handle:
            payload = tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError):
        return ""
    return str(payload.get("product_id", "")).strip()


def inspect_local_repository(
    context: BootstrapContext,
    repository: Path,
    keywords: Sequence[str],
) -> LocalRepository | None:
    top = _git_output(context, repository, "rev-parse", "--show-toplevel")
    if not top:
        return None
    root = Path(top).resolve()
    remotes = _repository_remotes(context, root)
    canonical = ""
    if "origin" in remotes and remotes["origin"]:
        canonical = remotes["origin"][0]
    elif remotes:
        canonical = next(iter(remotes.values()))[0]
    platform, github_slug, hf_slug = _parse_remote_identity(canonical)
    branch = _git_output(context, root, "branch", "--show-current")
    head = _git_output(context, root, "rev-parse", "HEAD")
    last_commit_at = _git_output(context, root, "log", "-1", "--format=%cI")
    dirty = bool(_git_output(context, root, "status", "--porcelain=v1", "--untracked-files=normal"))
    score, reasons = _score_repository(root, remotes, keywords, context.root)
    product_manifest = root / ".gfjd" / "product.toml"
    return LocalRepository(
        path=str(root),
        name=root.name,
        branch=branch,
        head=head,
        last_commit_at=last_commit_at,
        dirty=dirty,
        remotes=remotes,
        canonical_remote=canonical,
        github_slug=github_slug,
        huggingface_slug=hf_slug,
        platform=platform,
        relevance_score=score,
        relevance_reasons=reasons,
        product_manifest=str(product_manifest) if product_manifest.is_file() else "",
        product_id=_product_id_from_manifest(product_manifest),
    )


def discover_local_repositories(
    context: BootstrapContext,
    roots: Sequence[Path] | None = None,
) -> list[LocalRepository]:
    discovery = context.config.get("discovery", {})
    max_depth = int(discovery.get("max_depth", 6))
    max_repositories = int(discovery.get("max_repositories", 1_000))
    include_hidden = bool(discovery.get("include_hidden", False))
    exclusions = set(str(item) for item in discovery.get("exclude_directories", []))
    exclusions.update(_GIT_SKIP_DEFAULTS)
    keywords = [str(item) for item in discovery.get("keywords", [])]
    scan_roots = list(roots) if roots else default_scan_roots(context.root)
    candidates = _walk_candidate_repositories(
        scan_roots,
        max_depth=max_depth,
        max_repositories=max_repositories,
        include_hidden=include_hidden,
        exclusions=exclusions,
    )
    repositories = [
        repository
        for candidate in candidates
        if (repository := inspect_local_repository(context, candidate, keywords)) is not None
    ]
    return sorted(
        repositories,
        key=lambda item: (-item.relevance_score, item.path.casefold()),
    )


def duplicate_remote_groups(repositories: Sequence[LocalRepository]) -> list[dict[str, Any]]:
    groups: dict[str, list[str]] = defaultdict(list)
    for repository in repositories:
        for urls in repository.remotes.values():
            for url in urls:
                groups[normalise_remote_url(url)].append(repository.path)
    return [
        {"remote": remote, "paths": sorted(set(paths))}
        for remote, paths in sorted(groups.items())
        if remote and len(set(paths)) > 1
    ]


def discover_github_account(context: BootstrapContext) -> dict[str, Any]:
    if not shutil.which("gh"):
        return {"available": False, "authenticated": False, "login": "", "organizations": []}
    status = run_command(context, ["gh", "auth", "status", "--json", "hosts"], timeout=45)
    auth_payload: Any = None
    if status.stdout.strip():
        try:
            auth_payload = json.loads(status.stdout)
        except json.JSONDecodeError:
            auth_payload = None
    login_result = run_command(context, ["gh", "api", "user", "--jq", ".login"], timeout=45)
    login = login_result.stdout.strip() if login_result.ok else ""
    org_result = run_command(
        context,
        ["gh", "api", "user/orgs", "--paginate", "--jq", ".[].login"],
        timeout=60,
    )
    organizations = sorted(
        {line.strip() for line in org_result.stdout.splitlines() if line.strip()}
    )
    return {
        "available": True,
        "authenticated": bool(login),
        "login": login,
        "organizations": organizations,
        "auth_status": auth_payload,
    }


def discover_huggingface_account(context: BootstrapContext) -> dict[str, Any]:
    if not shutil.which("hf"):
        return {"available": False, "authenticated": False, "username": "", "organizations": []}
    result = run_command(context, ["hf", "auth", "whoami", "--format", "json"], timeout=45)
    username = ""
    organizations: list[str] = []
    parsed: Any = None
    if result.stdout.strip():
        try:
            parsed = json.loads(result.stdout)
        except json.JSONDecodeError:
            parsed = None
    if result.ok and isinstance(parsed, dict):
        username = str(
            parsed.get("name")
            or parsed.get("username")
            or parsed.get("user")
            or parsed.get("id")
            or ""
        ).strip()
        raw_orgs = parsed.get("orgs", parsed.get("organizations", []))
        if isinstance(raw_orgs, list):
            for item in raw_orgs:
                if isinstance(item, dict):
                    value = item.get("name") or item.get("id") or item.get("username")
                else:
                    value = item
                if value:
                    organizations.append(str(value).strip())
    if not username:
        # Compatibility fallback for older CLI versions without structured output.
        fallback = run_command(context, ["hf", "auth", "whoami"], timeout=45)
        lines = [line.strip() for line in fallback.stdout.splitlines() if line.strip()]
        if fallback.ok and lines:
            first = lines[0]
            username = (
                first.split(":", 1)[1].strip()
                if first.lower().startswith(("user:", "username:"))
                else first
            )
            for line in lines[1:]:
                if line.lower().startswith(("orgs:", "organizations:")):
                    organizations.extend(
                        part.strip() for part in line.split(":", 1)[1].split(",") if part.strip()
                    )
    return {
        "available": True,
        "authenticated": bool(username),
        "username": username,
        "organizations": sorted(set(organizations)),
        "raw": parsed if isinstance(parsed, dict) else [],
    }


def list_github_repositories(context: BootstrapContext, owner: str) -> list[dict[str, Any]]:
    if not owner or not shutil.which("gh"):
        return []
    fields = "name,nameWithOwner,url,visibility,isPrivate,isArchived,defaultBranchRef,updatedAt"
    result = run_command(
        context,
        [
            "gh",
            "repo",
            "list",
            owner,
            "--limit",
            "1000",
            "--json",
            fields,
            "--source",
        ],
        timeout=180,
    )
    if not result.ok:
        return []
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        return []
    return payload if isinstance(payload, list) else []


def _json_object_list(value: str) -> list[dict[str, Any]]:
    """Return a conservative list of JSON objects from CLI output."""

    try:
        payload = json.loads(value)
    except json.JSONDecodeError:
        return []
    if isinstance(payload, dict):
        for key in ("items", "repositories", "results", "data"):
            candidate = payload.get(key)
            if isinstance(candidate, list):
                payload = candidate
                break
    if not isinstance(payload, list):
        return []
    return [item for item in payload if isinstance(item, dict)]


def list_huggingface_repositories(
    context: BootstrapContext, namespace: str
) -> list[dict[str, Any]]:
    """List Hub repositories across current and recent ``hf`` CLI layouts.

    ``hf repos ls`` is preferred.  Recent older releases expose type-specific
    ``models|datasets|spaces ls`` commands instead, so the fallback preserves
    discovery rather than treating a CLI-version difference as an empty estate.
    """

    if not namespace or not shutil.which("hf"):
        return []
    result = run_command(
        context,
        [
            "hf",
            "repos",
            "ls",
            "--namespace",
            namespace,
            "--limit",
            "0",
            "--format",
            "json",
        ],
        timeout=180,
    )
    repositories = _json_object_list(result.stdout) if result.ok else []
    if repositories:
        return repositories

    discovered: list[dict[str, Any]] = []
    for plural, repo_type in (("models", "model"), ("datasets", "dataset"), ("spaces", "space")):
        fallback = run_command(
            context,
            [
                "hf",
                plural,
                "ls",
                "--author",
                namespace,
                "--limit",
                "1000",
                "--format",
                "json",
            ],
            timeout=180,
        )
        if not fallback.ok:
            continue
        for item in _json_object_list(fallback.stdout):
            enriched = dict(item)
            enriched.setdefault("repo_type", repo_type)
            discovered.append(enriched)
    return discovered


def _action(
    action_id: str,
    description: str,
    *,
    mutating: bool,
    status: str,
    command: Sequence[str] | None = None,
    reason: str = "",
) -> dict[str, Any]:
    return {
        "id": action_id,
        "description": description,
        "mutating": mutating,
        "status": status,
        "command": [redact_argument(str(value)) for value in (command or ())],
        "reason": reason,
    }


def _existing_origin(context: BootstrapContext) -> str:
    if not (context.root / ".git").exists():
        return ""
    return _git_output(context, context.root, "remote", "get-url", "origin")


def _repository_name(value: str) -> str:
    cleaned = value.strip().rstrip("/")
    return cleaned.rsplit("/", 1)[-1].removesuffix(".git") if cleaned else ""


def _inventory_identity(item: Mapping[str, Any]) -> str:
    for key in ("nameWithOwner", "id", "repo_id", "modelId", "name"):
        value = str(item.get(key, "")).strip()
        if value:
            return value
    return ""


def build_portfolio_reconciliation(
    context: BootstrapContext,
    *,
    local_repositories: Sequence[LocalRepository],
    github_repositories: Sequence[Mapping[str, Any]],
    huggingface_repositories: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Relate declared products to bounded local and platform inventories.

    This is advisory evidence, not an automatic canonicalisation decision.  An
    explicit ``local_path`` declaration is reported as the preferred source
    tree, while all matching clones and remotes remain visible for review.
    """

    registry_path = context.root / "portfolio" / "products.toml"
    try:
        with registry_path.open("rb") as handle:
            registry = tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        return {
            "schema_version": "1.0",
            "registry_path": str(registry_path),
            "products": [],
            "unresolved_products": [],
            "warnings": [f"Could not load portfolio registry: {exc}"],
        }

    products = registry.get("products", [])
    if not isinstance(products, list):
        products = []
    reconciled: list[dict[str, Any]] = []
    unresolved: list[str] = []
    warnings: list[str] = []
    for raw in products:
        if not isinstance(raw, dict):
            continue
        product_id = str(raw.get("id", "")).strip()
        declared_github = str(raw.get("repository", "")).strip()
        declared_hf = str(raw.get("huggingface_repository", "")).strip()
        github_name = _repository_name(declared_github)
        hf_name = _repository_name(declared_hf)
        expected_names = {name.casefold() for name in (github_name, hf_name) if name}
        local_path_value = str(raw.get("local_path", "")).strip()
        declared_local = ""
        if local_path_value:
            candidate = Path(local_path_value).expanduser()
            if not candidate.is_absolute():
                candidate = context.root / candidate
            try:
                declared_local = str(candidate.resolve())
            except OSError:
                declared_local = str(candidate)

        local_matches: list[dict[str, Any]] = []
        seen_paths: set[str] = set()
        for repository in local_repositories:
            reasons: list[str] = []
            if product_id and repository.product_id == product_id:
                reasons.append("product_manifest_id")
            if declared_local and repository.path == declared_local:
                reasons.append("declared_local_path")
            if repository.name.casefold() in expected_names:
                reasons.append("repository_name")
            if (
                repository.github_slug
                and _repository_name(repository.github_slug).casefold() in expected_names
            ):
                reasons.append("github_remote_name")
            if (
                repository.huggingface_slug
                and _repository_name(repository.huggingface_slug).casefold() in expected_names
            ):
                reasons.append("huggingface_remote_name")
            if not reasons:
                continue
            seen_paths.add(repository.path)
            local_matches.append(
                {
                    "path": repository.path,
                    "product_id": repository.product_id,
                    "canonical_remote": repository.canonical_remote,
                    "dirty": repository.dirty,
                    "head": repository.head,
                    "reasons": reasons,
                    "declared_preferred": repository.path == declared_local,
                }
            )
        if declared_local and declared_local not in seen_paths and Path(declared_local).is_dir():
            local_matches.insert(
                0,
                {
                    "path": declared_local,
                    "product_id": product_id
                    if declared_local == str(context.root.resolve())
                    else "",
                    "canonical_remote": "",
                    "dirty": False,
                    "head": "",
                    "reasons": ["declared_local_path", "not_yet_a_git_clone"],
                    "declared_preferred": True,
                },
            )

        github_matches = [
            dict(item)
            for item in github_repositories
            if _repository_name(_inventory_identity(item)).casefold() == github_name.casefold()
            and github_name
        ]
        hf_matches = [
            dict(item)
            for item in huggingface_repositories
            if _repository_name(_inventory_identity(item)).casefold() == hf_name.casefold()
            and hf_name
        ]
        preferred = [item for item in local_matches if item["declared_preferred"]]
        if len(preferred) == 1:
            status = "declared_local_identified"
        elif len(preferred) > 1:
            status = "ambiguous_declared_local"
        elif len(local_matches) == 1:
            status = "single_local_candidate"
        elif len(local_matches) > 1:
            status = "multiple_local_candidates"
        elif github_matches or hf_matches:
            status = "remote_only"
        else:
            status = "unresolved"
            if product_id:
                unresolved.append(product_id)
        if len(local_matches) > 1:
            warnings.append(
                f"Product {product_id or '<unknown>'} has {len(local_matches)} local candidates; "
                "do not delete or rewire any candidate without review."
            )
        reconciled.append(
            {
                "product_id": product_id,
                "product_class": str(raw.get("class", "")),
                "status": status,
                "declared_local_path": declared_local,
                "declared_github_repository": declared_github,
                "declared_huggingface_repository": declared_hf,
                "local_candidates": local_matches,
                "github_candidates": github_matches,
                "huggingface_candidates": hf_matches,
            }
        )
    return {
        "schema_version": "1.0",
        "registry_path": str(registry_path),
        "products": reconciled,
        "unresolved_products": unresolved,
        "warnings": warnings,
    }


def build_plan(
    context: BootstrapContext,
    *,
    scan_roots: Sequence[Path] | None = None,
    github_owner: str = "",
    github_repository: str = "",
    huggingface_namespace: str = "",
    mode: str = "plan",
) -> dict[str, Any]:
    preflight_payload = preflight(context)
    github_account = discover_github_account(context)
    huggingface_account = discover_huggingface_account(context)
    github_config = context.config.get("github", {})
    hf_config = context.config.get("huggingface", {})
    inferred_owner = (
        github_owner or str(github_config.get("owner", "")) or str(github_account.get("login", ""))
    )
    repository_name = github_repository or str(
        github_config.get(
            "repository",
            context.config.get("bootstrap", {}).get("repository_name", context.root.name),
        )
    )
    inferred_hf_namespace = (
        huggingface_namespace
        or str(hf_config.get("namespace", ""))
        or str(huggingface_account.get("username", ""))
    )
    local_repositories = discover_local_repositories(context, roots=scan_roots)
    existing_origin = _existing_origin(context)
    actions: list[dict[str, Any]] = []
    actions.append(
        _action(
            "verify-manifest",
            "Verify the source-tree checksum manifest before mutation.",
            mutating=False,
            status="required",
            command=[sys.executable, "-m", "gfjd.manifest", "--verify"],
        )
    )
    if not (context.root / ".git").exists():
        actions.append(
            _action(
                "initialise-git",
                "Initialise a Git repository with the configured default branch.",
                mutating=True,
                status="planned",
                command=["git", "init", "-b", str(context.config["bootstrap"]["default_branch"])],
            )
        )
    else:
        actions.append(
            _action(
                "initialise-git",
                "Use the existing local Git repository.",
                mutating=False,
                status="already_satisfied",
            )
        )
    actions.append(
        _action(
            "configure-git",
            "Apply repository-local safety and collaboration defaults.",
            mutating=True,
            status="planned",
        )
    )
    actions.append(
        _action(
            "initial-commit",
            "Create a commit only when the working tree has uncommitted content.",
            mutating=True,
            status="planned",
        )
    )
    github_slug = f"{inferred_owner}/{repository_name}" if inferred_owner else ""
    if existing_origin:
        actions.append(
            _action(
                "wire-github-remote",
                f"Retain and verify existing origin {existing_origin}.",
                mutating=False,
                status="already_satisfied",
            )
        )
    elif github_slug:
        visibility = str(github_config.get("visibility", "private"))
        actions.append(
            _action(
                "create-github-remote",
                f"Create or attach GitHub repository {github_slug} as origin; "
                f"default visibility is {visibility}.",
                mutating=True,
                status="planned",
                command=[
                    "gh",
                    "repo",
                    "create",
                    github_slug,
                    f"--{visibility}",
                    "--source",
                    ".",
                    "--remote",
                    "origin",
                ],
            )
        )
    else:
        actions.append(
            _action(
                "create-github-remote",
                "Create or attach the GitHub origin.",
                mutating=True,
                status="blocked",
                reason="No GitHub owner is configured or discoverable.",
            )
        )
    actions.append(
        _action(
            "push-main",
            "Push the local default branch without force and verify local/remote commit identity.",
            mutating=True,
            status="planned" if github_slug or existing_origin else "blocked",
        )
    )
    actions.append(
        _action(
            "apply-github-controls",
            "Apply repository features and produce a desired-versus-observed controls report.",
            mutating=True,
            status="opt_in",
        )
    )
    configured_hf = list(hf_config.get("repositories", []))
    for entry in configured_hf:
        name = str(entry.get("name", ""))
        repo_type = str(entry.get("repo_type", "dataset"))
        full_name = f"{inferred_hf_namespace}/{name}" if inferred_hf_namespace else name
        actions.append(
            _action(
                f"create-hf-{entry.get('id', name)}",
                f"Create missing private Hugging Face {repo_type} repository {full_name}.",
                mutating=True,
                status="opt_in" if inferred_hf_namespace else "blocked",
                command=[
                    "hf",
                    "repos",
                    "create",
                    full_name,
                    "--repo-type",
                    repo_type,
                    "--private",
                    "--exist-ok",
                ],
                reason="No Hugging Face namespace is configured or discoverable."
                if not inferred_hf_namespace
                else "",
            )
        )
    warnings: list[str] = []
    if not preflight_payload["tools"]["git"]["available"]:
        warnings.append("Git is not available; local repository initialisation cannot proceed.")
    if not github_account.get("authenticated"):
        warnings.append("GitHub CLI is not authenticated; remote creation will remain blocked.")
    if hf_config.get("enabled", True) and not huggingface_account.get("authenticated"):
        warnings.append(
            "Hugging Face CLI is not authenticated; Hub inventory/creation will remain blocked."
        )
    if existing_origin and github_slug:
        expected = normalise_remote_url(f"https://github.com/{github_slug}.git")
        observed = normalise_remote_url(existing_origin)
        if expected != observed:
            warnings.append(
                f"Existing origin {existing_origin!r} does not match configured "
                f"GitHub repository {github_slug!r}."
            )
    github_repositories = list_github_repositories(context, inferred_owner)
    hf_repositories = list_huggingface_repositories(context, inferred_hf_namespace)
    portfolio_reconciliation = build_portfolio_reconciliation(
        context,
        local_repositories=local_repositories,
        github_repositories=github_repositories,
        huggingface_repositories=hf_repositories,
    )
    warnings.extend(str(item) for item in portfolio_reconciliation.get("warnings", []))
    return {
        "schema_version": "1.0",
        "generated_at": utc_now(),
        "repository_root": str(context.root),
        "mode": mode,
        "preflight": preflight_payload,
        "accounts": {
            "github": github_account,
            "huggingface": huggingface_account,
            "resolved": {
                "github_owner": inferred_owner,
                "github_repository": repository_name,
                "github_slug": github_slug,
                "huggingface_namespace": inferred_hf_namespace,
            },
        },
        "remote_inventory": {
            "github": github_repositories,
            "huggingface": hf_repositories,
        },
        "local_repositories": [repository.as_dict() for repository in local_repositories],
        "duplicate_remote_groups": duplicate_remote_groups(local_repositories),
        "portfolio_reconciliation": portfolio_reconciliation,
        "actions": actions,
        "warnings": warnings,
    }


def validate_bootstrap_plan(context: BootstrapContext, plan: Mapping[str, Any]) -> None:
    """Validate the discovery/apply plan against the bundled public contract."""

    schema_path = context.root / "schemas" / "bootstrap_plan.schema.json"
    try:
        schema = read_json(schema_path)
    except (OSError, ValueError) as exc:
        raise BootstrapError(f"Could not load bootstrap-plan schema: {exc}") from exc
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(dict(plan)),
        key=lambda error: list(error.path),
    )
    if errors:
        rendered = "; ".join(
            f"{'.'.join(map(str, error.path)) or '<root>'}: {error.message}" for error in errors
        )
        raise BootstrapError(f"Bootstrap plan failed schema validation: {rendered}")


def _json_bytes(payload: Any) -> bytes:
    return (json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode(
        "utf-8"
    )


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
        handle.write(data)
        temporary = Path(handle.name)
    temporary.replace(path)


def render_plan_markdown(plan: Mapping[str, Any]) -> str:
    resolved = plan["accounts"]["resolved"]
    lines = [
        "# GFJD bootstrap plan",
        "",
        f"Generated: `{plan['generated_at']}`",
        f"Repository root: `{plan['repository_root']}`",
        f"GitHub target: `{resolved.get('github_slug') or 'unresolved'}`",
        f"Hugging Face namespace: `{resolved.get('huggingface_namespace') or 'unresolved'}`",
        "",
        "## Planned actions",
        "",
        "| Action | Status | Mutating | Description |",
        "|---|---|---:|---|",
    ]
    for action in plan["actions"]:
        description = str(action["description"]).replace("|", "\\|")
        mutating = "yes" if action["mutating"] else "no"
        lines.append(f"| `{action['id']}` | {action['status']} | {mutating} | {description} |")
    lines.extend(["", "## Relevant local repositories", ""])
    repositories = plan["local_repositories"]
    if repositories:
        lines.extend(
            [
                "| Score | Repository | Branch | Dirty | Remote |",
                "|---:|---|---|---:|---|",
            ]
        )
        for repository in repositories[:100]:
            lines.append(
                f"| {repository['relevance_score']} | `{repository['path']}` | "
                f"`{repository['branch'] or '(detached/unborn)'}` | "
                f"{'yes' if repository['dirty'] else 'no'} | "
                f"`{repository['canonical_remote'] or ''}` |"
            )
    else:
        lines.append("No local Git repositories were found within the bounded scan roots.")
    lines.extend(["", "## Portfolio reconciliation", ""])
    portfolio = plan.get("portfolio_reconciliation", {})
    products = portfolio.get("products", []) if isinstance(portfolio, dict) else []
    if products:
        lines.extend(
            [
                "| Product | Status | Preferred/candidate local paths | "
                "GitHub matches | Hugging Face matches |",
                "|---|---|---|---:|---:|",
            ]
        )
        for product in products:
            local_candidates = product.get("local_candidates", [])
            local_text = (
                "<br>".join(
                    f"`{item.get('path', '')}`"
                    + (" (declared)" if item.get("declared_preferred") else "")
                    for item in local_candidates[:5]
                )
                or "—"
            )
            lines.append(
                f"| `{product.get('product_id', '')}` | {product.get('status', '')} | "
                f"{local_text} | {len(product.get('github_candidates', []))} | "
                f"{len(product.get('huggingface_candidates', []))} |"
            )
    else:
        lines.append("No portfolio declarations could be reconciled.")
    lines.extend(["", "## Warnings", ""])
    warnings = plan["warnings"]
    lines.extend(f"- {warning}" for warning in warnings)
    if not warnings:
        lines.append("No bootstrap warnings were generated.")
    lines.extend(
        [
            "",
            "## Safety boundary",
            "",
            "The plan does not mutate any remote. `apply` requires explicit confirmation. The "
            "bootstrap never force-pushes, never deletes a remote repository, and never treats a "
            "discovered clone as canonical without an explicit configuration decision.",
            "",
        ]
    )
    return "\n".join(lines)


def write_plan(context: BootstrapContext, plan: Mapping[str, Any]) -> dict[str, str]:
    validate_bootstrap_plan(context, plan)
    json_path = context.output_dir / "bootstrap-plan.json"
    markdown_path = context.output_dir / "bootstrap-plan.md"
    local_path = context.output_dir / "local-repositories.json"
    commands_path = context.output_dir / "discovery-commands.json"
    portfolio_path = context.output_dir / "portfolio-reconciliation.json"
    atomic_write(json_path, _json_bytes(plan))
    atomic_write(markdown_path, (render_plan_markdown(plan) + "\n").encode("utf-8"))
    atomic_write(local_path, _json_bytes(plan["local_repositories"]))
    atomic_write(
        commands_path, _json_bytes([result.as_dict() for result in context.command_results])
    )
    atomic_write(portfolio_path, _json_bytes(plan["portfolio_reconciliation"]))
    return {
        "plan_json": str(json_path),
        "plan_markdown": str(markdown_path),
        "local_repositories": str(local_path),
        "command_receipts": str(commands_path),
        "portfolio_reconciliation": str(portfolio_path),
    }


def verify_repository_manifest(context: BootstrapContext) -> None:
    result = run_command(
        context,
        [sys.executable, "-m", "gfjd.manifest", "--verify"],
        cwd=context.root,
        timeout=120,
        check=True,
        env={"PYTHONPATH": str(context.root / "src")},
    )
    if "verified" not in result.stdout.lower():
        raise BootstrapError("Repository manifest command did not report successful verification")


def _git_config(context: BootstrapContext, key: str, value: str) -> None:
    run_command(
        context,
        ["git", "-C", str(context.root), "config", "--local", key, value],
        check=True,
    )


def initialise_git_repository(
    context: BootstrapContext,
    *,
    author_name: str,
    author_email: str,
) -> dict[str, Any]:
    if not shutil.which("git"):
        raise BootstrapError("Git is required but was not found on PATH")
    branch = str(context.config["bootstrap"].get("default_branch", "main"))
    created = False
    if not (context.root / ".git").exists():
        run_command(context, ["git", "init", "-b", branch], cwd=context.root, check=True)
        created = True
    git_config = context.config.get("git", {})
    _git_config(context, "pull.ff", str(git_config.get("pull_ff", "only")))
    _git_config(context, "fetch.prune", str(bool(git_config.get("fetch_prune", True))).lower())
    _git_config(
        context,
        "rerere.enabled",
        str(bool(git_config.get("rerere_enabled", True))).lower(),
    )
    _git_config(context, "core.autocrlf", str(git_config.get("autocrlf", "input")))
    _git_config(
        context,
        "commit.gpgsign",
        str(bool(git_config.get("commit_gpgsign", False))).lower(),
    )
    if author_name:
        _git_config(context, "user.name", author_name)
    if author_email:
        _git_config(context, "user.email", author_email)
    return {"created": created, "branch": branch}


def ensure_commit(context: BootstrapContext, message: str) -> dict[str, Any]:
    run_command(context, ["git", "-C", str(context.root), "add", "--all"], check=True)
    diff = run_command(
        context,
        ["git", "-C", str(context.root), "diff", "--cached", "--quiet"],
        timeout=30,
    )
    created = False
    if diff.returncode == 1:
        run_command(
            context,
            ["git", "-C", str(context.root), "commit", "-m", message],
            timeout=180,
            check=True,
        )
        created = True
    elif diff.returncode != 0:
        raise BootstrapError("Could not determine whether the index contains changes")
    head = _git_output(context, context.root, "rev-parse", "HEAD")
    if not head:
        raise BootstrapError("No Git commit exists after bootstrap commit step")
    return {"created": created, "head": head}


def _github_repository_exists(context: BootstrapContext, slug: str) -> dict[str, Any] | None:
    result = run_command(
        context,
        [
            "gh",
            "repo",
            "view",
            slug,
            "--json",
            "nameWithOwner,url,sshUrl,visibility,isPrivate,defaultBranchRef",
        ],
        timeout=60,
    )
    if not result.ok:
        return None
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, dict) else None


def ensure_github_remote(
    context: BootstrapContext,
    *,
    owner: str,
    repository: str,
    visibility: str,
    push: bool,
) -> dict[str, Any]:
    if not shutil.which("gh"):
        raise BootstrapError("GitHub CLI `gh` is required for remote creation")
    if visibility not in {"private", "public", "internal"}:
        raise BootstrapError(f"Unsupported GitHub visibility {visibility!r}")
    account = discover_github_account(context)
    if not account.get("authenticated"):
        raise BootstrapError("GitHub CLI is not authenticated; run `gh auth login` first")
    slug = f"{owner}/{repository}"
    remote_name = str(context.config["bootstrap"].get("remote_name", "origin"))
    existing_origin = _git_output(context, context.root, "remote", "get-url", remote_name)
    remote_payload = _github_repository_exists(context, slug)
    created = False
    if remote_payload is None:
        command = [
            "gh",
            "repo",
            "create",
            slug,
            f"--{visibility}",
            "--description",
            str(context.config["bootstrap"].get("description", "")),
            "--source",
            str(context.root),
            "--remote",
            remote_name,
            "--disable-wiki",
        ]
        run_command(context, command, cwd=context.root, timeout=180, check=True)
        created = True
        remote_payload = _github_repository_exists(context, slug)
        if remote_payload is None:
            raise BootstrapError(f"GitHub reported creation but {slug} cannot be inspected")
        # ``gh repo create --source --remote`` normally creates the remote itself.
        # Refresh the observed value before deciding whether a manual ``remote add``
        # is needed; otherwise a successful create would be followed by a false
        # "remote already exists" failure.
        existing_origin = _git_output(context, context.root, "remote", "get-url", remote_name)
    expected_urls = {
        str(remote_payload.get("url", "")),
        str(remote_payload.get("sshUrl", "")),
    }
    if existing_origin:
        if normalise_remote_url(existing_origin) != normalise_remote_url(
            str(remote_payload.get("url", ""))
        ):
            raise BootstrapError(
                f"Existing {remote_name} {existing_origin!r} does not match target {slug}; "
                "bootstrap will not rewrite it automatically"
            )
    else:
        remote_url = str(remote_payload.get("url", ""))
        if not remote_url:
            raise BootstrapError(f"No clone URL returned for {slug}")
        run_command(
            context,
            ["git", "-C", str(context.root), "remote", "add", remote_name, remote_url],
            check=True,
        )
    if push:
        branch = str(context.config["bootstrap"].get("default_branch", "main"))
        run_command(
            context,
            ["git", "-C", str(context.root), "push", "--set-upstream", remote_name, branch],
            timeout=300,
            check=True,
        )
        local_head = _git_output(context, context.root, "rev-parse", "HEAD")
        remote_head = _git_output(
            context, context.root, "ls-remote", remote_name, f"refs/heads/{branch}"
        )
        remote_sha = remote_head.split()[0] if remote_head else ""
        if not local_head or local_head != remote_sha:
            raise BootstrapError(
                f"Remote verification failed: local HEAD {local_head!r}, remote HEAD {remote_sha!r}"
            )
    return {
        "slug": slug,
        "created": created,
        "pushed": push,
        "url": str(remote_payload.get("url", "")),
        "accepted_clone_urls": sorted(url for url in expected_urls if url),
    }


def apply_github_repository_settings(context: BootstrapContext, slug: str) -> dict[str, Any]:
    github = context.config.get("github", {})
    command = [
        "gh",
        "repo",
        "edit",
        slug,
        "--description",
        str(context.config["bootstrap"].get("description", "")),
        f"--enable-issues={str(bool(github.get('enable_issues', True))).lower()}",
        f"--enable-projects={str(bool(github.get('enable_projects', True))).lower()}",
        f"--enable-wiki={str(bool(github.get('enable_wiki', False))).lower()}",
        f"--enable-discussions={str(bool(github.get('enable_discussions', False))).lower()}",
        f"--enable-merge-commit={str(bool(github.get('allow_merge_commit', False))).lower()}",
        f"--enable-squash-merge={str(bool(github.get('allow_squash_merge', True))).lower()}",
        f"--enable-rebase-merge={str(bool(github.get('allow_rebase_merge', True))).lower()}",
        f"--delete-branch-on-merge={str(bool(github.get('delete_branch_on_merge', True))).lower()}",
        "--allow-update-branch",
        "--squash-merge-commit-message",
        "pr-title-description",
    ]
    homepage = str(github.get("homepage", ""))
    if homepage:
        command.extend(["--homepage", homepage])
    for topic in github.get("topics", []):
        command.extend(["--add-topic", str(topic)])
    run_command(context, command, timeout=180, check=True)
    observed = run_command(
        context,
        [
            "gh",
            "repo",
            "view",
            slug,
            "--json",
            "nameWithOwner,url,visibility,hasIssuesEnabled,hasProjectsEnabled,hasWikiEnabled,hasDiscussionsEnabled,mergeCommitAllowed,squashMergeAllowed,rebaseMergeAllowed,deleteBranchOnMerge,repositoryTopics",
        ],
        timeout=60,
        check=True,
    )
    try:
        payload = json.loads(observed.stdout)
    except json.JSONDecodeError as exc:
        raise BootstrapError("Could not parse observed GitHub repository settings") from exc
    return payload if isinstance(payload, dict) else {}


def create_huggingface_repositories(
    context: BootstrapContext,
    *,
    namespace: str,
) -> list[dict[str, Any]]:
    if not shutil.which("hf"):
        raise BootstrapError("Hugging Face CLI `hf` is required for Hub repository creation")
    account = discover_huggingface_account(context)
    if not account.get("authenticated"):
        raise BootstrapError("Hugging Face CLI is not authenticated; run `hf auth login` first")
    configured = context.config.get("huggingface", {}).get("repositories", [])
    results: list[dict[str, Any]] = []
    for entry in configured:
        name = str(entry.get("name", ""))
        repo_type = str(entry.get("repo_type", "dataset"))
        visibility = str(entry.get("visibility", "private"))
        if not name:
            raise BootstrapError("Hugging Face repository entry has no name")
        repo_id = f"{namespace}/{name}"
        command = ["hf", "repos", "create", repo_id, "--repo-type", repo_type, "--exist-ok"]
        if visibility == "private":
            command.append("--private")
        if repo_type == "space" and entry.get("sdk"):
            command.extend(["--space-sdk", str(entry["sdk"])])
        result = run_command(context, command, timeout=180, check=True)
        plural = {"model": "models", "dataset": "datasets", "space": "spaces"}.get(repo_type)
        if not plural:
            raise BootstrapError(f"Unsupported Hugging Face repository type {repo_type!r}")
        observed_result = run_command(
            context,
            [
                "hf",
                plural,
                "info",
                repo_id,
                "--expand",
                "private,sha",
                "--format",
                "json",
            ],
            timeout=90,
            check=True,
        )
        try:
            observed = json.loads(observed_result.stdout)
        except json.JSONDecodeError as exc:
            raise BootstrapError(
                f"Could not parse Hugging Face repository evidence for {repo_id}"
            ) from exc
        if not isinstance(observed, dict):
            raise BootstrapError(f"Unexpected Hugging Face repository evidence for {repo_id}")
        observed_id = str(observed.get("id") or observed.get("repo_id") or repo_id)
        if observed_id.casefold() != repo_id.casefold():
            raise BootstrapError(
                f"Hugging Face repository identity mismatch: expected {repo_id}, "
                f"observed {observed_id}"
            )
        if "private" in observed and bool(observed["private"]) != (visibility == "private"):
            raise BootstrapError(
                f"Hugging Face visibility mismatch for {repo_id}: expected {visibility}"
            )
        results.append(
            {
                "id": str(entry.get("id", name)),
                "repo_id": repo_id,
                "repo_type": repo_type,
                "visibility": visibility,
                "output": result.stdout.strip(),
                "observed": observed,
                "verified": True,
                "trusted_publisher_required": True,
            }
        )
    return results


def append_audit_event(context: BootstrapContext, event: Mapping[str, Any]) -> dict[str, Any]:
    path = context.output_dir / "bootstrap-audit.jsonl"
    previous_sha256 = ""
    if path.is_file():
        lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        if lines:
            try:
                previous = json.loads(lines[-1])
                previous_sha256 = str(previous.get("event_sha256", ""))
            except json.JSONDecodeError as exc:
                raise BootstrapError(f"Malformed bootstrap audit log {path}") from exc
    payload = {
        "schema_version": "1.0",
        "recorded_at": utc_now(),
        "previous_sha256": previous_sha256,
        **event,
    }
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    payload["event_sha256"] = sha256_bytes(canonical.encode("utf-8"))
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")
    return payload


def apply_bootstrap(
    context: BootstrapContext,
    *,
    github_owner: str,
    github_repository: str,
    github_visibility: str,
    author_name: str,
    author_email: str,
    push: bool,
    apply_github_controls: bool,
    create_huggingface: bool,
    huggingface_namespace: str,
    confirmation: bool,
) -> dict[str, Any]:
    if not confirmation:
        raise BootstrapError("Refusing to mutate without explicit confirmation (`--yes`)")
    if not github_owner:
        account = discover_github_account(context)
        github_owner = str(account.get("login", ""))
    if not github_owner:
        raise BootstrapError("A GitHub owner is required and could not be inferred")
    if not github_repository:
        github_repository = str(
            context.config["bootstrap"].get("repository_name", context.root.name)
        )
    if not author_name or not author_email:
        account = discover_github_account(context)
        login = str(account.get("login", ""))
        author_name = author_name or login or "GFJD maintainer"
        author_email = author_email or (f"{login}@users.noreply.github.com" if login else "")
    verify_repository_manifest(context)
    git_result = initialise_git_repository(
        context,
        author_name=author_name,
        author_email=author_email,
    )
    commit_result = ensure_commit(
        context,
        str(
            context.config["bootstrap"].get(
                "initial_commit_message", "chore: initialise repository"
            )
        ),
    )
    remote_result = ensure_github_remote(
        context,
        owner=github_owner,
        repository=github_repository,
        visibility=github_visibility,
        push=push,
    )
    controls_result: dict[str, Any] = {}
    if apply_github_controls:
        controls_result = apply_github_repository_settings(context, remote_result["slug"])
    hf_result: list[dict[str, Any]] = []
    if create_huggingface:
        if not huggingface_namespace:
            account = discover_huggingface_account(context)
            huggingface_namespace = str(account.get("username", ""))
        if not huggingface_namespace:
            raise BootstrapError("A Hugging Face namespace is required and could not be inferred")
        hf_result = create_huggingface_repositories(
            context,
            namespace=huggingface_namespace,
        )
    receipt = {
        "schema_version": "1.0",
        "applied_at": utc_now(),
        "repository_root": str(context.root),
        "git": git_result,
        "commit": commit_result,
        "github": remote_result,
        "github_controls": controls_result,
        "huggingface": hf_result,
        "commands": [result.as_dict() for result in context.command_results],
    }
    receipt_bytes = _json_bytes(receipt)
    receipt["receipt_sha256"] = sha256_bytes(receipt_bytes)
    receipt_path = context.output_dir / "bootstrap-receipt.json"
    atomic_write(receipt_path, _json_bytes(receipt))
    append_audit_event(
        context,
        {
            "event_type": "bootstrap_applied",
            "actor": author_name,
            "repository": remote_result["slug"],
            "receipt_path": str(receipt_path),
            "receipt_sha256": receipt["receipt_sha256"],
        },
    )
    return receipt


def verify_bootstrap_receipt(path: Path) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        return [f"Missing bootstrap receipt: {path}"]
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"Malformed bootstrap receipt: {exc}"]
    expected = str(payload.pop("receipt_sha256", ""))
    actual = sha256_bytes(_json_bytes(payload))
    if not expected:
        errors.append("Bootstrap receipt has no receipt_sha256")
    elif expected != actual:
        errors.append("Bootstrap receipt checksum does not match its content")
    github = payload.get("github", {})
    if not isinstance(github, dict) or not github.get("slug"):
        errors.append("Bootstrap receipt has no GitHub repository slug")
    commit = payload.get("commit", {})
    if not isinstance(commit, dict) or not re.fullmatch(
        r"[0-9a-f]{40,64}", str(commit.get("head", ""))
    ):
        errors.append("Bootstrap receipt has no valid Git commit identity")
    return errors


def verify_audit_log(path: Path) -> list[str]:
    errors: list[str] = []
    previous_sha256 = ""
    if not path.is_file():
        return [f"Missing bootstrap audit log: {path}"]
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"Audit line {line_number} is malformed: {exc}")
            continue
        observed_previous = str(payload.get("previous_sha256", ""))
        if observed_previous != previous_sha256:
            errors.append(f"Audit line {line_number} does not chain to the previous event")
        expected = str(payload.pop("event_sha256", ""))
        canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        actual = sha256_bytes(canonical.encode("utf-8"))
        if expected != actual:
            errors.append(f"Audit line {line_number} has an invalid event checksum")
        previous_sha256 = expected
    return errors
