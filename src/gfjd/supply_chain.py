"""Dependency-lock inventory and deterministic SPDX 2.3 document construction."""

from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import quote

from .io import sha256_file

_NORMALISE_NAME = re.compile(r"[-_.]+")
_SPDX_SAFE = re.compile(r"[^A-Za-z0-9.-]+")


class SupplyChainError(ValueError):
    """Raised when a dependency lock cannot support reproducible release metadata."""


@dataclass(frozen=True, slots=True)
class LockedPackage:
    """One resolved package entry from the uv lock."""

    name: str
    version: str
    dependencies: tuple[str, ...]
    source: str

    @property
    def canonical_name(self) -> str:
        return canonical_package_name(self.name)

    @property
    def spdx_id(self) -> str:
        suffix = _SPDX_SAFE.sub("-", f"{self.canonical_name}-{self.version}").strip("-")
        return f"SPDXRef-Package-{suffix}"

    @property
    def purl(self) -> str:
        return f"pkg:pypi/{quote(self.canonical_name)}@{quote(self.version)}"


@dataclass(frozen=True, slots=True)
class LockInventory:
    """Canonical runtime and complete dependency views bound to one lock digest."""

    path: Path
    sha256: str
    format_version: int
    project_name: str
    project_version: str
    runtime_direct: tuple[str, ...]
    development_direct: tuple[str, ...]
    packages: tuple[LockedPackage, ...]

    @property
    def package_count(self) -> int:
        return len(self.packages)

    def selected_packages(self, scope: str) -> tuple[LockedPackage, ...]:
        if scope == "build":
            return self.packages
        if scope != "runtime":
            raise SupplyChainError(f"Unsupported dependency scope: {scope}")
        selected_names = _dependency_closure(self.packages, self.runtime_direct)
        return tuple(
            package for package in self.packages if package.canonical_name in selected_names
        )


def canonical_package_name(value: str) -> str:
    return _NORMALISE_NAME.sub("-", value).lower()


def load_lock_inventory(path: Path, *, project_name: str) -> LockInventory:
    """Load a uv lock and derive conservative runtime and complete dependency sets."""

    try:
        with path.open("rb") as handle:
            payload = tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise SupplyChainError(f"Could not read dependency lock {path}: {exc}") from exc
    lock_version = payload.get("version")
    if not isinstance(lock_version, int):
        raise SupplyChainError("uv.lock must declare an integer format version")
    raw_packages = payload.get("package")
    if not isinstance(raw_packages, list):
        raise SupplyChainError("uv.lock has no package array")

    canonical_project = canonical_package_name(project_name)
    root: dict[str, Any] | None = None
    packages: list[LockedPackage] = []
    identities: set[tuple[str, str]] = set()
    for raw in raw_packages:
        if not isinstance(raw, dict):
            raise SupplyChainError("uv.lock package entries must be tables")
        name = str(raw.get("name", ""))
        version = str(raw.get("version", ""))
        if not name or not version:
            raise SupplyChainError("uv.lock package entry is missing name or version")
        if canonical_package_name(name) == canonical_project:
            if root is not None:
                raise SupplyChainError(
                    f"uv.lock contains multiple project entries for {project_name}"
                )
            root = raw
            continue
        identity = (canonical_package_name(name), version)
        if identity in identities:
            raise SupplyChainError(f"uv.lock contains duplicate package identity {name}=={version}")
        identities.add(identity)
        dependencies = tuple(sorted(_dependency_names(raw.get("dependencies", []))))
        packages.append(
            LockedPackage(
                name=name,
                version=version,
                dependencies=dependencies,
                source=_source_location(raw.get("source")),
            )
        )
    if root is None:
        raise SupplyChainError(f"uv.lock has no project entry for {project_name}")
    packages.sort(key=lambda item: (item.canonical_name, item.version))
    runtime_direct = tuple(sorted(_dependency_names(root.get("dependencies", []))))
    optional = root.get("optional-dependencies", {})
    development_direct: tuple[str, ...] = ()
    if isinstance(optional, dict):
        development_direct = tuple(
            sorted(
                {
                    dependency
                    for values in optional.values()
                    for dependency in _dependency_names(values)
                }
            )
        )
    known_names = {package.canonical_name for package in packages}
    missing_runtime = sorted(set(runtime_direct) - known_names)
    if missing_runtime:
        raise SupplyChainError(
            "uv.lock runtime dependency references unresolved package(s): "
            + ", ".join(missing_runtime)
        )
    return LockInventory(
        path=path,
        sha256=sha256_file(path),
        format_version=lock_version,
        project_name=project_name,
        project_version=str(root.get("version", "")),
        runtime_direct=runtime_direct,
        development_direct=development_direct,
        packages=tuple(packages),
    )


def build_spdx_document(
    inventory: LockInventory,
    *,
    release_version: str,
    created_at: datetime,
    scope: str,
    namespace_base: str,
    project_uri: str,
) -> dict[str, Any]:
    """Build a deterministic SPDX 2.3 package graph from a resolved lock."""

    selected = inventory.selected_packages(scope)
    selected_by_name: dict[str, list[LockedPackage]] = {}
    for package in selected:
        selected_by_name.setdefault(package.canonical_name, []).append(package)
    root_id = "SPDXRef-Package-GFJD"
    packages: list[dict[str, Any]] = [
        {
            "SPDXID": root_id,
            "name": inventory.project_name,
            "versionInfo": release_version,
            "downloadLocation": project_uri,
            "filesAnalyzed": False,
            "licenseConcluded": "NOASSERTION",
            "licenseDeclared": "NOASSERTION",
            "copyrightText": "NOASSERTION",
            "externalRefs": [
                {
                    "referenceCategory": "PACKAGE-MANAGER",
                    "referenceType": "purl",
                    "referenceLocator": (
                        f"pkg:pypi/{quote(canonical_package_name(inventory.project_name))}"
                        f"@{quote(release_version)}"
                    ),
                }
            ],
        }
    ]
    for package in selected:
        packages.append(_spdx_package(package))

    direct_names = (
        set(inventory.runtime_direct)
        if scope == "runtime"
        else set(inventory.runtime_direct) | set(inventory.development_direct)
    )
    relationships: list[dict[str, str]] = [
        {
            "spdxElementId": "SPDXRef-DOCUMENT",
            "relationshipType": "DESCRIBES",
            "relatedSpdxElement": root_id,
        }
    ]
    for name in sorted(direct_names):
        for dependency in selected_by_name.get(name, []):
            relationships.append(_relationship(root_id, dependency.spdx_id))
    for package in selected:
        for name in package.dependencies:
            for dependency in selected_by_name.get(name, []):
                relationships.append(_relationship(package.spdx_id, dependency.spdx_id))
    relationships.sort(
        key=lambda item: (
            item["spdxElementId"],
            item["relationshipType"],
            item["relatedSpdxElement"],
        )
    )

    timestamp = created_at.strftime("%Y%m%dT%H%M%SZ")
    namespace = namespace_base.rstrip("/:#")
    separator = ":" if namespace.startswith("urn:") else "/"
    return {
        "spdxVersion": "SPDX-2.3",
        "dataLicense": "CC0-1.0",
        "SPDXID": "SPDXRef-DOCUMENT",
        "name": f"GFJD-{release_version}-{scope}-dependencies",
        "documentNamespace": (
            f"{namespace}{separator}{quote(release_version, safe='.-')}"
            f"{separator}{scope}{separator}{timestamp}"
        ),
        "creationInfo": {
            "created": created_at.isoformat(),
            "creators": ["Tool: gfjd-release-builder"],
        },
        "documentDescribes": [root_id],
        "packages": packages,
        "relationships": relationships,
        "comment": (
            f"Resolved {scope} dependency graph generated from uv.lock SHA-256 "
            f"{inventory.sha256}. Conditional dependencies are conservatively included."
        ),
    }


def _dependency_names(values: Any) -> set[str]:
    if not isinstance(values, list):
        return set()
    result: set[str] = set()
    for value in values:
        if isinstance(value, dict) and value.get("name"):
            result.add(canonical_package_name(str(value["name"])))
        elif isinstance(value, str):
            result.add(canonical_package_name(value))
    return result


def _source_location(value: Any) -> str:
    if not isinstance(value, dict):
        return "NOASSERTION"
    for key in ("registry", "url", "git", "path", "editable"):
        if key in value:
            return str(value[key])
    return "NOASSERTION"


def _dependency_closure(
    packages: tuple[LockedPackage, ...], direct_dependencies: tuple[str, ...]
) -> set[str]:
    by_name: dict[str, list[LockedPackage]] = {}
    for package in packages:
        by_name.setdefault(package.canonical_name, []).append(package)
    selected: set[str] = set()
    pending = list(direct_dependencies)
    while pending:
        name = pending.pop()
        if name in selected:
            continue
        selected.add(name)
        for package in by_name.get(name, []):
            pending.extend(package.dependencies)
    return selected


def _spdx_package(package: LockedPackage) -> dict[str, Any]:
    return {
        "SPDXID": package.spdx_id,
        "name": package.name,
        "versionInfo": package.version,
        "downloadLocation": package.source,
        "filesAnalyzed": False,
        "licenseConcluded": "NOASSERTION",
        "licenseDeclared": "NOASSERTION",
        "copyrightText": "NOASSERTION",
        "externalRefs": [
            {
                "referenceCategory": "PACKAGE-MANAGER",
                "referenceType": "purl",
                "referenceLocator": package.purl,
            }
        ],
    }


def _relationship(source: str, target: str) -> dict[str, str]:
    return {
        "spdxElementId": source,
        "relationshipType": "DEPENDS_ON",
        "relatedSpdxElement": target,
    }
