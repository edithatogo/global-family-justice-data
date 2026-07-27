"""CSV-to-JSON-Schema contract validation with deterministic coercion."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator, FormatChecker

from .io import read_csv, read_json
from .project import Project, load_toml
from .reporting import Report


@dataclass(frozen=True)
class DataContract:
    id: str
    schema_path: Path
    layer: str
    required: bool
    allow_empty: bool
    path: Path | None = None
    glob: str | None = None
    exclude_names: tuple[str, ...] = ()


@dataclass
class ValidatedTable:
    contract: DataContract
    path: Path
    headers: list[str]
    raw_rows: list[dict[str, str]]
    typed_rows: list[dict[str, Any]]


def load_contracts(project: Project) -> list[DataContract]:
    config_path = project.root / "config" / "data_contracts.toml"
    config = load_toml(config_path)
    contracts: list[DataContract] = []
    for raw in config.get("contracts", []):
        contracts.append(
            DataContract(
                id=str(raw["id"]),
                schema_path=project.resolve(str(raw["schema"])),
                layer=str(raw.get("layer", "unknown")),
                required=bool(raw.get("required", False)),
                allow_empty=bool(raw.get("allow_empty", False)),
                path=project.resolve(str(raw["path"])) if raw.get("path") else None,
                glob=str(raw["glob"]) if raw.get("glob") else None,
                exclude_names=tuple(str(value) for value in raw.get("exclude_names", [])),
            )
        )
    return contracts


def _schema_types(fragment: dict[str, Any]) -> set[str]:
    schema_type = fragment.get("type")
    if isinstance(schema_type, list):
        return {str(value) for value in schema_type}
    if isinstance(schema_type, str):
        return {schema_type}
    if "enum" in fragment:
        enum_values = fragment["enum"]
        return {type(value).__name__ for value in enum_values}
    if "const" in fragment:
        return {type(fragment["const"]).__name__}
    return set()


def coerce_csv_value(raw: str | None, fragment: dict[str, Any]) -> Any:
    """Coerce a CSV string into the primitive type expected by a schema property."""

    value = "" if raw is None else raw
    allowed = _schema_types(fragment)

    if value == "" and "null" in allowed:
        return None

    if "boolean" in allowed or "bool" in allowed:
        normalised = value.strip().lower()
        if normalised in {"true", "yes", "1", "y"}:
            return True
        if normalised in {"false", "no", "0", "n"}:
            return False
        return value

    if "integer" in allowed or "int" in allowed:
        try:
            return int(value.strip())
        except (TypeError, ValueError):
            return value

    if "number" in allowed or "float" in allowed:
        try:
            return float(value.strip())
        except (TypeError, ValueError):
            return value

    return value


def coerce_row(row: dict[str, str], schema: dict[str, Any]) -> dict[str, Any]:
    properties = schema.get("properties", {})
    return {key: coerce_csv_value(value, properties.get(key, {})) for key, value in row.items()}


def _expand_contract(project: Project, contract: DataContract) -> list[Path]:
    if contract.path is not None:
        return [contract.path] if contract.path.exists() else []
    if contract.glob is None:
        return []
    paths = []
    for path in project.root.glob(contract.glob):
        if not path.is_file() or path.name in contract.exclude_names:
            continue
        paths.append(path)
    return sorted(paths)


def validate_contracts(project: Project, report: Report) -> list[ValidatedTable]:
    """Validate every configured table and return typed rows for semantic checks."""

    tables: list[ValidatedTable] = []
    seen_contract_ids: set[str] = set()
    for contract in load_contracts(project):
        if contract.id in seen_contract_ids:
            report.error(
                "CONTRACT_DUPLICATE_ID",
                f"Duplicate data contract id {contract.id!r}",
                path="config/data_contracts.toml",
            )
            continue
        seen_contract_ids.add(contract.id)

        if not contract.schema_path.exists():
            report.error(
                "CONTRACT_SCHEMA_MISSING",
                f"Schema does not exist: {contract.schema_path}",
                path=contract.schema_path,
            )
            continue
        schema = read_json(contract.schema_path)
        try:
            Draft202012Validator.check_schema(schema)
        except Exception as exc:  # jsonschema exposes several schema exceptions
            report.error(
                "CONTRACT_SCHEMA_INVALID",
                f"Invalid JSON Schema: {exc}",
                path=contract.schema_path,
            )
            continue

        paths = _expand_contract(project, contract)
        if contract.required and not paths:
            expected = contract.path or contract.glob
            report.error(
                "CONTRACT_DATA_MISSING",
                f"Required contract {contract.id!r} matched no file ({expected})",
                path=str(expected),
            )
            continue
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        properties = schema.get("properties", {})
        required_fields = set(schema.get("required", []))
        additional_allowed = schema.get("additionalProperties", True) is not False

        for path in paths:
            relative_path = _relative(project, path)
            try:
                headers, raw_rows = read_csv(path)
            except (OSError, UnicodeError) as exc:
                report.error(
                    "CONTRACT_READ_FAILED",
                    f"Could not read CSV: {exc}",
                    path=relative_path,
                )
                continue

            header_set = set(headers)
            missing_headers = sorted(required_fields - header_set)
            if missing_headers:
                report.error(
                    "CONTRACT_MISSING_HEADERS",
                    f"Missing required header(s): {', '.join(missing_headers)}",
                    path=relative_path,
                )
            if not additional_allowed:
                unknown_headers = sorted(header_set - set(properties))
                if unknown_headers:
                    report.error(
                        "CONTRACT_UNKNOWN_HEADERS",
                        f"Unknown header(s): {', '.join(unknown_headers)}",
                        path=relative_path,
                    )
            duplicate_headers = sorted(_duplicates(headers))
            if duplicate_headers:
                report.error(
                    "CONTRACT_DUPLICATE_HEADERS",
                    f"Duplicate header(s): {', '.join(duplicate_headers)}",
                    path=relative_path,
                )
            if not raw_rows and not contract.allow_empty:
                report.error(
                    "CONTRACT_EMPTY_TABLE",
                    f"Contract {contract.id!r} does not allow an empty table",
                    path=relative_path,
                )

            typed_rows: list[dict[str, Any]] = []
            for row_number, raw_row in enumerate(raw_rows, start=2):
                typed = coerce_row(raw_row, schema)
                typed_rows.append(typed)
                errors = sorted(validator.iter_errors(typed), key=lambda error: list(error.path))
                for error in errors:
                    field = ".".join(str(part) for part in error.path)
                    message = error.message if not field else f"{field}: {error.message}"
                    report.error(
                        "CONTRACT_ROW_INVALID",
                        message,
                        path=relative_path,
                        row=row_number,
                        context={"contract_id": contract.id},
                    )

            tables.append(
                ValidatedTable(
                    contract=contract,
                    path=path,
                    headers=headers,
                    raw_rows=raw_rows,
                    typed_rows=typed_rows,
                )
            )

    report.metrics["contracts"] = len(seen_contract_ids)
    report.metrics["validated_tables"] = len(tables)
    report.metrics["validated_rows"] = sum(len(table.typed_rows) for table in tables)
    return tables


def tables_by_contract(tables: Iterable[ValidatedTable]) -> dict[str, list[ValidatedTable]]:
    result: dict[str, list[ValidatedTable]] = {}
    for table in tables:
        result.setdefault(table.contract.id, []).append(table)
    return result


def _duplicates(values: Iterable[str]) -> set[str]:
    seen: set[str] = set()
    duplicate: set[str] = set()
    for value in values:
        if value in seen:
            duplicate.add(value)
        seen.add(value)
    return duplicate


def _relative(project: Project, path: Path) -> str:
    try:
        return str(path.relative_to(project.root))
    except ValueError:
        return str(path)
