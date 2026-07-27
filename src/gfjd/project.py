"""Project discovery and configuration loading."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import tomllib
from typing import Any, Mapping

from .errors import ConfigurationError


class ProjectError(ConfigurationError):
    """Raised when a GFJD project cannot be discovered or configured."""


@dataclass(frozen=True)
class Project:
    """Resolved repository root and immutable configuration mapping."""

    root: Path
    config: Mapping[str, Any]

    @property
    def project_config(self) -> Mapping[str, Any]:
        return self.config["project"]

    @property
    def paths(self) -> Mapping[str, str]:
        return self.config.get("paths", {})

    def resolve(self, configured_path: str | Path) -> Path:
        path = Path(configured_path)
        return path if path.is_absolute() else self.root / path


def _candidate_roots(start: Path | None = None) -> list[Path]:
    candidates: list[Path] = []
    env_root = os.getenv("GFJD_ROOT")
    if env_root:
        candidates.append(Path(env_root).expanduser().resolve())

    start_path = (start or Path.cwd()).expanduser().resolve()
    candidates.extend([start_path, *start_path.parents])

    package_path = Path(__file__).resolve()
    candidates.extend(package_path.parents)

    unique: list[Path] = []
    seen: set[Path] = set()
    for candidate in candidates:
        if candidate not in seen:
            unique.append(candidate)
            seen.add(candidate)
    return unique


def find_project_root(start: Path | None = None) -> Path:
    """Find the nearest directory containing the GFJD project marker."""

    for candidate in _candidate_roots(start):
        if (candidate / "config" / "project.toml").is_file():
            return candidate
    raise ProjectError(
        "Could not find config/project.toml. Run inside the repository or set GFJD_ROOT."
    )


def load_toml(path: Path) -> dict[str, Any]:
    try:
        with path.open("rb") as handle:
            return tomllib.load(handle)
    except FileNotFoundError as exc:
        raise ProjectError(f"Missing configuration file: {path}") from exc
    except tomllib.TOMLDecodeError as exc:
        raise ProjectError(f"Invalid TOML in {path}: {exc}") from exc


def load_project(root: Path | str | None = None) -> Project:
    resolved_root = find_project_root(root) if root is None else Path(root).expanduser().resolve()
    config_path = resolved_root / "config" / "project.toml"
    config = load_toml(config_path)
    if "project" not in config:
        raise ProjectError(f"{config_path} has no [project] table")
    project_id = str(config["project"].get("id", ""))
    if project_id != "GFJD":
        raise ProjectError(f"Unexpected project id {project_id!r} in {config_path}")
    return Project(root=resolved_root, config=config)
