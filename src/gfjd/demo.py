"""Reproducible heterogeneous synthetic pilot.

The demo exercises five connector paths, declarative observation mappings,
batch combination, and silver-to-gold promotion. All inputs are explicitly
fictional and generated outputs live under ``build/``.
"""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .connectors import ConnectorResult, run_connector, verify_connector_receipt
from .io import read_csv, sha256_file, write_csv, write_json
from .pipeline import map_structured_csv, promote_observations
from .project import Project, load_project


class DemoError(RuntimeError):
    """Raised when the synthetic demo cannot complete reproducibly."""


@dataclass(frozen=True, slots=True)
class DemoResult:
    output_dir: Path
    summary_path: Path
    silver_path: Path
    gold_path: Path
    quarantine_path: Path
    connector_results: tuple[ConnectorResult, ...]
    mapped_rows: int
    gold_rows: int
    quarantined_rows: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "output_dir": str(self.output_dir),
            "summary_path": str(self.summary_path),
            "silver_path": str(self.silver_path),
            "gold_path": str(self.gold_path),
            "quarantine_path": str(self.quarantine_path),
            "connector_results": [result.to_dict() for result in self.connector_results],
            "mapped_rows": self.mapped_rows,
            "gold_rows": self.gold_rows,
            "quarantined_rows": self.quarantined_rows,
        }


def run_demo(
    project: Project | Path | str,
    output_dir: Path = Path("build/demo"),
    *,
    clean: bool = True,
) -> DemoResult:
    """Run the full synthetic demonstration and verify every connector receipt."""

    resolved = _project(project)
    destination = _resolve(resolved, output_dir)
    try:
        destination.relative_to(resolved.root / "build")
    except ValueError as exc:
        raise DemoError("Synthetic demo output must remain under build/") from exc
    if clean:
        shutil.rmtree(destination, ignore_errors=True)
    destination.mkdir(parents=True, exist_ok=True)

    keys = ("csv", "json", "html", "xlsx", "manual")
    connectors: list[ConnectorResult] = []
    mapping_results: list[dict[str, Any]] = []
    silver_parts: list[Path] = []
    fixed_time = datetime.fromisoformat(
        str(resolved.project_config.get("status_as_of", "2026-07-19")) + "T00:00:00+00:00"
    ).astimezone(UTC)
    for key in keys:
        connector_path = Path(f"examples/synthetic_pilot/connectors/{key}.toml")
        connector = run_connector(resolved, connector_path, executed_at=fixed_time)
        errors = verify_connector_receipt(resolved, connector.receipt_path)
        if errors:
            raise DemoError(f"Connector receipt verification failed for {key}: {'; '.join(errors)}")
        connectors.append(connector)
        silver_part = destination / "silver" / f"{key}.csv"
        rejected_part = destination / "quarantine" / f"{key}.mapping.json"
        result = map_structured_csv(
            resolved,
            Path(f"examples/synthetic_pilot/mappings/{key}.json"),
            connector.output_path,
            silver_part,
            rejected_part,
        )
        mapping_results.append(result)
        silver_parts.append(silver_part)

    combined_silver = destination / "silver" / "observations.csv"
    headers: list[str] | None = None
    rows: list[dict[str, str]] = []
    for path in silver_parts:
        current_headers, current_rows = read_csv(path)
        if headers is None:
            headers = current_headers
        elif current_headers != headers:
            raise DemoError(f"Mapped silver headers differ in {path}")
        rows.extend(current_rows)
    if headers is None:
        raise DemoError("Synthetic demo produced no mapped tables")
    rows.sort(key=lambda row: row.get("observation_id", ""))
    write_csv(combined_silver, headers, rows)

    gold = destination / "gold" / "observations.csv"
    quarantine = destination / "quarantine" / "promotion.csv"
    promotion_report = destination / "receipts" / "promotion.json"
    promotion = promote_observations(
        resolved,
        combined_silver,
        gold,
        quarantine,
        promotion_report,
    )
    _, gold_rows = read_csv(gold)
    _, quarantine_rows = read_csv(quarantine)
    summary_path = destination / "demo-summary.json"
    summary = {
        "schema_version": "1.0",
        "synthetic": True,
        "warning": "Fictional demonstration data; not an empirical family-justice dataset.",
        "connectors": [result.to_dict() for result in connectors],
        "mappings": mapping_results,
        "combined_silver": {
            "path": str(combined_silver),
            "sha256": sha256_file(combined_silver),
            "rows": len(rows),
        },
        "promotion": promotion,
        "gold_rows": len(gold_rows),
        "quarantined_rows": len(quarantine_rows),
    }
    write_json(summary_path, summary)
    return DemoResult(
        output_dir=destination,
        summary_path=summary_path,
        silver_path=combined_silver,
        gold_path=gold,
        quarantine_path=quarantine,
        connector_results=tuple(connectors),
        mapped_rows=len(rows),
        gold_rows=len(gold_rows),
        quarantined_rows=len(quarantine_rows),
    )


def verify_demo(project: Project | Path | str, output_dir: Path = Path("build/demo")) -> list[str]:
    """Verify a previously built demo without rerunning it."""

    resolved = _project(project)
    destination = _resolve(resolved, output_dir)
    summary_path = destination / "demo-summary.json"
    try:
        payload = json.loads(summary_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"Could not read demo summary: {exc}"]
    errors: list[str] = []
    if payload.get("synthetic") is not True:
        errors.append("Demo summary is not marked synthetic")
    for item in payload.get("connectors", []):
        if not isinstance(item, dict):
            errors.append("Malformed connector entry in demo summary")
            continue
        receipt_path = Path(str(item.get("receipt_path") or ""))
        errors.extend(verify_connector_receipt(resolved, receipt_path))
    silver = payload.get("combined_silver", {})
    if isinstance(silver, dict):
        path = Path(str(silver.get("path") or ""))
        resolved_path = path if path.is_absolute() else resolved.root / path
        if not resolved_path.is_file():
            errors.append("Combined demo silver output is missing")
        elif sha256_file(resolved_path) != silver.get("sha256"):
            errors.append("Combined demo silver checksum mismatch")
    else:
        errors.append("Malformed combined_silver entry in demo summary")
    return errors


def _project(value: Project | Path | str) -> Project:
    return value if isinstance(value, Project) else load_project(Path(value))


def _resolve(project: Project, path: Path) -> Path:
    candidate = path.expanduser()
    return candidate.resolve() if candidate.is_absolute() else (project.root / candidate).resolve()
