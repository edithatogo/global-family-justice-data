"""Bounded supplied Python lock/SPDX consistency, not external assurance.

No path-based lock loader, package installation, registry resolution or execution.
Only implementation fingerprints read files; the inventory Path is a label only.
"""

import hashlib
import json
import math
import re
import tomllib
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, cast

from gfjd import medallion_restore_inputs, security, supply_chain
from gfjd.medallion_replay import _timestamp

MIB = 1024 * 1024


class DependencyEvidenceError(ValueError):
    """Invalid bounded evidence with fixed diagnostics."""


def _require(value: bool) -> None:
    if not value:
        raise DependencyEvidenceError("Dependency evidence contract violation")


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    ).encode()


def _digest(value: Any) -> None:
    _require(type(value) is str and re.fullmatch(r"[0-9a-f]{64}", value) is not None)


def _text(value: Any) -> None:
    _require(type(value) is str and bool(value.strip()) and len(value) <= 4096)


def _name(value: Any) -> str:
    _require(
        type(value) is str
        and len(value) <= 128
        and re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?", value) is not None
    )
    return supply_chain.canonical_package_name(value)


def _tree(value: Any) -> None:
    pending = [(value, 0)]
    nodes = 0
    while pending:
        item, depth = pending.pop()
        nodes += 1
        _require(nodes <= 50000 and depth <= 16)
        if type(item) is str:
            _require(
                len(item) <= 4096
                and all(
                    ord(c) >= 32 and not 127 <= ord(c) <= 159 and not 0xD800 <= ord(c) <= 0xDFFF
                    for c in item
                )
            )
            _require(not any(pattern.search(item) for _, pattern in security.SECRET_PATTERNS))
        elif type(item) in (dict, list):
            _require(len(item) <= 2000)
            if type(item) is dict:
                _require(all(type(key) is str for key in item))
                pending.extend((key, depth + 1) for key in item)
                pending.extend((child, depth + 1) for child in item.values())
            else:
                pending.extend((child, depth + 1) for child in item)
        elif type(item) is int:
            _require(item.bit_length() <= 4096)
        elif type(item) is float:
            _require(math.isfinite(item))
        else:
            _require(item is None or type(item) is bool)


def _dependencies(raw: dict[str, Any]) -> tuple[set[str], set[str]]:
    def items(values: Any) -> set[str]:
        _require(type(values) is list)
        names = set()
        for value in values:
            _require(
                type(value) is dict
                and {"name"} <= set(value) <= {"name", "version", "source", "marker"}
            )
            names.add(_name(value["name"]))
            for field in ("version", "marker"):
                if field in value:
                    _text(value[field])
            if "source" in value:
                _require(value["source"] == {"registry": "https://pypi.org/simple"})
        return names

    core = items(raw.get("dependencies", []))
    grouped = set()
    for key in ("optional-dependencies", "dev-dependencies"):
        groups = raw.get(key, {})
        _require(type(groups) is dict)
        for values in groups.values():
            grouped.update(items(values))
    return core, grouped


def _lock(
    raw: bytes, project_name: str
) -> tuple[supply_chain.LockInventory, dict[tuple[str, str], set[str]], dict[str, int], int]:
    value = tomllib.loads(raw.decode("utf-8"))
    _tree(value)
    _require(type(value.get("version")) is int and value["version"] == 1)
    records = value.get("package")
    _require(type(records) is list and 1 <= len(records) <= 500)
    assert isinstance(records, list)
    project = _name(project_name)
    root = None
    packages = []
    identities = set()
    spdx_ids = {"SPDXRef-Package-GFJD"}
    distribution_by_package = {}
    distribution_sizes: dict[str, int] = {}
    root_core: set[str] = set()
    root_groups: set[str] = set()
    for record in records:
        _require(type(record) is dict and {"name", "version", "source"} <= set(record))
        name = _name(record["name"])
        version = record["version"]
        _text(version)
        identity = name, version
        _require(identity not in identities)
        identities.add(identity)
        core, groups = _dependencies(record)
        distributions = []
        if "sdist" in record:
            distributions.append(record["sdist"])
        wheels = record.get("wheels", [])
        _require(type(wheels) is list)
        distributions.extend(wheels)
        hashes = set()
        for distribution in distributions:
            _require(type(distribution) is dict and {"url", "hash", "size"} <= set(distribution))
            medallion_restore_inputs._locator(distribution["url"], "files.pythonhosted.org")
            digest = distribution["hash"]
            _require(type(digest) is str and digest.startswith("sha256:"))
            digest = digest[7:]
            _digest(digest)
            size = distribution["size"]
            _require(type(size) is int and size > 0)
            _require(digest not in distribution_sizes or distribution_sizes[digest] == size)
            distribution_sizes[digest] = size
            hashes.add(digest)
        distribution_by_package[identity] = hashes
        if name == project:
            _require(root is None and record["source"] == {"editable": "."})
            root = record
            root_core, root_groups = core, groups
        else:
            _require(record["source"] == {"registry": "https://pypi.org/simple"})
            _require(project not in core | groups)
            package = supply_chain.LockedPackage(
                name, version, tuple(sorted(core | groups)), "https://pypi.org/simple"
            )
            _require(package.spdx_id not in spdx_ids)
            spdx_ids.add(package.spdx_id)
            packages.append(package)
    _require(root is not None)
    assert root is not None
    known = Counter(package.canonical_name for package in packages)
    direct = root_core | root_groups
    _require(direct <= set(known))
    edge_count = 1 + sum(known[name] for name in direct)
    for package in packages:
        _require(set(package.dependencies) <= set(known))
        edge_count += sum(known[name] for name in package.dependencies)
    _require(edge_count <= 5000)
    inventory = supply_chain.LockInventory(
        Path("supplied-uv.lock"),
        _sha(raw),
        1,
        project,
        root["version"],
        tuple(sorted(root_core)),
        tuple(sorted(root_groups)),
        tuple(sorted(packages, key=lambda item: (item.canonical_name, item.version))),
    )
    return inventory, distribution_by_package, distribution_sizes, edge_count


def _assess(
    lock_raw: bytes,
    sbom_raw: bytes,
    package_bindings_raw: bytes,
    *,
    project_name: str,
    candidate_id: str,
    as_of: str,
    candidate_bank: dict[str, bytes],
    scope_objects: list[dict[str, Any]],
) -> dict[str, Any]:
    for raw in (lock_raw, sbom_raw, package_bindings_raw):
        _require(type(raw) is bytes and 0 < len(raw) <= MIB)
    _require(type(candidate_bank) is dict and 0 < len(candidate_bank) <= 1502)
    total = 0
    for digest, raw in candidate_bank.items():
        _digest(digest)
        _require(type(raw) is bytes and 0 < len(raw) <= 8 * MIB)
        total += len(raw)
    _require(total <= 26 * MIB)
    _require(type(scope_objects) is list and 1 <= len(scope_objects) <= 1502)
    _tree(scope_objects)
    _tree(project_name)
    _tree(candidate_id)
    _require(
        type(candidate_id) is str
        and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}", candidate_id) is not None
    )
    _timestamp(as_of)
    scope = {}
    for obj in scope_objects:
        _require(type(obj) is dict and {"object_id", "role", "sha256"} <= set(obj))
        _require(
            type(obj["object_id"]) is str
            and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}", obj["object_id"]) is not None
        )
        _require(obj["object_id"] not in scope)
        _digest(obj["sha256"])
        scope[obj["object_id"]] = obj
    _require({obj["sha256"] for obj in scope.values()} == set(candidate_bank))
    for digest, raw in candidate_bank.items():
        _require(_sha(raw) == digest)
    for raw in (lock_raw, sbom_raw, package_bindings_raw):
        _require(candidate_bank.get(_sha(raw)) == raw)
    supplied_sbom = medallion_restore_inputs.preflight(sbom_raw)
    bindings = medallion_restore_inputs.preflight(package_bindings_raw)
    _tree(supplied_sbom)
    _tree(bindings)
    inventory, distributions, sizes, edge_count = _lock(lock_raw, project_name)
    expected_sbom = supply_chain.build_spdx_document(
        inventory,
        release_version=inventory.project_version,
        created_at=datetime.fromisoformat(as_of.replace("Z", "+00:00")),
        scope="build",
        namespace_base="https://global-family-justice-data.example/spdx",
        project_uri="https://github.com/edithatogo/global-family-justice-data",
    )
    expected_raw = _canonical(expected_sbom)
    _require(len(expected_raw) <= MIB and expected_raw == _canonical(supplied_sbom))
    _require(
        type(bindings) is dict
        and set(bindings)
        == {"contract_version", "candidate_id", "lock_sha256", "sbom_sha256", "packages"}
    )
    _require(bindings["contract_version"] == "gfjd-candidate-package-bindings-v1")
    _require(
        bindings["candidate_id"] == candidate_id
        and bindings["lock_sha256"] == _sha(lock_raw)
        and bindings["sbom_sha256"] == _sha(sbom_raw)
    )
    rows = bindings["packages"]
    _require(type(rows) is list and len(rows) <= 500)
    seen = set()
    validated = []
    for row in rows:
        _require(
            type(row) is dict
            and set(row) == {"object_id", "name", "version", "distribution_sha256"}
        )
        obj_id = row["object_id"]
        _require(type(obj_id) is str and obj_id in scope and obj_id not in seen)
        seen.add(obj_id)
        obj = scope[obj_id]
        _require(obj["role"] == "package")
        name = _name(row["name"])
        _text(row["version"])
        _require(name != inventory.project_name and (name, row["version"]) in distributions)
        digest = row["distribution_sha256"]
        _digest(digest)
        _require(digest in distributions[(name, row["version"])] and obj["sha256"] == digest)
        _require(len(candidate_bank[digest]) == sizes[digest])
        validated.append({**row, "name": name, "size_bytes": sizes[digest]})
    for digest in set(sizes) & set(candidate_bank):
        _require(len(candidate_bank[digest]) == sizes[digest])
    components = (supply_chain, security, medallion_restore_inputs)
    return {
        "contract_version": "gfjd-candidate-dependency-evidence-v1",
        "status": "internal_consistency_verified",
        "candidate_id": candidate_id,
        "as_of": as_of,
        "lock_sha256": _sha(lock_raw),
        "sbom_sha256": _sha(sbom_raw),
        "package_bindings_sha256": _sha(package_bindings_raw),
        "package_count": len(inventory.packages) + 1,
        "relationship_count": edge_count,
        "distribution_count": len(sizes),
        "validated_package_bindings": sorted(validated, key=lambda row: row["object_id"]),
        "missing_distribution_sha256": sorted(set(sizes) - set(candidate_bank)),
        "unbound_package_object_ids": sorted(
            obj_id
            for obj_id, obj in scope.items()
            if obj["role"] == "package" and obj_id not in seen
        ),
        "implementation_sha256": _sha(Path(__file__).read_bytes()),
        "component_implementation_sha256": {
            component.__name__: _sha(Path(cast(str, component.__file__)).read_bytes())
            for component in components
        },
        "factual_requirements": dict.fromkeys(
            (
                "artifact_authenticity",
                "signatures",
                "provenance_attestations",
                "vulnerability_feed_freshness",
                "vulnerability_feed_completeness",
                "actual_imports",
                "release_authority",
            ),
            "unverified",
        ),
        "limitations": [
            "all-branches-all-locked-versions-not-environment-solver",
            "unbound-packages-unsupported",
            "distribution-locations-unrequested",
            "SBOM-licence-not-rights-clearance",
        ],
        "authority": dict.fromkeys(
            (
                "network",
                "source_access",
                "installation",
                "execution",
                "publication",
                "release",
                "rights_clearance",
                "gate_acceptance",
            ),
            False,
        ),
        "filesystem_access": "implementation-fingerprints-only",
    }


def assess_dependency_evidence(
    lock_raw: bytes,
    sbom_raw: bytes,
    package_bindings_raw: bytes,
    *,
    project_name: str,
    candidate_id: str,
    as_of: str,
    candidate_bank: dict[str, bytes],
    scope_objects: list[dict[str, Any]],
) -> dict[str, Any]:
    """Rebuild the full conservative SPDX graph and verify declared package bytes."""
    try:
        return _assess(
            lock_raw,
            sbom_raw,
            package_bindings_raw,
            project_name=project_name,
            candidate_id=candidate_id,
            as_of=as_of,
            candidate_bank=candidate_bank,
            scope_objects=scope_objects,
        )
    except Exception:
        raise DependencyEvidenceError("Dependency evidence contract violation") from None


def verify_dependency_evidence(
    lock_raw: bytes,
    sbom_raw: bytes,
    package_bindings_raw: bytes,
    report: dict[str, Any],
    *,
    project_name: str,
    candidate_id: str,
    as_of: str,
    candidate_bank: dict[str, bytes],
    scope_objects: list[dict[str, Any]],
) -> None:
    """Recompute every field without trusting self-hashes or success declarations."""
    try:
        expected = assess_dependency_evidence(
            lock_raw,
            sbom_raw,
            package_bindings_raw,
            project_name=project_name,
            candidate_id=candidate_id,
            as_of=as_of,
            candidate_bank=candidate_bank,
            scope_objects=scope_objects,
        )
        _require(type(report) is dict and _canonical(report) == _canonical(expected))
    except Exception:
        raise DependencyEvidenceError("Dependency evidence contract violation") from None
