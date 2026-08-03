"""Deterministic, portable public-product bundle builder.

This is a publication *candidate* builder: it creates inspectable artefacts and
provenance, but deliberately does not imply rights clearance or publication
approval.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .io import sha256_file, write_json
from .project import Project, load_project
from .warehouse import build_warehouse, verify_warehouse


class ProductError(RuntimeError):
    """Raised when a product bundle cannot be built or verified."""


@dataclass(frozen=True, slots=True)
class ProductBundleResult:
    output: Path
    artifacts: tuple[str, ...]
    manifest: Path


def build_products(
    project_or_root: Project | Path | str | None = None, output: Path = Path("build/products")
) -> ProductBundleResult:
    project = (
        project_or_root if isinstance(project_or_root, Project) else load_project(project_or_root)
    )
    destination = output if output.is_absolute() else project.root / output
    destination.mkdir(parents=True, exist_ok=True)
    warehouse = build_warehouse(project, destination / "gfjd.sqlite", source_date_epoch=0)
    rows: list[dict[str, Any]] = []
    for path in sorted((project.root / "data").rglob("*.csv")):
        relative = path.relative_to(project.root).as_posix()
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.reader(handle)
            header = next(reader, [])
            count = sum(1 for _ in reader)
        rows.append(
            {"path": relative, "rows": count, "columns": header, "sha256": sha256_file(path)}
        )
    (destination / "catalogue.json").write_text(
        json.dumps(
            {"schema_version": "1.0", "status": "candidate", "artifacts": rows},
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    html = (
        "<!doctype html><html lang='en'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width, initial-scale=1'>"
        "<title>GFJD product catalogue</title></head><body>"
        "<a href='#main'>Skip to main content</a>"
        "<main id='main'>"
        "<h1>Global Family Justice Data</h1>"
        "<p>This is a reproducible candidate bundle. Publication, rights and "
        "accessibility approval remain separate gates.</p>"
        "<p>Every resource is linked to its source path and SHA-256 digest in "
        "<a href='catalogue.json'>catalogue.json</a>.</p>"
        "<h2>Limitations and responsible use</h2>"
        "<p>This candidate does not establish complete coverage, comparable "
        "outcomes or rankings. Do not use it to identify people or infer family "
        "outcomes.</p>"
        "<nav aria-label='Support and corrections'><a href='README.md'>"
        "Definitions and limitations</a> "
        "<a href='corrections.md'>Corrections and takedown</a></nav>"
        "</main></body></html>\n"
    )
    (destination / "index.html").write_text(html, encoding="utf-8")
    (destination / "README.md").write_text(
        "# Candidate product bundle\n\n"
        "This bundle is a reproducible candidate, not an authorised publication. "
        "Coverage, rights, accessibility and responsible-use review remain pending.\n",
        encoding="utf-8",
    )
    (destination / "corrections.md").write_text(
        "# Corrections and takedown\n\n"
        "Report a suspected error or rights concern to the accountable project owner. "
        "Do not include personal or confidential information.\n",
        encoding="utf-8",
    )
    inventory = [
        {"path": "gfjd.sqlite", "sha256": warehouse.sha256},
        {"path": "gfjd.sqlite.metadata.json", "sha256": sha256_file(warehouse.metadata_path)},
        {"path": "catalogue.json", "sha256": sha256_file(destination / "catalogue.json")},
        {"path": "index.html", "sha256": sha256_file(destination / "index.html")},
        {"path": "README.md", "sha256": sha256_file(destination / "README.md")},
        {"path": "corrections.md", "sha256": sha256_file(destination / "corrections.md")},
    ]
    manifest = destination / "manifest.json"
    write_json(
        manifest,
        {
            "schema_version": "1.0",
            "status": "candidate",
            "publication_authorized": False,
            "artifacts": inventory,
        },
    )
    errors = verify_products(project, destination)
    if errors:
        raise ProductError("Product bundle failed verification: " + "; ".join(errors))
    return ProductBundleResult(destination, tuple(item["path"] for item in inventory), manifest)


def verify_products(project_or_root: Project | Path | str | None, output: Path) -> list[str]:
    project = (
        project_or_root if isinstance(project_or_root, Project) else load_project(project_or_root)
    )
    destination = output if output.is_absolute() else project.root / output
    manifest = destination / "manifest.json"
    if not manifest.is_file():
        return [f"Missing product manifest: {manifest}"]
    try:
        payload = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"Invalid product manifest: {exc}"]
    errors: list[str] = []
    if payload.get("publication_authorized") is not False:
        errors.append("Product manifest must remain publication_authorized=false until approval")
    index = destination / "index.html"
    if index.is_file():
        html = index.read_text(encoding="utf-8")
        required_markers = {
            "lang='en'": "document language",
            "<meta name='viewport'": "responsive viewport",
            "Skip to main content": "skip link",
            "<main id='main'>": "main landmark",
            "Limitations and responsible use": "responsible-use guidance",
            "catalogue.json": "catalogue link",
            "corrections.md": "correction/takedown link",
        }
        for marker, label in required_markers.items():
            if marker not in html:
                errors.append(f"Candidate HTML is missing {label}: {marker}")
    else:
        errors.append("Missing candidate HTML: index.html")
    for item in payload.get("artifacts", []):
        path = destination / str(item.get("path", ""))
        if not path.is_file():
            errors.append(f"Missing product artifact: {path.name}")
        elif sha256_file(path) != item.get("sha256"):
            errors.append(f"Product artifact digest mismatch: {path.name}")
    errors.extend(
        verify_warehouse(
            destination / "gfjd.sqlite", metadata_path=destination / "gfjd.sqlite.metadata.json"
        )
    )
    return errors
