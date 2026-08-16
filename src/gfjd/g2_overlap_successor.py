"""Verification for the preparation-only G2 overlap successor design."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any, cast

from gfjd.g2_exposure_chain import collect_bound_exposure_chain
from gfjd.g2_metadata_search_successor import canonical_url

DESIGN = Path("data/methods/g2/G2HOLDOUT-METADATA-EXPANSION-20260816-03/design")
MANIFEST = DESIGN / "SUCCESSOR_DESIGN_MANIFEST.sha256"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _safe(root: Path, relative: str) -> Path | None:
    candidate = Path(relative)
    if candidate.is_absolute() or ".." in candidate.parts or candidate.as_posix() != relative:
        return None
    path = root / candidate
    try:
        if not path.resolve().is_relative_to(root.resolve()):
            return None
    except (OSError, RuntimeError):
        return None
    current = root
    for part in candidate.parts:
        current /= part
        if current.is_symlink():
            return None
    return path


def _load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("design artifact must be an object")
    return value


def _builder_output(root: Path) -> dict[str, dict[str, Any]] | None:
    script = root / "scripts/build_g2_overlap_successor_design.py"
    spec = importlib.util.spec_from_file_location("g2_overlap_successor_builder", script)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return cast(dict[str, dict[str, Any]], module.build())


def verify_overlap_successor_design(root: Path) -> list[str]:
    """Recompute exact design semantics and detached bindings."""
    errors: list[str] = []
    try:
        plan = _load_object(root / DESIGN / "plan.json")
        ledger = _load_object(root / DESIGN / "ledger.json")
        query_manifest = _load_object(root / DESIGN / "query-manifest.json")
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError):
        return ["overlap successor design JSON is invalid"]

    rebuilt = _builder_output(root)
    if rebuilt is None:
        errors.append("overlap successor builder cannot be loaded")
    elif rebuilt != {"plan": plan, "ledger": ledger, "query_manifest": query_manifest}:
        errors.append("overlap successor builder equivalence mismatch")

    if ledger.get("current_observed_url_count") != 609 or len(ledger.get("denied_urls", [])) != 609:
        errors.append("all 609 observed URLs are not denied")
    denied = ledger.get("denied_urls", [])
    try:
        canonical_denied = {canonical_url(value) for value in denied}
    except (TypeError, ValueError):
        canonical_denied = set()
        errors.append("successor denied URL is invalid")
    if len(canonical_denied) != 609 or sorted(canonical_denied) != denied:
        errors.append("successor denied URLs are not unique canonical sorted values")

    predecessor = ledger.get("predecessor")
    if not isinstance(predecessor, dict):
        errors.append("successor predecessor descriptor is missing")
        prior_urls: set[str] = set()
    else:
        prior_urls, chain, chain_errors = collect_bound_exposure_chain(root, predecessor)
        errors.extend(chain_errors)
        if chain != ledger.get("predecessor_chain"):
            errors.append("successor predecessor chain projection mismatch")
    if ledger.get("cumulative_denied_url_count") != len(prior_urls | canonical_denied):
        errors.append("successor cumulative denied URL count mismatch")

    queries = query_manifest.get("queries", [])
    if (
        len(queries) != 208
        or [row.get("query_order") for row in queries] != list(range(1, 209))
        or len({row.get("query_id") for row in queries}) != 208
        or len({row.get("query_text") for row in queries}) != 208
    ):
        errors.append("successor exact query scope is invalid")
    if any(
        row.get("query_sha256")
        != hashlib.sha256(str(row.get("query_text", "")).encode()).hexdigest()
        for row in queries
    ):
        errors.append("successor query digest mismatch")
    flags = plan.get("authorization_flags", {})
    if any(flags.get(key) is not False for key in flags if key != "design_preparation_authorized"):
        errors.append("successor plan authorizes prohibited activity")
    if flags.get("design_preparation_authorized") is not True:
        errors.append("successor preparation authority is missing")

    manifest_path = root / MANIFEST
    if not manifest_path.is_file():
        return sorted(set(errors + ["successor detached manifest is missing"]))
    seen: set[str] = set()
    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        parts = line.split("  ", 1)
        if len(parts) != 2 or len(parts[0]) != 64 or parts[1] in seen:
            errors.append("successor detached manifest entry is malformed")
            continue
        expected, relative = parts
        seen.add(relative)
        path = _safe(root, relative)
        if path is None or not path.is_file() or _sha(path) != expected:
            errors.append(f"successor detached manifest mismatch: {relative}")
    required = {
        (DESIGN / name).as_posix() for name in ("plan.json", "ledger.json", "query-manifest.json")
    }
    if not required.issubset(seen):
        errors.append("successor detached manifest omits a design artifact")
    return sorted(set(errors))
