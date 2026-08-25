"""Preflight frozen G2 run identifiers before source artifacts are consumed."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


class G2RunPreflightError(ValueError):
    """Raised when a proposed run cannot produce schema-valid receipts."""


def validate_g2_run_identifiers(root: Path, *, packet_id: str, comparison_id: str) -> None:
    """Validate frozen identifiers without reading extraction or source artifacts."""

    schema_path = root.expanduser().resolve() / "schemas/g2_concordance.schema.json"
    try:
        schema: dict[str, Any] = json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise G2RunPreflightError(f"cannot read concordance schema: {exc}") from exc

    for property_name, value in (
        ("packet_id", packet_id),
        ("comparison_id", comparison_id),
    ):
        property_schema = schema.get("properties", {}).get(property_name)
        if not isinstance(property_schema, dict):
            raise G2RunPreflightError(f"concordance schema does not define {property_name}")
        errors = sorted(
            Draft202012Validator(property_schema).iter_errors(value),
            key=lambda item: list(item.path),
        )
        if errors:
            raise G2RunPreflightError(
                f"invalid {property_name}: " + "; ".join(error.message for error in errors)
            )
