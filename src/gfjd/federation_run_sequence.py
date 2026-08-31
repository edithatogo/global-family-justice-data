"""Bounded GFJD supplied RunEvent sequence profile; not observed execution.

Only this module's implementation fingerprint reads a file. Supplied identifiers
are never resolved; no input loader or execution facility exists. The unchanged
OpenLineage schema is evaluated locally in addition to this narrower profile.
"""

import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource
from referencing.exceptions import NoSuchResource

from gfjd.federation_metadata import MetadataError, parse_json, require, safe_url
from gfjd.federation_openlineage import SCHEMA_SHA256, SCHEMA_URL

VERSION = "gfjd-openlineage-run-sequence-v1"
TERMINALS = frozenset({"COMPLETE", "FAIL", "ABORT"})


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _deny(uri: str) -> Any:
    raise NoSuchResource(uri)


def _time(value: Any) -> datetime:
    require(isinstance(value, str))
    require(
        re.fullmatch(
            r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}"
            r"(?:\.[0-9]{1,6})?(?:Z|[+-][0-9]{2}:[0-9]{2})",
            value,
        )
        is not None
    )
    require(not value.endswith("-00:00"))
    if not value.endswith("Z"):
        require(int(value[-5:-3]) <= 23 and int(value[-2:]) <= 59)
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


def _entity(value: Any, direction: str | None = None) -> tuple[str, str]:
    require(isinstance(value, dict))
    allowed = {"namespace", "name", "facets"}
    if direction is not None:
        allowed.add(direction + "Facets")
    require({"namespace", "name"} <= set(value) <= allowed)
    for key in ("namespace", "name"):
        require(isinstance(value[key], str) and bool(value[key].strip()))
    for key in allowed - {"namespace", "name"}:
        require(key not in value or value[key] == {})
    return value["namespace"], value["name"]


def _assess(raw: bytes, expected_sha: str, schema_raw: bytes) -> dict[str, Any]:
    require(type(raw) is bytes and 0 < len(raw) <= 1024 * 1024)
    require(
        isinstance(expected_sha, str) and re.fullmatch(r"[0-9a-f]{64}", expected_sha) is not None
    )
    require(_sha(raw) == expected_sha)
    envelope = parse_json(raw)
    require(isinstance(envelope, dict) and set(envelope) == {"contract_version", "events"})
    require(envelope["contract_version"] == VERSION)
    events = envelope["events"]
    require(isinstance(events, list) and 2 <= len(events) <= 256)
    require(type(schema_raw) is bytes and 0 < len(schema_raw) <= 1024 * 1024)
    require(_sha(schema_raw) == SCHEMA_SHA256)
    schema = parse_json(schema_raw)
    registry: Registry[Any] = Registry(retrieve=_deny).with_resource(  # type: ignore[call-arg]
        SCHEMA_URL, Resource.from_contents(schema)
    )
    validator = Draft202012Validator(schema, registry=registry, format_checker=FormatChecker())
    identity = None
    previous_time = None
    terminal_index = None
    terminal_type = None
    hashes: list[str] = []
    event_types: list[str] = []
    datasets: dict[tuple[str, str, str], list[int]] = {}
    for index, event in enumerate(events):
        require(isinstance(event, dict))
        required = {"eventTime", "producer", "schemaURL", "eventType", "run", "job"}
        require(required <= set(event) <= required | {"inputs", "outputs"})
        require(event["schemaURL"] in (SCHEMA_URL, SCHEMA_URL + "#/$defs/RunEvent"))
        producer = safe_url(event["producer"])
        run = event["run"]
        require(isinstance(run, dict) and {"runId"} <= set(run) <= {"runId", "facets"})
        require("facets" not in run or run["facets"] == {})
        run_id = run["runId"]
        require(
            isinstance(run_id, str)
            and re.fullmatch(
                r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", run_id
            )
            is not None
        )
        namespace, name = _entity(event["job"])
        current_identity = (run_id, namespace, name, producer)
        require(identity is None or identity == current_identity)
        identity = current_identity
        timestamp = _time(event["eventTime"])
        require(previous_time is None or timestamp >= previous_time)
        previous_time = timestamp
        kind = event["eventType"]
        require(isinstance(kind, str))
        if index == 0:
            require(kind == "START")
        elif terminal_index is not None:
            require(kind == "OTHER")
        elif kind in TERMINALS:
            terminal_index, terminal_type = index, kind
        else:
            require(kind in {"RUNNING", "OTHER"})
        digest = _sha(_canonical(event))
        require(digest not in hashes)
        hashes.append(digest)
        event_types.append(kind)
        for direction in ("input", "output"):
            declarations = event.get(direction + "s", [])
            require(isinstance(declarations, list) and len(declarations) <= 100)
            seen = set()
            for declaration in declarations:
                pair = _entity(declaration, direction)
                require(pair not in seen)
                seen.add(pair)
                datasets.setdefault((direction, *pair), []).append(index)
        validator.validate(event)
    require(terminal_index is not None and identity is not None)
    assert terminal_index is not None and identity is not None
    return {
        "contract_version": "gfjd-openlineage-run-sequence-report-v1",
        "profile": VERSION,
        "sequence_profile_validated": True,
        "schema_validated": True,
        "sequence_sha256": expected_sha,
        "schema_sha256": SCHEMA_SHA256,
        "implementation_sha256": _sha(Path(__file__).read_bytes()),
        "run_id": identity[0],
        "job_namespace": identity[1],
        "job_name": identity[2],
        "producer": identity[3],
        "declared_terminal_type": terminal_type,
        "terminal_index": terminal_index,
        "event_count": len(events),
        "event_types": event_types,
        "canonical_event_sha256": hashes,
        "datasets": [
            {
                "direction": direction,
                "namespace": namespace,
                "name": name,
                "event_indices": indices,
                "event_types": [event_types[i] for i in indices],
                "post_terminal_only": all(i > terminal_index for i in indices),
            }
            for (direction, namespace, name), indices in sorted(datasets.items())
        ],
        "execution_observed": False,
        "production_verified": False,
        "factual_evidence": "unverified",
        "source_truth": "unverified",
        "full_conformance": "unverified",
        "coverage": "bounded-single-run-declared-lifecycle-profile-only",
        "limitations": [
            "empty-facets-only",
            "microsecond-offset-timestamps-only",
            "declared-dataset-membership-not-observed-input-or-production",
            "no-replay-association-or-execution-authentication",
        ],
        "filesystem_access": "implementation-fingerprint-only",
        "authority": dict.fromkeys(
            (
                "network",
                "source_access",
                "publication",
                "release",
                "rights_clearance",
                "custody",
                "gold_promotion",
                "maturity",
                "gate_acceptance",
                "partner_registration",
                "execution",
            ),
            False,
        ),
    }


def assess_run_sequence(
    sequence_raw: bytes, expected_sequence_sha256: str, schema_raw: bytes
) -> dict[str, Any]:
    """Validate declared lifecycle without resolving resources or observing a run."""
    try:
        return _assess(sequence_raw, expected_sequence_sha256, schema_raw)
    except Exception:
        raise MetadataError("Run sequence profile contract violation") from None


def verify_run_sequence(
    sequence_raw: bytes, expected_sequence_sha256: str, schema_raw: bytes, report: dict[str, Any]
) -> None:
    """Independently recompute every report field, rejecting boolean/integer aliases."""
    try:
        expected = assess_run_sequence(sequence_raw, expected_sequence_sha256, schema_raw)
        require(type(report) is dict and _canonical(report) == _canonical(expected))
    except Exception:
        raise MetadataError("Run sequence profile contract violation") from None
