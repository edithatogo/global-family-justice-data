"""Bounded aggregate API projection for private replay.

The adapter accepts only the frozen DataJud-style aggregation contract.  It
rejects case-level fields, approximate buckets, duplicate JSON keys and any
unexpected response structure.  The receipt is a reproducible supporting
artifact; it never authorizes layer promotion, publication or release.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

VERSION = "gfjd-medallion-api-aggregate-v1"
MAX_SOURCE_BYTES = 2 * 1024 * 1024
MAX_BUCKETS = 20
CONTRACT_KEYS = frozenset(
    {"extraction_version", "source_sha256", "request", "class_code", "class_name"}
)
FROZEN_CLASS_CODE = 1389
FROZEN_CLASS_NAME = "Ação de Alimentos"


class MedallionApiError(ValueError):
    """Fail-closed aggregate API extraction error."""


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode()


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise MedallionApiError("duplicate JSON key")
        result[key] = value
    return result


def _require(condition: bool, message: str = "medallion API contract violation") -> None:
    if not condition:
        raise MedallionApiError(message)


def extract_aggregate(source: bytes, contract: dict[str, Any]) -> dict[str, Any]:
    """Extract one exact aggregate bucket from one exact response body."""
    try:
        _require(isinstance(source, bytes) and 0 < len(source) <= MAX_SOURCE_BYTES)
        _require(isinstance(contract, dict) and set(contract) == CONTRACT_KEYS)
        _require(contract["extraction_version"] == VERSION)
        _require(contract["source_sha256"] == _sha(source), "source digest mismatch")
        request = contract["request"]
        _require(isinstance(request, dict) and bool(request))
        request_sha256 = _sha(_canonical(request))
        class_code = contract["class_code"]
        _require(class_code == FROZEN_CLASS_CODE)
        class_name = contract["class_name"]
        _require(class_name == FROZEN_CLASS_NAME)
        payload = json.loads(
            source.decode("utf-8"),
            object_pairs_hook=_unique_object,
            parse_constant=lambda _: (_ for _ in ()).throw(MedallionApiError("non-finite JSON")),
        )
        _require(isinstance(payload, dict))
        _require(set(payload) == {"took", "timed_out", "_shards", "hits", "aggregations"})
        _require(type(payload["took"]) is int and payload["took"] >= 0)
        _require(payload["timed_out"] is False)
        shards = payload["_shards"]
        _require(
            isinstance(shards, dict) and set(shards) <= {"total", "successful", "skipped", "failed"}
        )
        _require(type(shards.get("total")) is int and shards["total"] > 0)
        _require(type(shards.get("successful")) is int and shards["successful"] == shards["total"])
        _require(type(shards.get("failed")) is int and shards["failed"] == 0)
        hits = payload["hits"]
        _require(isinstance(hits, dict) and set(hits) <= {"total", "max_score", "hits"})
        _require(hits.get("hits") == [] and hits.get("max_score") is None)
        aggregation = payload["aggregations"]
        _require(isinstance(aggregation, dict) and set(aggregation) == {"case_classes"})
        terms = aggregation["case_classes"]
        _require(
            isinstance(terms, dict)
            and set(terms) == {"doc_count_error_upper_bound", "sum_other_doc_count", "buckets"}
        )
        _require(terms["doc_count_error_upper_bound"] == 0 and terms["sum_other_doc_count"] == 0)
        buckets = terms["buckets"]
        _require(isinstance(buckets, list) and 0 < len(buckets) <= MAX_BUCKETS)
        matches = []
        for bucket in buckets:
            _require(
                isinstance(bucket, dict) and set(bucket) <= {"key", "key_as_string", "doc_count"}
            )
            _require(type(bucket.get("doc_count")) is int and bucket["doc_count"] >= 0)
            _require(
                bucket.get("key") == class_code and bucket.get("key_as_string") == str(class_code)
            )
            matches.append(bucket)
        _require(len(matches) == 1, "aggregate class bucket is absent or ambiguous")
        bucket = matches[0]
        return {
            "extraction_version": VERSION,
            "source_sha256": _sha(source),
            "contract_sha256": _sha(_canonical(contract)),
            "implementation_sha256": _sha(Path(__file__).read_bytes()),
            "request_sha256": request_sha256,
            "class_code": class_code,
            "class_name": class_name,
            "value": bucket["doc_count"],
            "bucket_key": bucket.get("key_as_string", str(bucket.get("key"))),
            "promotion_authorized": False,
        }
    except MedallionApiError:
        raise
    except (UnicodeError, json.JSONDecodeError, TypeError, ValueError) as exc:
        raise MedallionApiError("medallion API extraction failed") from exc


def verify_aggregate(source: bytes, contract: dict[str, Any], receipt: dict[str, Any]) -> None:
    """Require exact recomputation of the bounded aggregate result."""
    if _canonical(receipt) != _canonical(extract_aggregate(source, contract)):
        raise MedallionApiError("API receipt does not match exact recomputation")
