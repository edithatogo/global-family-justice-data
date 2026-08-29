from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from gfjd.g2_successor_controls import (
    ROLE_POLICY,
    G2SuccessorControlError,
    collect_exposure_identities,
    record_complete_provider_results,
    verify_authorization_anchor,
    verify_connected_peer,
    verify_role_isolation,
    verify_successor_design,
)
from gfjd.io import sha256_file


def test_provider_over_return_is_completely_recorded_but_selection_bounded() -> None:
    result = record_complete_provider_results(
        [{"canonical_url": f"https://example.test/{index}"} for index in range(16)],
        requested_maximum=10,
        absolute_safety_cap=50,
    )
    assert result["observed_result_count"] == 16
    assert result["provider_over_returned"] is True
    assert result["all_observed_results_recorded"] is True
    assert sum(item["eligible_for_registration"] for item in result["observed_results"]) == 10


def test_provider_absolute_safety_cap_still_fails_closed() -> None:
    with pytest.raises(G2SuccessorControlError, match="absolute safety cap"):
        record_complete_provider_results(
            [{"canonical_url": f"https://example.test/{index}"} for index in range(6)],
            requested_maximum=5,
            absolute_safety_cap=5,
        )


def test_provider_result_rejects_snippets_and_arbitrary_metadata() -> None:
    with pytest.raises(G2SuccessorControlError, match="non-locator metadata"):
        record_complete_provider_results(
            [
                {
                    "canonical_url": "https://example.test/result",
                    "snippet": "must not be persisted",
                }
            ],
            requested_maximum=1,
            absolute_safety_cap=5,
        )


def test_exposure_collects_established_locator_and_digest_aliases() -> None:
    payload = {
        "content_sha256": "a" * 64,
        "source_sha256": "b" * 64,
        "models_endpoint": "https://example.test/models",
        "query_endpoint": "https://example.test/query",
        "source_definition_pdf": "https://example.test/definition.pdf",
    }
    assert collect_exposure_identities(payload) == {
        "urls": [
            "https://example.test/definition.pdf",
            "https://example.test/models",
            "https://example.test/query",
        ],
        "content_sha256": ["a" * 64, "b" * 64],
    }


def _write_json(path: Path, value: object) -> dict[str, str]:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True), encoding="utf-8")
    return {"path": path.name, "sha256": sha256_file(path)}


def test_authorization_must_match_execution_contract_anchor(tmp_path: Path) -> None:
    authorization = _write_json(tmp_path / "authorization.json", {"decision": "approved"})
    preparation = _write_json(tmp_path / "preparation.json", {"status": "prepared"})
    contract = tmp_path / "contract.json"
    contract.write_text(
        json.dumps(
            {"owner_authorization": authorization, "preparation_bundle": preparation},
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    interlock = tmp_path / "interlock.json"
    interlock.write_text(
        json.dumps(
            {"owner_authorization": authorization, "preparation_bundle": preparation},
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    assert (
        verify_authorization_anchor(
            tmp_path,
            execution_contract_path=Path("contract.json"),
            interlock_path=Path("interlock.json"),
        )
        == []
    )

    fictional = _write_json(tmp_path / "fictional.json", {"decision": "approved"})
    interlock.write_text(
        json.dumps(
            {"owner_authorization": fictional, "preparation_bundle": preparation},
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    assert verify_authorization_anchor(
        tmp_path,
        execution_contract_path=Path("contract.json"),
        interlock_path=Path("interlock.json"),
    ) == ["interlock authorization differs from the execution-contract trust anchor"]


def _role_bundles() -> list[dict[str, object]]:
    bundles = []
    for role, policy in ROLE_POLICY.items():
        bundles.append(
            {
                "role": role,
                "network_mode": policy["network_mode"],
                "network_url_allowlist": (
                    ["https://example.test/source"] if role == "orchestrator" else []
                ),
                "input_artifact_classes": policy["inputs"],
                "prohibited_artifact_classes": policy["prohibited"],
                "output_prefix": f"controlled/{role}",
            }
        )
    return bundles


def test_role_isolation_requires_exact_matrix_and_distinct_outputs() -> None:
    bundles = _role_bundles()
    assert verify_role_isolation(bundles, selected_urls=["https://example.test/source"]) == []

    drifted = copy.deepcopy(bundles)
    drifted[1]["input_artifact_classes"] = ["source_artifact", "extractor_b_output"]
    assert (
        "input classes differ"
        in verify_role_isolation(drifted, selected_urls=["https://example.test/source"])[0]
    )

    duplicate = copy.deepcopy(bundles)
    duplicate[2]["output_prefix"] = duplicate[1]["output_prefix"]
    assert verify_role_isolation(duplicate, selected_urls=["https://example.test/source"]) == [
        "role output prefixes are not distinct"
    ]


def test_connected_peer_must_equal_validated_public_dns_result() -> None:
    verify_connected_peer(
        validated_addresses=["93.184.216.34"], connected_peer_address="93.184.216.34"
    )
    with pytest.raises(G2SuccessorControlError, match="differs"):
        verify_connected_peer(
            validated_addresses=["93.184.216.34"], connected_peer_address="8.8.8.8"
        )
    with pytest.raises(G2SuccessorControlError, match="differs"):
        verify_connected_peer(
            validated_addresses=["93.184.216.34"], connected_peer_address="127.0.0.1"
        )


def test_repository_successor_design_is_bound(project_root: Path) -> None:
    path = Path("data/methods/g2/G2PROSPECTIVE-SUCCESSOR-20260829-02/design/design.json")
    assert verify_successor_design(project_root, path) == []
