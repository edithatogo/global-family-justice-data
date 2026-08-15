"""Semantic verification for the source-disabled G2 metadata-search successor."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit
from zoneinfo import ZoneInfo

from jsonschema import Draft202012Validator, FormatChecker

DESIGN = Path("data/methods/g2/G2HOLDOUT-METADATA-EXPANSION-20260816-02/design")
QUERY_MANIFEST = DESIGN / "successor-query-manifest.json"
DESIGN_MANIFEST = DESIGN / "SUCCESSOR_DESIGN_MANIFEST.sha256"
AUTHORITY_PREFIX = Path("data/methods/g2/G2HOLDOUT-METADATA-EXPANSION-20260816-02/authority")
FILE_SUFFIXES = {
    ".csv",
    ".doc",
    ".docx",
    ".json",
    ".ods",
    ".pdf",
    ".ppt",
    ".pptx",
    ".tar",
    ".xls",
    ".xlsx",
    ".xml",
    ".zip",
}
HTML_SUFFIXES = {"", ".asp", ".aspx", ".htm", ".html", ".php"}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def canonical_url(value: str) -> str:
    parsed = urlsplit(value)
    host = (parsed.hostname or "").rstrip(".").lower()
    if parsed.scheme.lower() not in {"http", "https"} or not host:
        return value
    port = parsed.port
    netloc = host if port in (None, 80, 443) else f"{host}:{port}"
    return urlunsplit((parsed.scheme.lower(), netloc, parsed.path or "/", parsed.query, ""))


def classify_url(value: str) -> str:
    parsed = urlsplit(value)
    if parsed.scheme.lower() not in {"http", "https"} or not parsed.hostname:
        return "other"
    suffix = Path(parsed.path.lower()).suffix
    if suffix in FILE_SUFFIXES:
        return "file"
    return "html" if suffix in HTML_SUFFIXES else "other"


def result_domain(value: str) -> str:
    return (urlsplit(value).hostname or "").rstrip(".").lower()


def _official_https_html(value: str, official_domain: str) -> str | None:
    parsed = urlsplit(value)
    host = result_domain(value)
    official = official_domain.rstrip(".").lower()
    if (
        parsed.scheme.lower() != "https"
        or classify_url(value) != "html"
        or not host
        or (host != official and not host.endswith(f".{official}"))
        or parsed.username
        or parsed.password
        or parsed.port not in (None, 443)
    ):
        return None
    return canonical_url(value)


def _safe_path(root: Path, relative: str, *, exact: Path | None = None) -> Path | None:
    candidate = Path(relative)
    if candidate.is_absolute() or ".." in candidate.parts or candidate.as_posix() != relative:
        return None
    if exact is not None and candidate != exact:
        return None
    path = root / candidate
    try:
        if not path.resolve().is_relative_to(root.resolve()):
            return None
    except (OSError, RuntimeError):
        return None
    current = root
    for part in candidate.parts:
        current = current / part
        if current.is_symlink():
            return None
    return path


def _bound(root: Path, descriptor: dict[str, str], *, exact: Path | None = None) -> bool:
    path = _safe_path(root, descriptor["path"], exact=exact)
    return path is not None and path.is_file() and _sha(path) == descriptor["sha256"]


def _validate_json(root: Path, payload: dict[str, Any], schema_name: str) -> list[str]:
    schema = json.loads((root / DESIGN / schema_name).read_text())
    return [
        error.message
        for error in Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(
            payload
        )
    ]


def _parse_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("timestamp lacks timezone offset")
    return parsed.astimezone(UTC)


def _verify_detached_manifest(root: Path, descriptor: dict[str, str]) -> list[str]:
    if not _bound(root, descriptor, exact=DESIGN_MANIFEST):
        return ["exact successor design manifest binding mismatch"]
    manifest_path = root / DESIGN_MANIFEST
    errors: list[str] = []
    seen: set[str] = set()
    for line in manifest_path.read_text().splitlines():
        parts = line.split("  ", 1)
        if len(parts) != 2 or len(parts[0]) != 64:
            errors.append("malformed successor design manifest entry")
            continue
        expected_sha, relative = parts
        if relative in seen:
            errors.append("duplicate successor design manifest entry")
            continue
        seen.add(relative)
        path = _safe_path(root, relative)
        if path is None or not path.is_file() or _sha(path) != expected_sha:
            errors.append(f"successor design manifest entry mismatch: {relative}")
    query_relative = QUERY_MANIFEST.as_posix()
    if query_relative not in seen:
        errors.append("successor query manifest absent from design manifest")
    return errors


def _builder_equivalent(root: Path, manifest: dict[str, Any]) -> bool:
    script = root / "scripts/build_g2_metadata_search_successor_manifest.py"
    spec = importlib.util.spec_from_file_location("g2_successor_runtime_builder", script)
    if spec is None or spec.loader is None:
        return False
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return bool(module.build() == manifest)


def _git_commit_binds(root: Path, commit: str, relative_path: str, expected_sha: str) -> bool:
    object_type = subprocess.run(
        ["git", "cat-file", "-t", commit], cwd=root, capture_output=True, text=True
    )
    if object_type.returncode != 0 or object_type.stdout.strip() != "commit":
        return False
    signature = subprocess.run(
        ["git", "verify-commit", commit], cwd=root, capture_output=True, text=True
    )
    if signature.returncode != 0:
        return False
    blob = subprocess.run(
        ["git", "show", f"{commit}:{relative_path}"], cwd=root, capture_output=True
    )
    return blob.returncode == 0 and hashlib.sha256(blob.stdout).hexdigest() == expected_sha


def _verify_authority(
    root: Path,
    bundle: dict[str, Any],
    *,
    now: datetime,
) -> list[str]:
    descriptor = bundle["authority_receipt"]
    authority_path = _safe_path(root, descriptor["path"])
    if (
        authority_path is None
        or not Path(descriptor["path"]).is_relative_to(AUTHORITY_PREFIX)
        or not _bound(root, descriptor)
    ):
        return ["successor authority receipt binding mismatch"]
    receipt = json.loads(authority_path.read_text(encoding="utf-8"))
    errors = _validate_json(root, receipt, "successor-authority-receipt.schema.json")
    if errors:
        return sorted(set(errors))
    if receipt["design_manifest"] != bundle["design_manifest"]:
        errors.append("authority receipt design manifest mismatch")
    decision_descriptor = receipt["owner_decision"]
    decision_path = _safe_path(root, decision_descriptor["path"])
    if decision_path is None or not _bound(root, decision_descriptor):
        errors.append("owner decision binding mismatch")
        return sorted(set(errors))
    decision = json.loads(decision_path.read_text(encoding="utf-8"))
    errors.extend(_validate_json(root, decision, "successor-owner-decision.schema.json"))
    if errors:
        return sorted(set(errors))
    if decision["design_manifest"] != bundle["design_manifest"]:
        errors.append("owner decision design manifest mismatch")
    if decision["query_manifest"] != bundle["query_manifest"]:
        errors.append("owner decision query manifest mismatch")
    if decision["freeze_commit"] != receipt["freeze_commit"]:
        errors.append("owner decision freeze commit mismatch")
    if bundle["authorized_interval"] != {
        "valid_from": decision["valid_from"],
        "valid_until": decision["valid_until"],
    }:
        errors.append("authorized interval mismatch")
    try:
        receipt_generated = _parse_time(receipt["generated_at"])
        freeze_verified = _parse_time(receipt["freeze_signature"]["verified_at"])
        decision_verified = _parse_time(receipt["owner_decision_signature"]["verified_at"])
        decided = _parse_time(decision["decided_at"])
        valid_from = _parse_time(decision["valid_from"])
        valid_until = _parse_time(decision["valid_until"])
        if not (
            freeze_verified
            <= decided
            <= decision_verified
            <= receipt_generated
            < valid_from
            < valid_until
            and receipt_generated <= now
        ):
            errors.append("authority chronology invalid or retrospectively authorized")
    except ValueError:
        errors.append("authority timestamp invalid")
    if not _git_commit_binds(
        root,
        receipt["freeze_commit"],
        receipt["design_manifest"]["path"],
        receipt["design_manifest"]["sha256"],
    ):
        errors.append("signed freeze commit does not bind design manifest")
    if not _git_commit_binds(
        root,
        receipt["owner_decision_commit"],
        decision_descriptor["path"],
        decision_descriptor["sha256"],
    ):
        errors.append("signed owner decision commit does not bind decision")
    return sorted(set(errors))


def _known_denied_urls(root: Path, descriptor: dict[str, str]) -> set[str]:
    if not _bound(root, descriptor):
        return set()
    ledger = json.loads((root / descriptor["path"]).read_text(encoding="utf-8"))
    values = set(ledger.get("denied_urls", []))
    for entry in ledger.get("entries", []):
        for key in ("url", "landing_page_url"):
            if entry.get(key):
                values.add(entry[key])
        values.update(entry.get("urls", []))
    return {canonical_url(value) for value in values}


def verify_successor_bundle(
    root: Path, bundle: dict[str, Any], *, now: datetime | None = None
) -> list[str]:
    """Return every schema, binding, projection and fail-closed semantic error."""
    now = (now or datetime.now(UTC)).astimezone(UTC)
    errors = _validate_json(root, bundle, "successor-execution-bundle.schema.json")
    if errors:
        return sorted(set(errors))
    manifest_descriptor = bundle["query_manifest"]
    if not _bound(root, manifest_descriptor, exact=QUERY_MANIFEST):
        return ["successor query manifest binding mismatch"]
    manifest = json.loads((root / manifest_descriptor["path"]).read_text(encoding="utf-8"))
    manifest_errors = _validate_json(root, manifest, "successor-query-manifest.schema.json")
    if manifest_errors:
        return sorted(set(manifest_errors))
    if not _builder_equivalent(root, manifest):
        return ["successor query manifest builder equivalence mismatch"]
    errors.extend(_verify_detached_manifest(root, bundle["design_manifest"]))
    errors.extend(_verify_authority(root, bundle, now=now))
    plan = json.loads((root / DESIGN / "successor-plan.json").read_text())
    expected_bindings = {
        key: plan["failed_predecessor"][key]
        for key in (
            "execution_stop",
            "stop_receipt",
            "passive_exposure_annex",
            "stop_panel",
            "lineage_index",
            "prior_exposure_ledger",
        )
    }
    if bundle["lineage_bindings"] != expected_bindings:
        errors.append("lineage binding set mismatch")
    if any(not _bound(root, item) for item in bundle["lineage_bindings"].values()):
        errors.append("lineage artifact binding mismatch")
    expected_provider = dict(manifest["provider_config"])
    expected_provider["execution_date"] = bundle["execution_date"]
    if bundle["provider_config"] != expected_provider:
        errors.append("provider configuration mismatch")
    all_passive: list[dict[str, Any]] = []
    official_html: list[str] = []
    previous_finished: datetime | None = None
    try:
        generated_at = _parse_time(bundle["generated_at"])
        valid_from = _parse_time(bundle["authorized_interval"]["valid_from"])
        valid_until = _parse_time(bundle["authorized_interval"]["valid_until"])
        if generated_at > now:
            errors.append("bundle generated_at is in the future")
    except ValueError:
        return sorted(set(errors + ["bundle timestamp invalid"]))
    for expected, event in zip(manifest["queries"], bundle["query_events"], strict=True):
        if event["provider_call_order"] != expected["query_order"]:
            errors.append(f"query {expected['query_id']} provider-call isolation mismatch")
        for key in ("query_order", "query_id", "query_text", "language"):
            if event[key] != expected[key]:
                errors.append(f"query {expected['query_id']} {key} mismatch")
        try:
            started = _parse_time(event["provider_call_started_at"])
            finished = _parse_time(event["provider_call_finished_at"])
            captured_date = (
                started.astimezone(ZoneInfo(manifest["provider_config"]["timezone"]))
                .date()
                .isoformat()
            )
            if not (valid_from <= started <= finished <= valid_until):
                errors.append(f"query {expected['query_id']} outside authorized interval")
            if previous_finished is not None and started < previous_finished:
                errors.append(f"query {expected['query_id']} call timing is nonmonotonic")
            previous_finished = finished
            if finished > generated_at or finished > now:
                errors.append(f"query {expected['query_id']} call timing is in the future")
        except ValueError:
            errors.append(f"query {expected['query_id']} timestamp invalid")
            captured_date = ""
        if (
            event["searched_on"] != bundle["execution_date"]
            or event["searched_on"] != captured_date
        ):
            errors.append(f"query {expected['query_id']} searched_on mismatch")
        if event["query_sha256"] != expected["query_sha256"]:
            errors.append(f"query {expected['query_id']} digest mismatch")
        if event["result_count"] != len(event["results"]):
            errors.append(f"query {expected['query_id']} result count mismatch")
        if event["result_sha256"] != hashlib.sha256(_canonical(event["results"])).hexdigest():
            errors.append(f"query {expected['query_id']} result digest mismatch")
        if [item["rank"] for item in event["results"]] != list(range(1, len(event["results"]) + 1)):
            errors.append(f"query {expected['query_id']} result ranks invalid")
        for result in event["results"]:
            kind = classify_url(result["url"])
            domain = result_domain(result["url"])
            if result["url_kind"] != kind:
                errors.append(f"query {expected['query_id']} URL kind mismatch")
            if result["domain"] != domain:
                errors.append(f"query {expected['query_id']} result domain mismatch")
            official = _official_https_html(result["url"], expected["official_domain"])
            if result["official_host_candidate"] != (official is not None):
                errors.append(f"query {expected['query_id']} official-host flag mismatch")
            passive = {
                "url": canonical_url(result["url"]),
                "url_kind": kind,
                "requested": False,
            }
            all_passive.append(passive)
            if official is not None:
                official_html.append(official)
    projection = sorted(
        {json.dumps(item, sort_keys=True): item for item in all_passive}.values(),
        key=lambda item: (item["url"], item["url_kind"]),
    )
    if bundle["candidate_hypotheses"] != projection:
        errors.append("candidate hypothesis projection mismatch")
    if bundle["exposure_events"] != projection:
        errors.append("exposure projection mismatch")
    urls = sorted({item["url"] for item in projection})
    if bundle["non_overlap_receipt"]["checked_known_urls"] != urls:
        errors.append("known-URL non-overlap projection mismatch")
    denied = _known_denied_urls(root, expected_bindings["prior_exposure_ledger"])
    if set(urls) & denied:
        errors.append("candidate overlaps reconstructable predecessor exposure")
    if bundle["proposed_official_html_allowlist"] != sorted(set(official_html)):
        errors.append("official HTML allowlist projection mismatch")
    return sorted(set(errors))
