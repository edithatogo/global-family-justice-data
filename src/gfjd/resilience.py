"""Deterministic critical-state backup and clean-room restore rehearsal.

This module is intentionally local and storage-agnostic. It creates a portable,
hash-manifested snapshot of the public repository control plane and verifies a safe
restore into an empty directory. Production object storage, retention, encryption,
and geographic redundancy remain deployment responsibilities.
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
import time
import zipfile
from collections.abc import Iterable, Sequence
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from .io import canonical_json_bytes, read_json, sha256_bytes, sha256_file, write_json
from .project import Project, load_project


class ResilienceError(RuntimeError):
    """Raised when backup or restore integrity cannot be established."""


DEFAULT_PATTERNS = (
    ".github/**/*.yml",
    "*.md",
    "*.cff",
    "Makefile",
    "pyproject.toml",
    "config/**/*.toml",
    "programme/**/*.csv",
    "programme/**/*.json",
    "programme/**/*.jsonl",
    "data/**/*.csv",
    "data/**/*.json",
    "data/**/*.md",
    "docs/**/*.md",
    "examples/**/*",
    "fixtures/**/*",
    "schemas/**/*.json",
    "scripts/**/*.py",
    "src/**/*.py",
    "tests/**/*.py",
)

REQUIRED_FILES = (
    "config/project.toml",
    "config/data_contracts.toml",
    "data/seed/jurisdiction_register.csv",
    "data/seed/source_register.csv",
    "programme/work_items.csv",
    "programme/evidence_register.csv",
    "schemas/observation.schema.json",
    "src/gfjd/validation.py",
    "tests/test_validation.py",
)


@dataclass(frozen=True, slots=True)
class BackupResult:
    archive_path: Path
    receipt_path: Path
    archive_sha256: str
    file_count: int
    payload_sha256: str

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["archive_path"] = str(payload["archive_path"])
        payload["receipt_path"] = str(payload["receipt_path"])
        return payload


@dataclass(frozen=True, slots=True)
class RestoreResult:
    output_dir: Path
    snapshot_dir: Path
    receipt_path: Path
    restored_file_count: int
    payload_sha256: str

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        for field in ("output_dir", "snapshot_dir", "receipt_path"):
            payload[field] = str(payload[field])
        return payload


def build_backup(
    project_or_root: Project | Path | str,
    output_dir: Path = Path("build/backup"),
    *,
    source_date_epoch: int | None = None,
    patterns: Sequence[str] = DEFAULT_PATTERNS,
    clean: bool = True,
) -> BackupResult:
    """Build a deterministic, self-verifying critical-state ZIP snapshot."""

    project = _project(project_or_root)
    destination = _output_dir(project, output_dir)
    if clean:
        shutil.rmtree(destination, ignore_errors=True)
    destination.mkdir(parents=True, exist_ok=True)
    epoch = _epoch(source_date_epoch)
    created_at = datetime.fromtimestamp(epoch, UTC).replace(microsecond=0)
    archive_path = destination / "gfjd-critical-state.zip"
    receipt_path = destination / "backup-build.json"
    if archive_path.exists():
        raise ResilienceError(f"Backup archive already exists: {archive_path}")

    source_files = _expand_inputs(project, patterns)
    relative_paths = {path.relative_to(project.root).as_posix() for path in source_files}
    missing_required = sorted(set(REQUIRED_FILES) - relative_paths)
    if missing_required:
        raise ResilienceError("Required backup inputs are missing: " + ", ".join(missing_required))

    with tempfile.TemporaryDirectory(prefix=".gfjd-backup-", dir=destination) as temp_name:
        snapshot = Path(temp_name) / "gfjd-critical-state"
        snapshot.mkdir(parents=True)
        for source in source_files:
            relative = source.relative_to(project.root)
            target = snapshot / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)

        payload_entries = _entries(snapshot)
        payload_sha256 = _entry_set_sha256(payload_entries)
        metadata = {
            "schema_version": "1.0",
            "project_id": str(project.project_config["id"]),
            "project_version": str(project.project_config["version"]),
            "created_at": created_at.isoformat(),
            "source_date_epoch": epoch,
            "file_count": len(payload_entries),
            "payload_sha256": payload_sha256,
            "included_patterns": list(patterns),
            "required_files": list(REQUIRED_FILES),
            "scope_note": (
                "Public repository critical state only; source-system objects, credentials, "
                "restricted data, and external service configuration are excluded."
            ),
        }
        _validate_backup_metadata(snapshot / "schemas/backup.schema.json", metadata)
        write_json(snapshot / "BACKUP.json", metadata)
        manifest_entries = _entries(snapshot)
        _write_manifest(snapshot / "MANIFEST.sha256", manifest_entries)
        _normalise_timestamps(snapshot, epoch)
        _deterministic_zip(snapshot, archive_path, epoch)

    archive_sha256 = sha256_file(archive_path)
    verification = verify_backup(archive_path)
    if verification:
        archive_path.unlink(missing_ok=True)
        raise ResilienceError("Built backup failed verification: " + "; ".join(verification))
    receipt = {
        "schema_version": "1.0",
        "archive_path": archive_path.relative_to(project.root).as_posix(),
        "archive_sha256": archive_sha256,
        "source_date_epoch": epoch,
        "file_count": len(source_files),
        "payload_sha256": payload_sha256,
        "verified": True,
    }
    write_json(receipt_path, receipt)
    return BackupResult(
        archive_path=archive_path,
        receipt_path=receipt_path,
        archive_sha256=archive_sha256,
        file_count=len(source_files),
        payload_sha256=payload_sha256,
    )


def verify_backup(archive_path: Path) -> list[str]:
    """Verify archive safety, CRCs, schema, manifest, required files, and payload digest."""

    archive = archive_path.expanduser().resolve()
    if not archive.is_file():
        return [f"Backup archive does not exist: {archive}"]
    errors: list[str] = []
    try:
        with zipfile.ZipFile(archive) as bundle:
            infos = bundle.infolist()
            if len(infos) > 20_000:
                errors.append("Backup contains more than 20,000 entries")
            total_uncompressed = sum(info.file_size for info in infos)
            if total_uncompressed > 2 * 1024 * 1024 * 1024:
                errors.append("Backup exceeds the 2 GiB uncompressed safety limit")
            names: set[str] = set()
            for info in infos:
                path = Path(info.filename)
                if path.is_absolute() or ".." in path.parts:
                    errors.append(f"Unsafe backup member path: {info.filename}")
                if info.filename in names:
                    errors.append(f"Duplicate backup member path: {info.filename}")
                names.add(info.filename)
                mode = (info.external_attr >> 16) & 0o170000
                if mode == 0o120000:
                    errors.append(f"Backup contains a symbolic link: {info.filename}")
            file_names = sorted(name for name in names if not name.endswith("/"))
            roots = {Path(name).parts[0] for name in file_names if Path(name).parts}
            if roots != {"gfjd-critical-state"}:
                errors.append("Backup must contain exactly one gfjd-critical-state root")
                return errors
            prefix = "gfjd-critical-state/"
            manifest_name = prefix + "MANIFEST.sha256"
            metadata_name = prefix + "BACKUP.json"
            if manifest_name not in names:
                errors.append("Backup is missing MANIFEST.sha256")
                return errors
            if metadata_name not in names:
                errors.append("Backup is missing BACKUP.json")
                return errors
            corrupt = bundle.testzip()
            if corrupt:
                errors.append(f"Backup CRC failure: {corrupt}")
            manifest_text = bundle.read(manifest_name).decode("utf-8")
            expected = _parse_manifest(manifest_text, errors)
            actual_relatives = {
                name.removeprefix(prefix) for name in file_names if name != manifest_name
            }
            errors.extend(
                f"Manifest file missing from archive: {relative}"
                for relative in sorted(set(expected) - actual_relatives)
            )
            errors.extend(
                f"Unmanifested backup file: {relative}"
                for relative in sorted(actual_relatives - set(expected))
            )
            for relative, digest in sorted(expected.items()):
                name = prefix + relative
                if name in names and sha256_bytes(bundle.read(name)) != digest:
                    errors.append(f"Backup checksum mismatch: {relative}")
            try:
                metadata = json.loads(bundle.read(metadata_name).decode("utf-8"))
                schema = json.loads(
                    bundle.read(prefix + "schemas/backup.schema.json").decode("utf-8")
                )
                _validate_metadata_object(schema, metadata, errors)
            except (KeyError, UnicodeError, json.JSONDecodeError) as exc:
                errors.append(f"Could not read backup metadata/schema: {exc}")
                return errors
            if isinstance(metadata, dict):
                payload_entries = [
                    (digest, relative)
                    for relative, digest in sorted(expected.items())
                    if relative != "BACKUP.json"
                ]
                if metadata.get("file_count") != len(payload_entries):
                    errors.append("Backup file_count does not match manifest payload")
                if metadata.get("payload_sha256") != _entry_set_sha256(payload_entries):
                    errors.append("Backup payload_sha256 does not match manifest payload")
                required = metadata.get("required_files", [])
                if isinstance(required, list):
                    for relative in required:
                        if relative not in expected:
                            errors.append(f"Required backup file is absent: {relative}")
    except (OSError, zipfile.BadZipFile) as exc:
        errors.append(f"Could not open backup archive: {exc}")
    return errors


def restore_backup(
    archive_path: Path,
    destination: Path,
    *,
    clean: bool = False,
) -> int:
    """Safely restore a verified backup into an empty destination directory."""

    errors = verify_backup(archive_path)
    if errors:
        raise ResilienceError("Cannot restore invalid backup: " + "; ".join(errors))
    target = destination.expanduser().resolve()
    if target.exists():
        if clean:
            shutil.rmtree(target)
        elif any(target.iterdir()):
            raise ResilienceError(f"Restore destination is not empty: {target}")
    target.mkdir(parents=True, exist_ok=True)
    restored = 0
    prefix = "gfjd-critical-state/"
    with zipfile.ZipFile(archive_path.expanduser().resolve()) as bundle:
        for info in sorted(bundle.infolist(), key=lambda item: item.filename):
            if info.is_dir():
                continue
            relative_name = info.filename.removeprefix(prefix)
            relative = Path(relative_name)
            if not relative_name or relative.is_absolute() or ".." in relative.parts:
                raise ResilienceError(f"Unsafe restore member: {info.filename}")
            output = target / relative
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(bundle.read(info.filename))
            restored += 1
    restored_errors = verify_restored_snapshot(target)
    if restored_errors:
        shutil.rmtree(target, ignore_errors=True)
        raise ResilienceError(
            "Restored snapshot failed verification: " + "; ".join(restored_errors)
        )
    return restored


def verify_restored_snapshot(snapshot_dir: Path) -> list[str]:
    """Verify the hash manifest and payload digest of a restored snapshot directory."""

    root = snapshot_dir.expanduser().resolve()
    manifest_path = root / "MANIFEST.sha256"
    metadata_path = root / "BACKUP.json"
    if not manifest_path.is_file():
        return [f"Restored snapshot is missing MANIFEST.sha256: {root}"]
    if not metadata_path.is_file():
        return [f"Restored snapshot is missing BACKUP.json: {root}"]
    errors: list[str] = []
    expected = _parse_manifest(manifest_path.read_text(encoding="utf-8"), errors)
    actual = {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() and path.name != "MANIFEST.sha256"
    }
    errors.extend(f"Restored file missing: {path}" for path in sorted(set(expected) - actual))
    errors.extend(f"Unexpected restored file: {path}" for path in sorted(actual - set(expected)))
    for relative, digest in sorted(expected.items()):
        path = root / relative
        if path.is_file() and sha256_file(path) != digest:
            errors.append(f"Restored checksum mismatch: {relative}")
    try:
        metadata = read_json(metadata_path)
        schema = read_json(root / "schemas/backup.schema.json")
        _validate_metadata_object(schema, metadata, errors)
        payload_entries = [
            (digest, relative)
            for relative, digest in sorted(expected.items())
            if relative != "BACKUP.json"
        ]
        if isinstance(metadata, dict):
            if metadata.get("file_count") != len(payload_entries):
                errors.append("Restored file_count does not match manifest payload")
            if metadata.get("payload_sha256") != _entry_set_sha256(payload_entries):
                errors.append("Restored payload_sha256 does not match manifest payload")
    except (OSError, ValueError) as exc:
        errors.append(f"Could not validate restored metadata: {exc}")
    return errors


def rehearse_restore(
    project_or_root: Project | Path | str,
    archive_path: Path,
    output_dir: Path = Path("build/restore-rehearsal"),
    *,
    clean: bool = True,
) -> RestoreResult:
    """Perform a destructive clean-room restore under build/ and emit a receipt."""

    project = _project(project_or_root)
    archive = _confined(project, archive_path)
    output = _output_dir(project, output_dir)
    if clean:
        shutil.rmtree(output, ignore_errors=True)
    output.mkdir(parents=True, exist_ok=True)
    snapshot = output / "snapshot"
    restored = restore_backup(archive, snapshot)
    metadata = read_json(snapshot / "BACKUP.json")
    receipt_path = output / "restore-receipt.json"
    receipt = {
        "schema_version": "1.0",
        "archive_path": archive.relative_to(project.root).as_posix(),
        "archive_sha256": sha256_file(archive),
        "snapshot_path": snapshot.relative_to(project.root).as_posix(),
        "restored_file_count": restored,
        "payload_sha256": metadata["payload_sha256"],
        "verification_errors": [],
        "verified": True,
    }
    write_json(receipt_path, receipt)
    return RestoreResult(
        output_dir=output,
        snapshot_dir=snapshot,
        receipt_path=receipt_path,
        restored_file_count=restored,
        payload_sha256=str(metadata["payload_sha256"]),
    )


def verify_restore_receipt(
    project_or_root: Project | Path | str,
    receipt_path: Path,
) -> list[str]:
    """Verify a restore receipt against the current archive and restored snapshot."""

    project = _project(project_or_root)
    receipt_file = _confined(project, receipt_path)
    if not receipt_file.is_file():
        return [f"Restore receipt does not exist: {receipt_file}"]
    try:
        receipt = read_json(receipt_file)
    except (OSError, ValueError) as exc:
        return [f"Could not read restore receipt: {exc}"]
    if not isinstance(receipt, dict):
        return ["Restore receipt root must be an object"]
    errors: list[str] = []
    try:
        archive = _confined(project, Path(str(receipt.get("archive_path") or "")))
        snapshot = _confined(project, Path(str(receipt.get("snapshot_path") or "")))
    except ResilienceError as exc:
        return [str(exc)]
    if not archive.is_file():
        errors.append("Restore receipt archive is missing")
    elif sha256_file(archive) != receipt.get("archive_sha256"):
        errors.append("Restore receipt archive checksum mismatch")
    restored_errors = verify_restored_snapshot(snapshot)
    errors.extend(restored_errors)
    if not restored_errors:
        metadata = read_json(snapshot / "BACKUP.json")
        if metadata.get("payload_sha256") != receipt.get("payload_sha256"):
            errors.append("Restore receipt payload digest mismatch")
        file_count = sum(1 for path in snapshot.rglob("*") if path.is_file())
        if file_count != receipt.get("restored_file_count"):
            errors.append("Restore receipt file count mismatch")
    return errors


def _project(value: Project | Path | str) -> Project:
    return value if isinstance(value, Project) else load_project(Path(value))


def _confined(project: Project, value: Path) -> Path:
    candidate = value.expanduser()
    resolved = (
        candidate.resolve() if candidate.is_absolute() else (project.root / candidate).resolve()
    )
    try:
        resolved.relative_to(project.root)
    except ValueError as exc:
        raise ResilienceError(f"Path escapes repository root: {value}") from exc
    return resolved


def _output_dir(project: Project, value: Path) -> Path:
    resolved = _confined(project, value)
    try:
        resolved.relative_to(project.root / "build")
    except ValueError as exc:
        raise ResilienceError("Backup and restore products must be written under build/") from exc
    return resolved


def _expand_inputs(project: Project, patterns: Sequence[str]) -> list[Path]:
    paths: set[Path] = set()
    for pattern in patterns:
        if not pattern or Path(pattern).is_absolute() or ".." in Path(pattern).parts:
            raise ResilienceError(f"Unsafe backup input pattern: {pattern!r}")
        for path in project.root.glob(pattern):
            resolved = path.resolve()
            try:
                resolved.relative_to(project.root)
            except ValueError as exc:
                raise ResilienceError(f"Backup input escapes repository root: {path}") from exc
            if resolved.is_file() and not _excluded(resolved, project.root):
                paths.add(resolved)
    return sorted(paths)


def _excluded(path: Path, root: Path) -> bool:
    relative = path.relative_to(root)
    blocked_parts = {"build", "dist", ".git", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
    return bool(set(relative.parts) & blocked_parts) or path.name in {
        "MANIFEST.sha256",
        ".coverage",
    }


def _entries(root: Path) -> list[tuple[str, str]]:
    return [
        (sha256_file(path), path.relative_to(root).as_posix())
        for path in sorted(root.rglob("*"))
        if path.is_file() and path.name != "MANIFEST.sha256"
    ]


def _entry_set_sha256(entries: Iterable[tuple[str, str]]) -> str:
    payload = [{"path": relative, "sha256": digest} for digest, relative in entries]
    return sha256_bytes(canonical_json_bytes(payload))


def _write_manifest(path: Path, entries: Iterable[tuple[str, str]]) -> None:
    path.write_text(
        "\n".join(f"{digest}  {relative}" for digest, relative in entries) + "\n",
        encoding="utf-8",
    )


def _parse_manifest(text: str, errors: list[str]) -> dict[str, str]:
    expected: dict[str, str] = {}
    for line_number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            digest, relative = line.split("  ", 1)
        except ValueError:
            errors.append(f"Malformed backup manifest line {line_number}")
            continue
        path = Path(relative)
        if path.is_absolute() or ".." in path.parts:
            errors.append(f"Unsafe backup manifest path on line {line_number}: {relative}")
            continue
        if relative in expected:
            errors.append(f"Duplicate backup manifest path: {relative}")
            continue
        if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
            errors.append(f"Invalid backup SHA-256 on line {line_number}")
            continue
        expected[relative] = digest
    return expected


def _validate_backup_metadata(schema_path: Path, metadata: dict[str, Any]) -> None:
    schema = read_json(schema_path)
    errors: list[str] = []
    _validate_metadata_object(schema, metadata, errors)
    if errors:
        raise ResilienceError("BACKUP.json failed schema: " + "; ".join(errors))


def _validate_metadata_object(
    schema: dict[str, Any],
    metadata: Any,
    errors: list[str],
) -> None:
    for error in sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(metadata),
        key=lambda item: list(item.path),
    ):
        location = ".".join(str(part) for part in error.path)
        errors.append(f"BACKUP.json{'.' + location if location else ''}: {error.message}")


def _normalise_timestamps(root: Path, epoch: int) -> None:
    for path in root.rglob("*"):
        os.utime(path, (epoch, epoch), follow_symlinks=False)
    os.utime(root, (epoch, epoch), follow_symlinks=False)


def _deterministic_zip(source_dir: Path, destination: Path, epoch: int) -> None:
    timestamp = time.gmtime(max(epoch, 315532800))[:6]
    with zipfile.ZipFile(
        destination,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as archive:
        for path in sorted(source_dir.rglob("*")):
            if not path.is_file():
                continue
            relative = Path(source_dir.name) / path.relative_to(source_dir)
            info = zipfile.ZipInfo(relative.as_posix(), date_time=timestamp)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            info.create_system = 3
            archive.writestr(
                info,
                path.read_bytes(),
                compress_type=zipfile.ZIP_DEFLATED,
                compresslevel=9,
            )


def _epoch(value: int | None) -> int:
    if value is not None:
        return int(value)
    environment = os.getenv("SOURCE_DATE_EPOCH")
    return int(environment) if environment else int(datetime.now(UTC).timestamp())
