"""Complete declared candidate assurance, not release clearance.

All candidate and native inputs are supplied bytes. Only implementation
fingerprints read local files; no provider, source or executable is requested.
"""

from collections import Counter
from pathlib import Path
from typing import Any

from . import (
    medallion_candidate_dependencies,
    medallion_candidate_inputs,
    medallion_candidate_native,
    medallion_candidate_scan,
)
from .medallion_qualification_inputs import canonical, sha

DIMENSIONS = (
    "fixity",
    "secrets",
    "prohibited_data",
    "disclosure",
    "dependencies",
    "provenance",
    "supply_chain",
    "locators",
)
STATUSES = ("checked_no_findings", "failed", "unsupported", "missing_evidence")


class CandidateAssuranceError(ValueError):
    """Fixed diagnostic without untrusted candidate content."""


def _require(value: bool) -> None:
    if not value:
        raise CandidateAssuranceError("Candidate assurance contract violation")


def _composition(
    obj: dict[str, Any], objects: dict[str, dict[str, Any]], scan: dict[str, Any]
) -> dict[str, Any]:
    targets = [
        objects[edge["target_object_id"]]["sha256"]
        for edge in obj["edges"]
        if edge["relation"] == "package_member"
    ]
    if obj["media_type"] not in {"application/zip", medallion_candidate_scan.XLSX}:
        return {"status": "unsupported", "code": "PACKAGE_FORMAT_UNSUPPORTED"}
    if scan["status"] != "checked_no_findings":
        return {"status": "unsupported", "code": "PACKAGE_SCAN_INCOMPLETE"}
    if not targets:
        return {"status": "missing_evidence", "code": "PACKAGE_MEMBER_EDGES_MISSING"}
    if Counter(targets) != Counter(scan["member_sha256"]):
        return {"status": "failed", "code": "PACKAGE_MEMBER_MULTISET_MISMATCH"}
    return {"status": "checked_no_findings", "code": "PACKAGE_MEMBER_MULTISET_VERIFIED"}


def _assess(
    plan_raw: bytes,
    expected_plan_sha256: str,
    scope_raw: bytes,
    candidate_bank: dict[str, bytes],
    evidence_bundles: dict[str, Any],
) -> dict[str, Any]:
    prepared = medallion_candidate_inputs.prepare_candidate_inputs(
        plan_raw, expected_plan_sha256, scope_raw, candidate_bank, evidence_bundles
    )
    plan, scope = prepared["plan"], prepared["scope"]
    objects = {obj["object_id"]: obj for obj in scope["objects"]}
    scans = {}
    for obj in scope["objects"]:
        digest = obj["sha256"]
        if digest not in scans:
            scans[digest] = medallion_candidate_scan.scan_candidate_bytes(
                candidate_bank[digest], obj["media_type"]
            )
    native = medallion_candidate_native.assess_native_evidence(prepared)
    dependency = None
    dependency_digests: set[str] = set()
    package_ids: set[str] = set()
    if "dependencies" in evidence_bundles:
        bundle = evidence_bundles["dependencies"]
        dependency = medallion_candidate_dependencies.assess_dependency_evidence(
            **bundle,
            candidate_id=plan["candidate_id"],
            as_of=plan["as_of"],
            candidate_bank=candidate_bank,
            scope_objects=scope["objects"],
        )
        dependency_digests = {
            sha(bundle[key]) for key in ("lock_raw", "sbom_raw", "package_bindings_raw")
        }
        package_ids = {item["object_id"] for item in dependency["validated_package_bindings"]}
    rows = []
    for identity, obj in sorted(objects.items()):
        scan = scans[obj["sha256"]]
        dimensions = dict.fromkeys(DIMENSIONS, "missing_evidence")
        dimensions["fixity"] = "checked_no_findings"
        dimensions.update(scan["checks"])
        dimensions["locators"] = (
            "checked_no_findings" if all(obj["locators"].values()) else "missing_evidence"
        )
        provenance = native["provenance"].get(
            identity,
            {
                "status": "missing_evidence",
                "roles": [],
                "references": [],
            },
        )
        dimensions["provenance"] = provenance["status"]
        dimensions["disclosure"] = native["disclosure"].get(identity, "unsupported")
        if dependency is not None:
            graph_status = (
                "checked_no_findings"
                if identity in package_ids
                or (obj["role"] != "package" and obj["sha256"] in dependency_digests)
                else "unsupported"
            )
            dimensions["dependencies"] = graph_status
            dimensions["supply_chain"] = graph_status
        composition = _composition(obj, objects, scan)
        # Distribution binding does not conceal incomplete archive composition.
        if obj["role"] == "package" and composition["status"] != "checked_no_findings":
            dimensions["supply_chain"] = composition["status"]
        if (
            any(edge["relation"] == "package_member" for edge in obj["edges"])
            and composition["status"] != "checked_no_findings"
        ):
            dimensions["provenance"] = composition["status"]
        _require(
            set(dimensions) == set(DIMENSIONS)
            and all(value in STATUSES for value in dimensions.values())
        )
        rows.append(
            {
                "object_id": identity,
                "logical_object_id": obj["logical_object_id"],
                "edition_id": obj["edition_id"],
                "layer": obj["layer"],
                "role": obj["role"],
                "lifecycle": obj["lifecycle"],
                "sha256": obj["sha256"],
                "dimensions": dimensions,
                "scan_sha256": sha(canonical(scan)),
                "findings": scan["findings"],
                "unsupported_codes": scan["unsupported_codes"],
                "provenance": provenance,
                "package_composition": composition,
            }
        )
    coverage = {
        dimension: {
            status: sum(row["dimensions"][dimension] == status for row in rows)
            for status in STATUSES
        }
        for dimension in DIMENSIONS
    }
    components = (
        medallion_candidate_inputs,
        medallion_candidate_scan,
        medallion_candidate_native,
        medallion_candidate_dependencies,
    )
    report = {
        "contract_version": "gfjd-candidate-assurance-v1",
        "candidate_id": plan["candidate_id"],
        "as_of": plan["as_of"],
        "plan_sha256": expected_plan_sha256,
        "scope_sha256": sha(scope_raw),
        "inventory": prepared["inventory_report"],
        "objects": rows,
        "coverage": coverage,
        "bundle_fingerprints": prepared["bundle_fingerprints"],
        "native_evidence": native["summaries"],
        "dependency_evidence": dependency,
        "mechanical_coverage_complete": all(
            row["dimensions"][dimension] == "checked_no_findings"
            for row in rows
            for dimension in DIMENSIONS
        ),
        "release_status": "blocked",
        "factual_requirements": dict.fromkeys(
            [
                "actual_inventory_completeness",
                "comprehensive_privacy_and_security_assurance",
                "rights_and_disclosure_acceptance",
                "current_vulnerability_assurance",
                "artifact_and_publisher_authenticity",
                "actual_remote_restore",
                "signing_custody",
                "accountable_release_acceptance",
            ],
            "unverified",
        ),
        "authority": dict.fromkeys(
            [
                "network",
                "source_access",
                "rights",
                "promotion",
                "publication",
                "release",
                "gate_acceptance",
            ],
            False,
        ),
        "limitations": [
            "Complete declared supplied inventory only; no assertion of complete real inventory.",
            "Pattern and header checks are bounded diagnostics, not comprehensive safety.",
            "Typed locator syntax only; embedded URLs and remote availability are unassessed.",
            "Internal graph consistency does not establish actual imports or authenticity.",
            "Zero scanner findings does not establish absence of unresolved critical risks.",
        ],
        "implementation_sha256": sha(Path(__file__).read_bytes()),
        "component_implementation_sha256": {
            module.__name__: sha(Path(str(module.__file__)).read_bytes()) for module in components
        },
    }
    report["report_sha256"] = sha(canonical(report))
    return report


def assess_candidate_assurance(
    plan_raw: bytes,
    expected_plan_sha256: str,
    scope_raw: bytes,
    candidate_bank: dict[str, bytes],
    evidence_bundles: dict[str, Any],
) -> dict[str, Any]:
    """Recompute every supplied component after complete input preflight."""
    try:
        return _assess(plan_raw, expected_plan_sha256, scope_raw, candidate_bank, evidence_bundles)
    except Exception:
        raise CandidateAssuranceError("Candidate assurance contract violation") from None


def verify_candidate_assurance(
    plan_raw: bytes,
    expected_plan_sha256: str,
    scope_raw: bytes,
    candidate_bank: dict[str, bytes],
    evidence_bundles: dict[str, Any],
    report: dict[str, Any],
) -> None:
    """Exact recomputation; report self-hashes do not prove correct assurance."""
    expected = assess_candidate_assurance(
        plan_raw, expected_plan_sha256, scope_raw, candidate_bank, evidence_bundles
    )
    try:
        _require(type(report) is dict and canonical(report) == canonical(expected))
    except Exception:
        raise CandidateAssuranceError("Candidate assurance contract violation") from None
