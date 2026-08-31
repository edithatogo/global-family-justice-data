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
from gfjd.federation_metadata import MetadataError
from gfjd.federation_replayed_bundle import prepare_replayed_bundle, verify_replayed_bundle
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
            "content_sha256": sha(source) if ordinal == 0 else None,
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
            "partners": ["dataset-estate-registry"],
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
    return (
        scope_raw,
        sha(scope_raw),
        {sha(raw): raw for raw, _ in documents},
        estate,
        standards,
        replay_raw,
        sha(replay_raw),
        {sha(raw): raw for raw in (source, contract_raw, receipt_raw)},
    )


def build_report() -> dict[str, Any]:
    inputs = fictional_inputs()
    artifacts = prepare_replayed_bundle(*inputs)
    verify_replayed_bundle(*inputs, artifacts)
    if artifacts != prepare_replayed_bundle(*inputs):
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
    incomplete[0] = canonical(scope)
    incomplete[1] = sha(incomplete[0])
    incomplete_artifacts = prepare_replayed_bundle(*incomplete)
    verify_replayed_bundle(*incomplete, incomplete_artifacts)
    if json.loads(incomplete_artifacts["bundle-manifest.json"])["incomplete_document_count"] != 1:
        raise ValueError("missing declaration was not retained")

    negative_checks = []
    for change in ("unrelated_object", "source_bytes", "extra_bank", "forged_output"):
        changed = list(copy.deepcopy(inputs))
        output = copy.deepcopy(artifacts)
        if change == "unrelated_object":
            scoped = json.loads(changed[0])
            scoped["objects"][0]["content_sha256"] = "0" * 64
            changed[0] = canonical(scoped)
            changed[1] = sha(changed[0])
        elif change == "source_bytes":
            digest = json.loads(changed[5])["inputs"]["source_sha256"]
            changed[7][digest] += b" "
        elif change == "extra_bank":
            changed[7][sha(b"{}")] = b"{}"
        else:
            forged = json.loads(output["bundle-manifest.json"])
            forged["authority"]["publication"] = True
            output["bundle-manifest.json"] = canonical(forged)
        try:
            if change == "forged_output":
                verify_replayed_bundle(*changed, output)
            else:
                prepare_replayed_bundle(*changed)
        except MetadataError:
            negative_checks.append(change)
        else:
            raise ValueError("fictional negative case was accepted")
    return {
        "rehearsal_id": "FICTIONAL-FEDERATION-BUNDLE-20260901-01",
        "synthetic": True,
        "factual_evidence": "unverified",
        "scope_sha256": inputs[1],
        "replay_sha256": inputs[6],
        "artifact_sha256": {name: sha(raw) for name, raw in sorted(artifacts.items())},
        "fixture_builder_sha256": {name: sha((ROOT / name).read_bytes()) for name in BUILDERS},
        "rehearsal_implementation_sha256": sha(Path(__file__).read_bytes()),
        "metadata_route_count": len(assessments),
        "metadata_profiles": sorted(profiles),
        "estate_role_count": len(estate_roles),
        "selected_entity_binding": manifest["replay_binding"],
        "provenance_pending_object_ids": manifest["provenance_pending_object_ids"],
        "incomplete_metadata_preserved": True,
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
