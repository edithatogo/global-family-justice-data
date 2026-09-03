"""Fictional end-to-end federation rehearsal; no source or provider access.

Developer-only rehearsal using checked-in fictional fixture builders. It reads
those builders, normative assets and estate configuration, never court sources.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import runpy
import stat
from pathlib import Path
from typing import Any

from gfjd.federation_bundle import ASSETS
from gfjd.federation_interface_bundle import prepare_interface_bundle, verify_interface_bundle
from gfjd.federation_metadata import MetadataError
from gfjd.federation_partner_interfaces import PINNED
from gfjd.medallion_estate import POLICY_REFERENCE, SOURCEFILES, prepare_estate
from gfjd.medallion_replay import replay_projection

ROOT = Path(__file__).resolve().parents[1]
BUILDERS = (
    "tests/test_federation_openlineage.py",
    "tests/test_federation_dcat.py",
    "tests/test_federation_rocrate.py",
    "tests/test_federation_croissant.py",
)


def canonical(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode()


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def fictional_inputs() -> tuple[Any, ...]:
    standards = {name: (ROOT / "src/gfjd/federation_specs" / name).read_bytes() for name in ASSETS}
    estate = {
        name: (ROOT / name).read_bytes().replace(b"edithatogo", b"fictional-estate")
        for name in SOURCEFILES
    }
    estate[POLICY_REFERENCE] = (ROOT / POLICY_REFERENCE).read_bytes()
    builders = [runpy.run_path(str(ROOT / name)) for name in BUILDERS]
    # Unwrap fixture factories explicitly: this is a development rehearsal,
    # not production input discovery or an independent data-extraction path.
    documents = [
        (canonical(builders[0]["event"].__wrapped__()), "application/json"),
        (builders[1]["data"].__wrapped__(), "application/n-triples"),
        (canonical(builders[2]["metadata"].__wrapped__()), "application/ld+json"),
        (
            canonical(
                builders[3]["metadata"].__wrapped__(standards["gfjd-croissant-profile-v1.json"])
            ),
            "application/ld+json",
        ),
    ]
    source = canonical([{"fictional": "FICTIONAL_INPUT_ONLY_MARKER"}])
    contract = {
        "contract_version": "gfjd-json-projection-v1",
        "source_sha256": sha(source),
        "projection": {"value": "fictional"},
        "valid_from": None,
        "recorded_at": "2026-08-31T00:00:00Z",
    }
    contract_raw = canonical(contract)
    receipt_raw = canonical(replay_projection(source, contract))
    objects = [
        {
            "object_id": f"fictional-{ordinal}",
            "canonical_id": f"urn:gfjd:source:fictional-{ordinal}",
            "kind": "source",
            "role": "source-catalogue",
            "content_sha256": sha(source) if ordinal == 0 else "a" * 64 if ordinal == 1 else None,
            "metadata_sha256": sha(raw),
            "media_type": media,
            "references": [f"https://example.invalid/fictional-{ordinal}"],
        }
        for ordinal, (raw, media) in enumerate(documents)
    ]
    scope_raw = canonical(
        {
            "contract_version": "gfjd-federation-reference-scope-v1",
            "state": "preparation",
            "estate_manifest_sha256": sha(prepare_estate(estate)["estate-manifest.json"]),
            "objects": objects,
            "partners": [
                "archive-govt-nz",
                "global-medicines-atlas",
                "dataset-estate-registry",
                "reimbursement-atlas",
            ],
        }
    )
    replay_raw = canonical(
        {
            "contract_version": "gfjd-federation-replay-attachment-v1",
            "mode": "projection",
            "selection": {
                "object_id": "fictional-0",
                "entity_role": "source",
                "event_id": None,
                "entity_sha256": sha(source),
            },
            "inputs": {
                "source_sha256": sha(source),
                "contract_sha256": sha(contract_raw),
                "receipt_sha256": sha(receipt_raw),
            },
        }
    )
    parquet_raw = canonical(
        {
            "contract_version": "gfjd-parquet-reference-declarations-v1",
            "scope_sha256": sha(scope_raw),
            "state": "preparation",
            "objects": [
                {
                    "object_id": "fictional-1",
                    "canonical_id": "urn:gfjd:source:fictional-1",
                    "content_format": "parquet",
                    "content_sha256": "a" * 64,
                    "blake3": "b" * 64,
                    "byte_count": 123,
                    "locations": [
                        {
                            "url": "https://example.invalid/fictional.parquet",
                            "revision": {"kind": "content_sha256", "value": "a" * 64},
                        }
                    ],
                }
            ],
        }
    )
    partner_raw = canonical(
        {
            "contract_version": "gfjd-partner-interface-references-v1",
            "scope_sha256": sha(scope_raw),
            "state": "preparation",
            "partners": [
                {
                    "partner_id": name,
                    **copy.deepcopy(PINNED.get(name, {"commit": None, "artifacts": {}})),
                }
                for name in json.loads(scope_raw)["partners"]
            ],
        }
    )
    contracts = [
        (ROOT / "src/gfjd/federation_specs" / name).read_bytes()
        for name in (
            "partner-archive-ownership.py.txt",
            "partner-archive-publication.schema.json",
            "shared-medallion-v1.schema.json",
            "shared-medallion-v2.schema.json",
            "shared-medallion-v3.schema.json",
            "partner-gma-federation.schema.json",
            "partner-gma-semantics.py.txt",
        )
    ]
    return (
        scope_raw,
        sha(scope_raw),
        {sha(raw): raw for raw, _ in documents},
        estate,
        standards,
        replay_raw,
        sha(replay_raw),
        {sha(raw): raw for raw in (source, contract_raw, receipt_raw)},
        parquet_raw,
        sha(parquet_raw),
        partner_raw,
        sha(partner_raw),
        {sha(raw): raw for raw in contracts},
    )


def rebind_scope(inputs: list[Any], scope: dict[str, Any]) -> None:
    inputs[0] = canonical(scope)
    inputs[1] = sha(inputs[0])
    for index in (8, 10):
        declaration = json.loads(inputs[index])
        declaration["scope_sha256"] = inputs[1]
        inputs[index] = canonical(declaration)
        inputs[index + 1] = sha(inputs[index])


def build_report() -> dict[str, Any]:
    inputs = fictional_inputs()
    artifacts = prepare_interface_bundle(*inputs)
    verify_interface_bundle(*inputs, artifacts)
    if artifacts != prepare_interface_bundle(*inputs):
        raise ValueError("fictional federation nondeterminism")
    manifest = json.loads(artifacts["bundle-manifest.json"])
    assessments = json.loads(artifacts["metadata-assessments.json"])
    profiles = {
        report.get("profile", report.get("contract_version")) for report in assessments.values()
    }
    expected_profiles = {
        "design_event_only",
        "gfjd-dcat-base-range-v1",
        "gfjd-rocrate-declarations-v1",
        "gfjd-croissant-declarations-v1",
    }
    estate_roles = json.loads(artifacts["estate/estate-manifest.json"])["roles"]
    if profiles != expected_profiles or len(assessments) != 4 or len(estate_roles) != 6:
        raise ValueError("fictional federation route/estate coverage mismatch")
    if (
        manifest["incomplete_document_count"] != 0
        or len(manifest["provenance_pending_object_ids"]) != 3
        or any(manifest["authority"].values())
    ):
        raise ValueError("fictional federation state mismatch")
    if b"FICTIONAL_INPUT_ONLY_MARKER" in b"".join(artifacts.values()):
        raise ValueError("fictional input payload escaped")

    # A missing factual declaration must remain incomplete, not be fabricated.
    incomplete = list(copy.deepcopy(inputs))
    scope = json.loads(incomplete[0])
    old = scope["objects"][2]["metadata_sha256"]
    document = json.loads(incomplete[2].pop(old))
    del document["@graph"][1]["datePublished"]
    raw = canonical(document)
    incomplete[2][sha(raw)] = raw
    scope["objects"][2]["metadata_sha256"] = sha(raw)
    rebind_scope(incomplete, scope)
    incomplete_artifacts = prepare_interface_bundle(*incomplete)
    verify_interface_bundle(*incomplete, incomplete_artifacts)
    if json.loads(incomplete_artifacts["bundle-manifest.json"])["incomplete_document_count"] != 1:
        raise ValueError("missing declaration was not retained")

    parquet = json.loads(artifacts["interfaces/parquet-reference-report.json"])
    partners = json.loads(artifacts["interfaces/partner-interface-report.json"])
    if parquet["parquet_format_verified"] or partners["bound_partner_count"] != 2:
        raise ValueError("fictional interface state mismatch")
    missing = list(copy.deepcopy(inputs))
    declaration = json.loads(missing[8])
    declaration["objects"][0]["blake3"] = None
    missing[8] = canonical(declaration)
    missing[9] = sha(missing[8])
    missing_outputs = prepare_interface_bundle(*missing)
    verify_interface_bundle(*missing, missing_outputs)
    missing_report = json.loads(missing_outputs["interfaces/parquet-reference-report.json"])
    if "fictional-1:missing_blake3" not in missing_report["issues"]:
        raise ValueError("missing Parquet declaration was not retained")

    negative_checks = []
    for change in (
        "unrelated_object",
        "source_bytes",
        "extra_bank",
        "forged_output",
        "source_as_parquet",
        "rows_as_parquet",
        "partner_text_as_parquet",
        "generated_as_parquet",
        "partner_contract_drift",
        "missing_sidecar",
    ):
        changed = list(copy.deepcopy(inputs))
        output = copy.deepcopy(artifacts)
        if change == "unrelated_object":
            scoped = json.loads(changed[0])
            scoped["objects"][0]["content_sha256"] = "0" * 64
            rebind_scope(changed, scoped)
        elif change == "source_bytes":
            digest = json.loads(changed[5])["inputs"]["source_sha256"]
            changed[7][digest] += b" "
        elif change == "extra_bank":
            changed[7][sha(b"{}")] = b"{}"
        elif change.endswith("_as_parquet"):
            replay = json.loads(changed[5])
            if change == "source_as_parquet":
                digest = replay["inputs"]["source_sha256"]
            elif change == "rows_as_parquet":
                receipt = json.loads(changed[7][replay["inputs"]["receipt_sha256"]])
                digest = sha(canonical(receipt["rows"]))
            elif change == "generated_as_parquet":
                digest = sha(artifacts["estate/estate-manifest.json"])
            else:
                digest = next(iter(changed[12]))
            scoped = json.loads(changed[0])
            scoped["objects"][1]["content_sha256"] = digest
            rebind_scope(changed, scoped)
            declaration = json.loads(changed[8])
            declaration["objects"][0]["content_sha256"] = digest
            declaration["objects"][0]["locations"][0]["revision"]["value"] = digest
            changed[8] = canonical(declaration)
            changed[9] = sha(changed[8])
        elif change == "partner_contract_drift":
            digest = next(iter(changed[12]))
            changed[12][digest] += b" "
        elif change == "missing_sidecar":
            changed[8] = b""
            changed[9] = sha(b"")
        else:
            forged = json.loads(output["bundle-manifest.json"])
            forged["authority"]["publication"] = True
            output["bundle-manifest.json"] = canonical(forged)
        try:
            if change == "forged_output":
                verify_interface_bundle(*changed, output)
            else:
                prepare_interface_bundle(*changed)
        except MetadataError:
            negative_checks.append(change)
        else:
            raise ValueError("fictional negative case was accepted")
    return {
        "rehearsal_id": "FICTIONAL-FEDERATION-INTERFACES-20260901-02",
        "synthetic": True,
        "factual_evidence": "unverified",
        "scope_sha256": inputs[1],
        "replay_sha256": inputs[6],
        "parquet_declaration_sha256": inputs[9],
        "partner_declaration_sha256": inputs[11],
        "partner_contract_sha256": sorted(inputs[12]),
        "artifact_sha256": {name: sha(raw) for name, raw in sorted(artifacts.items())},
        "fixture_builder_sha256": {name: sha((ROOT / name).read_bytes()) for name in BUILDERS},
        "rehearsal_implementation_sha256": sha(Path(__file__).read_bytes()),
        "metadata_route_count": len(assessments),
        "metadata_profiles": sorted(profiles),
        "estate_role_count": len(estate_roles),
        "selected_entity_binding": manifest["replay_binding"],
        "provenance_pending_object_ids": manifest["provenance_pending_object_ids"],
        "incomplete_metadata_preserved": True,
        "incomplete_parquet_preserved": True,
        "parquet_format_verified": parquet["parquet_format_verified"],
        "bound_partner_count": partners["bound_partner_count"],
        "pending_partner_ids": partners["pending_partner_ids"],
        "negative_cases_rejected": negative_checks,
        "authority": manifest["authority"],
        "limitation": "fictional machinery rehearsal; no empirical or partner acceptance",
    }


def safe_location(target: Path) -> None:
    """Reject links/special files; caller chooses an ordinary local output path."""
    for path in (target, *target.parents):
        if path.is_symlink():
            raise ValueError("symlink path")
        if path.exists():
            mode = path.lstat().st_mode
            if path == target:
                if not stat.S_ISREG(mode):
                    raise ValueError("nonregular report")
            elif not stat.S_ISDIR(mode):
                raise ValueError("non-directory ancestor")


def read_report(target: Path, limit: int) -> bytes:
    # O_NONBLOCK avoids blocking on a raced FIFO; fstat validates the opened
    # descriptor, not merely the earlier path. No platform isolation is claimed.
    descriptor = os.open(
        target, os.O_RDONLY | getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_NOFOLLOW", 0)
    )
    try:
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            raise ValueError("nonregular report")
        with os.fdopen(descriptor, "rb", closefd=False) as stream:
            return stream.read(limit)
    finally:
        os.close(descriptor)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--output", type=Path)
    action.add_argument("--verify", type=Path)
    action.add_argument("--output-directory", type=Path)
    action.add_argument("--verify-directory", type=Path)
    args = parser.parse_args(argv)
    expected = canonical(build_report()) + b"\n"
    verifying = args.verify is not None or args.verify_directory is not None
    directory = args.verify_directory if verifying else args.output_directory
    if directory is not None:
        target = directory / ("report-" + sha(expected) + ".json")
    else:
        target = args.verify if verifying else args.output
    target = target.absolute()
    try:
        safe_location(target)
        if verifying or target.exists():
            if read_report(target, len(expected) + 1) != expected:
                raise ValueError("report differs")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            safe_location(target)
            with target.open("xb") as stream:
                stream.write(expected)
    except (OSError, ValueError):
        print("fictional federation report unavailable or differs; no overwrite")
        return 1
    print("fictional federation exact recomputation passed; no promotion authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
