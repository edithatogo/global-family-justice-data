"""Deterministic, quarantine-only build for a bound G2 extraction output.

This deliberately has no gold-promotion path.  It converts a sealed
known-source extraction output into source-native bronze, normalised silver,
and quarantine records so a clean build can be reproduced without treating
the rows as accepted data.
"""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .io import read_json, sha256_file, write_json


class G2QuarantinePipelineError(RuntimeError):
    """Raised when a bound input cannot safely enter the quarantine pipeline."""


@dataclass(frozen=True, slots=True)
class G2QuarantineBuild:
    """Paths and digest of one deterministic quarantine-only build."""

    output_dir: Path
    receipt_path: Path
    rows: int


_BRONZE_FIELDS = (
    "source_record_key",
    "candidate_id",
    "source_id",
    "source_edition_id",
    "source_sha256",
    "source_format",
    "source_locator",
    "value",
    "period_label_source",
)
_SILVER_FIELDS = (
    "source_record_key",
    "candidate_id",
    "source_id",
    "source_edition_id",
    "source_sha256",
    "domain_code",
    "matter_type_code",
    "indicator_code",
    "statistic_type",
    "unit_code",
    "value",
    "period_label_source",
    "period_start",
    "period_end",
    "time_basis",
    "counted_entity_code",
    "population_scope_code",
)


def build_g2_quarantine_pipeline(
    *,
    packet_path: Path,
    extraction_path: Path,
    output_dir: Path,
) -> G2QuarantineBuild:
    """Build deterministic bronze, silver and quarantine records from sealed rows.

    The packet must bind the extraction schema and all packet source keys.  Every
    input row must remain explicitly quarantined; a non-quarantine row fails.
    """

    packet = _read_object(packet_path, "packet")
    rows = _read_rows(extraction_path)
    _validate_packet_rows(packet, rows)
    destination = output_dir.resolve()
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True)

    ordered = sorted(rows, key=lambda row: str(row["source_record_key"]))
    bronze = [{field: row[field] for field in _BRONZE_FIELDS} for row in ordered]
    silver = [{field: row[field] for field in _SILVER_FIELDS} for row in ordered]
    quarantine = [
        {
            "source_record_key": row["source_record_key"],
            "candidate_id": row["candidate_id"],
            "status": "quarantine",
            "reason_codes": ["G2_KNOWN_SOURCE_RECALIBRATION", "METHODS_ADJUDICATION_PENDING"],
        }
        for row in ordered
    ]
    bronze_path = destination / "bronze.json"
    silver_path = destination / "silver.json"
    quarantine_path = destination / "quarantine.json"
    gold_path = destination / "gold.json"
    write_json(bronze_path, bronze)
    write_json(silver_path, silver)
    write_json(quarantine_path, quarantine)
    write_json(gold_path, [])
    receipt_path = destination / "receipt.json"
    write_json(
        receipt_path,
        {
            "schema_version": "1.0",
            "pipeline": "g2_quarantine_only",
            "packet": {"path": str(packet_path), "sha256": sha256_file(packet_path)},
            "extraction": {"path": str(extraction_path), "sha256": sha256_file(extraction_path)},
            "rows": len(ordered),
            "outputs": {
                name: {"path": str(path), "sha256": sha256_file(path)}
                for name, path in (
                    ("bronze", bronze_path),
                    ("silver", silver_path),
                    ("quarantine", quarantine_path),
                    ("gold", gold_path),
                )
            },
            "promotion": {"gold_rows": 0, "quarantined_rows": len(ordered)},
            "boundary": (
                "Known-source pilot rows remain quarantined; this receipt is not methods "
                "adjudication, rights clearance, publication, release, or G2 acceptance."
            ),
        },
    )
    return G2QuarantineBuild(destination, receipt_path, len(ordered))


def verify_g2_quarantine_pipeline(receipt_path: Path) -> list[str]:
    """Verify output presence, digests and the no-promotion invariant."""

    receipt = _read_object(receipt_path, "receipt")
    errors: list[str] = []
    promotion = receipt.get("promotion")
    if not isinstance(promotion, dict) or promotion.get("gold_rows") != 0:
        errors.append("Quarantine pipeline must not promote gold rows")
    outputs = receipt.get("outputs")
    if not isinstance(outputs, dict):
        return [*errors, "Receipt outputs are malformed"]
    for name in ("bronze", "silver", "quarantine", "gold"):
        item = outputs.get(name)
        if not isinstance(item, dict):
            errors.append(f"Receipt output {name} is missing")
            continue
        path = Path(str(item.get("path") or ""))
        if not path.is_file():
            errors.append(f"Receipt output {name} is missing on disk")
        elif sha256_file(path) != item.get("sha256"):
            errors.append(f"Receipt output {name} digest mismatch")
    return errors


def _read_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = read_json(path)
    except (OSError, json.JSONDecodeError) as exc:
        raise G2QuarantinePipelineError(f"Could not read {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise G2QuarantinePipelineError(f"{label.capitalize()} must be a JSON object")
    return value


def _read_rows(path: Path) -> list[dict[str, Any]]:
    try:
        value = read_json(path)
    except (OSError, json.JSONDecodeError) as exc:
        raise G2QuarantinePipelineError(f"Could not read extraction output: {exc}") from exc
    if not isinstance(value, list) or not value or not all(isinstance(row, dict) for row in value):
        raise G2QuarantinePipelineError("Extraction output must be a non-empty array of objects")
    return value


def _validate_packet_rows(packet: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    sources = packet.get("sources")
    if not isinstance(sources, list):
        raise G2QuarantinePipelineError("Packet sources are malformed")
    expected = {item.get("source_record_key") for item in sources if isinstance(item, dict)}
    observed: set[str] = set()
    for row in rows:
        key = row.get("source_record_key")
        if not isinstance(key, str) or key in observed:
            raise G2QuarantinePipelineError("Extraction rows need unique source_record_key values")
        observed.add(key)
        if row.get("quarantine_status") != "quarantine":
            raise G2QuarantinePipelineError("Every G2 recalibration row must remain quarantined")
        for field in (*_BRONZE_FIELDS, *_SILVER_FIELDS):
            if field not in row:
                raise G2QuarantinePipelineError(f"Extraction row lacks required field {field}")
    if observed != expected:
        raise G2QuarantinePipelineError("Extraction output scope differs from packet sources")
