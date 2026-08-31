"""Validate supplied design events against unchanged, hash-bound OpenLineage 2-0-2.

No filesystem, network, execution or factual verification occurs. The stricter
GFJD preparation profile excludes runtime events, unknown fields and nonempty
facets. Producers use HTTPS DNS URLs without userinfo; timestamps exclude leap
seconds and unknown offsets. Structural success is not full conformance.
"""

import hashlib
import json
import math
import re
from datetime import datetime
from typing import Any, cast
from urllib.parse import urlsplit

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import ValidationError
from referencing import Registry, Resource
from referencing.exceptions import NoSuchResource

SCHEMA_URL = "https://openlineage.io/spec/2-0-2/OpenLineage.json"
SCHEMA_SHA256 = "69f68bee00b9beac88a87059c0102410e7bb05f3f43c46d02a0409831eceb0d2"
MAX_BYTES = 1024 * 1024
MAX_DEPTH = 16
MAX_NODES = 10000
MAX_ITEMS = 1000
MAX_STRING = 4096


class FederationError(ValueError):
    """Invalid federation input."""


def _require(condition: bool) -> None:
    if not condition:
        raise FederationError("federation design-event contract violation")


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    _require(len(pairs) <= MAX_ITEMS)
    result: dict[str, Any] = {}
    for key, value in pairs:
        _require(key not in result)
        result[key] = value
    return result


def _constant(value: str) -> None:
    raise FederationError("federation design-event contract violation")


def _parse(raw: bytes) -> dict[str, Any]:
    _require(type(raw) is bytes and 0 < len(raw) <= MAX_BYTES)
    value = json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs, parse_constant=_constant)
    stack = [(value, 0)]
    nodes = 0
    while stack:
        item, depth = stack.pop()
        nodes += 1
        _require(nodes <= MAX_NODES and depth <= MAX_DEPTH)
        if isinstance(item, dict):
            _require(len(item) <= MAX_ITEMS)
            stack.extend((part, depth + 1) for pair in item.items() for part in pair)
        elif isinstance(item, list):
            _require(len(item) <= MAX_ITEMS)
            stack.extend((part, depth + 1) for part in item)
        elif isinstance(item, str):
            _require(len(item) <= MAX_STRING)
            _require(
                all(
                    ord(c) >= 32 and not 127 <= ord(c) <= 159 and not 0xD800 <= ord(c) <= 0xDFFF
                    for c in item
                )
            )
        elif isinstance(item, float):
            _require(math.isfinite(item))
    _require(isinstance(value, dict))
    return cast(dict[str, Any], value)


def _deny_resource(uri: str) -> Resource[Any]:
    raise NoSuchResource(uri)


def _formats() -> FormatChecker:
    checker = FormatChecker()

    @checker.checks("date-time", raises=ValueError)
    def timestamp(value: Any) -> bool:
        if not isinstance(value, str):
            return True
        if not re.fullmatch(
            r"[0-9]{4}-[0-9]{2}-[0-9]{2}[Tt](?:[01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]"
            r"(?:\.[0-9]+)?(?:[Zz]|[+-](?:[01][0-9]|2[0-3]):[0-5][0-9])",
            value,
        ):
            return False
        return datetime.fromisoformat(value.upper().replace("Z", "+00:00")).tzinfo is not None

    @checker.checks("uri", raises=ValueError)
    def uri(value: Any) -> bool:
        if not isinstance(value, str):
            return True
        return (
            bool(re.match(r"[A-Za-z][A-Za-z0-9+.-]*:", value))
            and bool(urlsplit(value).scheme)
            and not any(c.isspace() or ord(c) > 127 for c in value)
            and not re.search(r"%(?![0-9A-Fa-f]{2})", value)
        )

    return checker


def _entity(value: dict[str, Any], *, direction: str = "") -> None:
    allowed = {"namespace", "name", "facets"}
    if direction:
        allowed.add(direction + "Facets")
    _require(set(value) <= allowed)
    for field in ("name", "namespace"):
        _require(bool(value[field].strip()))
    for key in ("facets", "inputFacets", "outputFacets"):
        _require(key not in value or value[key] == {})


def validate_design_event(event_bytes: bytes, schema_bytes: bytes) -> dict[str, Any]:
    """Return deterministic structural/profile evidence; invalid inputs raise FederationError."""
    try:
        _require(type(schema_bytes) is bytes and 0 < len(schema_bytes) <= MAX_BYTES)
        _require(hashlib.sha256(schema_bytes).hexdigest() == SCHEMA_SHA256)
        schema = _parse(schema_bytes)
        event = _parse(event_bytes)
        _require(event.get("schemaURL") == SCHEMA_URL)
        # Deliberately narrow URI profile: no guessing missing optional format
        # packages, no opaque producer labels, credentials or arbitrary schemes.
        producer = event.get("producer")
        _require(isinstance(producer, str))
        producer = cast(str, producer)
        _require(
            re.fullmatch(
                r"https://[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?"
                r"(?::[0-9]{1,5})?(?:[/?#][A-Za-z0-9._~:/?#@!$&'()*+,;=%-]*)?",
                producer,
            )
            is not None
        )
        parsed_producer = urlsplit(producer)
        _require(producer.count("#") <= 1)
        _require(parsed_producer.port is None or 1 <= parsed_producer.port <= 65535)
        _require(
            all(
                re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?", label)
                for label in (parsed_producer.hostname or "").split(".")
            )
        )
        _require(not str(event.get("eventTime", "")).endswith("-00:00"))
        registry: Registry[Any] = Registry(retrieve=_deny_resource).with_resource(  # type: ignore[call-arg]
            SCHEMA_URL, Resource.from_contents(schema)
        )
        Draft202012Validator(schema, registry=registry, format_checker=_formats()).validate(event)
        _require(
            set(event)
            <= {"eventTime", "producer", "schemaURL", "job", "dataset", "inputs", "outputs"}
        )
        _require(("job" in event) != ("dataset" in event))
        kind = "JobEvent" if "job" in event else "DatasetEvent"
        if kind == "DatasetEvent":
            _require("inputs" not in event and "outputs" not in event)
        _entity(event["job"] if kind == "JobEvent" else event["dataset"])
        for field, direction in (("inputs", "input"), ("outputs", "output")):
            for entity in event.get(field, []):
                _entity(entity, direction=direction)
        return {
            "contract_version": "gfjd-federation-design-event-v1",
            "event_sha256": hashlib.sha256(event_bytes).hexdigest(),
            "schema_sha256": SCHEMA_SHA256,
            "schema_validated": True,
            "profile": "design_event_only",
            "event_kind": kind,
            "factual_evidence": "unverified",
            "full_conformance": "unverified",
            "authority": dict.fromkeys(
                (
                    "network",
                    "source_access",
                    "publication",
                    "release",
                    "rights_clearance",
                    "custody",
                    "gold_promotion",
                    "gate_acceptance",
                    "partner_registration",
                ),
                False,
            ),
        }
    except FederationError:
        raise
    except (ValueError, TypeError, KeyError, RecursionError, ValidationError):
        # ValidationError contains the rejected document. Ordinary tracebacks
        # must not disclose it merely because the outer error text is fixed.
        raise FederationError("federation design-event contract violation") from None
