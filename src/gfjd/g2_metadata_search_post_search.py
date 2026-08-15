"""Network-disabled assembly controls for a future G2 successor search bundle."""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from gfjd.g2_metadata_search_successor import verify_successor_bundle

SCHEMA_ROOT = Path("data/methods/g2/G2HOLDOUT-METADATA-SEARCH-POSTRUN-20260816-01/schemas")
RECEIPT_SCHEMA = SCHEMA_ROOT / "g2_metadata_search_post_search_receipt.schema.json"
STOP_SCHEMA = SCHEMA_ROOT / "g2_metadata_search_post_search_stop.schema.json"
PANEL_SCHEMA = SCHEMA_ROOT / "g2_metadata_search_post_search_panel_input.schema.json"
BOUNDARY_SCHEMA = SCHEMA_ROOT / "g2_metadata_search_post_search_registrar_boundary.schema.json"
EVENT_LOG_SCHEMA = SCHEMA_ROOT / "g2_metadata_search_post_search_registrar_event_log.schema.json"
ATTESTATION_SCHEMA = SCHEMA_ROOT / "g2_metadata_search_post_search_commit_attestation.schema.json"
ZERO_BOUNDARIES = (
    "result_url_requests",
    "landing_page_requests",
    "source_file_requests",
    "head_requests",
    "redirects_followed",
    "persisted_snippets",
    "persisted_source_excerpts",
    "persisted_target_facts",
)


class PostSearchVerificationError(ValueError):
    """Raised when a registrar artifact cannot enter post-search assembly."""

    def __init__(self, errors: list[str]) -> None:
        self.errors = tuple(sorted(set(errors)))
        super().__init__("; ".join(self.errors))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def _parse_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("timestamp lacks timezone offset")
    return parsed.astimezone(UTC)


def _safe_repository_file(root: Path, relative: str) -> Path | None:
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
        current = current / part
        if current.is_symlink():
            return None
    return path if path.is_file() else None


def artifact(root: Path, relative: str) -> dict[str, str]:
    """Create a descriptor only for a safe, existing repository file."""
    path = _safe_repository_file(root, relative)
    if path is None:
        raise PostSearchVerificationError(["unsafe or missing repository artifact"])
    return {"path": relative, "sha256": _sha(path)}


def _read_bound(root: Path, descriptor: dict[str, str]) -> dict[str, Any]:
    errors = _descriptor_errors(root, descriptor)
    if errors:
        raise PostSearchVerificationError(errors)
    path = root / descriptor["path"]
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise PostSearchVerificationError(["artifact is not a JSON object"])
    return value


def _descriptor_errors(root: Path, descriptor: dict[str, str]) -> list[str]:
    if not isinstance(descriptor, dict):
        return ["artifact descriptor is not an object"]
    if set(descriptor) != {"path", "sha256"}:
        return ["artifact descriptor fields mismatch"]
    relative = descriptor.get("path")
    digest = descriptor.get("sha256", "")
    if not isinstance(relative, str) or not isinstance(digest, str):
        return ["artifact descriptor value type mismatch"]
    path = _safe_repository_file(root, relative)
    if path is None or _sha(path) != digest:
        return ["artifact binding mismatch"]
    return []


def _schema_errors(root: Path, schema_path: Path, value: dict[str, Any]) -> list[str]:
    schema = json.loads((root / schema_path).read_text(encoding="utf-8"))
    return [
        error.message
        for error in Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(value)
    ]


def _zero_boundary_errors(bundle: dict[str, Any]) -> list[str]:
    errors = []
    for field in ZERO_BOUNDARIES:
        if bundle.get(field) != 0:
            errors.append(f"registrar boundary is nonzero or missing: {field}")
    if bundle.get("violations") != []:
        errors.append("registrar reports violations")
    return errors


def _execution_identity(bundle: dict[str, Any]) -> dict[str, Any]:
    return {
        "bundle_id": bundle.get("bundle_id"),
        "execution_date": bundle.get("execution_date"),
        "tool_name": bundle.get("tool_name"),
        "tool_version": bundle.get("tool_version"),
        "query_manifest": bundle.get("query_manifest"),
        "design_manifest": bundle.get("design_manifest"),
        "authority_receipt": bundle.get("authority_receipt"),
    }


def _registrar_boundary_errors(
    bundle: dict[str, Any],
    bundle_descriptor: dict[str, str],
    boundary: dict[str, Any],
    event_log_descriptor: dict[str, str],
) -> list[str]:
    events = bundle.get("query_events")
    if not isinstance(events, list) or not events:
        return ["registrar query-event transcript is missing"]
    identity = _execution_identity(bundle)
    expected = {
        "registrar_bundle": bundle_descriptor,
        "registrar_event_log": event_log_descriptor,
        "run_id": bundle.get("bundle_id"),
        "execution_identity": identity,
        "execution_identity_sha256": hashlib.sha256(_canonical(identity)).hexdigest(),
        "provider_config_sha256": hashlib.sha256(
            _canonical(bundle.get("provider_config"))
        ).hexdigest(),
        "query_event_transcript_sha256": hashlib.sha256(_canonical(events)).hexdigest(),
        "first_provider_call_started_at": events[0].get("provider_call_started_at"),
        "last_provider_call_finished_at": events[-1].get("provider_call_finished_at"),
        "search_provider_calls": bundle.get("successor_provider_calls"),
        "logical_queries_submitted": bundle.get("successor_logical_query_submissions"),
        "successor_retries": bundle.get("successor_retries"),
        "prior_lineage_submissions": bundle.get("prior_lineage_submissions"),
        "cumulative_lineage_submissions": bundle.get("cumulative_lineage_submissions"),
        "violations": bundle.get("violations"),
        **{field: bundle.get(field) for field in ZERO_BOUNDARIES},
    }
    errors = []
    for field, expected_value in expected.items():
        if boundary.get(field) != expected_value:
            errors.append(f"registrar boundary cross-check mismatch: {field}")
    if boundary.get("non_search_network_requests") != 0:
        errors.append("registrar boundary reports non-search network requests")
    if boundary.get("outbound_contacts") != 0:
        errors.append("registrar boundary reports outbound contacts")
    if boundary.get("candidate_content_opened") is not False:
        errors.append("registrar boundary reports candidate content access")
    if boundary.get("source_content_opened") is not False:
        errors.append("registrar boundary reports source content access")
    if boundary.get("violations") != []:
        errors.append("registrar boundary reports violations")
    return errors


def _event_log_errors(
    bundle: dict[str, Any],
    bundle_descriptor: dict[str, str],
    event_log: dict[str, Any],
) -> list[str]:
    errors = []
    events = bundle.get("query_events", [])
    logged = event_log.get("events", [])
    if event_log.get("registrar_bundle") != bundle_descriptor:
        errors.append("registrar event log bundle binding mismatch")
    if event_log.get("run_id") != bundle.get("bundle_id"):
        errors.append("registrar event log run identity mismatch")
    if len(events) != 208 or len(logged) != 209:
        errors.append("registrar event log length mismatch")
        return errors
    previous: datetime | None = None
    for order, (source, recorded) in enumerate(zip(events, logged[:208], strict=True), start=1):
        expected = {
            "event_order": order,
            "occurred_at": source.get("provider_call_finished_at"),
            "event_type": "search_provider_call_completed",
            "query_id": source.get("query_id"),
            "non_search_network_requests": 0,
            "result_url_requests": 0,
            "landing_page_requests": 0,
            "source_file_requests": 0,
            "head_requests": 0,
            "redirects_followed": 0,
            "outbound_contacts": 0,
            "candidate_content_opened": False,
            "source_content_opened": False,
        }
        if recorded != expected:
            errors.append(f"registrar event log projection mismatch: {order}")
        try:
            occurred = _parse_time(recorded["occurred_at"])
            if previous is not None and occurred < previous:
                errors.append(f"registrar event log timing is nonmonotonic: {order}")
            previous = occurred
        except (KeyError, TypeError, ValueError):
            errors.append(f"registrar event log timestamp invalid: {order}")
    closure = logged[-1]
    expected_closure = {
        "event_order": 209,
        "occurred_at": event_log.get("generated_at"),
        "event_type": "boundary_closed",
        "query_id": None,
        "non_search_network_requests": 0,
        "result_url_requests": 0,
        "landing_page_requests": 0,
        "source_file_requests": 0,
        "head_requests": 0,
        "redirects_followed": 0,
        "outbound_contacts": 0,
        "candidate_content_opened": False,
        "source_content_opened": False,
    }
    if closure != expected_closure:
        errors.append("registrar event log boundary closure mismatch")
    try:
        if previous is not None and _parse_time(closure["occurred_at"]) < previous:
            errors.append("registrar event log boundary closure is backdated")
    except (KeyError, TypeError, ValueError):
        errors.append("registrar event log boundary timestamp invalid")
    return errors


def _git_commit_blob_matches(root: Path, commit: str, descriptor: dict[str, str]) -> bool:
    blob = subprocess.run(
        ["git", "show", f"{commit}:{descriptor['path']}"], cwd=root, capture_output=True
    )
    return blob.returncode == 0 and hashlib.sha256(blob.stdout).hexdigest() == descriptor["sha256"]


def _signed_attestation_errors(
    root: Path,
    attestation: dict[str, Any],
    *,
    bundle_descriptor: dict[str, str],
    boundary_descriptor: dict[str, str],
    event_log_descriptor: dict[str, str],
    owner_decision_commit: str,
) -> list[str]:
    errors = []
    expected = {
        "registrar_bundle": bundle_descriptor,
        "registrar_boundary_receipt": boundary_descriptor,
        "registrar_event_log": event_log_descriptor,
        "event_log_sha256": event_log_descriptor["sha256"],
        "required_ancestor_commit": owner_decision_commit,
    }
    for field, value in expected.items():
        if attestation.get(field) != value:
            errors.append(f"post-execution attestation mismatch: {field}")
    commit = attestation.get("attested_commit", "")
    object_type = subprocess.run(
        ["git", "cat-file", "-t", commit], cwd=root, capture_output=True, text=True
    )
    if object_type.returncode != 0 or object_type.stdout.strip() != "commit":
        errors.append("post-execution attestation object is not a commit")
        return errors
    signature = subprocess.run(
        ["git", "verify-commit", commit], cwd=root, capture_output=True, text=True
    )
    if signature.returncode != 0:
        errors.append("post-execution attestation commit signature is invalid")
    for descriptor in (bundle_descriptor, boundary_descriptor, event_log_descriptor):
        if not _git_commit_blob_matches(root, commit, descriptor):
            errors.append(f"post-execution commit blob mismatch: {descriptor['path']}")
    ancestry = subprocess.run(
        ["git", "merge-base", "--is-ancestor", owner_decision_commit, commit],
        cwd=root,
        capture_output=True,
    )
    if ancestry.returncode != 0:
        errors.append("post-execution commit does not descend from owner decision")
    return errors


def build_verified_receipt(
    root: Path,
    bundle_descriptor: dict[str, str],
    boundary_descriptor: dict[str, str],
    event_log_descriptor: dict[str, str],
    attestation_descriptor: dict[str, str],
    *,
    generated_at: str,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Verify an immutable registrar bundle and build an advisory-only receipt."""
    now = (now or datetime.now(UTC)).astimezone(UTC)
    bundle = _read_bound(root, bundle_descriptor)
    boundary = _read_bound(root, boundary_descriptor)
    event_log = _read_bound(root, event_log_descriptor)
    attestation = _read_bound(root, attestation_descriptor)
    errors = _zero_boundary_errors(bundle)
    errors.extend(_schema_errors(root, BOUNDARY_SCHEMA, boundary))
    errors.extend(_schema_errors(root, EVENT_LOG_SCHEMA, event_log))
    errors.extend(_schema_errors(root, ATTESTATION_SCHEMA, attestation))
    errors.extend(
        _registrar_boundary_errors(bundle, bundle_descriptor, boundary, event_log_descriptor)
    )
    errors.extend(_event_log_errors(bundle, bundle_descriptor, event_log))
    if boundary.get("registrar_session_id") != event_log.get("registrar_session_id"):
        errors.append("registrar session identity mismatch")
    if boundary.get("run_id") != event_log.get("run_id"):
        errors.append("registrar run identity mismatch")
    authority = _read_bound(root, bundle["authority_receipt"])
    errors.extend(
        _signed_attestation_errors(
            root,
            attestation,
            bundle_descriptor=bundle_descriptor,
            boundary_descriptor=boundary_descriptor,
            event_log_descriptor=event_log_descriptor,
            owner_decision_commit=authority.get("owner_decision_commit", ""),
        )
    )
    if attestation.get("registrar_session_id") != event_log.get("registrar_session_id"):
        errors.append("attested registrar session identity mismatch")
    if attestation.get("run_id") != event_log.get("run_id"):
        errors.append("attested registrar run identity mismatch")
    errors.extend(verify_successor_bundle(root, bundle, now=now))
    try:
        generated = _parse_time(generated_at)
        registrar_generated = _parse_time(bundle["generated_at"])
        boundary_generated = _parse_time(boundary["generated_at"])
        event_log_generated = _parse_time(event_log["generated_at"])
        attestation_generated = _parse_time(attestation["generated_at"])
        signature_verified = _parse_time(attestation["signature"]["verified_at"])
        if not (
            registrar_generated
            <= event_log_generated
            <= boundary_generated
            <= signature_verified
            <= attestation_generated
            <= generated
            <= now
        ):
            errors.append("post-search receipt timestamp is inconsistent or future")
    except (KeyError, TypeError, ValueError):
        errors.append("post-search receipt timestamp is invalid")
    if errors:
        raise PostSearchVerificationError(errors)
    receipt = {
        "schema_version": "1.0",
        "receipt_id": "G2-METADATA-SEARCH-POST-SEARCH-VERIFICATION",
        "generated_at": generated_at,
        "registrar_bundle": bundle_descriptor,
        "registrar_boundary_receipt": boundary_descriptor,
        "registrar_event_log": event_log_descriptor,
        "post_execution_commit_attestation": attestation_descriptor,
        "query_manifest": bundle["query_manifest"],
        "design_manifest": bundle["design_manifest"],
        "authority_receipt": bundle["authority_receipt"],
        "immutable_bindings_reverified": True,
        "successor_semantic_verification": "passed",
        "boundary_counts": {field: 0 for field in ZERO_BOUNDARIES},
        "outbound_contacts": 0,
        "candidate_content_opened": False,
        "source_content_opened": False,
        "panel_inputs_allowed": True,
        "status": "verified_for_advisory_panel_only",
        "g2_passage": False,
    }
    errors = _schema_errors(root, RECEIPT_SCHEMA, receipt)
    if errors:
        raise PostSearchVerificationError(errors)
    return receipt


def verify_receipt(
    root: Path, receipt: dict[str, Any], *, now: datetime | None = None
) -> list[str]:
    """Reverify a post-search receipt and its complete upstream bundle."""
    errors = _schema_errors(root, RECEIPT_SCHEMA, receipt)
    if errors:
        return sorted(set(errors))
    try:
        rebuilt = build_verified_receipt(
            root,
            receipt["registrar_bundle"],
            receipt["registrar_boundary_receipt"],
            receipt["registrar_event_log"],
            receipt["post_execution_commit_attestation"],
            generated_at=receipt["generated_at"],
            now=now,
        )
    except PostSearchVerificationError as exc:
        return list(exc.errors)
    if rebuilt != receipt:
        errors.append("post-search receipt projection mismatch")
    return sorted(set(errors))


def build_panel_input_index(
    root: Path,
    receipt_descriptor: dict[str, str],
    *,
    generated_at: str,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Build a descriptor-only panel packet without opening candidate content."""
    now = (now or datetime.now(UTC)).astimezone(UTC)
    receipt = _read_bound(root, receipt_descriptor)
    errors = verify_receipt(root, receipt, now=now)
    if errors:
        raise PostSearchVerificationError(errors)
    panel = {
        "schema_version": "1.0",
        "panel_input_id": "G2-METADATA-SEARCH-POST-SEARCH-PANEL-INPUT",
        "generated_at": generated_at,
        "post_search_receipt": receipt_descriptor,
        "registrar_bundle": receipt["registrar_bundle"],
        "registrar_boundary_receipt": receipt["registrar_boundary_receipt"],
        "registrar_event_log": receipt["registrar_event_log"],
        "post_execution_commit_attestation": receipt["post_execution_commit_attestation"],
        "query_manifest": receipt["query_manifest"],
        "design_manifest": receipt["design_manifest"],
        "authority_receipt": receipt["authority_receipt"],
        "panel_roles": [
            "methods_consistency_adviser",
            "exposure_boundary_adviser",
            "governance_risk_adviser",
        ],
        "descriptor_only": True,
        "network_access": False,
        "candidate_content_opened": False,
        "source_content_opened": False,
        "advisory_only": True,
        "owner_decision_required": True,
        "g2_passage": False,
    }
    try:
        if not (_parse_time(receipt["generated_at"]) <= _parse_time(generated_at) <= now):
            raise PostSearchVerificationError(["panel input predates verification receipt"])
    except (TypeError, ValueError) as exc:
        raise PostSearchVerificationError(["panel input timestamp is invalid"]) from exc
    errors = _schema_errors(root, PANEL_SCHEMA, panel)
    if errors:
        raise PostSearchVerificationError(errors)
    return panel


def verify_panel_input_index(
    root: Path, panel: dict[str, Any], *, now: datetime | None = None
) -> list[str]:
    """Rebuild a descriptor-only panel input and reject every projection drift."""
    errors = _schema_errors(root, PANEL_SCHEMA, panel)
    if errors:
        return sorted(set(errors))
    try:
        rebuilt = build_panel_input_index(
            root,
            panel["post_search_receipt"],
            generated_at=panel["generated_at"],
            now=now,
        )
    except PostSearchVerificationError as exc:
        return list(exc.errors)
    if rebuilt != panel:
        errors.append("panel input projection mismatch")
    return sorted(set(errors))


def build_stop_receipt(
    root: Path,
    bundle_descriptor: dict[str, str],
    *,
    errors: list[str],
    generated_at: str,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Build a terminal record for a failed post-search verification attempt."""
    if not errors or any(not isinstance(error, str) or not error for error in errors):
        raise PostSearchVerificationError(["stop receipt requires explicit errors"])
    descriptor_errors = _descriptor_errors(root, bundle_descriptor)
    if descriptor_errors:
        raise PostSearchVerificationError(descriptor_errors)
    now = (now or datetime.now(UTC)).astimezone(UTC)
    path = root / bundle_descriptor["path"]
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        bundle = value if isinstance(value, dict) else {}
    except (UnicodeDecodeError, json.JSONDecodeError):
        bundle = {}
    try:
        generated = _parse_time(generated_at)
        if generated > now:
            raise ValueError("future stop")
        if "generated_at" in bundle and generated < _parse_time(bundle["generated_at"]):
            raise ValueError("backdated stop")
    except ValueError as exc:
        raise PostSearchVerificationError(["stop receipt timestamp is invalid"]) from exc
    normalized = {
        field: value if isinstance((value := bundle.get(field)), int) and value >= 0 else -1
        for field in ZERO_BOUNDARIES
    }
    boundary_violation = any(value != 0 for value in normalized.values())
    receipt = {
        "schema_version": "1.0",
        "stop_id": "G2-METADATA-SEARCH-POST-SEARCH-STOP",
        "generated_at": generated_at,
        "registrar_bundle": bundle_descriptor,
        "errors": sorted(set(errors)),
        "observed_boundary_counts": normalized,
        "boundary_violation_or_unknown": boundary_violation,
        "harness_network_access": False,
        "harness_outbound_contacts": 0,
        "candidate_content_opened": False,
        "source_content_opened": False,
        "panel_inputs_allowed": False,
        "terminal": True,
        "status": "stopped_fail_closed",
        "g2_passage": False,
    }
    schema_errors = _schema_errors(root, STOP_SCHEMA, receipt)
    if schema_errors:
        raise PostSearchVerificationError(schema_errors)
    return receipt


def verify_stop_receipt(
    root: Path, receipt: dict[str, Any], *, now: datetime | None = None
) -> list[str]:
    errors = _schema_errors(root, STOP_SCHEMA, receipt)
    if errors:
        return sorted(set(errors))
    try:
        rebuilt = build_stop_receipt(
            root,
            receipt["registrar_bundle"],
            errors=receipt["errors"],
            generated_at=receipt["generated_at"],
            now=now,
        )
    except PostSearchVerificationError as exc:
        return list(exc.errors)
    if rebuilt != receipt:
        errors.append("stop receipt projection mismatch")
    return sorted(set(errors))
