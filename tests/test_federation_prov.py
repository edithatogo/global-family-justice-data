"""Fictional replay evidence, never source publication or actual remote custody."""

import copy
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

from gfjd import federation_prov as prov
from gfjd.medallion_replay import replay_projection


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


@pytest.fixture
def projection() -> tuple:
    source = canonical([{"fictional": "FICTIONAL_PRIVATE_MARKER"}])
    contract = {
        "contract_version": "gfjd-json-projection-v1",
        "source_sha256": sha(source),
        "projection": {"value": "fictional"},
        "valid_from": None,
        "recorded_at": "2026-08-31T00:00:00Z",
    }
    return source, contract, replay_projection(source, contract)


def test_tampered_receipt_red(projection: tuple) -> None:
    source, contract, receipt = projection
    receipt["rows"][0]["value"] = "rewritten"
    with pytest.raises(prov.ProvenanceError):
        prov.prepare_projection_prov(source, contract, receipt)


def test_projection(projection: tuple) -> None:
    output = prov.prepare_projection_prov(*projection)
    assert set(output) == {"provenance.nt", "provenance-report.json"}
    assert b"FICTIONAL_PRIVATE_MARKER" not in b"".join(output.values())
    assert b"wasDerivedFrom" in output["provenance.nt"]
    assert b"Activity" not in output["provenance.nt"]
    assert b"2026-08-31" not in output["provenance.nt"]
    assert sha(canonical(projection[2])) != projection[2]["snapshot_sha256"]
    assert sha(canonical(projection[2])).encode() in output["provenance.nt"]
    assert output == prov.prepare_projection_prov(*projection)
    prov.verify_projection_prov(*projection, output)


def test_changed_edge_and_rehashed_report(projection: tuple) -> None:
    output = prov.prepare_projection_prov(*projection)
    output["provenance.nt"] = output["provenance.nt"].replace(b"wasDerivedFrom", b"wasRevisionOf")
    report = json.loads(output["provenance-report.json"])
    report["provenance_sha256"] = sha(output["provenance.nt"])
    output["provenance-report.json"] = canonical(report)
    with pytest.raises(prov.ProvenanceError):
        prov.verify_projection_prov(*projection, output)


@pytest.fixture
def pipeline() -> tuple:
    from gfjd.medallion_pipeline import build_pipeline_event

    path = Path(__file__).parents[1] / "scripts/rehearse_medallion_lineage.py"
    spec = importlib.util.spec_from_file_location("fictional_rehearsal", path)
    assert spec and spec.loader
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    entries, sources, safeties, custodies, contracts = [], {}, {}, {}, {}
    parent = None
    for value, clock in (("0007", "2026-08-31T00:00:00Z"), ("0009", "2026-08-31T01:00:00Z")):
        source, safety, custody, contract = helper.fictional_inputs(value, clock)
        entry = build_pipeline_event(
            source,
            safety,
            custody,
            contract,
            partition="fictional",
            valid_until=None,
            supersedes=parent,
        )
        parent = entry["history_event"]["event_id"]
        entries.append(entry)
        sources[sha(source)] = source
        safeties[sha(safety)] = safety
        custodies[sha(custody)] = custody
        contracts[sha(canonical(contract))] = contract
    return entries, sources, safeties, custodies, contracts


def test_pipeline(pipeline: tuple) -> None:
    output = prov.prepare_pipeline_prov(*pipeline)
    assert b"wasRevisionOf" in output["provenance.nt"]
    assert b"0007" not in output["provenance.nt"]
    assert b"0009" not in output["provenance.nt"]
    report = json.loads(output["provenance-report.json"])
    assert not any(report["authority"].values())
    assert report["history_event_count"] == 2
    prov.verify_pipeline_prov(*pipeline, output)


@pytest.mark.parametrize(
    "mode", ["missing_parent", "cross_partition", "extra_bank", "changed_rows"]
)
def test_pipeline_invalid(pipeline: tuple, mode: str) -> None:
    entries, sources, safeties, custodies, contracts = copy.deepcopy(pipeline)
    if mode == "missing_parent":
        entries.pop(0)
    elif mode == "cross_partition":
        entries[1]["history_event"]["partition"] = "other"
    elif mode == "extra_bank":
        sources[sha(b"extra")] = b"extra"
    else:
        entries[1]["pipeline"]["silver"]["rows"][0]["value"] = "changed"
    with pytest.raises(prov.ProvenanceError):
        prov.prepare_pipeline_prov(entries, sources, safeties, custodies, contracts)


def test_no_network(projection: tuple, monkeypatch: pytest.MonkeyPatch) -> None:
    import socket

    def forbidden(*args: object, **kwargs: object) -> None:
        raise AssertionError("network attempted")

    monkeypatch.setattr(socket, "socket", forbidden)
    prov.prepare_projection_prov(*projection)


def test_same_bytes_have_no_self_edges(projection: tuple) -> None:
    source = canonical([{"value": "fictional"}])
    contract = projection[1]
    contract["source_sha256"] = sha(source)
    contract["projection"] = {"value": "value"}
    receipt = replay_projection(source, contract)
    result = prov.prepare_projection_prov(source, contract, receipt)
    for line in result["provenance.nt"].decode().splitlines():
        subject, predicate, obj, _ = line.split()
        if "wasDerivedFrom" in predicate or "wasRevisionOf" in predicate:
            assert subject != obj


@pytest.mark.parametrize("kind", ["extra", "missing", "authority"])
def test_exact_outputs(projection: tuple, kind: str) -> None:
    outputs = prov.prepare_projection_prov(*projection)
    if kind == "extra":
        outputs["extra.nt"] = b""
    elif kind == "missing":
        del outputs["provenance.nt"]
    else:
        report = json.loads(outputs["provenance-report.json"])
        report["authority"]["publication"] = True
        outputs["provenance-report.json"] = canonical(report)
    with pytest.raises(prov.ProvenanceError):
        prov.verify_projection_prov(*projection, outputs)


def test_bounds(projection: tuple, pipeline: tuple) -> None:
    source, contract, receipt = projection
    receipt["extra"] = "x" * (1024 * 1024 + 1)
    with pytest.raises(prov.ProvenanceError):
        prov.prepare_projection_prov(source, contract, receipt)
    with pytest.raises(prov.ProvenanceError):
        prov.prepare_pipeline_prov([pipeline[0][0]] * 101, *pipeline[1:])


def test_validly_rebuilt_cross_partition_rejected(pipeline: tuple) -> None:
    from gfjd.medallion_pipeline import build_pipeline_event

    entries, sources, safety, custody, contracts = copy.deepcopy(pipeline)
    second = entries[1]["pipeline"]
    entries[1] = build_pipeline_event(
        sources[second["source_sha256"]],
        safety[second["safety_receipt_sha256"]],
        custody[second["custody_receipt_sha256"]],
        contracts[second["contract_sha256"]],
        partition="wrong-partition",
        valid_until=None,
        supersedes=entries[0]["history_event"]["event_id"],
    )
    with pytest.raises(prov.ProvenanceError):
        prov.prepare_pipeline_prov(entries, sources, safety, custody, contracts)


def test_missing_parent_without_extra_banks(pipeline: tuple) -> None:
    entries, sources, safety, custody, contracts = copy.deepcopy(pipeline)
    entries = entries[1:]
    refs = entries[0]["pipeline"]
    banks = [
        {refs[key]: bank[refs[key]]}
        for bank, key in (
            (sources, "source_sha256"),
            (safety, "safety_receipt_sha256"),
            (custody, "custody_receipt_sha256"),
            (contracts, "contract_sha256"),
        )
    ]
    with pytest.raises(prov.ProvenanceError):
        prov.prepare_pipeline_prov(entries, *banks)
