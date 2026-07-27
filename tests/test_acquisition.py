from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from gfjd.acquisition import (
    AcquisitionError,
    acquire_local_file,
    read_manifest,
    validate_public_url,
    verify_acquisition_manifest,
)
from gfjd.project import load_project


def test_controlled_local_acquisition_writes_hash_and_manifest(
    project_root: Path, tmp_path: Path
) -> None:
    project = load_project(project_root)
    destination = tmp_path / "raw"
    source = tmp_path / "source.txt"
    source.write_text("family justice source\n", encoding="utf-8")

    manifest, manifest_path = acquire_local_file(
        project,
        source_id="TEST-SOURCE",
        input_path=source,
        destination_root=destination,
        rights_status="cleared",
        redistribution_status="allowed",
    )

    assert manifest["stored_path"]
    assert (destination / manifest["stored_path"]).read_bytes() == source.read_bytes()
    assert read_manifest(manifest_path)["sha256"] == manifest["sha256"]
    assert verify_acquisition_manifest(project, manifest_path) == []
    schema = json.loads(
        (project_root / "schemas/acquisition_manifest.schema.json").read_text(encoding="utf-8")
    )
    errors = list(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(manifest)
    )
    assert errors == []


def test_restricted_source_is_manifest_only(project_root: Path, tmp_path: Path) -> None:
    project = load_project(project_root)
    destination = tmp_path / "raw"
    source = tmp_path / "restricted.pdf"
    source.write_bytes(b"not really a pdf")

    manifest, manifest_path = acquire_local_file(
        project,
        source_id="TEST-RESTRICTED",
        input_path=source,
        destination_root=destination,
        rights_status="restricted",
        redistribution_status="metadata_only",
    )

    assert manifest["stored_path"] == ""
    assert manifest["status"] == "metadata_only"
    assert manifest_path.is_file()
    assert not (destination / "files").exists()


def test_public_url_guard_rejects_private_address() -> None:
    with pytest.raises(AcquisitionError, match="non-public address"):
        validate_public_url("https://127.0.0.1/private")


def test_local_acquisition_rejects_expected_checksum_mismatch(
    project_root: Path, tmp_path: Path
) -> None:
    project = load_project(project_root)
    source = tmp_path / "source.txt"
    source.write_text("content", encoding="utf-8")
    with pytest.raises(AcquisitionError, match="Checksum mismatch"):
        acquire_local_file(
            project,
            source_id="TEST-SOURCE",
            input_path=source,
            destination_root=tmp_path / "raw",
            expected_sha256="0" * 64,
        )


def test_local_acquisition_rejects_missing_input(
    project_root: Path, tmp_path: Path
) -> None:
    with pytest.raises(AcquisitionError, match="does not exist"):
        acquire_local_file(
            load_project(project_root),
            source_id="TEST-MISSING",
            input_path=tmp_path / "missing.csv",
            destination_root=tmp_path / "raw",
        )


def test_acquisition_verification_detects_tampered_stored_file(
    project_root: Path, tmp_path: Path
) -> None:
    project = load_project(project_root)
    destination = tmp_path / "raw"
    source = tmp_path / "source.txt"
    source.write_text("original", encoding="utf-8")
    manifest, manifest_path = acquire_local_file(
        project,
        source_id="TEST-TAMPER",
        input_path=source,
        destination_root=destination,
        rights_status="cleared",
        redistribution_status="allowed",
    )
    stored = destination / manifest["stored_path"]
    stored.write_text("tampered", encoding="utf-8")
    errors = verify_acquisition_manifest(project, manifest_path)
    assert any("checksum does not match" in error for error in errors)


def test_public_url_guard_rejects_credentials_and_plain_http() -> None:
    with pytest.raises(AcquisitionError, match="scheme"):
        validate_public_url("http://example.com/data")
    with pytest.raises(AcquisitionError, match="Credentials"):
        validate_public_url("https://user:secret@example.com/data")
