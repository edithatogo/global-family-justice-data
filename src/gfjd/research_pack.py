"""Build non-evidentiary jurisdiction research handoff packs."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from .io import read_csv, sha256_file, write_csv, write_json
from .project import Project


class ResearchPackError(RuntimeError):
    pass


def build_research_pack(project: Project, jurisdiction_id: str, output_root: Path) -> Path:
    root = output_root if output_root.is_absolute() else project.root / output_root
    root = root.resolve()
    if project.root / "build" not in root.parents:
        raise ResearchPackError("Research packs must be written under build/")
    _, jurisdictions = read_csv(project.root / "data/seed/jurisdiction_register.csv")
    jurisdiction = next(
        (row for row in jurisdictions if row.get("jurisdiction_id") == jurisdiction_id), None
    )
    if jurisdiction is None:
        raise ResearchPackError(f"Unknown jurisdiction: {jurisdiction_id}")
    _, institutions = read_csv(project.root / "data/seed/institution_register.csv")
    _, sources = read_csv(project.root / "data/seed/source_register.csv")
    languages = [
        part.strip() for part in jurisdiction.get("search_languages", "").split(",") if part.strip()
    ]
    domains = (
        "judiciary/court administration",
        "justice ministry",
        "statistics/open data",
        "annual reports",
    )
    pack = {
        "schema_version": "1.0",
        "jurisdiction_id": jurisdiction_id,
        "generated_on": str(project.project_config["status_as_of"]),
        "status": "non_evidentiary_handoff",
        "institutions": [
            {
                key: row.get(key, "")
                for key in ("institution_id", "name", "institution_type", "court_level")
            }
            for row in institutions
            if row.get("jurisdiction_id") == jurisdiction_id
        ],
        "sources": [
            {
                "source_id": row.get("source_id", ""),
                "title": row.get("title", ""),
                "source_type": row.get("source_type", ""),
            }
            for row in sources
            if row.get("jurisdiction_id") in {jurisdiction_id, ""}
        ],
        "search_plan": [
            {
                "domain": domain,
                "language": language,
                "query_guidance": (
                    f"Search official {domain} sources using registered terminology; "
                    "record results separately."
                ),
            }
            for language in languages
            for domain in domains
        ],
        "limitations": [
            "This pack is not evidence.",
            "No source finding, coverage state, or enquiry outcome is inferred.",
        ],
    }
    schema = json.loads(
        (project.root / "schemas/research_pack.schema.json").read_text(encoding="utf-8")
    )
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(pack),
        key=lambda error: list(error.path),
    )
    if errors:
        raise ResearchPackError(
            "Research pack failed schema: " + "; ".join(error.message for error in errors)
        )
    destination = root / jurisdiction_id
    destination.mkdir(parents=True, exist_ok=True)
    write_json(destination / "research-pack.json", pack)
    write_csv(
        destination / "search-plan.csv",
        ["domain", "language", "query_guidance"],
        pack["search_plan"],
    )
    write_json(
        destination / "MANIFEST.json",
        {
            name: sha256_file(destination / name)
            for name in ("research-pack.json", "search-plan.csv")
        },
    )
    return destination
