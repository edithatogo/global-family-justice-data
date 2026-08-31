"""Fictional XLSX/custody inputs; no provider retrieval or empirical evidence."""

import copy
import hashlib
import io
import json
import zipfile

import pytest
from blake3 import blake3

from gfjd.medallion_pipeline import (
    PipelineError,
    build_pipeline_event,
    replay_pipeline,
    replay_pipeline_history,
    verify_pipeline,
    verify_pipeline_append_only,
)


def encoded(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def fictional_workbook(*, extra: dict[str, str] | None = None) -> bytes:
    ns = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    rel = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    parts = {
        "_rels/.rels": (
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            f'<Relationship Id="rId1" Type="{rel}/officeDocument" '
            'Target="xl/workbook.xml"/></Relationships>'
        ),
        "[Content_Types].xml": '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>',
        "xl/workbook.xml": (
            f'<workbook xmlns="{ns}" xmlns:r="{rel}"><sheets>'
            '<sheet name="Fictional" sheetId="1" r:id="rId1"/></sheets></workbook>'
        ),
        "xl/_rels/workbook.xml.rels": (
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            f'<Relationship Id="rId1" Type="{rel}/worksheet" '
            'Target="worksheets/sheet1.xml"/></Relationships>'
        ),
        "xl/worksheets/sheet1.xml": (
            f'<worksheet xmlns="{ns}"><sheetData><row r="1">'
            '<c r="A1" t="inlineStr"><is><t>Measure</t></is></c>'
            '<c r="B1" t="inlineStr"><is><t>Count</t></is></c></row><row r="2">'
            '<c r="A2" t="inlineStr"><is><t>Fictional applications</t></is></c>'
            '<c r="B2" t="n"><v>0007</v></c></row></sheetData></worksheet>'
        ),
    }
    parts.update(extra or {})
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as archive:
        for name, value in sorted(parts.items()):
            archive.writestr(zipfile.ZipInfo(name), value)
    return output.getvalue()


def inputs(source: bytes | None = None) -> tuple:
    source = source or fictional_workbook()
    safe = {
        "inventory_id": "FICTIONAL-XLSX",
        "payload_path": "fictional.xlsx",
        "sha256": sha(source),
        "blake3": blake3(source).hexdigest(),
        "size_bytes": len(source),
        "disposition": "public_safe",
        "findings": [],
    }
    safety = encoded(
        {"contract_version": "gfjd-public-archive-safety-v1", "status": "pass", "objects": [safe]}
    )
    item = {key: safe[key] for key in ("inventory_id", "sha256", "blake3", "size_bytes")}
    item["replicas"] = [
        {
            "provider": provider,
            "url": f"https://{host}/fictional/not-retrieved",
            "anonymous_get_verified": True,
            "retrieved_sha256": sha(source),
            "retrieved_blake3": blake3(source).hexdigest(),
        }
        for provider, host in (("github", "github.com"), ("huggingface", "huggingface.co"))
    ]
    custody = encoded(
        {
            "contract_version": "gfjd-public-b0-custody-v1",
            "safety_receipt_sha256": sha(safety),
            "objects": [item],
        }
    )
    contract = {
        "pipeline_version": "gfjd-custody-xlsx-projection-v1",
        "inventory_id": "FICTIONAL-XLSX",
        "safety_receipt_sha256": sha(safety),
        "custody_receipt_sha256": sha(custody),
        "extraction_contract": {
            "extraction_version": "gfjd-medallion-xlsx-v1",
            "source_sha256": sha(source),
            "sheet_name": "Fictional",
            "header_row": 1,
            "columns": ["A", "B"],
            "data_rows": [2],
        },
        "projection_contract": {
            "contract_version": "gfjd-json-projection-v1",
            "source_sha256": sha(encoded([{"Measure": "Fictional applications", "Count": "0007"}])),
            "projection": {"measure": "Measure", "value": "Count"},
            "valid_from": None,
            "recorded_at": "2026-08-31T00:00:00Z",
        },
    }
    return source, safety, custody, contract


def test_recomputes_xlsx_to_source_labelled_b1_and_unpromoted_silver() -> None:
    args = inputs()
    result = replay_pipeline(*args)
    assert result["b1"]["rows"] == [{"Measure": "Fictional applications", "Count": "0007"}]
    assert result["silver"]["rows"] == [{"measure": "Fictional applications", "value": "0007"}]
    assert result["source_sha256"] == sha(args[0])
    assert result["b1_rows_sha256"] != result["source_sha256"]
    assert result["custody_claims_consistent"] is True
    assert result["selected_object_safety_recomputed"] is True
    assert result["current_remote_custody_verified"] is False
    assert result["semantic_review_required"] is True
    assert all(value is False for value in result["authority"].values())
    verify_pipeline(*args, result)
    assert result == replay_pipeline(*args)


@pytest.mark.parametrize("field", ["safety_receipt_sha256", "custody_receipt_sha256"])
def test_binding_mismatch_stops(field: str) -> None:
    source, safety, custody, contract = inputs()
    contract[field] = "0" * 64
    with pytest.raises(PipelineError):
        replay_pipeline(source, safety, custody, contract)


@pytest.mark.parametrize(
    "change",
    [
        "duplicate_object",
        "duplicate_provider",
        "truthy_flag",
        "retrieval_digest",
        "credential_url",
        "wrong_host",
    ],
)
def test_self_consistent_custody_tampering_stops(change: str) -> None:
    source, safety, raw, contract = inputs()
    custody = json.loads(raw)
    item = custody["objects"][0]
    replica = item["replicas"][0]
    if change == "duplicate_object":
        custody["objects"].append(copy.deepcopy(item))
    elif change == "duplicate_provider":
        item["replicas"].append(copy.deepcopy(replica))
    elif change == "truthy_flag":
        replica["anonymous_get_verified"] = 1
    elif change == "retrieval_digest":
        replica["retrieved_sha256"] = "0" * 64
    elif change == "credential_url":
        replica["url"] = "https://credential@github.com/fictional"
    else:
        replica["url"] = "https://github.com.evil.invalid/fictional"
    raw = encoded(custody)
    contract["custody_receipt_sha256"] = sha(raw)
    with pytest.raises(PipelineError):
        replay_pipeline(source, safety, raw, contract)


def test_forged_safety_pass_does_not_override_recomputed_source_scan() -> None:
    source = fictional_workbook(extra={"prohibited.csv": "case_number,value\nfictional,7\n"})
    with pytest.raises(PipelineError):
        replay_pipeline(*inputs(source))


def test_transformation_or_output_tampering_stops() -> None:
    args = inputs()
    result = replay_pipeline(*args)
    result["silver"]["rows"][0]["value"] = "8"
    with pytest.raises(PipelineError):
        verify_pipeline(*args, result)
    args[3]["projection_contract"]["source_sha256"] = sha(args[0])
    with pytest.raises(PipelineError):
        replay_pipeline(*args)


def test_malformed_or_oversize_receipts_fail_with_fixed_error() -> None:
    source, safety, custody, contract = inputs()
    for raw in (b"[", b'{"x":1,"x":2}', b"x" * (1024 * 1024 + 1)):
        contract["safety_receipt_sha256"] = sha(raw)
        with pytest.raises(PipelineError, match="pipeline validation failed"):
            replay_pipeline(source, raw, custody, contract)


def history_fixture() -> tuple:
    source, safety, custody, first_contract = inputs()
    first = build_pipeline_event(
        source,
        safety,
        custody,
        first_contract,
        partition="fictional-partition",
        valid_until=None,
        supersedes=None,
    )
    second_contract = copy.deepcopy(first_contract)
    second_contract["projection_contract"]["recorded_at"] = "2026-09-01T00:00:00Z"
    second = build_pipeline_event(
        source,
        safety,
        custody,
        second_contract,
        partition="fictional-partition",
        valid_until=None,
        supersedes=first["history_event"]["event_id"],
    )
    return (
        [first, second],
        {sha(source): source},
        {sha(safety): safety},
        {sha(custody): custody},
        {sha(encoded(value)): value for value in (first_contract, second_contract)},
    )


def test_full_custody_to_partition_history_recomputes_all_links() -> None:
    args = history_fixture()
    original = copy.deepcopy(args[0])
    result = replay_pipeline_history(*args)
    assert result["history"]["event_count"] == 2
    assert result["history"]["revisions"][0]["recorded_until"] == "2026-09-01T00:00:00Z"
    assert result["current_remote_custody_verified"] is False
    assert result["promotion_authorized"] is False
    assert original == args[0]
    assert result == replay_pipeline_history(*args)


@pytest.mark.parametrize("rewrite", ["custody", "outer_source"])
def test_linked_append_guard_preserves_custody_and_outer_bytes(rewrite: str) -> None:
    entries, sources, safety_bank, custody_bank, contracts = history_fixture()
    old = copy.deepcopy(entries[:1])
    checkpoint = replay_pipeline_history(old, sources, safety_bank, custody_bank, contracts)[
        "entries_sha256"
    ]
    banks = (sources, safety_bank, custody_bank, contracts)
    assert (
        verify_pipeline_append_only(old, entries, *banks, previous_entries_sha256=checkpoint)[
            "history"
        ]["event_count"]
        == 2
    )
    if rewrite == "outer_source":
        source, safety, custody, contract = inputs(
            fictional_workbook(extra={"fictional-note.txt": "Fictional revision"})
        )
    else:
        source, safety, custody, contract = inputs()
        changed = json.loads(custody)
        changed["objects"][0]["replicas"][0]["url"] += "-rewritten"
        custody = encoded(changed)
        contract["custody_receipt_sha256"] = sha(custody)
    sources[sha(source)] = source
    safety_bank[sha(safety)] = safety
    custody_bank[sha(custody)] = custody
    contracts[sha(encoded(contract))] = contract
    replacement = build_pipeline_event(
        source,
        safety,
        custody,
        contract,
        partition="fictional-partition",
        valid_until=None,
        supersedes=None,
    )
    assert replacement["history_event"] == old[0]["history_event"]
    assert replacement != old[0]
    replay_pipeline_history([replacement], *banks)
    for prior, proposed, anchor in (
        (old, [replacement], checkpoint),
        (old, [], checkpoint),
        (old, entries, "0" * 64),
        ([replacement], [replacement], checkpoint),
    ):
        with pytest.raises(PipelineError):
            verify_pipeline_append_only(prior, proposed, *banks, previous_entries_sha256=anchor)


@pytest.mark.parametrize(
    "change", ["source", "safety", "contract", "link", "event", "rows", "fork"]
)
def test_history_chain_rejects_tampered_banks_and_receipts(change: str) -> None:
    args = history_fixture()
    if change == "source":
        args[1][next(iter(args[1]))] = b"not original"
    elif change == "safety":
        args[2][next(iter(args[2]))] = b"not original"
    elif change == "contract":
        next(iter(args[4].values()))["projection_contract"]["valid_from"] = "2020-01-01T00:00:00Z"
    elif change == "link":
        args[0][0]["link_sha256"] = "0" * 64
    elif change == "event":
        args[0][0]["history_event"]["partition"] = "other"
    elif change == "rows":
        args[0][0]["pipeline"]["b1"]["rows"][0]["Count"] = "changed"
    else:
        args[0].append(copy.deepcopy(args[0][1]))
    with pytest.raises(PipelineError):
        replay_pipeline_history(*args)
