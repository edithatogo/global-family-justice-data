"""Deterministic public-contract inventory and drift verification.

The lock protects the machine-readable interfaces that downstream data products and
contributor packs depend on. JSON schemas are canonicalised before hashing, CSV files
contribute their exact header contract rather than mutable rows, and TOML contracts are
hashed byte-for-byte.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path
import tomllib
from typing import Any

from .harness import HarnessIssue, HarnessReport
from .io import canonical_json_bytes, write_json
from .project import Project

LOCK_SCHEMA_VERSION = "1.0"
DEFAULT_LOCK_PATH = Path("config/contract_lock.json")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _csv_header_bytes(path: Path) -> bytes:
    text = path.read_text(encoding="utf-8-sig")
    reader = csv.reader(io.StringIO(text))
    try:
        header = next(reader)
    except StopIteration:
        header = []
    return canonical_json_bytes(header)


def _canonical_toml_bytes(path: Path) -> bytes:
    """Validate TOML while preserving its intentional textual contract."""

    data = path.read_bytes()
    tomllib.loads(data.decode("utf-8"))
    return data


def contract_inputs(project: Project) -> list[tuple[str, str, bytes]]:
    """Return sorted ``(path, kind, canonical-bytes)`` contract inputs."""

    root = project.root
    entries: list[tuple[str, str, bytes]] = []
    for path in sorted((root / "schemas").glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        entries.append((path.relative_to(root).as_posix(), "json_schema", canonical_json_bytes(payload)))

    contract_toml = root / "config" / "data_contracts.toml"
    if contract_toml.is_file():
        entries.append((
            contract_toml.relative_to(root).as_posix(),
            "toml_contract",
            _canonical_toml_bytes(contract_toml),
        ))

    for directory in (root / "data" / "seed", root / "data" / "census", root / "programme"):
        if not directory.exists():
            continue
        for path in sorted(directory.glob("*.csv")):
            entries.append((path.relative_to(root).as_posix(), "csv_header", _csv_header_bytes(path)))
    return entries


def build_contract_lock(project: Project) -> dict[str, Any]:
    entries = [
        {"path": relative, "kind": kind, "sha256": _sha256(content)}
        for relative, kind, content in contract_inputs(project)
    ]
    inventory_digest = _sha256(canonical_json_bytes(entries))
    return {
        "schema_version": LOCK_SCHEMA_VERSION,
        "project_id": str(project.project_config.get("id", "GFJD")),
        "contract_version": str(project.project_config.get("contract_version", "")),
        "entry_count": len(entries),
        "inventory_sha256": inventory_digest,
        "entries": entries,
    }


def write_contract_lock(project: Project, path: Path | None = None) -> Path:
    destination = path or project.root / DEFAULT_LOCK_PATH
    if not destination.is_absolute():
        destination = project.root / destination
    destination = destination.resolve()
    try:
        destination.relative_to(project.root)
    except ValueError as exc:
        raise ValueError("Contract lock must remain inside the repository") from exc
    write_json(destination, build_contract_lock(project))
    return destination


def verify_contract_lock(project: Project, path: Path | None = None) -> HarnessReport:
    destination = path or project.root / DEFAULT_LOCK_PATH
    if not destination.is_absolute():
        destination = project.root / destination
    issues: list[HarnessIssue] = []
    if not destination.is_file():
        issues.append(
            HarnessIssue(
                "error",
                "CONTRACT_LOCK_MISSING",
                str(destination.relative_to(project.root)),
                "Contract lock is required",
            )
        )
        return HarnessReport("public contract lock", tuple(issues), {"entry_count": 0})
    try:
        expected = json.loads(destination.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        issues.append(
            HarnessIssue(
                "error",
                "CONTRACT_LOCK_INVALID",
                str(destination),
                f"Could not read contract lock: {exc}",
            )
        )
        return HarnessReport("public contract lock", tuple(issues), {"entry_count": 0})

    actual = build_contract_lock(project)
    if expected.get("schema_version") != LOCK_SCHEMA_VERSION:
        issues.append(
            HarnessIssue(
                "error",
                "CONTRACT_LOCK_SCHEMA",
                str(destination),
                "Unsupported contract-lock schema_version",
            )
        )
    if expected.get("contract_version") != actual["contract_version"]:
        issues.append(
            HarnessIssue(
                "error",
                "CONTRACT_VERSION_DRIFT",
                str(destination),
                "Contract version differs from config/project.toml",
            )
        )

    expected_entries = {
        str(item.get("path")): (str(item.get("kind")), str(item.get("sha256")))
        for item in expected.get("entries", [])
        if isinstance(item, dict)
    }
    actual_entries = {
        str(item["path"]): (str(item["kind"]), str(item["sha256"]))
        for item in actual["entries"]
    }
    for relative in sorted(set(expected_entries) - set(actual_entries)):
        issues.append(
            HarnessIssue(
                "error", "CONTRACT_REMOVED", relative, "Locked contract input is missing"
            )
        )
    for relative in sorted(set(actual_entries) - set(expected_entries)):
        issues.append(
            HarnessIssue(
                "error", "CONTRACT_ADDED", relative, "New contract input is not locked"
            )
        )
    for relative in sorted(set(expected_entries) & set(actual_entries)):
        if expected_entries[relative] != actual_entries[relative]:
            issues.append(
                HarnessIssue("error", "CONTRACT_DRIFT", relative, "Public contract changed")
            )
    if expected.get("inventory_sha256") != actual["inventory_sha256"]:
        issues.append(
            HarnessIssue(
                "error",
                "CONTRACT_INVENTORY_DRIFT",
                str(destination),
                "Contract inventory digest differs",
            )
        )
    if expected.get("entry_count") != actual["entry_count"]:
        issues.append(
            HarnessIssue(
                "error",
                "CONTRACT_COUNT_DRIFT",
                str(destination),
                "Contract entry count differs",
            )
        )
    return HarnessReport(
        "public contract lock",
        tuple(issues),
        {
            "entry_count": actual["entry_count"],
            "inventory_sha256": actual["inventory_sha256"],
        },
    )
