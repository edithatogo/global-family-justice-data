"""Build minimal, digest-bound input workspaces for isolated G2 roles."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import tempfile
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from .io import sha256_file, write_json


class G2RoleIsolationError(ValueError):
    """Raised when a role workspace cannot be built or verified safely."""


def bind_role_inputs(
    root: Path, specifications: Sequence[dict[str, str]]
) -> list[dict[str, str]]:
    """Resolve an allowlist and compute its digests without copying any input.

    The returned records are suitable for prospective review and for passing
    unchanged to :func:`build_role_workspace`.  Computing the digest here
    avoids manually transcribed hashes while retaining the builder's separate
    fail-closed recomputation.
    """

    resolved_root = root.expanduser().resolve()
    bound: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in specifications:
        target_name = str(item.get("target_name") or "")
        if not target_name or Path(target_name).name != target_name or target_name in {".", ".."}:
            raise G2RoleIsolationError(f"invalid target_name: {target_name!r}")
        if target_name in seen:
            raise G2RoleIsolationError(f"duplicate target_name: {target_name}")
        seen.add(target_name)
        source_relative = str(item.get("source_path") or "")
        source_path = _confined(resolved_root, Path(source_relative))
        if source_path.is_symlink() or not source_path.is_file():
            raise G2RoleIsolationError(
                f"source is missing or not a regular file: {source_relative}"
            )
        bound.append(
            {
                "source_path": source_path.relative_to(resolved_root).as_posix(),
                "target_name": target_name,
                "sha256": sha256_file(source_path),
            }
        )
    if not bound:
        raise G2RoleIsolationError("at least one role input is required")
    return bound


def build_role_workspace(
    root: Path,
    *,
    destination: Path,
    packet_id: str,
    role: str,
    source_commit: str,
    generated_at: str,
    inputs: Sequence[dict[str, str]],
) -> Path:
    """Atomically create a workspace containing only explicitly bound inputs."""

    resolved_root = root.expanduser().resolve()
    resolved_destination = _confined(resolved_root, destination, require_exists=False)
    if resolved_destination.exists():
        raise G2RoleIsolationError(f"role workspace already exists: {resolved_destination}")
    if not inputs:
        raise G2RoleIsolationError("at least one role input is required")

    normalised = _normalise_inputs(resolved_root, inputs)
    resolved_destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(
        tempfile.mkdtemp(prefix=f".{resolved_destination.name}.", dir=resolved_destination.parent)
    )
    try:
        input_root = temporary / "inputs"
        input_root.mkdir()
        receipt_inputs: list[dict[str, Any]] = []
        for item in normalised:
            destination_path = input_root / item["target_name"]
            _copy_regular_file(item["source_path"], destination_path)
            actual = sha256_file(destination_path)
            if actual != item["sha256"]:
                raise G2RoleIsolationError(
                    f"copied input digest differs for {item['target_name']}: {actual}"
                )
            receipt_inputs.append(
                {
                    "target_name": item["target_name"],
                    "source_path": item["source_relative"],
                    "sha256": actual,
                    "byte_count": destination_path.stat().st_size,
                }
            )

        receipt = {
            "schema_version": "1.0",
            "packet_id": packet_id,
            "role": role,
            "source_commit": source_commit,
            "generated_at": generated_at,
            "workspace_policy": "explicit_allowlist_only",
            "inputs": receipt_inputs,
            "entry_allowlist": ["inputs", "isolation-receipt.json"],
            "network_access": False,
            "source_contents_embedded_in_receipt": False,
        }
        write_json(temporary / "isolation-receipt.json", receipt)
        os.replace(temporary, resolved_destination)
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise

    errors = verify_role_workspace(resolved_root, resolved_destination)
    if errors:
        raise G2RoleIsolationError("; ".join(errors))
    return resolved_destination / "isolation-receipt.json"


def verify_role_workspace(root: Path, workspace: Path | None = None) -> list[str]:
    """Recompute a role workspace's allowlist, types, sizes and digests."""

    from .io import read_json

    if workspace is None:
        workspace = root
        resolved_workspace = workspace.expanduser().resolve()
        resolved_root = _discover_project_root(resolved_workspace)
    else:
        resolved_root = root.expanduser().resolve()
        resolved_workspace = _confined(resolved_root, workspace)
    errors: list[str] = []
    if resolved_workspace.is_symlink() or not resolved_workspace.is_dir():
        return ["role workspace must be a real directory"]
    receipt_path = resolved_workspace / "isolation-receipt.json"
    if not receipt_path.is_file() or receipt_path.is_symlink():
        return ["isolation receipt is missing or is a symbolic link"]
    receipt = read_json(receipt_path)
    if (
        not isinstance(receipt, dict)
        or receipt.get("workspace_policy") != "explicit_allowlist_only"
    ):
        return ["isolation receipt policy is invalid"]

    root_entries = sorted(path.name for path in resolved_workspace.iterdir())
    if root_entries != ["inputs", "isolation-receipt.json"]:
        errors.append(f"unexpected workspace entries: {root_entries}")
    input_root = resolved_workspace / "inputs"
    if input_root.is_symlink() or not input_root.is_dir():
        errors.append("inputs path must be a real directory")
        return errors

    inputs = receipt.get("inputs")
    if not isinstance(inputs, list) or not inputs:
        errors.append("receipt inputs must be a non-empty array")
        return errors
    expected_names = sorted(str(item.get("target_name") or "") for item in inputs)
    actual_names = sorted(path.name for path in input_root.iterdir())
    if actual_names != expected_names:
        errors.append(
            f"isolated input set differs: expected {expected_names}, found {actual_names}"
        )
    for item in inputs:
        target = input_root / str(item.get("target_name") or "")
        if target.is_symlink() or not target.is_file():
            errors.append(f"isolated input is missing or not regular: {target.name}")
            continue
        if target.stat().st_size != item.get("byte_count"):
            errors.append(f"isolated input byte count differs: {target.name}")
        if sha256_file(target) != item.get("sha256"):
            errors.append(f"isolated input digest differs: {target.name}")
    return errors


def _normalise_inputs(root: Path, inputs: Sequence[dict[str, str]]) -> list[dict[str, Any]]:
    normalised: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in inputs:
        target_name = str(item.get("target_name") or "")
        if not target_name or Path(target_name).name != target_name or target_name in {".", ".."}:
            raise G2RoleIsolationError(f"invalid target_name: {target_name!r}")
        if target_name in seen:
            raise G2RoleIsolationError(f"duplicate target_name: {target_name}")
        seen.add(target_name)
        source_relative = str(item.get("source_path") or "")
        source_path = _confined(root, Path(source_relative))
        if source_path.is_symlink() or not source_path.is_file():
            raise G2RoleIsolationError(
                f"source is missing or not a regular file: {source_relative}"
            )
        expected = str(item.get("sha256") or "").lower()
        actual = sha256_file(source_path)
        if actual != expected:
            raise G2RoleIsolationError(
                f"source digest differs for {source_relative}: expected {expected}, found {actual}"
            )
        normalised.append(
            {
                "target_name": target_name,
                "source_relative": source_relative,
                "source_path": source_path,
                "sha256": expected,
            }
        )
    return normalised


def _copy_regular_file(source: Path, destination: Path) -> None:
    descriptor = os.open(source, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    try:
        with os.fdopen(descriptor, "rb", closefd=True) as source_handle:
            descriptor = -1
            with destination.open("xb") as destination_handle:
                shutil.copyfileobj(source_handle, destination_handle, length=1024 * 1024)
    finally:
        if descriptor >= 0:
            os.close(descriptor)


def _confined(root: Path, path: Path, *, require_exists: bool = True) -> Path:
    candidate = path if path.is_absolute() else root / path
    resolved = candidate.expanduser().resolve(strict=require_exists)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise G2RoleIsolationError(f"path escapes repository root: {path}") from exc
    return resolved


def _discover_project_root(path: Path) -> Path:
    for parent in (path, *path.parents):
        if (parent / "pyproject.toml").is_file() and (parent / "schemas").is_dir():
            return parent.resolve()
    raise G2RoleIsolationError(f"could not discover project root from workspace: {path}")


def main(argv: Sequence[str] | None = None) -> int:
    """Provide an unambiguous one-path verifier for isolated execution roles."""

    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    verify = subparsers.add_parser("verify", help="verify one isolated role workspace")
    verify.add_argument("workspace", type=Path)
    args = parser.parse_args(argv)
    errors = verify_role_workspace(args.workspace)
    print(json.dumps({"workspace": str(args.workspace), "errors": errors}, sort_keys=True))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
