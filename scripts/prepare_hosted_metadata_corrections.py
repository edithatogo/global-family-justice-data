"""Prepare bounded metadata corrections from pinned Hub metadata snapshots."""

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry-snapshot", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw = (args.registry_snapshot / "catalog.json").read_bytes()
    require(
        hashlib.sha256(raw).hexdigest()
        == ("edf71865933c31b3047043db8844d7ea3edf54e546323e6793fe681cd2d0f26f"),
        "Registry predecessor changed",
    )
    schema_raw = (args.registry_snapshot / "catalog.schema.json").read_bytes()
    require(
        hashlib.sha256(schema_raw).hexdigest()
        == ("92220ad58029e4d21ca3fb5e73c8ea8e45576d9b6ff712292ecbf57ed90b3a6f"),
        "Registry schema changed",
    )
    catalog = json.loads(raw)
    before = json.loads(raw)
    expected = {
        "edithatogo/gfjd-source-catalogue",
        "edithatogo/gfjd-observations",
        "edithatogo/gfjd-outcomes-evidence",
        "edithatogo/gfjd-extraction-benchmark",
    }
    found = set()
    for item in catalog["datasets"]:
        if item["repo_id"] in expected:
            found.add(item["repo_id"])
            item.update(
                origin_repository="https://github.com/edithatogo/global-family-justice-data",
                upstream_source="GFJD repository-generated distribution; product payload absent",
                status="public_metadata_scaffold_no_product_payload",
                access="public",
                rights_status="no_product_payload_published",
                viewer_status="not_verified",
            )
    require(found == expected, "Existing GFJD entries differ")
    require(
        all(item["repo_id"] != "edithatogo/gfjd-source-archive" for item in catalog["datasets"]),
        "Archive already registered",
    )
    catalog["datasets"].append(
        {
            "repo_id": "edithatogo/gfjd-source-archive",
            "family": "gfjd",
            "role": "source_archive",
            "canonical_repo_id": "edithatogo/gfjd-source-catalogue",
            "origin_repository": "https://github.com/edithatogo/global-family-justice-data",
            "upstream_source": "Six exact-edition source objects in GFJD inventory",
            "status": "public_source_objects_observed_policy_reconciliation_pending",
            "access": "public",
            "rights_status": "exact_edition_review_required_no_blanket_clearance",
            "viewer_status": "not_verified",
        }
    )
    catalog["generated_at"] = datetime.now(UTC).isoformat()
    Draft202012Validator(json.loads(schema_raw), format_checker=FormatChecker()).validate(catalog)
    other_before = [x for x in before["datasets"] if x["repo_id"] not in expected]
    other_after = [
        x
        for x in catalog["datasets"]
        if x["repo_id"] not in expected | {"edithatogo/gfjd-source-archive"}
    ]
    require(other_before == other_after, "Unrelated registry entry changed")
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output / "catalog.json").write_text(json.dumps(catalog, indent=2) + "\n")
    (args.output / "catalog.schema.json").write_bytes(schema_raw)
    (args.output / "catalog.before.json").write_bytes(raw)
    print(
        json.dumps(
            {
                "schema_valid": True,
                "unrelated_entries_preserved": len(other_before),
                "updated": 4,
                "added": 1,
                "output": str(args.output),
            }
        )
    )


if __name__ == "__main__":
    main()
