"""Offline fixity of prospective preparation; no execution authority."""

import hashlib
import json
from pathlib import Path

from gfjd import govuk_metadata_contract as runtime

ROOT = Path(__file__).resolve().parents[1]


def test_offline_contract_bundle_is_complete_and_bound() -> None:
    bundle = json.loads(
        (ROOT / "data/methods/g2-repro/offline-api-contract-bundle-2026-08-31.json").read_bytes()
    )
    expected = {
        "data/methods/g2-repro/offline-api-contract-2026-08-31.json",
        "data/methods/g2-repro/api-interface-evidence-2026-08-31.json",
        "docs/methods/g2-api-interface-qualification-2026-08-31.md",
        "docs/methods/g2-offline-api-contract-2026-08-31.md",
        "src/gfjd/govuk_metadata_contract.py",
        "tests/test_govuk_metadata_contract.py",
        "tests/test_offline_api_contract_bundle.py",
    }
    assert {item["path"] for item in bundle["bindings"]} == expected
    assert len(bundle["bindings"]) == len(expected)
    for item in bundle["bindings"]:
        raw = (ROOT / item["path"]).read_bytes()
        assert item["sha256"] == hashlib.sha256(raw).hexdigest()
        assert item["bytes"] == len(raw)
    assert bundle["execution_ready"] is False
    assert bundle["network_requests"] == 0
    assert bundle["historical_failed_evidence_reused"] is False
    assert bundle["qualification"] == "synthetic_offline_only"


def test_machine_contract_has_no_execution_or_acceptance_authority() -> None:
    contract = json.loads(
        (ROOT / "data/methods/g2-repro/offline-api-contract-2026-08-31.json").read_bytes()
    )
    assert all(value is False for value in contract["authority"].values())
    assert all(value is False for value in contract["execution_readiness"].values())
    assert contract["limits"]["network_requests"] == 0
    assert contract["date_policy"]["fallback_between_date_fields"] is False
    assert contract["retention"]["partial_passing_observations_on_failure"] is False
    assert contract["retention"]["fingerprints_are_anonymization"] is False
    assert contract["limits"] == {
        "input_bytes": runtime.MAX_BYTES,
        "results": runtime.MAX_RESULTS,
        "depth": runtime.MAX_DEPTH,
        "nodes": runtime.MAX_NODES,
        "array_items": runtime.MAX_ARRAY_ITEMS,
        "object_members": runtime.MAX_OBJECT_MEMBERS,
        "string_characters": runtime.MAX_STRING_CHARS,
        "network_requests": 0,
    }
    assert set(contract["root_required"]) == runtime.ROOT_REQUIRED
    assert set(contract["root_incidental"]) == runtime.ROOT_OPTIONAL
    assert set(contract["row_required"]) == runtime.ROW_REQUIRED
    assert (
        set(contract["row_optional_semantic"] + contract["row_incidental"]) == runtime.ROW_OPTIONAL
    )
