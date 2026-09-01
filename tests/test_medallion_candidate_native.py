"""Fictional native associations, never public execution evidence."""

import copy
import json
from pathlib import Path

from blake3 import blake3

from gfjd import medallion_candidate_native as native
from gfjd.medallion_candidate_inputs import bundle_fingerprint, prepare_candidate_inputs
from gfjd.medallion_candidate_native import assess_native_evidence
from tests.test_medallion_candidate_inputs import call, encoded, fixture, sha
from tests.test_medallion_qualification import AS_OF, arguments
from tests.test_medallion_qualification import fixture as qualification_fixture


def test_missing_native_evidence_remains_missing():
    report = assess_native_evidence(call(fixture()))
    assert report["provenance"]["FICTIONAL"]["status"] == "missing_evidence"
    assert report["disclosure"]["FICTIONAL"] == "unsupported"
    assert report["summaries"]["qualification"]["status"] == "missing_evidence"


def candidate_object(identity, logical, edition, layer, role, raw):
    return {
        "object_id": identity,
        "logical_object_id": logical,
        "edition_id": edition,
        "layer": layer,
        "role": role,
        "lifecycle": "active",
        "sha256": sha(raw),
        "blake3": blake3(raw).hexdigest(),
        "size_bytes": len(raw),
        "media_type": "application/json",
        "edges": [],
        "locators": {"github": None, "huggingface": None},
    }


def qualification_candidate():
    source_scope, source_records, source_bank, contract = qualification_fixture(Path.cwd())
    scope, scope_sha, contract, records, payloads = arguments(
        source_scope, source_records, source_bank, contract
    )
    objects, bank, counter = [], {}, 0
    for digest, wrapper_raw in records.items():
        wrapper = json.loads(wrapper_raw)
        logical, edition, layer = (
            wrapper["object_id"],
            wrapper["edition_id"],
            wrapper["record"]["layer"],
        )
        objects.append(
            candidate_object(f"wrapper-{counter}", logical, edition, layer, "metadata", wrapper_raw)
        )
        counter += 1
        bank[digest] = wrapper_raw
        for artifact_role, payload_digest in wrapper["artifacts"].items():
            raw = payloads[payload_digest]
            role = (
                "data"
                if artifact_role in {"source", "rows"}
                else "transformation"
                if artifact_role == "contract"
                else "manifest"
                if artifact_role == "manifest"
                else "metadata"
            )
            objects.append(
                candidate_object(f"artifact-{counter}", logical, edition, layer, role, raw)
            )
            counter += 1
            bank[payload_digest] = raw
    for label, raw in (("native-scope", scope), ("layer-contract", contract)):
        objects.append(candidate_object(label, label, "CONTROL", "cross_layer", "metadata", raw))
        bank[sha(raw)] = raw
    candidate_scope = {
        "contract_version": "gfjd-candidate-assurance-scope-v1",
        "candidate_id": "FICTIONAL",
        "objects": objects,
    }
    bundle = {
        "scope_raw": scope,
        "scope_sha256": scope_sha,
        "layer_contract_raw": contract,
        "record_bank": records,
        "payload_bank": payloads,
        "as_of": AS_OF,
    }
    plan = {
        "contract_version": "gfjd-candidate-assurance-plan-v1",
        "state": "preparation",
        "candidate_id": "FICTIONAL",
        "as_of": AS_OF,
        "scope_sha256": sha(encoded(candidate_scope)),
        "evidence_bindings": {
            "qualification": bundle_fingerprint(bundle),
            "restore": None,
            "lifecycle": None,
            "dependencies": None,
        },
    }
    plan_raw = encoded(plan)
    return prepare_candidate_inputs(
        plan_raw, sha(plan_raw), encoded(candidate_scope), bank, {"qualification": bundle}
    )


def test_recomputes_qualification_and_preserves_all_cells():
    report = assess_native_evidence(qualification_candidate())
    summary = report["summaries"]["qualification"]
    assert summary["status"] == "recomputed" and summary["cell_count"] == 5
    assert len(summary["cells"]) == 5
    assert all(
        set(cell)
        == {
            "object_id_sha256",
            "edition_id_sha256",
            "layer",
            "record_sha256",
            "lifecycle_state",
            "dimensions",
            "mapped_candidate_ids",
        }
        for cell in summary["cells"]
    )
    assert all("source" not in str(cell).lower() for cell in summary["cells"])
    assert any(item["status"] == "checked_no_findings" for item in report["provenance"].values())


def test_unrelated_gold_bytes_cannot_borrow_disclosure():
    prepared = qualification_candidate()
    gold = next(
        obj
        for obj in prepared["scope"]["objects"]
        if obj["layer"] == "gold" and obj["role"] == "data"
    )
    unrelated = copy.deepcopy(gold)
    raw = b'{"fictional":"unrelated"}'
    unrelated.update(
        object_id="unrelated-gold",
        sha256=sha(raw),
        blake3=blake3(raw).hexdigest(),
        size_bytes=len(raw),
    )
    prepared["scope"]["objects"].append(unrelated)
    prepared["candidate_bank"][sha(raw)] = raw
    report = assess_native_evidence(prepared)
    assert report["disclosure"]["unrelated-gold"] == "unsupported"
    assert report["provenance"]["unrelated-gold"]["status"] == "missing_evidence"


def test_derived_provenance_requires_exact_declared_source_edge():
    prepared = qualification_candidate()
    gold = next(
        obj
        for obj in prepared["scope"]["objects"]
        if obj["layer"] == "gold" and obj["role"] == "data"
    )
    source = next(
        obj
        for obj in prepared["scope"]["objects"]
        if obj["layer"] == "silver" and obj["role"] == "data"
    )
    assert assess_native_evidence(prepared)["provenance"][gold["object_id"]]["status"] == (
        "missing_evidence"
    )
    gold["edges"] = [{"relation": "source", "target_object_id": source["object_id"]}]
    assert assess_native_evidence(prepared)["provenance"][gold["object_id"]]["status"] == (
        "checked_no_findings"
    )
    gold["edges"] = [{"relation": "source", "target_object_id": "native-scope"}]
    assert assess_native_evidence(prepared)["provenance"][gold["object_id"]]["status"] == "failed"


def test_lifecycle_matches_unique_exact_sibling_not_scope_order(monkeypatch):
    matching = {
        "object_id": "matching",
        "logical_object_id": "LOGICAL",
        "edition_id": "EDITION",
        "layer": "gold",
        "role": "data",
        "lifecycle": "active",
        "sha256": "a" * 64,
    }
    unrelated = {
        **matching,
        "object_id": "unrelated",
        "role": "metadata",
        "sha256": "b" * 64,
    }
    report = {
        "as_of": "2026-09-01T00:00:00Z",
        "heads": [{"artifact_id": "ART", "state": "active"}],
        "inventory": [
            {
                "artifact_id": "ART",
                "object_id": "LOGICAL",
                "edition_id": "EDITION",
                "layer": "gold",
                "content_sha256": "a" * 64,
                "state": "active",
            }
        ],
        "declared_provider_backlog": [],
    }
    monkeypatch.setattr(
        native.medallion_lifecycle, "assess_lifecycle_journal", lambda *a, **k: report
    )
    prepared = {
        "plan": {"as_of": report["as_of"]},
        "scope": {"objects": [matching, unrelated]},
    }
    summary = native._lifecycle(
        {
            "plan_raw": b"x",
            "expected_plan_sha256": "x",
            "scope_raw": b"x",
            "layer_contract_raw": b"x",
            "checkpoint_raw": b"x",
            "event_bank": {},
            "receipt_bank": {},
        },
        prepared,
    )
    assert summary["cells"][0]["candidate_id"] == "matching"


def test_lifecycle_preserves_missing_inactive_history_with_current_sibling(monkeypatch):
    current = {
        "object_id": "current",
        "logical_object_id": "LOGICAL",
        "edition_id": "EDITION",
        "layer": "gold",
        "role": "data",
        "lifecycle": "active",
        "sha256": "a" * 64,
    }
    report = {
        "as_of": "2026-09-01T00:00:00Z",
        "heads": [{"artifact_id": "CURRENT", "state": "active"}],
        "inventory": [
            {
                "artifact_id": "OLD",
                "object_id": "LOGICAL",
                "edition_id": "EDITION",
                "layer": "gold",
                "content_sha256": "b" * 64,
                "state": "withdrawn",
            },
            {
                "artifact_id": "CURRENT",
                "object_id": "LOGICAL",
                "edition_id": "EDITION",
                "layer": "gold",
                "content_sha256": "a" * 64,
                "state": "active",
            },
        ],
        "declared_provider_backlog": [],
    }
    monkeypatch.setattr(
        native.medallion_lifecycle, "assess_lifecycle_journal", lambda *a, **k: report
    )
    prepared = {"plan": {"as_of": report["as_of"]}, "scope": {"objects": [current]}}
    summary = native._lifecycle(
        {
            "plan_raw": b"x",
            "expected_plan_sha256": "x",
            "scope_raw": b"x",
            "layer_contract_raw": b"x",
            "checkpoint_raw": b"x",
            "event_bank": {},
            "receipt_bank": {},
        },
        prepared,
    )
    assert len(summary["historical_digest_only_gaps"]) == 1
    assert summary["cells"][0]["candidate_id"] is None
