"""Fictional full-cohort qualification; no acquired sources or factual acceptance."""

import copy
import io
import json
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

import pytest
from blake3 import blake3

from gfjd import medallion_quality_checks, medallion_replay, medallion_xlsx
from gfjd.medallion import record_sha256
from gfjd.medallion_history import build_event
from gfjd.medallion_qualification import DIMENSIONS, qualify_layers, verify_qualification
from gfjd.medallion_qualification_inputs import LAYERS, canonical, sha
from gfjd.quality import MANDATORY_GOLD_FIELDS

AS_OF = "2026-08-31T00:00:00Z"


def fictional_workbook(row: dict[str, str]) -> bytes:
    s, r, p, t = medallion_xlsx.S, medallion_xlsx.R, medallion_xlsx.P, medallion_xlsx.T
    cells = []
    for number, values in ((1, list(row)), (2, list(row.values()))):
        contents = ""
        for index, value in enumerate(values):
            column = chr(65 + index) if index < 26 else "A" + chr(65 + index - 26)
            contents += f'<c r="{column}{number}" t="inlineStr"><is><t>{escape(value)}</t></is></c>'
        cells.append(f'<row r="{number}">{contents}</row>')
    parts = {
        "[Content_Types].xml": f'<Types xmlns="{t}"/>',
        "_rels/.rels": (
            f'<Relationships xmlns="{p}"><Relationship Id="r1" '
            f'Type="{r}/officeDocument" Target="xl/workbook.xml"/></Relationships>'
        ),
        "xl/workbook.xml": (
            f'<workbook xmlns="{s}" xmlns:r="{r}"><sheets>'
            '<sheet name="Fictional" sheetId="1" r:id="r1"/></sheets></workbook>'
        ),
        "xl/_rels/workbook.xml.rels": (
            f'<Relationships xmlns="{p}"><Relationship Id="r1" '
            f'Type="{r}/worksheet" Target="worksheets/sheet1.xml"/></Relationships>'
        ),
        "xl/worksheets/sheet1.xml": (
            f'<worksheet xmlns="{s}"><sheetData>{"".join(cells)}</sheetData></worksheet>'
        ),
    }
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w") as archive:
        for name, value in sorted(parts.items()):
            archive.writestr(zipfile.ZipInfo(name), value)
    return stream.getvalue()


def fixture(root: Path) -> tuple[dict, list[dict], dict[str, bytes], bytes]:
    row = dict.fromkeys(MANDATORY_GOLD_FIELDS, "FICTIONAL")
    row.update(
        observation_id="FICTIONAL-1",
        value="10",
        unit="count",
        period_start="2026-01-01",
        period_end="2026-12-31",
        stage_start="FICTIONAL-START",
        stage_end="FICTIONAL-END",
    )
    source = fictional_workbook(row)
    bank: dict[str, bytes] = {}

    def put(value: object) -> str:
        raw = value if isinstance(value, bytes) else canonical(value)
        bank[sha(raw)] = raw
        return sha(raw)

    source_id = put(source)
    safe = {
        "inventory_id": "FICTIONAL",
        "payload_path": "fictional.xlsx",
        "sha256": source_id,
        "blake3": blake3(source).hexdigest(),
        "size_bytes": len(source),
        "disposition": "public_safe",
        "findings": [],
    }
    safety_id = put(
        {"contract_version": "gfjd-public-archive-safety-v1", "status": "pass", "objects": [safe]}
    )
    custody_item = {key: safe[key] for key in ("inventory_id", "sha256", "blake3", "size_bytes")}
    custody_item["replicas"] = [
        {
            "provider": provider,
            "url": f"https://{host}/fictional/not-retrieved",
            "anonymous_get_verified": True,
            "retrieved_sha256": source_id,
            "retrieved_blake3": safe["blake3"],
        }
        for provider, host in (("github", "github.com"), ("huggingface", "huggingface.co"))
    ]
    custody_id = put(
        {
            "contract_version": "gfjd-public-b0-custody-v1",
            "safety_receipt_sha256": safety_id,
            "objects": [custody_item],
        }
    )
    capture_id = put({"synthetic": True, "not_retrieved": True})
    records = []

    def add(layer: str, evidence: dict, refs: dict) -> None:
        previous = LAYERS[LAYERS.index(layer) - 1] if layer != "b0" else None
        if records:
            evidence["predecessor_receipt_sha256"] = record_sha256(records[-1]["record"])
        records.append(
            {
                "object_id": "FICTIONAL",
                "edition_id": "FICTIONAL-EDITION",
                "record": {
                    "contract_version": "gfjd-medallion-layers-v1",
                    "object_id": "FICTIONAL",
                    "layer": layer,
                    "previous_layer": previous,
                    "lifecycle_state": "active",
                    "evidence": evidence,
                },
                "artifacts": refs,
            }
        )

    add(
        "b0",
        {
            "source_edition_id": "FICTIONAL-EDITION",
            "content_sha256": source_id,
            "content_blake3": safe["blake3"],
            "size_bytes": len(source),
            "media_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "capture_receipt_sha256": capture_id,
            "safety_receipt_sha256": safety_id,
            "custody_receipt_sha256": custody_id,
        },
        {"source": source_id, "capture": capture_id, "safety": safety_id, "custody": custody_id},
    )
    extraction = {
        "extraction_version": medallion_xlsx.VERSION,
        "source_sha256": source_id,
        "sheet_name": "Fictional",
        "header_row": 1,
        "columns": [chr(65 + i) if i < 26 else "A" + chr(65 + i - 26) for i in range(len(row))],
        "data_rows": [2],
    }
    b1 = medallion_xlsx.extract_xlsx(source, extraction)
    extraction_id, b1_id, rows_id = put(extraction), put(b1), put(b1["rows"])
    add(
        "b1",
        {
            "extraction_contract_sha256": extraction_id,
            "transformation_receipt_sha256": b1_id,
            "source_labels_preserved": True,
        },
        {"source": source_id, "contract": extraction_id, "receipt": b1_id, "rows": rows_id},
    )
    projection = {
        "contract_version": medallion_replay.VERSION,
        "source_sha256": rows_id,
        "projection": {key: key for key in row},
        "valid_from": "2026-01-01T00:00:00Z",
        "recorded_at": AS_OF,
    }
    silver = medallion_replay.replay_projection(bank[rows_id], projection)
    projection_id, silver_id = put(projection), put(silver)
    add(
        "silver",
        {
            "mapping_contract_sha256": projection_id,
            "field_lineage_sha256": sha(canonical(silver["field_lineage"])),
            "semantic_review_reference": "FICTIONAL-PENDING",
            "valid_from": projection["valid_from"],
            "recorded_at": AS_OF,
        },
        {"source": rows_id, "contract": projection_id, "receipt": silver_id, "rows": rows_id},
    )
    policy = {
        "contract_version": medallion_quality_checks.VERSION,
        "source_sha256": rows_id,
        "small_cell_threshold": 5,
    }
    quality_id = put(medallion_quality_checks.assess_quality(bank[rows_id], policy))
    add(
        "gold",
        {
            "quality_report_sha256": quality_id,
            "comparability_disposition": "FICTIONAL-PENDING",
            "disclosure_assessment_sha256": "f" * 64,
            "owner_decision_reference": "FICTIONAL-PENDING",
        },
        {"rows": rows_id, "policy": put(policy), "quality": quality_id},
    )
    release_scope = {
        "contract_version": "gfjd-platinum-scope-v1",
        "release_id": "FICTIONAL-RELEASE",
        "object_ids": ["FICTIONAL"],
    }
    federation = {
        "contract_version": "gfjd-federation-composition-v1",
        "release_id": "FICTIONAL-RELEASE",
        "objects": [
            {
                "object_id": "FICTIONAL",
                "content_sha256": rows_id,
                "canonical_object_id": "FICTIONAL-CANONICAL",
            }
        ],
    }
    scope_id, federation_id = put(release_scope), put(federation)
    manifest = {
        "contract_version": "gfjd-platinum-composition-v1",
        "release_id": "FICTIONAL-RELEASE",
        "scope_sha256": scope_id,
        "federation_sha256": federation_id,
        "objects": [
            {
                "object_id": "FICTIONAL",
                "layer": "gold",
                "sha256": rows_id,
                "size_bytes": len(bank[rows_id]),
                "media_type": "application/json",
            }
        ],
    }
    manifest_id = put(manifest)
    add(
        "platinum",
        {
            "release_manifest_sha256": manifest_id,
            "federation_manifest_sha256": federation_id,
            "release_gate_reference": "FICTIONAL-PENDING",
            "public_snapshot_reference": "FICTIONAL-NOT-PUBLISHED",
        },
        {"manifest": manifest_id, "federation": federation_id, "scope": scope_id},
    )
    scope = {
        "contract_version": "gfjd-qualification-scope-v1",
        "objects": [
            {
                "object_id": "FICTIONAL",
                "edition_id": "FICTIONAL-EDITION",
                "layers": {
                    layer: {"state": "active", "reason_codes": [], "disposition_reference": None}
                    for layer in LAYERS
                },
            }
        ],
    }
    return scope, records, bank, (root / "config/medallion_layers.json").read_bytes()


def arguments(scope: dict, records: list[dict], bank: dict, contract: bytes) -> tuple:
    raw = canonical(scope)
    return raw, sha(raw), contract, {sha(canonical(r)): canonical(r) for r in records}, bank


def evaluate(values: tuple) -> dict:
    return qualify_layers(*arguments(*values), as_of=AS_OF)


def rebind(records: list[dict]) -> None:
    for previous, current in zip(records, records[1:], strict=False):
        current["record"]["evidence"]["predecessor_receipt_sha256"] = record_sha256(
            previous["record"]
        )


def prune(records: list[dict], bank: dict) -> dict:
    referenced = {digest for record in records for digest in record["artifacts"].values()}
    return {digest: raw for digest, raw in bank.items() if digest in referenced}


def test_five_layers_eight_dimensions_with_real_recomputation(project_root: Path) -> None:
    values = fixture(project_root)
    original = copy.deepcopy(values)
    report = evaluate(values)
    assert [cell["layer"] for cell in report["coverage"]] == list(LAYERS)
    for cell in report["coverage"]:
        assert set(cell["dimensions"]) == set(DIMENSIONS)
        assert cell["dimensions"]["fixity"] == "verified"
        assert cell["dimensions"]["rights"] == cell["dimensions"]["restore"] == "pending"
        assert cell["promotion_authorized"] is False
    assert report["coverage"][3]["dimensions"]["quality"] == "verified"
    assert report["coverage"][4]["mechanical_checks"]["composition"]["object_count"] == 1
    assert all(flag is False for flag in report["authority"].values())
    verify_qualification(*arguments(*values), report, as_of=AS_OF)
    assert evaluate(values) == report and values == original


@pytest.mark.parametrize("change", ["missing", "invalid", "quarantined"])
def test_upstream_blockers_remain_visible(project_root: Path, change: str) -> None:
    scope, records, bank, contract = fixture(project_root)
    if change == "missing":
        records.pop(0)
    elif change == "invalid":
        records[0]["record"]["evidence"]["size_bytes"] = True
        records[0]["artifacts"] = {}
        rebind(records)
    else:
        scope["objects"][0]["layers"]["b0"].update(
            state="quarantined", reason_codes=["FICTIONAL"], disposition_reference="FICTIONAL"
        )
        records[0]["record"].update(
            lifecycle_state="quarantined",
            quarantine={"reason_codes": ["FICTIONAL"], "disposition_reference": "FICTIONAL"},
        )
        records[0]["artifacts"] = {}
        rebind(records)
    report = evaluate((scope, records, prune(records, bank), contract))
    assert len(report["coverage"]) == 5
    assert all(cell["blockers"] for cell in report["coverage"])
    assert report["coverage"][-1]["dimensions"]["reproducibility"] != "verified"


@pytest.mark.parametrize("layer,role", [("b1", "contract"), ("silver", "rows"), ("gold", "rows")])
def test_cross_layer_substitution_fails(project_root: Path, layer: str, role: str) -> None:
    scope, records, bank, contract = fixture(project_root)
    item = records[LAYERS.index(layer)]
    replacement = (
        canonical({"fictional": "wrong contract"})
        if role == "contract"
        else canonical([{"fictional": "wrong rows"}])
    )
    bank[sha(replacement)] = replacement
    item["artifacts"][role] = sha(replacement)
    report = evaluate((scope, records, prune(records, bank), contract))
    assert (
        "layer_contract_or_evidence_binding_failed"
        in report["coverage"][LAYERS.index(layer)]["blockers"]
    )


def test_forged_report_cannot_rehash_to_pass(project_root: Path) -> None:
    values = fixture(project_root)
    report = evaluate(values)
    report["coverage"][0]["dimensions"]["rights"] = "verified"
    report["report_sha256"] = sha(
        canonical({k: v for k, v in report.items() if k != "report_sha256"})
    )
    with pytest.raises(ValueError):
        verify_qualification(*arguments(*values), report, as_of=AS_OF)


@pytest.mark.parametrize("change", ["source_mismatch", "blocked_safety"])
def test_unqualified_source_never_reaches_extraction(
    project_root: Path, monkeypatch: pytest.MonkeyPatch, change: str
) -> None:
    scope, records, bank, contract = fixture(project_root)
    if change == "source_mismatch":
        raw = b"FICTIONAL-WRONG-SOURCE"
        bank[sha(raw)] = raw
        records[1]["artifacts"]["source"] = sha(raw)
    else:
        safety = json.loads(bank[records[0]["artifacts"]["safety"]])
        safety["objects"][0]["disposition"] = "blocked"
        raw = canonical(safety)
        bank[sha(raw)] = raw
        records[0]["artifacts"]["safety"] = sha(raw)
        records[0]["record"]["evidence"]["safety_receipt_sha256"] = sha(raw)
        # No contradictory custody assertion: exercise the failed scan disposition.
        del records[0]["artifacts"]["custody"]
        rebind(records)

    def forbidden(*args: object, **kwargs: object) -> None:
        pytest.fail("unqualified source reached XLSX extraction")

    monkeypatch.setattr(medallion_xlsx, "extract_xlsx", forbidden)
    report = evaluate((scope, records, prune(records, bank), contract))
    assert report["coverage"][1]["blockers"]


@pytest.mark.parametrize("tamper", [False, True])
def test_history_recomputes_scoped_tip_not_claimed_hash(project_root: Path, tamper: bool) -> None:
    scope, records, bank, contract = fixture(project_root)
    silver = records[2]
    projection = json.loads(bank[silver["artifacts"]["contract"]])
    rows = bank[silver["artifacts"]["source"]]
    event = build_event(rows, projection, partition="FICTIONAL", supersedes=None, valid_until=None)
    history = {
        "version": "gfjd-qualification-history-v1",
        "object_id": "FICTIONAL",
        "edition_id": "FICTIONAL-EDITION",
        "events": [event],
        "sources": [{"sha256": sha(rows), "rows": json.loads(rows)}],
    }
    checkpoint = {
        "version": "gfjd-qualification-history-v1",
        "object_id": "FICTIONAL",
        "edition_id": "FICTIONAL-EDITION",
        "previous_events": [event],
        "previous_events_sha256": sha(canonical([event])),
    }
    if tamper:
        history["events"][0]["projection_receipt"]["rows"][0]["value"] = "999"
    for role, value in (("history", history), ("checkpoint", checkpoint)):
        raw = canonical(value)
        bank[sha(raw)] = raw
        silver["artifacts"][role] = sha(raw)
    report = evaluate((scope, records, bank, contract))
    cell = report["coverage"][2]
    if tamper:
        assert cell["dimensions"]["reproducibility"] == "failed"
    else:
        result = cell["mechanical_checks"]["history"]
        assert result["scoped_replay"] == "verified"
        assert result["checkpoint_authenticity"] is False
        assert "checkpoint_authenticity" in cell["pending_requirements"]


def test_wrong_review_kind_is_not_borrowed(project_root: Path) -> None:
    scope, records, bank, contract = fixture(project_root)
    review = {
        "contract_version": "gfjd-review-binding-v1",
        "object_id": "FICTIONAL",
        "edition_id": "FICTIONAL-EDITION",
        "layer": "b0",
        "content_sha256": records[0]["artifacts"]["source"],
        "review_kind": "owner",
        "decision_reference": "FICTIONAL",
        "reviewer_reference": "FICTIONAL",
        "issued_at": "2026-01-01T00:00:00Z",
        "expires_at": "2027-01-01T00:00:00Z",
        "status": "accepted",
        "conditions": [],
        "conflicts": [],
    }
    raw = canonical(review)
    bank[sha(raw)] = raw
    records[0]["artifacts"]["rights"] = sha(raw)
    report = evaluate((scope, records, bank, contract))
    assert report["coverage"][0]["dimensions"]["rights"] == "failed"
    assert all(cell["blockers"] for cell in report["coverage"])


@pytest.mark.parametrize("role", ["owner", "disclosure"])
def test_gold_review_evidence_reference_must_match(project_root: Path, role: str) -> None:
    scope, records, bank, contract = fixture(project_root)
    review = {
        "contract_version": "gfjd-review-binding-v1",
        "object_id": "FICTIONAL",
        "edition_id": "FICTIONAL-EDITION",
        "layer": "gold",
        "content_sha256": records[3]["artifacts"]["rows"],
        "review_kind": role,
        "decision_reference": "FICTIONAL-WRONG-REFERENCE",
        "reviewer_reference": "FICTIONAL",
        "issued_at": "2026-01-01T00:00:00Z",
        "expires_at": "2027-01-01T00:00:00Z",
        "status": "accepted",
        "conditions": [],
        "conflicts": [],
    }
    raw = canonical(review)
    bank[sha(raw)] = raw
    records[3]["artifacts"][role] = sha(raw)
    report = evaluate((scope, records, bank, contract))
    assert f"{role}_review_failed" in report["coverage"][3]["blockers"]
    assert all(cell["dimensions"]["fixity"] == "verified" for cell in report["coverage"][:3])
    assert report["coverage"][4]["blockers"]


@pytest.mark.parametrize("mode", ["missing", "unsupported"])
def test_unavailable_safety_never_means_safety_verified(project_root: Path, mode: str) -> None:
    scope, records, bank, contract = fixture(project_root)
    if mode == "missing":
        del records[0]["artifacts"]["safety"], records[0]["artifacts"]["custody"]
    else:
        records[0]["record"]["evidence"]["media_type"] = "application/fictional-unsupported"
        rebind(records)
    report = evaluate((scope, records, prune(records, bank), contract))
    b0 = report["coverage"][0]
    assert b0["dimensions"]["fixity"] == "verified"
    assert b0["dimensions"]["quality"] == mode
    assert f"source_safety_{mode}" in b0["blockers"]
    assert report["coverage"][4]["dimensions"]["reproducibility"] != "verified"


@pytest.mark.parametrize("change", ["missing_object", "extra_record", "extra_payload"])
def test_cohort_denominator_cannot_be_hidden(project_root: Path, change: str) -> None:
    scope, records, bank, contract = fixture(project_root)
    if change == "missing_object":
        absent = copy.deepcopy(scope["objects"][0])
        absent["object_id"] = "FICTIONAL-MISSING"
        scope["objects"].append(absent)
        report = evaluate((scope, records, bank, contract))
        assert len(report["coverage"]) == 10
        assert all(
            cell["blockers"]
            for cell in report["coverage"]
            if cell["object_id"] == "FICTIONAL-MISSING"
        )
    else:
        if change == "extra_record":
            extra = copy.deepcopy(records[0])
            extra["object_id"] = extra["record"]["object_id"] = "FICTIONAL-EXTRA"
            records.append(extra)
        else:
            bank[sha(b"FICTIONAL-EXTRA")] = b"FICTIONAL-EXTRA"
        with pytest.raises(ValueError):
            evaluate((scope, records, bank, contract))


@pytest.mark.parametrize("role", ["capture", "custody"])
def test_required_b0_receipts_cannot_be_silently_omitted(project_root: Path, role: str) -> None:
    scope, records, bank, contract = fixture(project_root)
    del records[0]["artifacts"][role]
    report = evaluate((scope, records, prune(records, bank), contract))
    first = report["coverage"][0]
    assert first["dimensions"]["fixity"] == "verified"
    assert first["dimensions"]["completeness"] == "missing"
    assert f"required_{role}_evidence_missing" in first["blockers"]
    assert report["coverage"][4]["blockers"]


@pytest.mark.parametrize("field", ["content_sha256", "content_blake3", "size_bytes"])
def test_proven_b0_fixity_failure_is_failed_not_pending(project_root: Path, field: str) -> None:
    scope, records, bank, contract = fixture(project_root)
    records[0]["record"]["evidence"][field] = 1 if field == "size_bytes" else "0" * 64
    rebind(records)
    report = evaluate((scope, records, bank, contract))
    first = report["coverage"][0]
    assert first["dimensions"]["fixity"] == "failed"
    assert first["dimensions"]["quarantine"] == "blocked"
    assert "original_content_fixity_failed" in first["blockers"]
    assert report["coverage"][1]["dimensions"]["quarantine"] == "blocked"


def test_bad_receipt_preserves_independently_verified_original_fixity(project_root: Path) -> None:
    scope, records, bank, contract = fixture(project_root)
    records[0]["record"]["evidence"]["custody_receipt_sha256"] = "0" * 64
    rebind(records)
    report = evaluate((scope, records, bank, contract))
    first = report["coverage"][0]
    assert first["dimensions"]["fixity"] == "verified"
    assert first["dimensions"]["reproducibility"] == "failed"
    assert first["blockers"]
