"""Portable SQLite warehouse for GFJD release and analytical use.

The CSV contracts remain the auditable source of truth.  This module compiles
those contracts into a read-only-friendly SQLite database with contextual views,
input fingerprints and deterministic table ordering.  It also provides a guarded
query/export path that denies mutating SQLite operations.
"""

from __future__ import annotations

import csv
import json
import os
import sqlite3
import tempfile
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from . import __version__
from .io import canonical_json_bytes, read_json, sha256_bytes, sha256_file, write_json
from .project import Project, load_project
from .reporting import Report
from .schema_validation import ValidatedTable, load_contracts, validate_contracts


class WarehouseError(RuntimeError):
    """Raised when a warehouse cannot be built, verified or queried safely."""


TABLE_NAMES = {
    "jurisdictions": "jurisdictions",
    "sources": "sources",
    "indicators": "indicators",
    "matter_types": "matter_types",
    "institutions": "institutions",
    "source_editions": "source_editions",
    "outcomes_evidence": "outcomes_evidence",
    "extractions": "extractions",
    "reviews": "reviews",
    "jurisdiction_universe": "jurisdiction_universe",
    "search_logs": "search_logs",
    "coverage_assessments": "coverage_assessments",
    "silver_observations": "observations_silver",
    "gold_observations": "observations_gold",
}


@dataclass(frozen=True, slots=True)
class WarehouseBuildResult:
    database_path: Path
    metadata_path: Path
    sha256: str
    input_fingerprint: str
    tables: dict[str, int]
    views: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "database_path": str(self.database_path),
            "metadata_path": str(self.metadata_path),
            "sha256": self.sha256,
            "input_fingerprint": self.input_fingerprint,
            "tables": self.tables,
            "views": list(self.views),
        }


@dataclass(frozen=True, slots=True)
class QueryResult:
    columns: tuple[str, ...]
    rows: tuple[tuple[Any, ...], ...]
    truncated: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "columns": list(self.columns),
            "rows": [list(row) for row in self.rows],
            "truncated": self.truncated,
        }


def build_warehouse(
    project_or_root: Project | Path | str | None = None,
    output_path: Path = Path("build/warehouse/gfjd.sqlite"),
    *,
    generated_at: datetime | None = None,
    source_date_epoch: int | None = None,
) -> WarehouseBuildResult:
    project = _project(project_or_root)
    destination = _resolve(project, output_path)
    if source_date_epoch is not None:
        if generated_at is not None:
            raise WarehouseError("Use either generated_at or source_date_epoch, not both")
        generated_at = datetime.fromtimestamp(source_date_epoch, tz=UTC)
    timestamp = _timestamp(generated_at, project)
    report = Report("warehouse contracts")
    tables = validate_contracts(project, report)
    if report.error_count:
        raise WarehouseError(
            "Cannot build warehouse from invalid contracts:\n"
            + "\n".join(issue.render() for issue in report.errors[:30])
        )

    contracts = {contract.id: contract for contract in load_contracts(project)}
    grouped: dict[str, list[ValidatedTable]] = {}
    for table in tables:
        grouped.setdefault(table.contract.id, []).append(table)
    input_entries = _input_entries(project, tables)
    input_fingerprint = _input_fingerprint(input_entries)

    destination.parent.mkdir(parents=True, exist_ok=True)
    metadata_path = destination.with_suffix(destination.suffix + ".metadata.json")
    with tempfile.TemporaryDirectory(prefix=".gfjd-warehouse-", dir=destination.parent) as temp:
        temporary = Path(temp) / destination.name
        connection = sqlite3.connect(temporary)
        try:
            _configure_build(connection)
            _create_metadata_table(connection)
            row_counts: dict[str, int] = {}
            for contract_id, table_name in TABLE_NAMES.items():
                contract = contracts.get(contract_id)
                if contract is None:
                    raise WarehouseError(f"Warehouse contract is not configured: {contract_id}")
                schema = read_json(contract.schema_path)
                contract_tables = grouped.get(contract_id, [])
                row_counts[table_name] = _load_contract_table(
                    connection,
                    project,
                    table_name,
                    schema,
                    contract_tables,
                )
            views = _create_views(connection)
            _create_indexes(connection)
            metadata = {
                "schema_version": "1.0",
                "project_version": str(project.project_config.get("version", "unknown")),
                "contract_version": str(project.project_config.get("contract_version", "unknown")),
                "ontology_version": str(project.project_config.get("ontology_version", "unknown")),
                "tool_version": __version__,
                "generated_at": timestamp.isoformat().replace("+00:00", "Z"),
                "input_fingerprint": input_fingerprint,
                "table_counts": row_counts,
                "views": list(views),
            }
            for key, value in metadata.items():
                connection.execute(
                    "INSERT INTO _gfjd_metadata(key, value) VALUES (?, ?)",
                    (key, json.dumps(value, ensure_ascii=False, sort_keys=True)),
                )
            connection.commit()
            connection.execute("PRAGMA user_version = 1")
            connection.execute("VACUUM")
        finally:
            connection.close()
        os.replace(temporary, destination)

    database_hash = sha256_file(destination)
    metadata_payload = {
        "schema_version": "1.0",
        "database": destination.name,
        "database_sha256": database_hash,
        "generated_at": timestamp.isoformat().replace("+00:00", "Z"),
        "input_fingerprint": input_fingerprint,
        "inputs": input_entries,
        "tables": row_counts,
        "views": list(views),
    }
    write_json(metadata_path, metadata_payload)
    errors = verify_warehouse(destination, metadata_path=metadata_path)
    if errors:
        destination.unlink(missing_ok=True)
        metadata_path.unlink(missing_ok=True)
        raise WarehouseError("Built warehouse failed verification: " + "; ".join(errors))
    return WarehouseBuildResult(
        database_path=destination,
        metadata_path=metadata_path,
        sha256=database_hash,
        input_fingerprint=input_fingerprint,
        tables=row_counts,
        views=views,
    )


def verify_warehouse(
    database_path: Path,
    *,
    metadata_path: Path | None = None,
) -> list[str]:
    database = database_path.expanduser().resolve()
    errors: list[str] = []
    if not database.is_file():
        return [f"Warehouse database does not exist: {database}"]
    try:
        connection = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    except sqlite3.Error as exc:
        return [f"Could not open warehouse read-only: {exc}"]
    try:
        quick_check = connection.execute("PRAGMA quick_check").fetchone()
        if not quick_check or quick_check[0] != "ok":
            errors.append(f"SQLite quick_check failed: {quick_check}")
        names = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type IN ('table','view')"
            )
        }
        required = {"_gfjd_metadata", *TABLE_NAMES.values(), "v_gold_observations_context"}
        for name in sorted(required - names):
            errors.append(f"Warehouse object is missing: {name}")
        metadata_rows = dict(connection.execute("SELECT key, value FROM _gfjd_metadata"))
        for key in ("schema_version", "input_fingerprint", "table_counts"):
            if key not in metadata_rows:
                errors.append(f"Warehouse metadata key is missing: {key}")
        if connection.execute("PRAGMA user_version").fetchone()[0] != 1:
            errors.append("Warehouse user_version is not 1")
    except sqlite3.Error as exc:
        errors.append(f"Warehouse verification query failed: {exc}")
    finally:
        connection.close()

    sidecar = metadata_path or database.with_suffix(database.suffix + ".metadata.json")
    if sidecar.exists():
        try:
            payload = read_json(sidecar)
            if payload.get("database_sha256") != sha256_file(database):
                errors.append("Warehouse sidecar checksum does not match database")
            if payload.get("database") != database.name:
                errors.append("Warehouse sidecar database name does not match")
        except (OSError, ValueError, AttributeError) as exc:
            errors.append(f"Could not validate warehouse sidecar: {exc}")
    elif metadata_path is not None:
        errors.append(f"Warehouse metadata sidecar does not exist: {sidecar}")
    return errors


def verify_warehouse_receipt(
    project_or_root: Project | Path | str | None, receipt_path: Path
) -> list[str]:
    """Verify the warehouse sidecar, database, and every recorded input digest."""

    project = _project(project_or_root)
    receipt = _resolve(project, receipt_path)
    if not receipt.is_file():
        return [f"Warehouse receipt does not exist: {receipt}"]
    try:
        payload = read_json(receipt)
    except (OSError, ValueError, AttributeError) as exc:
        return [f"Could not read warehouse receipt: {exc}"]
    database_name = payload.get("database")
    if not isinstance(database_name, str) or not database_name:
        return ["Warehouse receipt is missing database"]
    database = receipt.parent / database_name
    errors = verify_warehouse(database, metadata_path=receipt)
    inputs = payload.get("inputs")
    if not isinstance(inputs, list):
        errors.append("Warehouse receipt is missing the input manifest")
        return errors
    normalised: list[dict[str, str]] = []
    for index, item in enumerate(inputs):
        if not isinstance(item, dict):
            errors.append(f"Warehouse input entry {index} is not an object")
            continue
        path_value = item.get("path")
        expected = item.get("sha256")
        contract_id = item.get("contract_id")
        if not isinstance(path_value, str) or not path_value:
            errors.append(f"Warehouse input entry {index} has no path")
            continue
        if not isinstance(expected, str) or not expected:
            errors.append(f"Warehouse input entry {index} has no sha256")
            continue
        if not isinstance(contract_id, str) or not contract_id:
            errors.append(f"Warehouse input entry {index} has no contract_id")
            continue
        candidate = _resolve(project, Path(path_value))
        try:
            candidate.relative_to(project.root)
        except ValueError:
            errors.append(f"Warehouse input escapes repository root: {path_value}")
            continue
        if not candidate.is_file():
            errors.append(f"Warehouse input is missing: {path_value}")
        elif sha256_file(candidate) != expected:
            errors.append(f"Warehouse input checksum mismatch: {path_value}")
        normalised.append({"path": path_value, "sha256": expected, "contract_id": contract_id})
    normalised.sort(key=lambda item: (item["contract_id"], item["path"]))
    expected_fingerprint = payload.get("input_fingerprint")
    if isinstance(expected_fingerprint, str):
        actual_fingerprint = _input_fingerprint(normalised)
        if actual_fingerprint != expected_fingerprint:
            errors.append("Warehouse input manifest fingerprint mismatch")
    else:
        errors.append("Warehouse receipt is missing input_fingerprint")
    return errors


def inspect_warehouse(database_path: Path) -> dict[str, Any]:
    """Return deterministic metadata and object counts from a read-only warehouse."""

    database = database_path.expanduser().resolve()
    errors = verify_warehouse(database)
    if errors:
        raise WarehouseError("; ".join(errors))
    connection = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    try:
        metadata = {
            key: json.loads(value)
            for key, value in connection.execute(
                "SELECT key, value FROM _gfjd_metadata ORDER BY key"
            )
        }
        objects: list[dict[str, Any]] = []
        rows = connection.execute(
            "SELECT type, name FROM sqlite_master "
            "WHERE type IN ('table','view') ORDER BY type, name"
        )
        for object_type, name in rows:
            item: dict[str, Any] = {"type": object_type, "name": name}
            if object_type == "table" and name != "sqlite_sequence":
                item["rows"] = connection.execute(
                    f"SELECT COUNT(*) FROM {_quote(name)}"  # nosec B608 - identifier is validated by _quote
                ).fetchone()[0]
            objects.append(item)
    finally:
        connection.close()
    return {
        "database_path": str(database),
        "sha256": sha256_file(database),
        "metadata": metadata,
        "objects": objects,
    }


def query_warehouse(database_path: Path, sql: str, *, limit: int = 1000) -> QueryResult:
    """Execute one guarded read-only query against a warehouse."""

    if limit <= 0 or limit > 100_000:
        raise WarehouseError("Query limit must be between 1 and 100000")
    statement = sql.strip().rstrip(";").strip()
    if not statement:
        raise WarehouseError("SQL query is empty")
    if ";" in statement:
        raise WarehouseError("Only one SQL statement is allowed")
    first = statement.split(None, 1)[0].upper()
    if first not in {"SELECT", "WITH", "EXPLAIN"}:
        raise WarehouseError("Only SELECT, WITH or EXPLAIN queries are allowed")

    database = database_path.expanduser().resolve()
    connection = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    connection.set_authorizer(_read_only_authorizer)
    try:
        cursor = connection.execute(statement)
        if cursor.description is None:
            raise WarehouseError("Query produced no tabular result")
        rows = cursor.fetchmany(limit + 1)
        columns = tuple(item[0] for item in cursor.description)
        truncated = len(rows) > limit
        return QueryResult(columns=columns, rows=tuple(rows[:limit]), truncated=truncated)
    except sqlite3.Error as exc:
        raise WarehouseError(f"Warehouse query failed: {exc}") from exc
    finally:
        connection.close()


def export_query(
    database_path: Path,
    sql: str,
    output_path: Path,
    *,
    output_format: str = "csv",
    limit: int = 100_000,
) -> QueryResult:
    result = query_warehouse(database_path, sql, limit=limit)
    output = output_path.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    if output_format == "csv":
        with output.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, lineterminator="\n")
            writer.writerow(result.columns)
            writer.writerows(result.rows)
    elif output_format == "json":
        rows = [dict(zip(result.columns, row, strict=True)) for row in result.rows]
        write_json(
            output,
            {"columns": list(result.columns), "rows": rows, "truncated": result.truncated},
        )
    else:
        raise WarehouseError("output_format must be csv or json")
    return result


def _project(value: Project | Path | str | None) -> Project:
    if isinstance(value, Project):
        return value
    if value is None:
        return load_project()
    return load_project(Path(value))


def _resolve(project: Project, value: Path) -> Path:
    candidate = value.expanduser()
    return candidate.resolve() if candidate.is_absolute() else (project.root / candidate).resolve()


def _timestamp(value: datetime | None, project: Project) -> datetime:
    if value is None:
        configured = str(project.project_config.get("status_as_of", ""))
        try:
            value = datetime.fromisoformat(configured).replace(tzinfo=UTC)
        except ValueError:
            value = datetime.now(tz=UTC)
    if value.tzinfo is None:
        raise WarehouseError("generated_at must include a timezone")
    return value.astimezone(UTC).replace(microsecond=0)


def _configure_build(connection: sqlite3.Connection) -> None:
    connection.execute("PRAGMA page_size = 4096")
    connection.execute("PRAGMA journal_mode = OFF")
    connection.execute("PRAGMA synchronous = OFF")
    connection.execute("PRAGMA temp_store = MEMORY")
    connection.execute("PRAGMA foreign_keys = OFF")
    connection.execute("PRAGMA encoding = 'UTF-8'")


def _create_metadata_table(connection: sqlite3.Connection) -> None:
    connection.execute(
        "CREATE TABLE _gfjd_metadata (key TEXT PRIMARY KEY NOT NULL, value TEXT NOT NULL)"
    )


def _load_contract_table(
    connection: sqlite3.Connection,
    project: Project,
    table_name: str,
    schema: dict[str, Any],
    tables: Sequence[ValidatedTable],
) -> int:
    properties = schema.get("properties", {})
    columns = list(properties)
    definitions = [f"{_quote(column)} {_sql_type(properties[column])}" for column in columns]
    definitions.append('"_source_file" TEXT NOT NULL')
    connection.execute(  # nosec B608 - table and column identifiers are validated by _quote
        f"CREATE TABLE {_quote(table_name)} ({', '.join(definitions)})"
    )
    rows: list[tuple[Any, ...]] = []
    for table in sorted(tables, key=lambda value: value.path.as_posix()):
        source_file = _relative(project.root, table.path)
        for row in table.typed_rows:
            values = [_sqlite_value(row.get(column)) for column in columns]
            rows.append((*values, source_file))
    rows.sort(key=_row_sort_key)
    if rows:
        placeholders = ",".join("?" for _ in range(len(columns) + 1))
        connection.executemany(
            f"INSERT INTO {_quote(table_name)} VALUES ({placeholders})",  # nosec B608 - identifier is validated
            rows,
        )
    return len(rows)


def _create_views(connection: sqlite3.Connection) -> tuple[str, ...]:
    connection.executescript(
        """
        CREATE VIEW v_jurisdiction_sources AS
        SELECT
            j.jurisdiction_id,
            j.name AS jurisdiction_name,
            j.coverage_status,
            COUNT(s.source_id) AS source_count,
            SUM(CASE WHEN s.official_status = 'official' THEN 1 ELSE 0 END) AS official_source_count
        FROM jurisdictions AS j
        LEFT JOIN sources AS s ON s.jurisdiction_id = j.jurisdiction_id
        GROUP BY j.jurisdiction_id, j.name, j.coverage_status;

        CREATE VIEW v_gold_observations_context AS
        SELECT
            o.*,
            j.name AS jurisdiction_name,
            i.name AS indicator_name,
            i.domain AS indicator_domain,
            m.label AS matter_type_name,
            s.title AS source_title,
            s.publisher AS source_publisher,
            s.source_url
        FROM observations_gold AS o
        LEFT JOIN jurisdictions AS j ON j.jurisdiction_id = o.jurisdiction_id
        LEFT JOIN indicators AS i ON i.indicator_id = o.indicator_id
        LEFT JOIN matter_types AS m ON m.matter_type_id = o.matter_type_harmonised
        LEFT JOIN sources AS s ON s.source_id = o.source_id;

        CREATE VIEW v_census_readiness AS
        SELECT
            j.jurisdiction_id,
            j.name,
            j.coverage_status,
            COUNT(DISTINCT s.source_id) AS source_count,
            COUNT(DISTINCT l.search_log_id) AS search_log_count,
            COUNT(DISTINCT CASE WHEN l.review_status = 'accepted' THEN l.search_log_id END)
                AS accepted_search_log_count,
            COUNT(DISTINCT CASE WHEN c.review_status = 'accepted' THEN c.assessment_id END)
                AS accepted_assessment_count
        FROM jurisdictions AS j
        LEFT JOIN sources AS s ON s.jurisdiction_id = j.jurisdiction_id
        LEFT JOIN search_logs AS l ON l.jurisdiction_id = j.jurisdiction_id
        LEFT JOIN coverage_assessments AS c ON c.jurisdiction_id = j.jurisdiction_id
        GROUP BY j.jurisdiction_id, j.name, j.coverage_status;
        """
    )
    return ("v_jurisdiction_sources", "v_gold_observations_context", "v_census_readiness")


def _create_indexes(connection: sqlite3.Connection) -> None:
    statements = [
        "CREATE UNIQUE INDEX idx_jurisdictions_id ON jurisdictions(jurisdiction_id)",
        "CREATE UNIQUE INDEX idx_sources_id ON sources(source_id)",
        "CREATE INDEX idx_sources_jurisdiction ON sources(jurisdiction_id)",
        "CREATE UNIQUE INDEX idx_indicators_id ON indicators(indicator_id)",
        "CREATE UNIQUE INDEX idx_matter_types_id ON matter_types(matter_type_id)",
        "CREATE INDEX idx_gold_jurisdiction ON observations_gold(jurisdiction_id)",
        "CREATE INDEX idx_gold_indicator ON observations_gold(indicator_id)",
        "CREATE INDEX idx_gold_matter ON observations_gold(matter_type_harmonised)",
        "CREATE INDEX idx_gold_period ON observations_gold(period_start, period_end)",
        "CREATE INDEX idx_search_jurisdiction ON search_logs(jurisdiction_id)",
        "CREATE INDEX idx_coverage_jurisdiction ON coverage_assessments(jurisdiction_id)",
    ]
    for statement in statements:
        connection.execute(statement)


def _input_entries(project: Project, tables: Iterable[ValidatedTable]) -> list[dict[str, str]]:
    entries = [
        {
            "path": _relative(project.root, table.path),
            "sha256": sha256_file(table.path),
            "contract_id": table.contract.id,
        }
        for table in tables
    ]
    entries.sort(key=lambda item: (item["contract_id"], item["path"]))
    return entries


def _input_fingerprint(entries: Iterable[dict[str, str]]) -> str:
    return sha256_bytes(canonical_json_bytes(list(entries)))


def _sql_type(fragment: dict[str, Any]) -> str:
    value = fragment.get("type")
    types = set(value if isinstance(value, list) else [value])
    if "boolean" in types or "integer" in types:
        return "INTEGER"
    if "number" in types:
        return "REAL"
    return "TEXT"


def _sqlite_value(value: Any) -> Any:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return value


def _row_sort_key(row: tuple[Any, ...]) -> bytes:
    return canonical_json_bytes([_json_safe(value) for value in row])


def _json_safe(value: Any) -> Any:
    if isinstance(value, bytes):
        return value.hex()
    return value


def _quote(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def _relative(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def _read_only_authorizer(
    action: int,
    arg1: str | None,
    arg2: str | None,
    database: str | None,
    trigger: str | None,
) -> int:
    del arg1, arg2, database, trigger
    allowed = {
        sqlite3.SQLITE_SELECT,
        sqlite3.SQLITE_READ,
        sqlite3.SQLITE_FUNCTION,
        sqlite3.SQLITE_RECURSIVE,
    }
    return sqlite3.SQLITE_OK if action in allowed else sqlite3.SQLITE_DENY
