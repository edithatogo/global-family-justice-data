"""Two supplied complete banks, independently qualified; never a public restore.

Only implementation fingerprint files are read. No network, cache or artifact
loader is used. Provider locations are unrequested declarations.
"""

from pathlib import Path
from typing import Any

from . import medallion_restore_inputs
from .medallion_qualification import qualify_layers
from .medallion_qualification_inputs import canonical, sha


def _require(condition: bool) -> None:
    if not condition:
        raise ValueError("restore rehearsal contract failed")


def _rebuild_verified(report: dict[str, Any]) -> bool:
    active = [cell for cell in report["coverage"] if cell["lifecycle"]["state"] == "active"]
    if not any(cell["layer"] != "b0" for cell in active):
        return False
    for cell in active:
        required = ["completeness", "fixity", "quarantine"]
        if cell["layer"] != "b0":
            required += ["lineage", "reproducibility"]
        if cell["layer"] in {"b0", "gold"}:
            required.append("quality")
        if cell["blockers"] or any(cell["dimensions"][key] != "verified" for key in required):
            return False
    return True


def assess_restore_rehearsal(
    plan_raw: bytes,
    expected_plan_sha256: str,
    scope_raw: bytes,
    expected_scope_sha256: str,
    layer_contract_raw: bytes,
    replica_banks: dict[str, dict[str, bytes]],
) -> dict[str, Any]:
    """Verify complete inputs first, then reproduce the frozen report twice."""
    _require(type(replica_banks) is dict and set(replica_banks) == {"github", "huggingface"})
    prepared = {
        provider: medallion_restore_inputs.prepare_replica(
            plan_raw,
            expected_plan_sha256,
            scope_raw,
            expected_scope_sha256,
            layer_contract_raw,
            replica_banks[provider],
            provider,
        )
        for provider in ("github", "huggingface")
    }
    qualifications = {}
    for provider, inputs in prepared.items():
        result = qualify_layers(
            inputs["scope_raw"],
            expected_scope_sha256,
            inputs["layer_contract_raw"],
            inputs["record_bank"],
            inputs["eligible_payload_bank"],
            as_of=inputs["plan"]["as_of"],
        )
        _require(sha(canonical(result)) == inputs["plan"]["expected_qualification_sha256"])
        qualifications[provider] = result
    _require(canonical(qualifications["github"]) == canonical(qualifications["huggingface"]))
    qualification = qualifications["github"]
    report = {
        "contract_version": "gfjd-two-replica-restore-rehearsal-v1",
        "plan_sha256": expected_plan_sha256,
        "scope_sha256": expected_scope_sha256,
        "layer_contract_sha256": sha(layer_contract_raw),
        "release_id": prepared["github"]["plan"]["release_id"],
        "as_of": prepared["github"]["plan"]["as_of"],
        "supplied_inventory_fixity": "verified",
        "expected_report_reproduction": "verified",
        "qualification_sha256": sha(canonical(qualification)),
        "qualification": qualification,
        "offline_rebuild_verified": _rebuild_verified(qualification),
        "replicas": {
            provider: {
                "inventory": inputs["inventory_report"],
                "preservation_edges": inputs["preservation_edges"],
                "binding_sha256": inputs["binding"]["report_sha256"],
                "qualification_sha256": sha(canonical(qualifications[provider])),
            }
            for provider, inputs in prepared.items()
        },
        "implementation_sha256": sha(Path(__file__).read_bytes()),
        "input_implementation_sha256": sha(Path(medallion_restore_inputs.__file__).read_bytes()),
        "public_restore": "unverified",
        "factual_requirements": dict.fromkeys(
            [
                "anonymous_retrieval",
                "provider_independence",
                "no_cache_acquisition",
                "remote_availability",
                "real_release_inventory_completeness",
            ],
            "unverified",
        ),
        "limitations": [
            "Supplied complete declared inventory only; no provider was requested.",
            "Inactive and auxiliary bytes receive fixity, not semantic qualification.",
            "Mechanical reproduction does not accept pending factual layer requirements.",
        ],
        "authority": dict.fromkeys(
            [
                "network",
                "source_access",
                "rights",
                "promotion",
                "publication",
                "release",
                "transfer",
                "gate_acceptance",
            ],
            False,
        ),
    }
    report["report_sha256"] = sha(canonical(report))
    return report


def verify_restore_rehearsal(
    plan_raw: bytes,
    expected_plan_sha256: str,
    scope_raw: bytes,
    expected_scope_sha256: str,
    layer_contract_raw: bytes,
    replica_banks: dict[str, dict[str, bytes]],
    report: dict[str, Any],
) -> None:
    """Recompute, never trust a report's claimed success or supplied self-hash."""
    expected = assess_restore_rehearsal(
        plan_raw,
        expected_plan_sha256,
        scope_raw,
        expected_scope_sha256,
        layer_contract_raw,
        replica_banks,
    )
    _require(canonical(report) == canonical(expected))
