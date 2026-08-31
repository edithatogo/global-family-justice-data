"""Offline selected-XLSX safety/custody bindings and unpromoted B1/Silver replay.

Recorded provider assertions are checked for consistency, not re-observed.
Callers must separately authorize source handling; this module grants no access.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, cast
from urllib.parse import urlsplit

from blake3 import blake3

from . import medallion_history, medallion_replay, medallion_xlsx, public_archive
from .security import PROHIBITED_PUBLIC_DATA_HEADERS

VERSION = "gfjd-custody-xlsx-projection-v1"
MAX_RECEIPT_BYTES = 1024 * 1024


class PipelineError(ValueError):
    """Input cannot establish this bounded candidate replay."""


def _require(condition: bool) -> None:
    if not condition:
        raise PipelineError("pipeline validation failed")


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode()


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    _require(len(pairs) <= 128)
    for key, value in pairs:
        _require(key not in result and len(key) <= 128)
        result[key] = value
    return result


def _nonfinite(value: str) -> None:
    raise PipelineError("pipeline validation failed")


def _load(raw: bytes) -> dict[str, Any]:
    _require(isinstance(raw, bytes) and len(raw) <= MAX_RECEIPT_BYTES)
    value = json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs, parse_constant=_nonfinite)
    _require(isinstance(value, dict))
    return dict(value)


def _objects(receipt: dict[str, Any]) -> dict[str, dict[str, Any]]:
    objects = receipt.get("objects")
    _require(isinstance(objects, list) and 0 < len(objects) <= 100)
    result = {}
    for item in cast(list[Any], objects):
        _require(isinstance(item, dict))
        identity = item.get("inventory_id")
        _require(isinstance(identity, str) and bool(identity) and len(identity) <= 128)
        _require(identity not in result)
        result[identity] = item
    return result


def _custody(safety: dict[str, Any], custody: dict[str, Any], selected: str) -> dict[str, Any]:
    _require(safety.get("contract_version") == public_archive.CONTRACT_VERSION)
    _require(custody.get("contract_version") == public_archive.CUSTODY_CONTRACT_VERSION)
    _require(safety.get("status") == "pass")
    safe_objects, custody_objects = _objects(safety), _objects(custody)
    _require(set(safe_objects) == set(custody_objects) and selected in safe_objects)
    hosts = {"github": "github.com", "huggingface": "huggingface.co"}
    for identity, safe in safe_objects.items():
        item = custody_objects[identity]
        _require(safe.get("disposition") == "public_safe" and safe.get("findings") == [])
        for field in ("sha256", "blake3", "size_bytes"):
            _require(
                type(item.get(field)) is type(safe.get(field))
                and item.get(field) == safe.get(field)
            )
        _require(type(safe.get("size_bytes")) is int and safe["size_bytes"] > 0)
        for field in ("sha256", "blake3"):
            _require(
                isinstance(safe.get(field), str)
                and re.fullmatch(r"[0-9a-f]{64}", safe[field]) is not None
            )
        replicas = item.get("replicas")
        _require(isinstance(replicas, list) and len(replicas) == 2)
        seen = set()
        for replica in cast(list[Any], replicas):
            _require(isinstance(replica, dict))
            provider = replica.get("provider")
            _require(isinstance(provider, str) and provider in hosts and provider not in seen)
            seen.add(provider)
            url = replica.get("url")
            _require(isinstance(url, str) and 0 < len(url) <= 4096)
            _require(all(ord(char) >= 32 for char in url) and "\\" not in url)
            parsed = urlsplit(url)
            _require(parsed.scheme == "https" and parsed.netloc == hosts[provider])
            _require(not parsed.query and not parsed.fragment and parsed.path.startswith("/"))
            _require(replica.get("anonymous_get_verified") is True)
            _require(replica.get("retrieved_sha256") == safe["sha256"])
            _require(replica.get("retrieved_blake3") == safe["blake3"])
    return safe_objects[selected]


def _labels(labels: Any) -> None:
    for label in labels:
        _require(isinstance(label, str))
        identity = re.sub(r"[^a-z0-9]+", "_", label.casefold()).strip("_")
        _require(identity not in PROHIBITED_PUBLIC_DATA_HEADERS)


def replay_pipeline(
    source: bytes, safety_bytes: bytes, custody_bytes: bytes, contract: dict[str, Any]
) -> dict[str, Any]:
    """Recompute selected-source mechanics; never grant rights or layer acceptance."""
    try:
        _require(isinstance(source, bytes) and 0 < len(source) <= 8 * 1024 * 1024)
        _require(
            isinstance(contract, dict)
            and set(contract)
            == {
                "pipeline_version",
                "inventory_id",
                "safety_receipt_sha256",
                "custody_receipt_sha256",
                "extraction_contract",
                "projection_contract",
            }
        )
        _require(contract["pipeline_version"] == VERSION)
        _require(isinstance(contract["inventory_id"], str))
        safety, custody = _load(safety_bytes), _load(custody_bytes)
        _require(contract["safety_receipt_sha256"] == _sha(safety_bytes))
        _require(contract["custody_receipt_sha256"] == _sha(custody_bytes))
        _require(custody.get("safety_receipt_sha256") == _sha(safety_bytes))
        safe = _custody(safety, custody, contract["inventory_id"])
        _require(safe["sha256"] == _sha(source) and safe["blake3"] == blake3(source).hexdigest())
        _require(safe["size_bytes"] == len(source))
        _require(
            isinstance(safe.get("payload_path"), str)
            and safe["payload_path"].lower().endswith(".xlsx")
        )
        _require(safe.get("disposition") == "public_safe" and safe.get("findings") == [])
        # Extraction's hard ZIP budgets run before the broader existing scanner.
        b1 = medallion_xlsx.extract_xlsx(source, contract["extraction_contract"])
        _require(not public_archive._scan_bytes(source, "selected.xlsx"))
        _require(not public_archive._scan_zip(source, "selected.xlsx"))
        for row in b1["rows"]:
            _labels(row)
        b1_rows = _canonical(b1["rows"])
        silver = medallion_replay.replay_projection(b1_rows, contract["projection_contract"])
        _labels(contract["projection_contract"]["projection"])
        receipt = {
            "pipeline_version": VERSION,
            "inventory_id": contract["inventory_id"],
            "source_sha256": _sha(source),
            "safety_receipt_sha256": _sha(safety_bytes),
            "custody_receipt_sha256": _sha(custody_bytes),
            "contract_sha256": _sha(_canonical(contract)),
            "implementation_sha256": _sha(Path(__file__).read_bytes()),
            "safety_implementation_sha256": _sha(Path(public_archive.__file__).read_bytes()),
            "b1_rows_sha256": _sha(b1_rows),
            "b1": b1,
            "silver": silver,
            "custody_claims_consistent": True,
            "selected_object_safety_recomputed": True,
            "current_remote_custody_verified": False,
            "semantic_review_required": True,
            "authority": dict.fromkeys(
                (
                    "network",
                    "source_access",
                    "rights_clearance",
                    "publication",
                    "release",
                    "promotion",
                    "g2_acceptance",
                ),
                False,
            ),
        }
        receipt["receipt_sha256"] = _sha(_canonical(receipt))
        return receipt
    except (
        ValueError,
        TypeError,
        KeyError,
        AttributeError,
        OverflowError,
        RecursionError,
        OSError,
    ):
        raise PipelineError("pipeline validation failed") from None


def verify_pipeline(
    source: bytes,
    safety_bytes: bytes,
    custody_bytes: bytes,
    contract: dict[str, Any],
    receipt: dict[str, Any],
) -> None:
    """Require an exact source-and-receipt recomputation, including all false flags."""
    expected = replay_pipeline(source, safety_bytes, custody_bytes, contract)
    try:
        _require(_canonical(receipt) == _canonical(expected))
    except (ValueError, TypeError, OverflowError, RecursionError):
        raise PipelineError("pipeline validation failed") from None


def build_pipeline_event(
    source: bytes,
    safety_bytes: bytes,
    custody_bytes: bytes,
    contract: dict[str, Any],
    *,
    partition: str,
    valid_until: str | None,
    supersedes: str | None,
) -> dict[str, Any]:
    """Bind original B0 and B1 lineage to one source-recomputed history event."""
    pipeline = replay_pipeline(source, safety_bytes, custody_bytes, contract)
    event = medallion_history.build_event(
        _canonical(pipeline["b1"]["rows"]),
        contract["projection_contract"],
        partition=partition,
        valid_until=valid_until,
        supersedes=supersedes,
    )
    linked: dict[str, Any] = {"pipeline": pipeline, "history_event": event}
    linked["link_sha256"] = _sha(_canonical(linked))
    return linked


def verify_pipeline_append_only(
    old_entries: list[dict[str, Any]],
    new_entries: list[dict[str, Any]],
    sources: dict[str, bytes],
    safety_receipts: dict[str, bytes],
    custody_receipts: dict[str, bytes],
    contracts: dict[str, dict[str, Any]],
    *,
    previous_entries_sha256: str,
) -> dict[str, Any]:
    """Check full linked prefixes against a trusted immutable prior checkpoint.

    The checkpoint must come from prior evidence, not the proposed replacement.
    Projection IDs alone cannot detect custody-only or outer-source rewrites.
    """
    previous = replay_pipeline_history(
        old_entries, sources, safety_receipts, custody_receipts, contracts
    )
    current = replay_pipeline_history(
        new_entries, sources, safety_receipts, custody_receipts, contracts
    )
    if (
        previous["entries_sha256"] != previous_entries_sha256
        or len(new_entries) < len(old_entries)
        or _canonical(new_entries[: len(old_entries)]) != _canonical(old_entries)
    ):
        raise PipelineError("pipeline validation failed")
    return current


def replay_pipeline_history(
    entries: list[dict[str, Any]],
    sources: dict[str, bytes],
    safety_receipts: dict[str, bytes],
    custody_receipts: dict[str, bytes],
    contracts: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Rebuild the entire XLSX-to-B1-to-Silver-to-correction chain from bytes.

    Input banks use exact content digests, not paths or retrieval callbacks. All
    source/receipt banks are bounded and checked, including unused supplied bytes.
    This never upgrades recorded retrieval assertions into current remote evidence.
    """
    try:
        _require(isinstance(entries, list) and len(entries) <= 100)
        for bank in (sources, safety_receipts, custody_receipts):
            _require(isinstance(bank, dict) and len(bank) <= 100)
            size = 0
            for digest, raw in bank.items():
                _require(isinstance(raw, bytes))
                size += len(raw)
                _require(size <= 8 * 1024 * 1024 and digest == _sha(raw))
        _require(isinstance(contracts, dict) and len(contracts) <= 100)
        contract_size = 0
        for digest, contract in contracts.items():
            raw = _canonical(contract)
            contract_size += len(raw)
            _require(contract_size <= MAX_RECEIPT_BYTES and digest == _sha(raw))
        events = []
        rebuilt_entries = []
        b1_sources = {}
        for entry in entries:
            _require(
                isinstance(entry, dict)
                and set(entry) == {"pipeline", "history_event", "link_sha256"}
            )
            pipeline, event = entry["pipeline"], entry["history_event"]
            rebuilt = build_pipeline_event(
                sources[pipeline["source_sha256"]],
                safety_receipts[pipeline["safety_receipt_sha256"]],
                custody_receipts[pipeline["custody_receipt_sha256"]],
                contracts[pipeline["contract_sha256"]],
                partition=event["partition"],
                valid_until=event["valid_until"],
                supersedes=event["supersedes"],
            )
            _require(_canonical(entry) == _canonical(rebuilt))
            b1_raw = _canonical(rebuilt["pipeline"]["b1"]["rows"])
            b1_sources[_sha(b1_raw)] = b1_raw
            events.append(rebuilt["history_event"])
            rebuilt_entries.append(rebuilt)
        receipt = {
            "pipeline_version": VERSION,
            "entries_sha256": _sha(_canonical(rebuilt_entries)),
            "history": medallion_history.replay_history(events, b1_sources),
            "current_remote_custody_verified": False,
            "semantic_review_required": True,
            "promotion_authorized": False,
        }
        receipt["receipt_sha256"] = _sha(_canonical(receipt))
        return receipt
    except (
        ValueError,
        TypeError,
        KeyError,
        AttributeError,
        OverflowError,
        RecursionError,
        OSError,
    ):
        raise PipelineError("pipeline validation failed") from None
