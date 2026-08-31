"""Supplied fictional banks are not observed public restores."""

import json
import runpy
from pathlib import Path
from unittest.mock import patch

import pytest
from blake3 import blake3

from gfjd import medallion_restore as restore
from gfjd.medallion_qualification import qualify_layers
from gfjd.medallion_qualification_inputs import canonical, sha

_fixture_module = runpy.run_path(str(Path(__file__).with_name("test_medallion_qualification.py")))
AS_OF = _fixture_module["AS_OF"]
arguments = _fixture_module["arguments"]
fixture = _fixture_module["fixture"]


def restore_arguments(*, blocked=False):
    scope, records, payloads, contract = fixture(Path(__file__).parents[1])
    if blocked:
        gold = next(record for record in records if record["record"]["layer"] == "gold")
        del gold["artifacts"]["quality"]
        payloads = _fixture_module["prune"](records, payloads)
    args = arguments(scope, records, payloads, contract)
    scope_raw, scope_sha, contract_raw, record_bank, payload_bank = args
    report = qualify_layers(*args, as_of=AS_OF)
    bank = {**record_bank, **payload_bank, scope_sha: scope_raw, sha(contract_raw): contract_raw}
    plan = {
        "contract_version": "gfjd-two-replica-restore-plan-v1",
        "state": "preparation",
        "release_id": "FICTIONAL-RESTORE",
        "scope_sha256": scope_sha,
        "layer_contract_sha256": sha(contract_raw),
        "as_of": AS_OF,
        "expected_qualification_sha256": sha(canonical(report)),
        "record_sha256": sorted(record_bank),
        "payload_sha256": sorted(payload_bank),
        "auxiliary_sha256": [],
        "inventory": [
            {"sha256": digest, "blake3": blake3(raw).hexdigest(), "size_bytes": len(raw)}
            for digest, raw in sorted(bank.items())
        ],
        "providers": {
            provider: {
                "locators": {digest: f"https://{host}/FICTIONAL/{digest}" for digest in bank}
            }
            for provider, host in (("github", "github.com"), ("huggingface", "huggingface.co"))
        },
    }
    raw = canonical(plan)
    return (
        raw,
        sha(raw),
        scope_raw,
        scope_sha,
        contract_raw,
        {"github": dict(bank), "huggingface": dict(bank)},
    )


def test_five_layers_rebuilt_twice_without_public_claim():
    args = restore_arguments()
    with patch.object(restore, "qualify_layers", wraps=qualify_layers) as qualifier:
        report = restore.assess_restore_rehearsal(*args)
    assert qualifier.call_count == 2
    assert report["offline_rebuild_verified"] is True
    assert report["public_restore"] == "unverified"
    assert len(report["qualification"]["coverage"]) == 5
    assert not any(report["authority"].values())
    restore.verify_restore_rehearsal(*args, report)


def test_missing_peer_stops_before_either_qualifier():
    args = restore_arguments()
    args[-1]["huggingface"].pop(next(iter(args[-1]["huggingface"])))
    with patch.object(restore, "qualify_layers") as qualifier, pytest.raises(ValueError):
        restore.assess_restore_rehearsal(*args)
    qualifier.assert_not_called()


def test_expected_hash_and_report_tampering_rejected():
    args = restore_arguments()
    report = restore.assess_restore_rehearsal(*args)
    report["public_restore"] = "verified"
    with pytest.raises(ValueError):
        restore.verify_restore_rehearsal(*args, report)


@pytest.mark.parametrize("layer", ["b0", "gold", "silver", "platinum"])
def test_reproduced_failure_never_success(layer):
    args = restore_arguments()
    with patch.object(restore, "qualify_layers", wraps=qualify_layers):
        report = restore.assess_restore_rehearsal(*args)["qualification"]
    cell = next(cell for cell in report["coverage"] if cell["layer"] == layer)
    cell["blockers"].append("FICTIONAL-failure")
    assert not restore._rebuild_verified(report)


def test_empty_or_b0_only_not_vacuous_rebuild():
    assert not restore._rebuild_verified({"coverage": []})


def test_expected_blocked_qualification_reproduces_without_rebuild_pass():
    report = restore.assess_restore_rehearsal(*restore_arguments(blocked=True))
    assert report["expected_report_reproduction"] == "verified"
    assert report["supplied_inventory_fixity"] == "verified"
    assert report["offline_rebuild_verified"] is False
    assert any(cell["blockers"] for cell in report["qualification"]["coverage"])


def test_wrong_expected_qualification_binding_stops():
    args = list(restore_arguments())
    plan = json.loads(args[0])
    plan["expected_qualification_sha256"] = "0" * 64
    args[0] = canonical(plan)
    args[1] = sha(args[0])
    with pytest.raises(ValueError, match="restore rehearsal contract failed"):
        restore.assess_restore_rehearsal(*args)


def test_plan_time_change_cannot_reuse_expected_report():
    args = list(restore_arguments())
    plan = json.loads(args[0])
    plan["as_of"] = "2026-09-01T00:00:00Z"
    args[0] = canonical(plan)
    args[1] = sha(args[0])
    with pytest.raises(ValueError):
        restore.assess_restore_rehearsal(*args)


@pytest.mark.parametrize("dimension", ["completeness", "fixity", "quarantine", "quality"])
def test_unverified_gold_dimension_blocks_rebuild(dimension):
    report = restore.assess_restore_rehearsal(*restore_arguments())["qualification"]
    cell = next(cell for cell in report["coverage"] if cell["layer"] == "gold")
    cell["dimensions"][dimension] = "pending"
    assert not restore._rebuild_verified(report)


def test_only_b0_active_not_rebuild():
    report = restore.assess_restore_rehearsal(*restore_arguments())["qualification"]
    for cell in report["coverage"]:
        if cell["layer"] != "b0":
            cell["lifecycle"]["state"] = "quarantined"
    assert not restore._rebuild_verified(report)


def test_no_network_or_artifact_loader():
    args = restore_arguments()
    with patch("socket.socket", side_effect=AssertionError("network forbidden")):
        report = restore.assess_restore_rehearsal(*args)
    assert report["factual_requirements"]["no_cache_acquisition"] == "unverified"
    assert "FICTIONAL-RESTORE" in canonical(report).decode()
