from __future__ import annotations

from pathlib import Path

import pytest

from gfjd.io import sha256_file
from gfjd.project import load_project
from gfjd.release import ReleaseError, build_release, diff_releases, verify_release


def test_release_build_is_deterministic_and_verifiable(project_root: Path, tmp_path: Path) -> None:
    project = load_project(project_root)
    epoch = 1784419200
    first = build_release(
        project,
        version="0.3.0-test",
        output_root=tmp_path / "first",
        source_date_epoch=epoch,
        allow_version_override=True,
    )
    second = build_release(
        project,
        version="0.3.0-test",
        output_root=tmp_path / "second",
        source_date_epoch=epoch,
        allow_version_override=True,
    )
    first_dir = Path(first["release_dir"])
    second_dir = Path(second["release_dir"])
    first_zip = Path(first["archive_path"])
    second_zip = Path(second["archive_path"])

    assert verify_release(first_dir) == []
    assert verify_release(second_dir) == []
    assert sha256_file(first_zip) == sha256_file(second_zip)
    diff = diff_releases(first_dir, second_dir)
    for table in diff["tables"].values():
        assert table["added"] == []
        assert table["removed"] == []
        assert table["changed"] == []
    assert (first_dir / "programme/programme-status.json").is_file()
    assert (first_dir / "MANIFEST.sha256").is_file()


def test_stable_release_is_blocked_until_g6_passes(project_root: Path, tmp_path: Path) -> None:
    project = load_project(project_root)
    with pytest.raises(ReleaseError, match="requires G6"):
        build_release(
            project,
            version="1.0.0",
            output_root=tmp_path,
            source_date_epoch=1784419200,
            allow_version_override=True,
        )


def test_release_verifier_detects_tampering(project_root: Path, tmp_path: Path) -> None:
    project = load_project(project_root)
    result = build_release(
        project,
        version="0.3.0-tamper-test",
        output_root=tmp_path,
        source_date_epoch=1784419200,
        allow_version_override=True,
    )
    release_dir = Path(result["release_dir"])
    (release_dir / "README.md").write_text("tampered\n", encoding="utf-8")
    assert "Checksum mismatch: README.md" in verify_release(release_dir)
