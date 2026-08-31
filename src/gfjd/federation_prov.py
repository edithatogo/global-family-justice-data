"""Replay-bound provenance preparation; no factual execution or publication claim."""

import hashlib
import json
import math
from typing import Any

from gfjd.medallion_pipeline import replay_pipeline_history
from gfjd.medallion_replay import verify_projection

VERSION = "gfjd-replayed-provenance-v1"
MAX_JSON_BYTES = 8 * 1024 * 1024
PROV = "http://www.w3.org/ns/prov#"
RDF_TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"


class ProvenanceError(ValueError):
    """Rejected provenance inputs or outputs."""


def _require(condition: bool) -> None:
    if not condition:
        raise ProvenanceError("Provenance preparation contract violation")


def _canonical(value: Any) -> bytes:
    pending = [(value, 0)]
    nodes = text_size = 0
    while pending:
        item, depth = pending.pop()
        nodes += 1
        _require(nodes <= 200000 and depth <= 32)
        if type(item) is dict:
            _require(len(item) <= 10000 and all(type(key) is str for key in item))
            pending.extend((part, depth + 1) for pair in item.items() for part in pair)
        elif type(item) is list:
            _require(len(item) <= 10000)
            pending.extend((part, depth + 1) for part in item)
        elif type(item) is str:
            text_size += len(item)
            _require(len(item) <= 1024 * 1024 and text_size <= MAX_JSON_BYTES)
        elif type(item) is float:
            _require(math.isfinite(item))
        else:
            _require(item is None or type(item) in (bool, int))
    raw = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode()
    _require(len(raw) <= MAX_JSON_BYTES)
    return raw


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _bank(bank: dict[str, bytes]) -> None:
    _require(type(bank) is dict and len(bank) <= 100)
    total = 0
    for digest, raw in bank.items():
        _require(type(raw) is bytes)
        total += len(raw)
        _require(total <= MAX_JSON_BYTES and digest == _sha(raw))


class _Graph:
    """Only content-addressed entities and fixed predicates; no raw input terms."""

    def __init__(self) -> None:
        self.lines: set[str] = set()
        self.entities: set[str] = set()

    def entity(self, raw: bytes) -> str:
        identifier = "urn:gfjd:sha256:" + _sha(raw)
        self.entities.add(identifier)
        self.lines.add(f"<{identifier}> <{RDF_TYPE}> <{PROV}Entity> .")
        return identifier

    def edge(self, child: str, parent: str, relation: str = "wasDerivedFrom") -> None:
        if child != parent:
            self.lines.add(f"<{child}> <{PROV}{relation}> <{parent}> .")

    def output(self, bindings: dict[str, Any], mode: str, count: int) -> dict[str, bytes]:
        nt = ("\n".join(sorted(self.lines)) + "\n").encode()
        report = {
            "contract_version": VERSION,
            "mode": mode,
            "bindings": bindings,
            "provenance_sha256": _sha(nt),
            "entity_count": len(self.entities),
            "statement_count": len(self.lines),
            "history_event_count": count,
            "revision_semantics": "verified-history-record-artifact-revisions-not-row-identity",
            "coverage": "replayed-byte-derivations-only-not-full-PROV-CONSTRAINTS",
            "implementation_fingerprint_io": (
                "existing-replay-helpers-read-their-implementation-files"
            ),
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
                    "promotion",
                    "maturity",
                    "gate_acceptance",
                    "partner_registration",
                ),
                False,
            ),
        }
        return {"provenance.nt": nt, "provenance-report.json": _canonical(report) + b"\n"}


def prepare_projection_prov(
    source: bytes, contract: dict[str, Any], receipt: dict[str, Any]
) -> dict[str, bytes]:
    """Recompute supplied projection before describing exact-byte derivations.

    Existing replay fingerprints read implementation files. No source loader,
    transport, Activity, Agent or inferred timestamp is introduced.
    """
    try:
        _require(type(source) is bytes and 0 < len(source) <= 1024 * 1024)
        contract_raw, receipt_raw = _canonical(contract), _canonical(receipt)
        verify_projection(source, contract, receipt)
        graph = _Graph()
        origin = graph.entity(source)
        mapping = graph.entity(contract_raw)
        rows = graph.entity(_canonical(receipt["rows"]))
        record = graph.entity(receipt_raw)
        graph.edge(rows, origin)
        graph.edge(record, rows)
        graph.edge(record, mapping)
        return graph.output(
            {
                "source_sha256": _sha(source),
                "contract_sha256": _sha(contract_raw),
                "receipt_bytes_sha256": _sha(receipt_raw),
            },
            "projection",
            0,
        )
    except Exception:
        raise ProvenanceError("Provenance preparation contract violation") from None


def prepare_pipeline_prov(
    entries: list[dict[str, Any]],
    sources: dict[str, bytes],
    safety_receipts: dict[str, bytes],
    custody_receipts: dict[str, bytes],
    contracts: dict[str, dict[str, Any]],
) -> dict[str, bytes]:
    """Replay the complete history before exporting B0/B1/Silver and revision edges.

    Revision edges connect exact serialized history-record artifacts, not row
    content hashes. Identical data across revisions has no false self-edge.
    Supplied safety/custody declarations remain unverified historical claims.
    """
    try:
        _require(type(entries) is list and 0 < len(entries) <= 100)
        entries_raw = _canonical(entries)
        for bank in (sources, safety_receipts, custody_receipts):
            _bank(bank)
        _require(type(contracts) is dict and len(contracts) <= 100)
        contract_raws = {digest: _canonical(contract) for digest, contract in contracts.items()}
        _bank(contract_raws)
        for bank, field in (
            (sources, "source_sha256"),
            (safety_receipts, "safety_receipt_sha256"),
            (custody_receipts, "custody_receipt_sha256"),
            (contract_raws, "contract_sha256"),
        ):
            _require(set(bank) == {entry["pipeline"][field] for entry in entries})
        replay = replay_pipeline_history(
            entries, sources, safety_receipts, custody_receipts, contracts
        )
        graph = _Graph()
        history_entities: dict[str, str] = {}
        for entry in entries:
            pipeline, history = entry["pipeline"], entry["history_event"]
            b0 = graph.entity(sources[pipeline["source_sha256"]])
            b1 = graph.entity(_canonical(pipeline["b1"]["rows"]))
            silver = graph.entity(_canonical(pipeline["silver"]["rows"]))
            mapping = graph.entity(contract_raws[pipeline["contract_sha256"]])
            pipeline_entity = graph.entity(_canonical(pipeline))
            history_entity = graph.entity(_canonical(history))
            graph.edge(b1, b0)
            graph.edge(silver, b1)
            graph.edge(pipeline_entity, b0)
            graph.edge(pipeline_entity, silver)
            graph.edge(pipeline_entity, mapping)
            for bank, field in (
                (safety_receipts, "safety_receipt_sha256"),
                (custody_receipts, "custody_receipt_sha256"),
            ):
                graph.edge(pipeline_entity, graph.entity(bank[pipeline[field]]))
            graph.edge(history_entity, b1)
            graph.edge(history_entity, silver)
            if history["supersedes"] is not None:
                graph.edge(history_entity, history_entities[history["supersedes"]], "wasRevisionOf")
            history_entities[history["event_id"]] = history_entity
        return graph.output(
            {
                "entries_bytes_sha256": _sha(entries_raw),
                "replay_receipt_bytes_sha256": _sha(_canonical(replay)),
                "source_sha256": sorted(sources),
                "safety_sha256": sorted(safety_receipts),
                "custody_sha256": sorted(custody_receipts),
                "contract_sha256": sorted(contracts),
            },
            "pipeline_history",
            len(entries),
        )
    except Exception:
        raise ProvenanceError("Provenance preparation contract violation") from None


def _verify(expected: dict[str, bytes], artifacts: dict[str, bytes]) -> None:
    _require(type(artifacts) is dict and set(artifacts) == set(expected))
    _require(all(type(raw) is bytes and raw == expected[name] for name, raw in artifacts.items()))


def verify_projection_prov(
    source: bytes, contract: dict[str, Any], receipt: dict[str, Any], artifacts: dict[str, bytes]
) -> None:
    """Verify the exact output set and bytes by full source recomputation."""
    _verify(prepare_projection_prov(source, contract, receipt), artifacts)


def verify_pipeline_prov(
    entries: list[dict[str, Any]],
    sources: dict[str, bytes],
    safety_receipts: dict[str, bytes],
    custody_receipts: dict[str, bytes],
    contracts: dict[str, dict[str, Any]],
    artifacts: dict[str, bytes],
) -> None:
    """Verify every edge and report field by complete pipeline-history replay."""
    _verify(
        prepare_pipeline_prov(entries, sources, safety_receipts, custody_receipts, contracts),
        artifacts,
    )
