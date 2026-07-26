"""Lightweight validation for the starter CSV registers."""
from __future__ import annotations

from pathlib import Path
import csv
import sys
from urllib.parse import urlparse
from datetime import date

ROOT = Path(__file__).resolve().parents[2]

SPECS = {
    "data/seed/jurisdiction_register.csv": {
        "required": ["jurisdiction_id", "name", "level", "coverage_status"],
        "unique": "jurisdiction_id",
    },
    "data/seed/source_register.csv": {
        "required": ["source_id", "jurisdiction_id", "title", "publisher", "source_url", "last_verified"],
        "unique": "source_id",
    },
    "data/seed/indicator_dictionary.csv": {
        "required": ["indicator_id", "domain", "name", "definition", "core_release"],
        "unique": "indicator_id",
    },
}


def read_rows(path: Path):
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        return reader.fieldnames or [], rows


def validate() -> list[str]:
    errors: list[str] = []
    jurisdiction_ids: set[str] = set()

    for relative, spec in SPECS.items():
        path = ROOT / relative
        if not path.exists():
            errors.append(f"Missing file: {relative}")
            continue
        headers, rows = read_rows(path)
        missing_headers = [h for h in spec["required"] if h not in headers]
        if missing_headers:
            errors.append(f"{relative}: missing headers {missing_headers}")
            continue
        ids: set[str] = set()
        for index, row in enumerate(rows, start=2):
            for field in spec["required"]:
                if not (row.get(field) or "").strip():
                    errors.append(f"{relative}:{index}: required field {field!r} is blank")
            value = (row.get(spec["unique"]) or "").strip()
            if value in ids:
                errors.append(f"{relative}:{index}: duplicate {spec['unique']} {value!r}")
            ids.add(value)
        if relative.endswith("jurisdiction_register.csv"):
            jurisdiction_ids = ids

    source_path = ROOT / "data/seed/source_register.csv"
    if source_path.exists():
        _, rows = read_rows(source_path)
        for index, row in enumerate(rows, start=2):
            jurisdiction_id = (row.get("jurisdiction_id") or "").strip()
            if jurisdiction_ids and jurisdiction_id not in jurisdiction_ids:
                errors.append(f"source_register.csv:{index}: unknown jurisdiction_id {jurisdiction_id!r}")
            url = (row.get("source_url") or "").strip()
            parsed = urlparse(url)
            if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                errors.append(f"source_register.csv:{index}: invalid source_url {url!r}")
            verified = (row.get("last_verified") or "").strip()
            try:
                date.fromisoformat(verified)
            except ValueError:
                errors.append(f"source_register.csv:{index}: invalid ISO date {verified!r}")

    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("Validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Validation passed for jurisdiction, source and indicator seed registers.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
