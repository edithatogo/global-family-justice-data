"""Offline historical-route preparation; never grants network or G2 authority.

Version 2 inventories persisted JSON/JSONL without altering frozen v1 snapshots.
Unknown exposure remains a blocker even when an official index replaces search.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

from .g2_future_exposure import canonical_url


class HistoricalControlError(ValueError):
    """A local input or historical contract cannot be verified."""


SCOPE = "data/methods/g2"
MAX_FILE_BYTES = 8 * 1024 * 1024
MAX_TOTAL_BYTES = 64 * 1024 * 1024
MAX_RESPONSE_BYTES = 2 * 1024 * 1024
LOWER = datetime(2024, 1, 1, tzinfo=UTC)
UPPER = datetime(2026, 8, 29, 5, 17, 40, tzinfo=UTC)
IDENTITIES = {
    "edition_id": "edition_ids",
    "edition_alias": "edition_ids",
    "source_edition_id": "edition_ids",
    "edition_ids": "edition_ids",
    "source_id": "source_ids",
    "source_ids": "source_ids",
    "source_series_id": "source_series_ids",
    "source_series_ids": "source_series_ids",
    "source_sha256": "content_sha256",
    "content_sha256": "content_sha256",
    "product_id": "product_ids",
    "product_ids": "product_ids",
}
AUTHORITY = dict.fromkeys(
    (
        "network",
        "source_access",
        "extraction",
        "rights_clearance",
        "maturity",
        "g2_acceptance",
        "publication",
        "release",
    ),
    False,
)


def _digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False
        ).encode("utf-8")
        + b"\n"
    )


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise HistoricalControlError("duplicate JSON key")
        result[key] = value
    return result


def _constant(value: str) -> Any:
    raise HistoricalControlError("non-finite JSON number")


def _load(raw: bytes) -> Any:
    try:
        return json.loads(raw, object_pairs_hook=_pairs, parse_constant=_constant)
    except (ValueError, UnicodeError, RecursionError) as error:
        raise HistoricalControlError("invalid JSON input") from error


def _safe(root: Path, path: Path) -> None:
    current = root
    for part in path.relative_to(root).parts:
        current /= part
        if current.is_symlink():
            raise HistoricalControlError("symlink input is prohibited")
    if not path.is_file():
        raise HistoricalControlError("missing input file")


def _walk(
    value: Any,
    values: dict[str, set[str]],
    gaps: set[str],
    *,
    base: str | None = None,
    key: str = "",
    depth: int = 0,
    references: list[tuple[str, str]] | None = None,
) -> None:
    if depth > 64:
        raise HistoricalControlError("metadata nesting budget exceeded")
    if isinstance(value, dict):
        request = value.get("request")
        if isinstance(request, dict) and isinstance(request.get("url"), str):
            base = request["url"]
        quarantine = value.get("coarse_exposure_quarantine")
        if isinstance(quarantine, dict) and quarantine.get(
            "blocks_future_search_based_unseen_claims"
        ):
            gaps.add("unenumerated_exposure")
        if value.get("status") == "reconstruction_incomplete":
            gaps.add("incomplete_passive_exposure_reconstruction")
        if value.get("status") == "terminal_stopped_manifest_response_budget_exceeded":
            gaps.add("incomplete_manifest_enumeration")
        if references is not None and isinstance(value.get("path"), str):
            reference_path, digest = value["path"], value.get("sha256")
            if reference_path.startswith(SCOPE + "/") and digest is not None:
                if ".." in Path(reference_path).parts or "\\" in reference_path:
                    raise HistoricalControlError("unsafe reference path")
                if not isinstance(digest, str) or not re.fullmatch(r"[a-f0-9]{64}", digest):
                    raise HistoricalControlError("invalid reference digest")
                references.append((reference_path, digest))
        for name, child in value.items():
            if name in IDENTITIES and child is not None:
                items = child if isinstance(child, list) else [child]
                for item in items:
                    if not isinstance(item, (str, int)) or isinstance(item, bool):
                        raise HistoricalControlError("invalid exposure identity")
                    values[IDENTITIES[name]].add(str(item).strip().casefold())
            _walk(child, values, gaps, base=base, key=name, depth=depth + 1, references=references)
    elif isinstance(value, list):
        for child in value:
            _walk(child, values, gaps, base=base, key=key, depth=depth + 1, references=references)
    elif isinstance(value, str):
        if re.match(r"(?i)^(?:https?|file)://", value):
            values["urls"].add(canonical_url(value))
        elif key == "locators" and value.startswith("/"):
            if base is None:
                gaps.add("unresolved_relative_locator")
            else:
                values["urls"].add(canonical_url(urljoin(base, value)))


def audit_repository(root: Path) -> dict[str, Any]:
    """Inventory every persisted G2 JSON/JSONL input, including empty ledgers.

    Deliberately not a lifetime or live-hosted completeness attestation. No
    response text, source bytes, title, snippet or inferred source URL is emitted.
    """
    root = root.resolve()
    scope = root / SCOPE
    current = root
    for part in Path(SCOPE).parts:
        current /= part
        if current.is_symlink():
            raise HistoricalControlError("symlink inventory scope")
    entries = list(scope.rglob("*"))
    if len(entries) > 2000 or any(path.is_symlink() for path in entries):
        raise HistoricalControlError("symlink or oversized inventory")
    paths = sorted(path for path in entries if path.is_file())
    if any(path.suffix not in {".json", ".jsonl", ".sha256", ".md", ".csv"} for path in paths):
        raise HistoricalControlError("unexpected file type in metadata inventory")
    if not paths or len(paths) > 1000:
        raise HistoricalControlError("input inventory missing or exceeds file budget")
    values: dict[str, set[str]] = {name: set() for name in {"urls", *IDENTITIES.values()}}
    gaps: set[str] = set()
    inputs = []
    references: list[tuple[str, str]] = []
    total = 0
    for path in paths:
        _safe(root, path)
        size = path.stat().st_size
        total += size
        if size > MAX_FILE_BYTES or total > MAX_TOTAL_BYTES:
            raise HistoricalControlError("metadata byte budget exceeded")
        raw = path.read_bytes()
        if len(raw) != size:
            raise HistoricalControlError("input changed during audit")
        records = []
        if path.suffix == ".json":
            records = [_load(raw)]
        elif path.suffix == ".jsonl":
            records = [_load(line) for line in raw.splitlines()]
        file_gaps: set[str] = set()
        for record in records:
            if not isinstance(record, (dict, list)):
                raise HistoricalControlError("metadata records must be objects or arrays")
            if not path.name.endswith(".schema.json"):
                _walk(record, values, file_gaps, references=references)
        gaps.update(file_gaps)
        inputs.append(
            {
                "path": path.relative_to(root).as_posix(),
                "sha256": _digest(raw),
                "bytes": len(raw),
                "records": len(records),
                "role": "parsed_metadata"
                if path.suffix in {".json", ".jsonl"}
                else "binding_only_auxiliary",
                "gap_codes": sorted(file_gaps),
            }
        )
    file_digests = {item["path"]: item["sha256"] for item in inputs}
    reference_checks = []
    for reference_path, digest in sorted(set(references)):
        if file_digests.get(reference_path) == digest:
            status = "exact_binding_verified"
        elif reference_path not in file_digests and digest in file_digests.values():
            status = "same_bytes_retained_at_other_inventory_path"
        else:
            status = "missing_or_changed_reference"
            gaps.add(status)
        reference_checks.append({"path": reference_path, "sha256": digest, "status": status})
    normalized = {name: sorted(items) for name, items in sorted(values.items())}
    # Hash locators instead of duplicating file paths or metadata text in public receipts.
    identities = {
        name: sorted(_digest(item.encode()) for item in items) for name, items in normalized.items()
    }
    return {
        "schema_version": "2.0",
        "scope": SCOPE,
        "inputs": inputs,
        "reference_checks": reference_checks,
        "canonicalization": "gfjd_future_exposure_v1_plus_metadata_inventory_v2",
        "coverage": "repository_persisted_json_jsonl_only_not_lifetime_or_live_hosted",
        "inventory_valid": True,
        "execution_ready": False,
        "blockers": sorted(gaps),
        "identity_sha256": identities,
        "counts": {name: len(items) for name, items in identities.items()},
        "authority": dict(AUTHORITY),
    }


def verify_audit(root: Path, audit: dict[str, Any]) -> list[str]:
    """Recompute input membership, exact digests and normalized identities."""
    try:
        return [] if audit_repository(root) == audit else ["audit does not reproduce"]
    except (OSError, ValueError) as error:
        return [str(error)]


def _timestamp(value: Any) -> datetime:
    if not isinstance(value, str) or not re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:Z|[+-]\d{2}:\d{2})", value
    ):
        raise HistoricalControlError("explicit zoned publication timestamp required")
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


def evaluate_metadata(raw: bytes, audit: dict[str, Any], *, root: Path) -> dict[str, Any]:
    """Offline synthetic-testable evaluator; outputs hypotheses, never editions.

    Recomputes its audit against the repository before use. A future execution
    runner is intentionally absent; this API grants no source access.
    All parsable locators are retained before eligibility/contract assessment.
    """
    if len(raw) > MAX_RESPONSE_BYTES:
        raise HistoricalControlError("response byte budget exceeded; exposure unknown")
    payload = _load(raw)
    if not isinstance(payload, dict) or not isinstance(payload.get("results"), list):
        raise HistoricalControlError("response schema invalid; exposure unknown")
    if verify_audit(root, audit):
        raise HistoricalControlError("verified version 2 inventory required")
    stops = set(audit["blockers"])
    rows = payload["results"]
    if len(rows) > 100:
        stops.add("result_budget_exceeded")
    if (
        set(payload) - {"results", "total", "start"}
        or type(payload.get("total")) is not int
        or payload["total"] != len(rows)
        or payload["total"] > 100
        or type(payload.get("start", 0)) is not int
        or payload.get("start", 0) != 0
    ):
        stops.add("incomplete_or_changed_enumeration_contract")
    observed = []
    eligible = []
    seen: set[str] = set()
    denied = set(audit["identity_sha256"]["urls"])
    for ordinal, row in enumerate(rows, 1):
        if not isinstance(row, dict) or not isinstance(row.get("link"), str):
            stops.add("missing_locator_exposure_unknown")
            continue
        link = row["link"]
        try:
            url = canonical_url(urljoin("https://www.gov.uk", link))
        except ValueError:
            stops.add("unparseable_locator_exposure_unknown")
            continue
        observed.append({"ordinal": ordinal, "url": url, "requested": False})
        if url in seen:
            stops.add("duplicate_locator")
        seen.add(url)
        if (
            not re.fullmatch(r"/government/statistics/[a-z0-9][a-z0-9-]*", link)
            or set(row) != {"link", "public_timestamp", "format", "title"}
            or row.get("format") not in {"official_statistics", "national_statistics"}
            or not isinstance(row.get("title"), str)
            or not row["title"]
        ):
            stops.add("result_schema_or_locator_contract")
            continue
        try:
            timestamp = _timestamp(row.get("public_timestamp"))
        except ValueError:
            stops.add("publication_timestamp_missing_or_ambiguous")
            continue
        if LOWER <= timestamp < UPPER and _digest(url.encode()) not in denied:
            eligible.append(
                {
                    "url": url,
                    "public_timestamp": timestamp.isoformat(),
                    "meaning": "absent_from_enumerated_metadata_only",
                }
            )
    if len(eligible) < 2:
        stops.add("fewer_than_two_metadata_hypotheses")
    eligible.sort(key=lambda row: (row["public_timestamp"], row["url"]))
    return {
        "schema_version": "1.0",
        "status": "terminal_stop" if stops else "metadata_hypotheses_only",
        "response_sha256": _digest(raw),
        "audit_sha256": _digest(_bytes(audit)),
        "observations": observed,
        "stop_reasons": sorted(stops),
        "selected": [] if stops else eligible[:4],
        "execution_ready": False,
        "authority": dict(AUTHORITY),
    }


def write_once(path: Path, value: dict[str, Any]) -> None:
    """Refuse to repair or overwrite an existing audit/receipt."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(_bytes(value))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if (args.root.resolve() / SCOPE) in args.output.resolve().parents:
        raise HistoricalControlError("audit output must be outside its input inventory")
    audit = audit_repository(args.root)
    write_once(args.output, audit)
    print(
        json.dumps(
            {"counts": audit["counts"], "blockers": audit["blockers"], "execution_ready": False},
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
